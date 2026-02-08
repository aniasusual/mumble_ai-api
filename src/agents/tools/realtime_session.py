"""Tool to create an OpenAI Realtime session (via Emergent proxy if available)."""
import os
from typing import Any, Dict, Optional

import aiohttp


async def create_realtime_session(
    model_id: str = "gpt-4o-realtime-preview-2024-12-17",
    voice: str = "verse",
) -> Dict[str, Any]:
    """
    Create an ephemeral OpenAI Realtime session using OPENAI_API_KEY only.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    # Guard against incorrect model_id from LLM tool calls
    if not model_id or "realtime" not in model_id:
        model_id = "gpt-4o-realtime-preview-2024-12-17"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model_id, "voice": voice},
        ) as response:
            payload = await response.json()

    return {
        "provider": "openai",
        "model": model_id,
        "voice": voice,
        "session": payload,
    }

    if not openai_api_key:
        raise ValueError("Neither EMERGENT_LLM_KEY nor OPENAI_API_KEY is set")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model_id, "voice": voice},
        ) as response:
            payload = await response.json()

    return {
        "provider": "openai",
        "model": model_id,
        "voice": voice,
        "session": payload,
    }
