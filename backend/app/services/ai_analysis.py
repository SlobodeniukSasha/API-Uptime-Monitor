import asyncio
import json
from functools import lru_cache
import hashlib
import aiohttp

from redis import asyncio as aioredis

from backend.app.core.config import settings

redis = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
)

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
                return "AI response error"

            data = await resp.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "AI parsing error"


def create_analysis_prompt(url: str, error: str, search_results: list) -> str:
    """
    Build a compact and effective prompt for AI incident analysis.
    DuckDuckGo results come as a dict.
    """

    print(f"🔍 search_results type: {type(search_results)}")
    print(f"🔍 search_results: {search_results}")

    if not search_results:
        search_summary = "No search results available."

    elif isinstance(search_results, list):
        search_items = []
        for i, item in enumerate(search_results):
            title = item.get('title', 'No title').strip()
            snippet = item.get('snippet', '').strip()

            if title or snippet:
                if snippet:
                    if len(snippet) > 200:
                        snippet = snippet[:197] + "..."
                    search_items.append(f"{i + 1}. {title}\n   {snippet}")
                else:
                    search_items.append(f"{i + 1}. {title}")

        search_summary = "\n\n".join(search_items) if search_items else "No relevant search results found."

        print("-" * 50)
        print(search_summary)
        print("-" * 50)

    return f"""
You are a Senior SRE/DevOps Engineer. Your task is to quickly analyze an incident detected by the monitoring system.

## Incident Details:
- URL: {url}
- Error: {error}

## Internet Search Summary:
{search_summary}

## You must provide:
1. A short root cause analysis (5–7 sentences).
2. A clear step-by-step resolution plan (3–5 steps).

Respond in the following STRICT format:

ANALYSIS:
[text]

RESOLUTION:
1. [step]
2. [step]
3. [step]
"""


@lru_cache(maxsize=200)
def prompt_cache_key(url: str, error: str) -> str:
    """
    Generate a persistent cache key for identical incidents.
    Useful for Redis or in-memory caching.
    """
    normalized_error = " ".join(error.lower().split()[:10])
    payload = f"{url}:{normalized_error}"
    return hashlib.md5(payload.encode()).hexdigest()


async def ai_analyze_issue(url: str, error_message: str, ddg_results: list) -> tuple[str, str]:
    """
    AI-driven incident analysis with Redis caching.
    Returns: (analysis_text, resolution_steps)
    """

    cache_key = prompt_cache_key(url, error_message[:200])

    cached = await redis.get(cache_key)

    if cached:
        try:
            data = json.loads(cached)
            return data["analysis"], data["resolution"]
        except json.JSONDecodeError:
            pass

    prompt = create_analysis_prompt(url, error_message, ddg_results)

    print(prompt)

    try:
        response = await asyncio.wait_for(
            call_gemini(prompt),
            timeout=25
        )
    except asyncio.TimeoutError:
        return ("AI timeout", "AI service is not responding — handle manually.")
    except Exception as e:
        return ("AI error", f"Failed to process AI request: {e}")

    print("-" * 50)
    print("Gemini_Response: ", response)
    print("-" * 50)

    analysis = []
    resolution = []
    mode = None

    import re

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

    # Save result in Redis for 1 hour (3600 seconds)
    await redis.set(cache_key, json.dumps(result), ex=3600)

    return result["analysis"], result["resolution"]

# async def ai_analyze_issue(url: str, error_message: str, ddg_results: dict) -> tuple[str, str]:
#     """
#     Return (ai_analysis, ai_recommendations)
#     """
#
#     search_text = "\n".join(
#         f"- {item.get('title')} — {item.get('href')}"
#         for item in ddg_results[:10]
#     ) or "Ничего не найдено"
#
#     prompt_analysis = f"""
#         Проаналізуй можливу причину проблеми з API.
#
#         URL: {url}
#         Error: {error_message}
#
#         Останні результати пошуку:
#         {search_text}
#
#         Сформулюй короткий, технічний аналіз (5–8 речень).
#     """
#
#     prompt_recommend = f"""
#         На основі аналізу сформуй рекомендації для користувача:
#
#         URL: {url}
#         Статус: {error_message}
#
#         Результати пошуку:
#         {search_text}
#
#         Дай 4–6 практичних рекомендацій, як вирішити проблему.
#     """
#
#     analysis = await call_gemini(prompt_analysis)
#     recs = await call_gemini(prompt_recommend)
#
#     return analysis, recs

# async def ai_generate(prompt: str) -> str:
#     if not OPENROUTER_KEY:
#         return "AI disabled: No OpenRouter API key."
#
#     url = "https://openrouter.ai/api/v1/chat/completions"
#
#     body = {
#         "model": "mistralai/mistral-tiny",
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }
#
#     async with httpx.AsyncClient(timeout=20) as client:
#         r = await client.post(
#             url,
#             json=body,
#             headers={
#                 "Authorization": f"Bearer {OPENROUTER_KEY}",
#                 "HTTP-Referer": "http://localhost",
#                 "X-Title": "API-Health-Monitor"
#             }
#         )
#         data = r.json()
#         return data["choices"][0]["message"]["content"]
#
#
# async def generate_ai_analysis(error_message: str, status: str) -> str:
#     prompt = (
#         f"You are a monitoring expert. A service returned status '{status}'. "
#         f"Error message: {error_message}. "
#         f"Provide a technical root-cause analysis."
#     )
#     return await ai_generate(prompt)
#
#
# async def generate_ai_recommendations(error_message: str, status: str) -> str:
#     prompt = (
#         f"You are SRE engineer. A service status: {status}. "
#         f"Error: {error_message}. "
#         f"Give a list of recommended actions to fix the issue."
#     )
#     return await ai_generate(prompt)
