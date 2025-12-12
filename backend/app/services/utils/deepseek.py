import aiohttp
import logging

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = settings.DEEPSEEK_API_KEY


async def call_gemini(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(DEEPSEEK_URL, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                logger.error(f"DeepSeek API error: {resp.status} | {error_text}")
                return "AI response error"

            data = await resp.json()

    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Failed to parse DeepSeek response: {e}")
        return "AI parsing error"
