import aiohttp
import logging

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
)


async def call_gemini(prompt: str) -> str:
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}],
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_URL, json=payload) as resp:
            if resp.status != 200:
                logger.error(f"Gemini API error: {resp.status}")
                return "AI response error"
            data = await resp.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logger.error(f"Failed to parse Gemini response: {e}")
        return "AI parsing error"
