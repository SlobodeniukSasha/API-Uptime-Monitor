from celery.utils.log import get_task_logger

log = get_task_logger(__name__)


def create_analysis_prompt(url: str, error: str, search_results: list) -> str:
    if not search_results:
        search_summary = "No search results available."
        log.info("No search results for incident: %s", url)
    else:
        log.info(f"Creating prompt for {url} with {len(search_results)} search results")
        parts = []
        for i, item in enumerate(search_results[:10]):
            title = item.get("title", "No title").strip()
            snippet = item.get("snippet", "").strip()
            snippet = snippet[:200] + "..." if len(snippet) > 200 else snippet

            parts.append(f"{i + 1}. {title}\n   {snippet}")

        search_summary = "\n\n".join(parts)
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
