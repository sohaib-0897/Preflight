import hashlib
import os
import tempfile
import uuid
from pathlib import Path
from typing import Protocol


class ArtifactStore(Protocol):
    def put(self, data: bytes) -> dict: ...
    def get(self, key: str) -> bytes: ...


class LocalStore:
    def __init__(self, root=None):
        self.root = Path(root or os.environ.get("PREFLIGHT_ARTIFACT_ROOT", ".local/artifacts")).resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    def path(self, key):
        if str(uuid.UUID(key)) != key:
            raise ValueError("Invalid artifact key")
        return self.root / key

    def put(self, data):
        if len(data) > 16*1024*1024:
            raise ValueError("Artifact exceeds 16 MiB")
        if sum(p.stat().st_size for p in self.root.iterdir() if p.is_file()) + len(data) > 64*1024*1024:
            raise ValueError("Local artifact quota exceeded")
        key = str(uuid.uuid4())
        handle, temp = tempfile.mkstemp(dir=self.root, prefix=".pending-")
        try:
            with os.fdopen(handle, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.path(key))
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        return {"key": key, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "media_type": "application/json"}

    def get(self, key):
        path = self.path(key)
        if path.is_symlink():
            raise ValueError("Symlink artifact refused")
        return path.read_bytes()
