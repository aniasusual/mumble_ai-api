import os
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.mongo import MongoDb
from emergentintegrations.llm.utils import get_integration_proxy_url

from ..prompts.miaAgent import MIA_AGENT_PROMPT


def get_mia_agent(
    model_id: str = "gpt-4.1-mini",
    debug_mode: bool = False,
    access_token: Optional[str] = None,
) -> Agent:
    """
    Create Mia landing page agent.

    Args:
        model_id: LLM model ID
        debug_mode: Enable debug logging
        access_token: Optional access token

    Returns:
        Agent: Mia landing page chat agent
    """
    db_url = os.getenv("MONGODB_URL")
    if not db_url:
        raise ValueError("MONGODB_URL environment variable is not set")

    db = MongoDb(db_url=db_url)

    emergent_api_key = os.getenv("EMERGENT_LLM_KEY")
    if not emergent_api_key:
        raise ValueError("EMERGENT_LLM_KEY environment variable is not set")

    emergent_proxy_url = get_integration_proxy_url()
    llm_base_url = f"{emergent_proxy_url}/llm"

    return Agent(
        id="mia-agent",
        name="Mia",
        role="Friendly AI language tutor for Mumble AI landing page",
        model=OpenAIChat(
            id=model_id,
            api_key=emergent_api_key,
            base_url=llm_base_url,
        ),
        tools=[],
        markdown=False,
        description=MIA_AGENT_PROMPT,
        instructions=[
            "You are Mia, the friendly landing page assistant",
            "Keep responses conversational and engaging",
            "Max 2-3 sentences per response",
            "Be enthusiastic but not salesy",
            "Use specific product details when answering questions",
            "Encourage users to join the waitlist",
            "If asked unrelated questions, gently steer back to Mumble AI"
        ],
        add_history_to_context=True,
        num_history_runs=5,
        db=db,
        enable_user_memories=False,  # Landing page - no need for long-term memory
        enable_agentic_memory=False,  # Landing page - no need for agent memory
        add_datetime_to_context=False,  # Landing page - time not relevant
    )
