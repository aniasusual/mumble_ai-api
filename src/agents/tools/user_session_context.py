"""Tool for accessing user and session context information."""
from typing import Optional
from agno.run import RunContext


def get_user_session_context(run_context: RunContext) -> dict:
    """
    Get current user and session information from the request context.

    This tool accesses user_id from JWT and job_id from the run request
    (session_id field mapped to job id).

    Returns:
        dict: Dictionary containing:
            - user_id: The authenticated user's ID (from JWT 'sub' claim)
            - job_id: The current job ID (from run session_id)
            - base_language: User's base language (from dependencies)
            - metadata: Additional request metadata if available
    """
    return {
        "user_id": run_context.user_id,
        "job_id": run_context.session_id,
        "base_language": run_context.dependencies.get("base_language") if run_context.dependencies else None,
        "metadata": run_context.metadata if run_context.metadata else None,
    }


def get_current_user_id(run_context: RunContext) -> str:
    """
    Get the current authenticated user's ID.

    Returns:
        str: The user ID extracted from the JWT token.
    """
    if not run_context.user_id:
        return "No user authenticated"
    return run_context.user_id


def get_current_job_id(run_context: RunContext) -> Optional[str]:
    """
    Get the current job ID.

    Returns:
        str: The job ID from the request context, or None if not available.
    """
    return run_context.session_id
