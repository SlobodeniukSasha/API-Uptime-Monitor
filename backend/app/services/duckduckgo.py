import asyncio
from ddgs import DDGS


async def duckduckgo_search(query: str, max_results: int = 5):
    """
    Performs a search in DuckDuckGo using the ddgs library and returns a list of words:
    [{'title': ..., 'href': ..., 'snippet': ...}, ...]
    """
    loop = asyncio.get_running_loop()

    def _search():
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(
                    query=query,
                    region="wt-wt",
                    backend="html",
                    safesearch="moderate",
                    max_results=max_results
            ):
                snippet = r.get("snippet") or r.get("body") or ""
                if snippet:
                    results.append({
                        "title": r.get("title", ""),
                        "href": r.get("href", ""),
                        "snippet": snippet[:300]
                    })
        return results

    return await loop.run_in_executor(None, _search)
