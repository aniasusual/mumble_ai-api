"""
User context tools for accessing user_id and session_id from RunContext.

These tools demonstrate how AgentOS JWT middleware automatically injects
user_id and session_id into the RunContext, making them available to all tools.
"""

import os
from typing import Optional, Dict, Any
from agno.run import RunContext
from motor.motor_asyncio import AsyncIOMotorClient


def get_user_learning_profile(run_context: RunContext) -> str:
    """
    Get the user's learning profile from the database.

    This tool accesses user_id from RunContext (automatically injected by JWT middleware)
    and fetches the user's learning preferences, target language, and proficiency level.

    Args:
        run_context: RunContext object with user_id from JWT token

    Returns:
        User's learning profile as formatted string
    """
    user_id = run_context.user_id

    if not user_id:
        return "Error: User not authenticated. No user_id found in context."

    # Note: In a real implementation, you'd query the database
    # For now, we'll return the user_id to demonstrate it's accessible
    return f"""User Learning Profile:
- User ID: {user_id}
- Status: Profile accessible via RunContext
- Note: User ID automatically extracted from JWT token by AgentOS middleware

To implement full profile fetching:
1. Connect to MongoDB using run_context
2. Query users collection with user_id
3. Return user's base_language, learning goals, progress, etc.
"""


def get_session_context(run_context: RunContext) -> str:
    """
    Get the current session context information.

    This tool accesses both user_id and session_id from RunContext.
    - user_id: Automatically from JWT token
    - session_id: Can be from JWT or passed per-request by frontend

    Args:
        run_context: RunContext object with user_id and session_id

    Returns:
        Session context information as formatted string
    """
    user_id = run_context.user_id
    session_id = run_context.session_id

    if not user_id:
        return "Error: User not authenticated."

    result = f"""Session Context:
- User ID: {user_id}
- Session ID: {session_id or 'No session selected'}
- Run ID: {run_context.run_id}
"""

    if session_id:
        result += f"""
Session Details:
- Context automatically scoped to this session
- Chat history preserved across runs
- Progress tracked for this learning session

To fetch full session data:
1. Query sessions collection with session_id and user_id
2. Return title, notes, chat_history, progress, etc.
"""
    else:
        result += """
Note: No session_id found. Frontend should pass session_id when calling agent endpoints.
Example: POST /agents/mumble-ai-coach/runs
         Body: {{"message": "...", "session_id": "session-123"}}
"""

    return result


def save_learning_progress(
    run_context: RunContext,
    progress_data: str,
    lesson_completed: Optional[str] = None
) -> str:
    """
    Save the user's learning progress to their session.

    This tool demonstrates writing data scoped to a specific user and session.

    Args:
        run_context: RunContext with user_id and session_id
        progress_data: Progress information to save
        lesson_completed: Optional lesson identifier

    Returns:
        Confirmation message
    """
    user_id = run_context.user_id
    session_id = run_context.session_id

    if not user_id:
        return "Error: Cannot save progress - user not authenticated."

    if not session_id:
        return "Error: Cannot save progress - no session selected. Please select a learning session first."

    # In a real implementation, you would:
    # 1. Connect to MongoDB
    # 2. Update the session document with progress
    # 3. Add to chat_history or progress field

    return f"""Progress Saved Successfully:
- User: {user_id}
- Session: {session_id}
- Progress: {progress_data}
- Lesson: {lesson_completed or 'N/A'}
- Timestamp: Current time would be recorded

Implementation note: This is a placeholder. Real implementation would:
1. Query sessions collection
2. Update progress field
3. Append to chat_history
4. Update session's updated_at timestamp
"""


def get_user_base_language(run_context: RunContext) -> str:
    """
    Get the user's native/base language from their profile.

    This is critical for the language learning coach to provide
    explanations in the user's native language.

    Args:
        run_context: RunContext with user_id

    Returns:
        User's base language (e.g., "English", "Spanish")
    """
    user_id = run_context.user_id

    if not user_id:
        return "English"  # Default fallback

    # In real implementation:
    # user = await db.users.find_one({"id": user_id})
    # return user.get("base_language", "English")

    return f"English (fetched for user_id: {user_id})"


# Example of a more complex tool accessing dependencies and metadata
def get_complete_learning_context(run_context: RunContext) -> Dict[str, Any]:
    """
    Get complete learning context including user, session, dependencies, and metadata.

    Demonstrates accessing all available context from RunContext.

    Args:
        run_context: Complete RunContext object

    Returns:
        Dictionary with all context information
    """
    return {
        "user_id": run_context.user_id,
        "session_id": run_context.session_id,
        "run_id": run_context.run_id,
        "dependencies": run_context.dependencies,
        "metadata": run_context.metadata,
        "session_state": run_context.session_state,
        "knowledge_filters": run_context.knowledge_filters,
    }
