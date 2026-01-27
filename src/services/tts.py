import logging
import base64
from emergentintegrations.llm.openai import OpenAITextToSpeech
from typing import Dict

from ..models import ChatRequest
from ..agents.miaAgent import get_mia_agent


# Store Mia agent instances per session (in production, use Redis)
# NOTE: Mia is SEPARATE from the main team agents - used only for landing page chat
mia_agents_tts: Dict[str, object] = {}


class TTSService:
    """Service for text-to-speech generation and voice chat with Mia."""

    def __init__(self, api_key: str):
        self.tts = OpenAITextToSpeech(api_key=api_key)
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

    async def generate_speech(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 1.0,
        model: str = "tts-1",
        response_format: str = "mp3"
    ) -> bytes:
        """Generate speech audio from text."""
        try:
            audio_bytes = await self.tts.generate_speech(
                text=text,
                model=model,
                voice=voice,
                speed=speed,
                response_format=response_format
            )
            return audio_bytes
        except Exception as e:
            self.logger.error(f"TTS error: {str(e)}")
            raise

    async def chat_with_voice(self, request: ChatRequest) -> dict:
        """Chat with Mia (landing page agent) and get voice response."""
        try:
            session_id = request.session_id

            # Create Mia agent if not exists for this session
            if session_id not in mia_agents_tts:
                mia_agents_tts[session_id] = get_mia_agent()

            mia = mia_agents_tts[session_id]

            # Run agent with the user message
            response = await mia.arun(request.message, session_id=session_id)
            text_response = response.content if hasattr(response, 'content') else str(response)

            # Generate audio from response
            audio_bytes = await self.generate_speech(
                text=text_response,
                model="tts-1",
                voice="nova",
                speed=1.0,
                response_format="mp3"
            )

            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

            return {
                "response": text_response,
                "audio": audio_base64,
                "session_id": session_id
            }
        except Exception as e:
            self.logger.error(f"Chat voice error: {str(e)}")
            raise
