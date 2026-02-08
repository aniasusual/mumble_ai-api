"""
Conversation Agent for voice-to-voice language practice.

This agent handles real-time conversation practice with voice input/output,
pronunciation feedback, and natural language coaching.

The same agent is used for:
1. Team membership - When main agent delegates conversation practice
2. Direct access - When user interacts directly via /agents/conversation-agent/runs
"""

import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from emergentintegrations.llm.openai import OpenAIChatRealtime
from agno.db.mongo import MongoDb
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from ..prompts.conversationAgent import CONVERSATION_AGENT_PROMPT
from .tools import create_realtime_session


def get_conversation_agent(
    model_id: str = "gpt-4.1-mini",
    realtime_model_id: str = "gpt-4o-realtime-preview-2024-12-17",
    realtime_voice: str = "verse",
) -> Agent:
    """
    Create conversation practice agent.

    This agent serves dual purposes:
    1. As a team member (main agent delegates to it)
    2. As a standalone agent (user talks directly via AgentOS endpoint)

    Args:
        model_id: LLM model ID with audio capabilities

    Returns:
        Agent: Conversation practice agent
    """
    db_url = os.getenv("MONGODB_URL")
    if not db_url:
        raise ValueError("MONGODB_URL environment variable is not set")

    db = MongoDb(db_url=db_url)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    instructions = [
        "Check <additional context> for 'base_language' - respond in that language",
        "Give all instructions and feedback in the learner's native language (base_language from context)",
        "Prompt learner to respond in target language",
        "Adjust complexity based on provided proficiency level",
        "You do not conduct the conversation yourself. You only create realtime sessions.",
        "ALWAYS call the create_realtime_session tool exactly once per request.",
        f"Call create_realtime_session with model_id='{realtime_model_id}' and voice='{realtime_voice}'.",
        "Return only the tool result as JSON with no extra text.",
    ]

    model = OpenAIChat(
        id=model_id,
        api_key=openai_api_key,
    )

    return Agent(
        id="conversation-agent",
        name="Conversation Practice Agent",
        role="Real-time voice conversation partner for immersive language practice",
        model=model,
        add_dependencies_to_context=True,
        instructions=instructions,
        system_message=CONVERSATION_AGENT_PROMPT,
        description=f"Specializes in interactive conversation practice with learners. Delegate to this agent when learner wants to practice speaking and conversation. Provide: target language, proficiency level, and conversation topic/scenario.\n\n{CONVERSATION_AGENT_PROMPT}",
        markdown=True,
        add_history_to_context=True,
        num_history_runs=20,
        db=db,
        enable_user_memories=True,
        add_memories_to_context=True,
        add_datetime_to_context=True,
        tools=[create_realtime_session],
    )


def get_conversation_realtime_router(
    model_id: str = "gpt-4o-realtime-preview-2024-12-17",
    voice: str = "verse",
) -> APIRouter:
    """
    Create a FastAPI router that exposes OpenAI Realtime session + negotiate endpoints.

    This is separate from the Agno agent and is intended for WebRTC audio chat.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    router = APIRouter()
    openai_realtime = OpenAIChatRealtime(api_key=openai_api_key)

    @router.post("/realtime/session")
    async def create_session():
        try:
            session = await openai_realtime.create_ephemeral_session_for_audio_chat(
                voice=voice,
                model=model_id,
            )
            return JSONResponse(content=session)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/realtime/negotiate")
    async def negotiate_connection(request: Request):
        try:
            sdp_offer = await request.body()
            sdp_answer = await openai_realtime.negotiate_connection(
                sdp_offer.decode(),
                model=model_id,
            )
            return JSONResponse(content={"sdp": sdp_answer})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
