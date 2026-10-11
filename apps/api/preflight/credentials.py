"""Encrypted server-only values. The local key must accompany database backups."""

import os
from pathlib import Path
from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field
from sqlalchemy import select
from .auth import Name, current_user, get_db, authorize, audit
from .db import Credential, Workspace, Project

router = APIRouter(prefix="/api/v1")


def cipher():
    configured = os.environ.get("PREFLIGHT_CREDENTIAL_KEY")
    if configured:
        return Fernet(configured.encode())
    path = Path(os.environ.get("PREFLIGHT_CREDENTIAL_KEY_FILE", ".local/credential.key"))
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    import tempfile

    if not path.exists():
        fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".credential-")
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(Fernet.generate_key())
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, path)
            except FileExistsError:
                pass
        finally:
            os.unlink(temporary)
    if path.is_symlink() or path.stat().st_mode & 0o077:
        raise RuntimeError("Credential key must be a private regular file")
    return Fernet(path.read_bytes())


class CredentialInput(Name):
    value: str = Field(min_length=1, max_length=4096)


def workspace_access(db, user, workspace_id, role="viewer"):
    workspace = db.get(Workspace, workspace_id)
    if not workspace:
        raise HTTPException(404, "Workspace not found")
    authorize(db, user, workspace.org_id, role)
    return workspace


def metadata(item):
    return {
        "id": item.id,
        "name": item.name,
        "workspace_id": item.workspace_id,
        "active": bool(item.active),
        "created_at": item.created_at,
    }


@router.post("/workspaces/{workspace_id}/credentials", status_code=201)
def create(
    workspace_id: str, body: CredentialInput, user=Depends(current_user), db=Depends(get_db)
):
    workspace = workspace_access(db, user, workspace_id, "developer")
    item = Credential(
        workspace_id=workspace_id,
        name=body.name,
        ciphertext=cipher().encrypt(body.value.encode()).decode(),
    )
    db.add(item)
    db.flush()
    audit(db, user, workspace.org_id, "credential.create", item.id)
    db.commit()
    return metadata(item)


@router.get("/workspaces/{workspace_id}/credentials")
def list_credentials(workspace_id: str, user=Depends(current_user), db=Depends(get_db)):
    workspace_access(db, user, workspace_id)
    return [
        metadata(c)
        for c in db.scalars(select(Credential).where(Credential.workspace_id == workspace_id))
    ]


@router.post("/credentials/{credential_id}/revoke")
def revoke(credential_id: str, user=Depends(current_user), db=Depends(get_db)):
    item = db.get(Credential, credential_id)
    if not item:
        raise HTTPException(404, "Credential not found")
    workspace = workspace_access(db, user, item.workspace_id, "admin")
    item.active = 0
    audit(db, user, workspace.org_id, "credential.revoke", item.id)
    db.commit()
    return metadata(item)


def reference(db, project_id, credential_id):
    if not credential_id:
        return None
    project = db.get(Project, project_id)
    item = db.get(Credential, credential_id)
    if not item or not item.active or item.workspace_id != project.workspace_id:
        raise HTTPException(404, "Credential reference not available in project workspace")
    return item


def reveal(db, project_id, credential_id):
    item = reference(db, project_id, credential_id)
    return cipher().decrypt(item.ciphertext.encode()).decode() if item else None
