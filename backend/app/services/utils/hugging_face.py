import logging

from openai import OpenAI

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=settings.HUGGING_FACE_API_KEY,
)


async def call_huggingface(prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=512
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling HuggingFace model: {e}")
        return "AI response error"
