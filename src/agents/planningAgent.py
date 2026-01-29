import os
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.mongo import MongoDb
from emergentintegrations.llm.utils import get_integration_proxy_url

from ..prompts.planningAgent import PLANNING_AGENT_PROMPT
from .tools import (
    get_user_learning_profile,
    get_session_context,
    save_learning_progress,
)


def get_planning_agent(
    model_id: str = "gpt-4.1-mini",
    debug_mode: bool = False,
    access_token: Optional[str] = None,
) -> Agent:
    """
    Create curriculum design agent.

    Args:
        model_id: LLM model ID
        debug_mode: Enable debug logging
        access_token: Optional access token

    Returns:
        Agent: Planning agent for curriculum design

    Note:
        The {base_language} template variable in instructions is automatically replaced
        at runtime with the value from dependencies parameter (passed from team).
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
        id="planning-agent",
        name="Curriculum Planning Agent",
        debug_mode=True,
        role="Expert curriculum designer who creates personalized language learning plans",
        model=OpenAIChat(
            id=model_id,
            api_key=emergent_api_key,
            base_url=llm_base_url,
        ),
        add_dependencies_to_context=True,  # Adds dependencies to user message
        tools=[
            get_user_learning_profile,
            get_session_context,
            save_learning_progress,
        ],
        markdown=True,
        description=f"Specializes in creating comprehensive, personalized language curricula. Delegate to this agent when you need to design a learning plan or curriculum. Provide: native language, target language, proficiency level, and learning goals.\n\n{PLANNING_AGENT_PROMPT}",
        instructions=[
            "Check <additional context> for 'base_language' - respond in that language",
            "Target language provided by Main Agent during delegation",
            "Use get_user_learning_profile to understand user's learning style and preferences",
            "Use get_session_context to see what topics were covered previously",
            "Use save_learning_progress when curriculum milestones are completed",
            "Apply contrastive analysis to identify language-specific challenges",
            "Prioritize concepts absent in native language (e.g., articles, tones, cases)",
            "Design pronunciation drills for non-native sounds",
            "Address common errors specific to this language pair",
            "Create progressive curriculum balancing all four skills",
            "Include clear objectives, activities, and success criteria for each lesson",
            "Reference learner's native language (base_language from context) when explaining complex target language concepts",
        ],
        add_history_to_context=True,
        num_history_runs=5,
        db=db,
        enable_user_memories=True,
        enable_agentic_memory=True,
        add_datetime_to_context=True,
    )
