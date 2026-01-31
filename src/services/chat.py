import logging
from typing import Dict

from ..models import ChatRequest, ChatResponse
from ..agents.miaAgent import get_mia_agent


# Store Mia agent instances per job (in production, use Redis)
# NOTE: Mia is SEPARATE from the main team agents - used only for landing page chat
mia_agents: Dict[str, object] = {}


class ChatService:
    """Service for managing landing page chat interactions with Mia."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a chat message to Mia (landing page agent) and get response."""
        try:
            job_id = request.job_id

            # Create Mia agent if not exists for this job
            if job_id not in mia_agents:
                mia_agents[job_id] = get_mia_agent()

            mia = mia_agents[job_id]

            # Run agent with the user message
            response = await mia.arun(request.message, session_id=job_id)

            return ChatResponse(
                response=response.content if hasattr(response, 'content') else str(response),
                job_id=job_id
            )
        except Exception as e:
            self.logger.error(f"Chat error: {str(e)}")
            raise
