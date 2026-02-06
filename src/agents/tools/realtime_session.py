"""Tool to create an OpenAI Realtime session (via Emergent proxy if available)."""
import os
from typing import Any, Dict, Optional

import aiohttp
from emergentintegrations.llm.utils import get_integration_proxy_url


async def create_realtime_session(
    model_id: str = "gpt-4o-realtime-preview-2024-12-17",
    voice: str = "verse",
) -> Dict[str, Any]:
    """
    Create an ephemeral OpenAI Realtime session.

    Prefers Emergent proxy when EMERGENT_LLM_KEY is set.
    Falls back to OpenAI direct when OPENAI_API_KEY is set.
    """
    emergent_api_key = os.getenv("EMERGENT_LLM_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if emergent_api_key:
        proxy_url = get_integration_proxy_url().rstrip("/")
        realtime_base_url = f"{proxy_url}/llm/realtime"
        headers = {
            "Authorization": f"Bearer {emergent_api_key}",
            "Content-Type": "application/json",
        }
        url = f"{realtime_base_url}/sessions"
    else:
        if not openai_api_key:
            raise ValueError("Neither EMERGENT_LLM_KEY nor OPENAI_API_KEY is set")
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json",
        }
        url = "https://api.openai.com/v1/realtime/sessions"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers=headers,
            json={"model": model_id, "voice": voice},
        ) as response:
            payload = await response.json()

    return {
        "provider": "emergent" if emergent_api_key else "openai",
        "model": model_id,
        "voice": voice,
        "session": payload,
    }
