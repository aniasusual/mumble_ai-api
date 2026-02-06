"""
Agent tools directory.

Note: Custom user context tools are not needed. Agno automatically handles:
- User memories: enable_user_memories=True on agents
- Session history: Automatically saved when db is configured
- User context: user_id from JWT, job_id from run session_id

All agents in this application use Agno's built-in memory and session management.
No custom tools are required for basic user context operations.
"""

from .user_session_context import (
    get_user_session_context,
    get_current_user_id,
    get_current_job_id,
)
from .realtime_session import create_realtime_session

__all__ = [
    "get_user_session_context",
    "get_current_user_id",
    "get_current_job_id",
    "create_realtime_session",
]
