import os
from typing import Optional

from agno.agent import Agent
from agno.models.google import Gemini
from agno.db.mongo import MongoDb

from ..prompts.planningAgent import PLANNING_AGENT_PROMPT


def get_planning_agent(
    model_id: str = "gemini-2.0-flash",
    debug_mode: bool = False,
    access_token: Optional[str] = None,
) -> Agent:
    # Initialize MongoDB connection - happens after .env is loaded
    db_url = os.getenv("MONGODB_URL")
    if not db_url:
        raise ValueError("MONGODB_URL environment variable is not set")

    db = MongoDb(db_url=db_url)

    return Agent(
        id="planning-agent",  # Unique identifier for better team delegation
        name="Planning Agent",  # Human-readable name
        role="Plan the curriculum for this session and provide instructions for next session",  # Role description
        model=Gemini(id=model_id),
        tools=[],
        markdown=True,
        description=PLANNING_AGENT_PROMPT,
        add_history_to_context=True,
        db=db,
        enable_user_memories=True,
        enable_agentic_memory=True,
    )
