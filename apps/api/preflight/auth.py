import hashlib
import secrets
import time
import os
from collections import defaultdict, deque
from threading import Lock
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from .db import User, Session, Organization, Membership, Workspace, Project, AuditEvent

router = APIRouter(prefix="/api/v1")
ph = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)
DUMMY_HASH = ph.hash(secrets.token_hex(24))
ROLE_RANK = {"viewer": 0, "developer": 1, "admin": 2, "owner": 3}
limits = defaultdict(deque)
limit_lock = Lock()


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def email_valid(cls, value):
        value = value.strip().lower()
        if (
            value.count("@") != 1
            or "." not in value.split("@")[1]
            or any(c.isspace() for c in value)
        ):
            raise ValueError("A valid email address is required")
        return value


class Name(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def clean(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be blank")
        return value.strip()


class MemberInput(BaseModel):
    email: str
    role: str

    @field_validator("role")
    @classmethod
    def role_valid(cls, v):
        if v not in {"admin", "developer", "viewer"}:
            raise ValueError("Role must be admin, developer or viewer")
        return v


async def get_db(request: Request):
    with request.app.state.db.sessions() as session:
        yield session


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


def current_user(request: Request, db=Depends(get_db)):
    token = request.cookies.get("preflight_session", "")
    session = db.get(Session, digest(token)) if token else None
    if not session or session.expires < time.time():
        raise HTTPException(401, "Sign in required")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        csrf = request.headers.get("x-csrf-token", "")
        if not secrets.compare_digest(csrf, session.csrf):
            raise HTTPException(403, "CSRF token required")
    return db.get(User, session.user_id)


def authorize(db, user, org_id, role="viewer"):
    membership = db.scalar(
        select(Membership).where(Membership.user_id == user.id, Membership.org_id == org_id)
    )
    if not membership:
        raise HTTPException(404, "Resource not found")
    if ROLE_RANK[membership.role] < ROLE_RANK[role]:
        raise HTTPException(403, "Insufficient role")
    return membership


def project_access(db, user, project_id, role="viewer"):
    project = db.get(Project, project_id)
    workspace = db.get(Workspace, project.workspace_id) if project else None
    if not workspace:
        raise HTTPException(404, "Resource not found")
    authorize(db, user, workspace.org_id, role)
    return project, workspace.org_id


def audit(db, user, org_id, action, subject):
    db.add(AuditEvent(org_id=org_id, user_id=user.id, action=action, subject=subject))


def rate_limit(request):
    key = request.client.host if request.client else "unknown"
    with limit_lock:
        ts = time.monotonic()
        # Bound memory even when requests use many source addresses.
        if len(limits) > 10000:
            limits.clear()
        q = limits[key]
        while q and q[0] < ts - 60:
            q.popleft()
        if len(q) >= 20:
            raise HTTPException(429, "Try again in a minute")
        q.append(ts)


def new_session(db, user, response):
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    db.add(Session(digest=digest(token), user_id=user.id, csrf=csrf, expires=time.time() + 86400))
    db.commit()
    response.set_cookie(
        "preflight_session",
        token,
        httponly=True,
        secure=os.environ.get("PREFLIGHT_COOKIE_SECURE", "false").lower() == "true",
        samesite="strict",
        max_age=86400,
        path="/",
    )
    return {"id": user.id, "email": user.email, "csrf_token": csrf}


@router.post("/auth/register", status_code=201)
def register(body: Credentials, request: Request, response: Response, db=Depends(get_db)):
    rate_limit(request)
    user = User(email=body.email, password=ph.hash(body.password))
    org = Organization(name="My organization")
    db.add_all([user, org])
    try:
        db.flush()
        db.add(Membership(user_id=user.id, org_id=org.id, role="owner"))
        db.add(Workspace(org_id=org.id, name="My workspace"))
        audit(db, user, org.id, "user.register", user.id)
        return new_session(db, user, response)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Registration unavailable for this email")


@router.post("/auth/login")
def login(body: Credentials, request: Request, response: Response, db=Depends(get_db)):
    rate_limit(request)
    user = db.scalar(select(User).where(User.email == body.email))
    try:
        ph.verify(user.password if user else DUMMY_HASH, body.password)
    except VerificationError:
        raise HTTPException(401, "Invalid email or password")
    if not user:
        raise HTTPException(401, "Invalid email or password")
    return new_session(db, user, response)


@router.get("/auth/me")
def me(request: Request, user=Depends(current_user), db=Depends(get_db)):
    session = db.get(Session, digest(request.cookies["preflight_session"]))
    memberships = db.scalars(select(Membership).where(Membership.user_id == user.id)).all()
    return {
        "id": user.id,
        "email": user.email,
        "csrf_token": session.csrf,
        "organizations": [
            {"id": m.org_id, "name": db.get(Organization, m.org_id).name, "role": m.role}
            for m in memberships
        ],
    }


@router.post("/auth/logout")
def logout(request: Request, response: Response, user=Depends(current_user), db=Depends(get_db)):
    session = db.get(Session, digest(request.cookies["preflight_session"]))
    db.delete(session)
    db.commit()
    response.delete_cookie("preflight_session", path="/")
    return {"ok": True}


@router.post("/organizations", status_code=201)
def create_org(body: Name, user=Depends(current_user), db=Depends(get_db)):
    org = Organization(name=body.name)
    db.add(org)
    db.flush()
    db.add(Membership(org_id=org.id, user_id=user.id, role="owner"))
    audit(db, user, org.id, "organization.create", org.id)
    db.commit()
    return {"id": org.id, "name": org.name}


@router.get("/organizations/{org_id}/members")
def members(org_id: str, user=Depends(current_user), db=Depends(get_db)):
    authorize(db, user, org_id)
    return [
        {"email": db.get(User, m.user_id).email, "role": m.role}
        for m in db.scalars(select(Membership).where(Membership.org_id == org_id))
    ]


@router.post("/organizations/{org_id}/members", status_code=201)
def add_member(org_id: str, body: MemberInput, user=Depends(current_user), db=Depends(get_db)):
    caller = authorize(db, user, org_id, "admin")
    if body.role == "admin" and caller.role != "owner":
        raise HTTPException(403, "Only owners can assign admins")
    target = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    if not target:
        raise HTTPException(404, "User must register first")
    if db.scalar(
        select(Membership).where(Membership.user_id == target.id, Membership.org_id == org_id)
    ):
        raise HTTPException(409, "Already a member")
    db.add(Membership(org_id=org_id, user_id=target.id, role=body.role))
    audit(db, user, org_id, "member.add", target.id)
    db.commit()
    return {"email": target.email, "role": body.role}


@router.get("/workspaces")
def workspaces(user=Depends(current_user), db=Depends(get_db)):
    orgs = select(Membership.org_id).where(Membership.user_id == user.id)
    return [
        {"id": w.id, "org_id": w.org_id, "name": w.name}
        for w in db.scalars(
            select(Workspace).where(Workspace.org_id.in_(orgs)).order_by(Workspace.name)
        )
    ]


@router.post("/organizations/{org_id}/workspaces", status_code=201)
def create_workspace(org_id: str, body: Name, user=Depends(current_user), db=Depends(get_db)):
    authorize(db, user, org_id, "admin")
    w = Workspace(org_id=org_id, name=body.name)
    db.add(w)
    db.flush()
    audit(db, user, org_id, "workspace.create", w.id)
    db.commit()
    return {"id": w.id, "name": w.name, "org_id": org_id}


@router.get("/workspaces/{workspace_id}/projects")
def projects(
    workspace_id: str,
    offset: int = 0,
    limit: int = 50,
    user=Depends(current_user),
    db=Depends(get_db),
):
    w = db.get(Workspace, workspace_id)
    if not w:
        raise HTTPException(404, "Resource not found")
    authorize(db, user, w.org_id)
    if offset < 0 or not 1 <= limit <= 100:
        raise HTTPException(422, "Invalid pagination")
    return [
        {"id": p.id, "name": p.name, "workspace_id": p.workspace_id}
        for p in db.scalars(
            select(Project)
            .where(Project.workspace_id == workspace_id)
            .order_by(Project.name)
            .offset(offset)
            .limit(limit)
        )
    ]


@router.post("/workspaces/{workspace_id}/projects", status_code=201)
def create_project(workspace_id: str, body: Name, user=Depends(current_user), db=Depends(get_db)):
    w = db.get(Workspace, workspace_id)
    if not w:
        raise HTTPException(404, "Resource not found")
    authorize(db, user, w.org_id, "developer")
    p = Project(workspace_id=w.id, name=body.name)
    db.add(p)
    db.flush()
    audit(db, user, w.org_id, "project.create", p.id)
    db.commit()
    return {"id": p.id, "name": p.name, "workspace_id": p.workspace_id}


@router.get("/organizations/{org_id}/audit")
def audit_events(org_id: str, user=Depends(current_user), db=Depends(get_db)):
    authorize(db, user, org_id, "admin")
    return [
        {"action": e.action, "subject": e.subject, "at": e.at}
        for e in db.scalars(
            select(AuditEvent)
            .where(AuditEvent.org_id == org_id)
            .order_by(AuditEvent.at.desc())
            .limit(100)
        )
    ]
