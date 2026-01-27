"""
Conversation Agent for voice-to-voice language practice.

This agent handles real-time conversation practice with voice input/output,
pronunciation feedback, and natural language coaching.
"""

import os
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.mongo import MongoDb
from emergentintegrations.llm.utils import get_integration_proxy_url

from ..prompts.conversationAgent import CONVERSATION_AGENT_PROMPT


def get_conversation_agent(
    model_id: str = "gpt-4.1-mini",
    native_language: str = None,
) -> Agent:
    """
    Create conversation practice agent.

    Args:
        model_id: LLM model ID
        native_language: Learner's native language

    Returns:
        Agent: Conversation practice agent (receives target language and level from Main Agent)
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

    instructions = [
        f"Learner's native language: {native_lang}",
        "Target language and proficiency level provided by Main Agent during delegation",
        f"Give all instructions and feedback in {native_lang}",
        "Prompt learner to respond in target language",
        "Adjust complexity based on provided proficiency level",
        "Create realistic conversation scenarios",
        "Provide constructive corrections with explanations",
        "Session length: 10-15 exchanges",
        "When complete, summarize and return control to Main Agent",
    ]

    model = OpenAIChat(
        id=model_id,
        api_key=emergent_api_key,
        base_url=llm_base_url,
    )

    return Agent(
        id="conversation-agent",
        name="Conversation Practice Agent",
        role="Expert conversation partner for immersive language practice sessions with real-time feedback",
        model=model,
        instructions=instructions,
        description=f"Specializes in interactive conversation practice with learners. Delegate to this agent when learner wants to practice speaking and conversation. Provide: target language, proficiency level, and conversation topic/scenario.\n\n{CONVERSATION_AGENT_PROMPT}",
        tools=[],
        markdown=True,
        add_history_to_context=True,
        num_history_runs=10,
        db=db,
        enable_user_memories=True,
        enable_agentic_memory=True,
        add_datetime_to_context=True,
    )

