from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import logging

from ...core import settings
from ...models import ChatRequest, ChatResponse
from ...services import ChatService, TTSService


router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
chat_service = ChatService()
tts_service = TTSService(api_key=settings.EMERGENT_LLM_KEY)


class TTSRequest(BaseModel):
    """TTS request model."""
    text: str
    voice: str = "nova"
    speed: float = 1.0


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with Mia (text only)."""
    try:
        return await chat_service.chat(request)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/chat-voice")
async def chat_with_voice(request: ChatRequest):
    """Chat with Mia (text + audio response)."""
    try:
        return await tts_service.chat_with_voice(request)
    except Exception as e:
        logger.error(f"Chat voice error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat voice failed: {str(e)}")


@router.post("/tts")
async def generate_speech(request: TTSRequest):
    """Generate speech from text."""
    try:
        audio_bytes = await tts_service.generate_speech(
            text=request.text,
            voice=request.voice,
            speed=request.speed
        )
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
