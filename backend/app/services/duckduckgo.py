import httpx
# async def duckduckgo_search(query: str) -> dict:
#     url = "https://api.duckduckgo.com/"
#
#     params = {
#         "q": query,
#         "format": "json",
#         "no_html": 1,
#         "no_redirect": 1
#     }
#
#     try:
#         async with httpx.AsyncClient(timeout=10) as client:
#             resp = await client.get(url, params=params)
#             data = resp.json()
#             return {
#                 "abstract": data.get("Abstract"),
#                 "abstract_url": data.get("AbstractURL"),
#                 "related_topics": data.get("RelatedTopics", [])
#             }
#     except Exception as e:
#         print(f'DuckDuckG0 ERROR: {e}')
#         return {"error": str(e)}


# import asyncio
# from ddgs import DDGS
#
#
# async def duckduckgo_search(query: str, max_results: int = 2):
#     loop = asyncio.get_running_loop()
#
#     def _search():
#         with DDGS() as ddgs:
#             return ddgs.text(
#                 query=query,
#                 region="wt-wt",
#                 safesearch="moderate",
#                 timelimit="w",
#                 max_results=max_results
#             )
#
#     results = await loop.run_in_executor(None, _search)
#     return list(results)


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
