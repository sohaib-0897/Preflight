import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, event, ForeignKey, String, Text, JSON, Integer, Float, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def uid():
    return str(uuid.uuid4())


def now():
    return datetime.now(timezone.utc).isoformat()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(120))


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "org_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))


class Session(Base):
    __tablename__ = "sessions"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    csrf: Mapped[str] = mapped_column(String(64))
    expires: Mapped[float] = mapped_column(Float)


class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))


class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    framework: Mapped[str] = mapped_column(String(40), default="native")


class AgentVersion(Base):
    __tablename__ = "agent_versions"
    __table_args__ = (UniqueConstraint("agent_id", "version"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id"), index=True)
    version: Mapped[str] = mapped_column(String(60))
    fingerprint: Mapped[str] = mapped_column(String(64))
    config: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String, default=now)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    __table_args__ = (UniqueConstraint("project_id", "idempotency_key"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    version_id: Mapped[str] = mapped_column(ForeignKey("agent_versions.id"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(16), default="CREATED", index=True)
    config: Mapped[dict] = mapped_column(JSON)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[str] = mapped_column(String, default=now)
    lease_until: Mapped[float] = mapped_column(Float, default=0)
    worker_id: Mapped[str | None] = mapped_column(String, nullable=True)


class RunTransition(Base):
    __tablename__ = "run_transitions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("evaluation_runs.id"), index=True)
    previous: Mapped[str] = mapped_column(String)
    current: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(Text, default="")
    at: Mapped[str] = mapped_column(String, default=now)


class ScenarioAttempt(Base):
    __tablename__ = "scenario_attempts"
    __table_args__ = (UniqueConstraint("run_id", "scenario_id", "trial"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("evaluation_runs.id"), index=True)
    scenario_id: Mapped[str] = mapped_column(String)
    trial: Mapped[int] = mapped_column(Integer)
    result: Mapped[dict] = mapped_column(JSON)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String)
    at: Mapped[str] = mapped_column(String, default=now)


class ReleasePolicy(Base):
    __tablename__ = "release_policies"
    __table_args__ = (UniqueConstraint("project_id", "name", "version"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String)
    version: Mapped[int] = mapped_column(Integer)
    config: Mapped[dict] = mapped_column(JSON)


class HumanReview(Base):
    __tablename__ = "human_reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    attempt_id: Mapped[str] = mapped_column(ForeignKey("scenario_attempts.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    outcome: Mapped[str] = mapped_column(String)
    justification: Mapped[str] = mapped_column(Text)
    at: Mapped[str] = mapped_column(String, default=now)


# Immutable evidence tables share a payload but retain relational parent constraints.
def evidence_table(name, parent, parent_table):
    return type(name, (Base,), {
        "__tablename__": name,
        "id": mapped_column(String(36), primary_key=True, default=uid),
        parent: mapped_column(String(36), ForeignKey(parent_table + ".id"), index=True),
        "payload": mapped_column(JSON, nullable=False),
        "created_at": mapped_column(String, default=now),
    })

TraceEvent = evidence_table("trace_events", "attempt_id", "scenario_attempts")
ToolCall = evidence_table("tool_calls", "attempt_id", "scenario_attempts")
AccuracyAssessment = evidence_table("accuracy_assessments", "attempt_id", "scenario_attempts")
SecurityFinding = evidence_table("security_findings", "attempt_id", "scenario_attempts")
Artifact = evidence_table("artifacts", "run_id", "evaluation_runs")
ReleaseDecision = evidence_table("release_decisions", "run_id", "evaluation_runs")
Dataset = evidence_table("datasets", "project_id", "projects")
Scenario = evidence_table("scenarios", "dataset_id", "datasets")
GroundTruthRecord = evidence_table("ground_truth_records", "scenario_id", "scenarios")
EvaluationConfiguration = evidence_table("evaluation_configurations", "run_id", "evaluation_runs")


class Benchmark(Base):
    __tablename__ = "benchmarks"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)


BenchmarkVersion = evidence_table("benchmark_versions", "benchmark_id", "benchmarks")


class Credential(Base):
    __tablename__ = "credentials"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    ciphertext: Mapped[str] = mapped_column(Text)
    active: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(String, default=now)


class Database:
    async def readiness(self):
        from sqlalchemy import text
        async with self.async_sessions() as session:
            return await session.scalar(text("SELECT 1"))

    def __init__(self, url=None):
        url = url or os.environ.get("DATABASE_URL", "sqlite:///./.local/preflight.sqlite")
        if url.startswith("sqlite"):
            os.makedirs(".local", mode=0o700, exist_ok=True)
            os.chmod(".local", 0o700)
        self.engine = create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {}, pool_pre_ping=True)
        if url.startswith("sqlite"):
            @event.listens_for(self.engine, "connect")
            def pragmas(connection, _):
                connection.execute("PRAGMA foreign_keys=ON")
                connection.execute("PRAGMA busy_timeout=10000")
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from sqlalchemy.pool import NullPool
        async_url = url.replace("sqlite://", "sqlite+aiosqlite://", 1) if url.startswith("sqlite://") else url
        # NullPool supports CLI/tests using independent event loops without sharing driver connections.
        self.async_engine = create_async_engine(async_url, poolclass=NullPool)
        self.async_sessions = async_sessionmaker(self.async_engine, expire_on_commit=False)

    def initialize(self):
        Base.metadata.create_all(self.engine)
