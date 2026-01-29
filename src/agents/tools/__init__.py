"""
Tools for accessing user and session context in agents.

These tools demonstrate how to access user_id and session_id
from the RunContext provided by AgentOS JWT middleware.
"""

from .user_context import (
    get_user_learning_profile,
    get_session_context,
    save_learning_progress,
)

__all__ = [
    "get_user_learning_profile",
    "get_session_context",
    "save_learning_progress",
]
