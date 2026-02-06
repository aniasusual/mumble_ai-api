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
from .tools import get_user_session_context, get_current_user_id, get_current_job_id


def get_main_agent(
    model_id: str = "gpt-4.1-mini"
) -> Team:
    """
    Create main language learning coach team.

    Args:
        model_id: LLM model ID (e.g., "gpt-4.1-mini", "gpt-4o", "gemini-2.0-flash")

    Returns:
        Team: Main agent coordinating specialized language learning agents

    Note:
        The {base_language} template variable in instructions is automatically replaced
        at runtime with the value from dependencies parameter (passed from frontend).
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

    # Agents will use {base_language} template variable from runtime dependencies
    planning_agent = get_planning_agent()
    conversation_agent = get_conversation_agent()

    return Team(
        id="mumble-ai-coach",
        db=db,
        name="Language Learning Coach",
        role="Professional language tutor who delivers personalized, human-like language learning experiences",
        description="Interactive language coach helping learners master new languages.",
        add_dependencies_to_context=True,  # Adds dependencies to user message
        add_memories_to_context=True,  # Inject user memories into context
        system_message=SYSTEM_PROMPT,
        instructions=[
            "CRITICAL: Check the <additional context> section in the user message for 'base_language' field",
            "ALWAYS respond in the base_language specified in the context (e.g., if base_language is 'English', respond in English)",
            "First interaction: Ask what language they want to learn in their native language (base_language from context)",
            "Assess proficiency level through natural conversation",
            "Always communicate in the learner's native language (base_language) except during target language practice",
            "Gather complete profile (target language, level, goals) before delegating to Planning Agent",
            "Use get_member_information tool to see available team members and their capabilities",
            "Delegate curriculum design to Planning Agent with full context (native lang, target lang, level, goals)",
            
            # Conversation practice trigger
            "When the learner is ready for conversation practice, say exactly: 'Let's practice conversation!' followed by the topic/scenario",
            "Use phrases like 'free conversation', 'practice speaking', or 'let's talk' to trigger the conversation practice UI",
            "Before starting conversation practice, briefly explain what the learner will practice and the scenario",
            
            "After delegated agent completes, review their response and synthesize it into your guidance",
            "Track progress and adapt learning path based on performance",
            "Provide clear, encouraging feedback like a human tutor would",
        ],
        members=[planning_agent, conversation_agent],
        # tools=[get_user_session_context, get_current_user_id, get_current_job_id],
        model=OpenAIChat(
            id=model_id,
            api_key=emergent_api_key,
            base_url=llm_base_url,
        ),
        enable_agentic_memory=True,
        markdown=True,
        debug_mode=True,
        add_history_to_context=True,
        num_history_runs=10,
        add_datetime_to_context=True,
        add_team_history_to_members=True,
        num_team_history_runs=10,
        show_members_responses=True,
        get_member_information_tool=True,
        add_member_tools_to_context=True,
        share_member_interactions=True,
        store_member_responses=True,
        respond_directly=True,

    )
