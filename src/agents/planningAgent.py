import os
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.mongo import MongoDb
from emergentintegrations.llm.utils import get_integration_proxy_url

from ..prompts.planningAgent import PLANNING_AGENT_PROMPT


def get_planning_agent(
    model_id: str = "gpt-4.1-mini",
    debug_mode: bool = False,
    access_token: Optional[str] = None,
    native_language: str = None,
) -> Agent:
    """
    Create curriculum design agent.

    Args:
        model_id: LLM model ID
        debug_mode: Enable debug logging
        access_token: Optional access token
        native_language: Learner's native language

    Returns:
        Agent: Planning agent for curriculum design
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
    native_lang = native_language or "User's native language"

    return Agent(
        id="planning-agent",
        name="Curriculum Designer",
        role=f"Curriculum specialist creating personalized learning paths for {native_lang} speakers",
        model=OpenAIChat(
            id=model_id,
            api_key=emergent_api_key,
            base_url=llm_base_url,
        ),
        tools=[],
        markdown=True,
        description=PLANNING_AGENT_PROMPT,
        instructions=[
            f"Learner's native language: {native_lang}",
            "Target language provided by Main Agent during delegation",
            "Apply contrastive analysis to identify language-specific challenges",
            "Prioritize concepts absent in native language (e.g., articles, tones, cases)",
            "Design pronunciation drills for non-native sounds",
            "Address common errors specific to this language pair",
            "Create progressive curriculum balancing all four skills",
            "Include clear objectives, activities, and success criteria for each lesson",
            f"Reference {native_lang} when explaining complex target language concepts",
        ],
        add_history_to_context=True,
        num_history_runs=5,
        db=db,
        enable_user_memories=True,
        enable_agentic_memory=True,
        add_datetime_to_context=True,
    )
