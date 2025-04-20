"""InMemoryBackend implementation."""
import json
import os.path
from typing import Dict, Generic

from fastapi_sessions.backends.session_backend import (
    BackendError,
    SessionBackend,
    SessionModel,
)
from fastapi_sessions.frontends.session_frontend import ID
from pydantic import BaseModel
import threading

class JsonFileMemoryBackend(Generic[ID, SessionModel], SessionBackend[ID, SessionModel]):
    """Stores session data in a dictionary."""

    def __init__(self, filename, model: BaseModel) -> None:
        """Initialize a new json file database."""
        self.filename = filename
        self.model = model
        self.lock = threading.Lock()
        with self.lock:
            if not os.path.exists(self.filename):
                with open(self.filename, mode='w') as fp:
                    json.dump({}, fp, indent=4)

    async def create(self, session_id: ID, data: SessionModel):
        """Create a new session entry."""
        with self.lock:
            sessions = await self.read_sessions()
            str_session_id = str(session_id)
            if sessions.get(str_session_id):
                raise BackendError("create can't overwrite an existing session")
            sessions[str_session_id] = data.model_dump()
            await self.write_sessions(sessions)

    async def read(self, session_id: ID):
        """Read an existing session data."""
        with self.lock:
            sessions = await self.read_sessions()
            data = sessions.get(str(session_id))
            if not data:
                return
            return self.model.model_validate(data)

    async def update(self, session_id: ID, data: SessionModel) -> None:
        """Update an existing session."""
        with self.lock:
            sessions = await self.read_sessions()
            str_session_id = str(session_id)
            if sessions.get(str_session_id):
                sessions[str_session_id] = data.model_dump()
            else:
                raise BackendError("session does not exist, cannot update")
            await self.write_sessions(sessions)

    async def delete(self, session_id: ID) -> None:
        """D"""
        with self.lock:
            sessions = await self.read_sessions()
            str_session_id = str(session_id)
            if sessions.get(str_session_id):
                del sessions[str_session_id]
                await self.write_sessions(sessions)

    async def read_sessions(self):
        with open(self.filename, mode='r') as fp:
            sessions = json.load(fp)
        return sessions

    async def write_sessions(self, sessions):
        with open(self.filename, mode='w') as fp:
            json.dump(sessions, fp, indent=4)

