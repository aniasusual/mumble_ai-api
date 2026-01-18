import os
from typing import Optional
from agno.team import Team
from .planningAgent import get_planning_agent
from agno.agent import Agent
from agno.models.google import Gemini
from agno.db.mongo import MongoDb

from ..prompts.mainAgent import SYSTEM_PROMPT


def get_main_agent(
    model_id: str = "gemini-2.0-flash",
    debug_mode: bool = False,
    access_token: Optional[str] = None,
) -> Agent:

    # Initialize MongoDB connection - happens after .env is loaded
    db_url = os.getenv("MONGODB_URL")
    if not db_url:
        raise ValueError("MONGODB_URL environment variable is not set")

    db = MongoDb(db_url=db_url)

    

    planning_agent = get_planning_agent()

    return Team(
        name="Mumble AI Main Agent",
        instructions=SYSTEM_PROMPT,  # Add instructions to guide team behavior
        members=[planning_agent],
        model=Gemini(id=model_id),
        add_history_to_context=True,
        db=db,
        enable_user_memories=True,
        enable_agentic_memory=True,
        # Note: enable_user_memories and enable_agentic_memory are NOT supported on Team
        # They should be configured on individual member agents instead
    )
