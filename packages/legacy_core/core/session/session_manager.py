"""Cognitive Session Manager - Core Engine."""

import uuid


class CognitiveSessionManager:
    """The main cognitive session manager."""

    def __init__(self):
        self._sessions = {}
        self._metrics = {
            "created": 0,
            "active": 0,
            "completed": 0,
            "failed": 0,
        }

    def create_session(
        self,
        user_id="",
        hospital_id="",
        tenant_id="",
        session_type="general",
        intent="",
        metadata=None,
    ):
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        correlation_id = f"corr_{uuid.uuid4().hex[:16]}"
        context_id = f"ctx_{uuid.uuid4().hex[:16]}"

        from core.session.session import CognitiveSession, SessionMetadata

        metadata_obj = SessionMetadata(
            session_id=session_id,
            correlation_id=correlation_id,
            context_id=context_id,
        )

        session = CognitiveSession(
            metadata=metadata_obj,
            user_id=user_id,
            hospital_id=hospital_id,
            tenant_id=tenant_id,
            session_type=session_type,
            intent=intent,
        )

        self._sessions[session_id] = session
        self._metrics["created"] += 1
        return session

    def get_session(self, session_id):
        return self._sessions.get(session_id)

    def activate_session(self, session_id):
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.activate()
        self._metrics["active"] += 1
        return True

    def pause_session(self, session_id):
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.pause()
        return True

    def resume_session(self, session_id):
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.resume()
        return True

    def complete_session(self, session_id, result=None):
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.complete(result)
        self._metrics["completed"] += 1
        self._metrics["active"] = max(0, self._metrics["active"] - 1)
        return True

    def fail_session(self, session_id, error):
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.fail(error)
        self._metrics["failed"] += 1
        self._metrics["active"] = max(0, self._metrics["active"] - 1)
        return True

    def cancel_session(self, session_id, reason=""):
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.cancel(reason)
        return True

    def archive_session(self, session_id):
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.archive()
        return True

    def find_by_user(self, user_id):
        return [s for s in self._sessions.values() if s.user_id == user_id]

    def find_active(self):
        return [s for s in self._sessions.values() if s.state == "active"]

    def get_metrics(self):
        return self._metrics.copy()
