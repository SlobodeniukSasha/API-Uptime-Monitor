import asyncio
import json
from logging import getLogger

from redis import asyncio as aioredis

from backend.app.services.utils.hugging_face import call_huggingface
from backend.app.services.utils.cache import prompt_cache_key
from backend.app.services.utils.prompts import create_analysis_prompt
from backend.app.core.config import settings

logger = getLogger(__name__)

redis = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
)


async def ai_analyze_issue(url: str, error_message: str, ddg_results: list) -> tuple[str, str]:
    """
    AI-driven incident analysis with Redis caching.
    Returns: (analysis_text, resolution_steps)
    """

    cache_key = prompt_cache_key(url, error_message[:200])

    cached = await redis.get(cache_key)

    logger.info('-' * 50)
    logger.info('Inside_ai_analise')
    logger.info('-' * 50)

    if cached:
        try:
            data = json.loads(cached)

            logger.info('-' * 50)
            logger.info('Returning data from cache: ', data)
            logger.info('-' * 50)
            return data["analysis"], data["resolution"]
        except json.JSONDecodeError:
            pass

    prompt = create_analysis_prompt(url, error_message, ddg_results)

    logger.debug('-' * 50)
    logger.info(f'\nAI Model prompt: {prompt}')
    logger.debug('-' * 50)

    try:
        response = await asyncio.wait_for(
            call_huggingface(prompt),
            timeout=25
        )

    except asyncio.TimeoutError:
        return ("AI timeout", "AI service is not responding — handle manually.")
    except Exception as e:
        return ("AI error", f"Failed to process AI request: {e}")

    logger.info('-' * 50)
    logger.info(f'AI Model response: {response}')
    logger.info('-' * 50)

    analysis = []
    resolution = []
    mode = None

    # import re

    # TODO
    # analysis_text = re.findall('PATTERN', response)
    for line in response.splitlines():
        text = line.strip()
        if not text:
            continue
        if text.upper().startswith("ANALYSIS"):
            mode = "analysis"
            continue
        elif text.upper().startswith("RESOLUTION"):
            mode = "resolution"
            continue
        if mode == "analysis":
            analysis.append(text)
        elif mode == "resolution":
            resolution.append(text)

    result = {
        "analysis": " ".join(analysis) if analysis else "Analysis not found",
        "resolution": "\n".join(resolution) if resolution else "Resolution steps not found"
    }

    await redis.set(cache_key, json.dumps(result), ex=3600)

    logger.info('-' * 50)
    logger.info('Returning_ai_analise')
    logger.info('-' * 50)

    return result["analysis"], result["resolution"]
