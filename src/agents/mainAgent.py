import os
from typing import Optional
from agno.models.openai import OpenAIChat
from agno.team import Team
from .planningAgent import get_planning_agent
from .conversationAgent import get_conversation_agent
from agno.agent import Agent
from agno.db.mongo import MongoDb
from emergentintegrations.llm.utils import get_integration_proxy_url


from ..prompts.mainAgent import SYSTEM_PROMPT


def get_main_agent(
    model_id: str = "gpt-4.1-mini",
    native_language: str = None,
) -> Team:
    """
    Create main language learning coach team.

    Args:
        model_id: LLM model ID (e.g., "gpt-4.1-mini", "gpt-4o", "gemini-2.0-flash")
        native_language: Learner's native language (e.g., "Hindi", "English")

    Returns:
        Team: Main agent coordinating specialized language learning agents
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
    native_lang = native_language or "User's native language (to be determined)"

    planning_agent = get_planning_agent(
        model_id=model_id,
        native_language=native_language,
    )

    conversation_agent = get_conversation_agent(
        model_id=model_id,
        native_language=native_language,
    )

    return Team(
        id="mumble-ai-coach",
        name="Language Learning Coach",
        role="Professional language tutor who delivers personalized, human-like language learning experiences",
        description=f"Interactive language coach for {native_lang} speakers learning new languages through conversation-based assessment and practice.",
        system_message=SYSTEM_PROMPT,
        instructions=[
            f"Learner's native language: {native_lang}",
            "First interaction: Ask what language they want to learn",
            "Assess proficiency level through natural conversation",
            f"Always communicate in {native_lang} except during target language practice",
            "Gather complete profile (target language, level, goals) before delegating to Planning Agent",
            "Use get_member_information tool to see available team members and their capabilities",
            "Delegate curriculum design to Planning Agent with full context (native lang, target lang, level, goals)",
            "When learner needs speaking practice, delegate to Conversation Agent with context (target lang, level, scenario)",
            "After delegated agent completes, review their response and synthesize it into your guidance",
            "Track progress and adapt learning path based on performance",
            "Provide clear, encouraging feedback like a human tutor would",
        ],
        members=[planning_agent, conversation_agent],
        model=OpenAIChat(
            id=model_id,
            api_key=emergent_api_key,
            base_url=llm_base_url,
        ),
        markdown=True,
        debug_mode=True,
        add_history_to_context=True,
        num_history_runs=10,
        add_datetime_to_context=True,
        db=db,
        add_team_history_to_members=True,
        num_team_history_runs=10,
        show_members_responses=True,
        get_member_information_tool=True,
        add_member_tools_to_context=True,
        share_member_interactions=True,
        store_member_responses=True
    )
