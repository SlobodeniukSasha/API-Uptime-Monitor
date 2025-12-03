import json
import pytest
import asyncio

from unittest.mock import AsyncMock, patch
from aioresponses import aioresponses

from backend.app.services.duckduckgo import duckduckgo_search
from backend.app.services.ai_analysis import (
    call_gemini,
    create_analysis_prompt,
    prompt_cache_key,
    ai_analyze_issue,
    GEMINI_URL,
)


@pytest.fixture
def mock_redis():
    """Простой мок для Redis"""
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock()
    redis_mock.set = AsyncMock()
    return redis_mock


@pytest.mark.asyncio
async def test_call_gemini_success():
    response_data = {
        "candidates": [{
            "content": {"parts": [{"text": "Hello world"}]}
        }]
    }

    with aioresponses() as m:
        m.post(GEMINI_URL, payload=response_data)

        result = await call_gemini("Ping")
        assert result == "Hello world"


@pytest.mark.asyncio
async def test_call_gemini_bad_status():
    with aioresponses() as m:
        m.post(GEMINI_URL, status=500)

        result = await call_gemini("Ping")
        assert result == "AI response error"


@pytest.mark.asyncio
async def test_call_gemini_parse_error():
    response_data = {"wrong": "data"}

    with aioresponses() as m:
        m.post(GEMINI_URL, payload=response_data)

        result = await call_gemini("Ping")
        assert result == "AI parsing error"


def test_prompt_cache_key_stable():
    key1 = prompt_cache_key("https://site.com", "Internal Server Error")
    key2 = prompt_cache_key("https://site.com", "Internal Server Error")

    assert key1 == key2


def test_prompt_cache_key_different():
    key1 = prompt_cache_key("https://site.com", "Error A")
    key2 = prompt_cache_key("https://site.com", "Error B")

    assert key1 != key2


def test_create_analysis_prompt_basic():
    prompt = create_analysis_prompt(
        "https://a.com",
        "500 error",
        {"results": [{"title": "Fix 500"}, {"title": "Cause 500"}]}
    )

    assert "You are a Senior SRE/DevOps Engineer." in prompt


@pytest.mark.asyncio
async def test_ai_analyze_issue_hits_cache(mock_redis):
    cached = {"analysis": "cached A", "resolution": "cached R"}

    await mock_redis.set(
        prompt_cache_key("https://x", "err"),
        json.dumps(cached)
    )

    a, r = await ai_analyze_issue("https://x", "err", {})

    assert a == "cached A"
    assert r == "cached R"


@pytest.mark.asyncio
async def test_ai_analyze_issue_calls_gemini_and_caches(mock_redis):
    fake_response = """
ANALYSIS:
This is analysis line.

RESOLUTION:
1. Step one
2. Step two
"""

    with patch("backend.app.services.ai_analysis.call_gemini", AsyncMock(return_value=fake_response)):
        a, r = await ai_analyze_issue("https://a", "err", {})

    assert "analysis" in a.lower()
    assert "resolution" in r.lower()

    cache_key = prompt_cache_key("https://a", "err")
    cached_raw = await mock_redis.get(cache_key)

    assert cached_raw is not None
    cached = json.loads(cached_raw)
    assert "analysis" in cached
    assert "resolution" in cached



@pytest.mark.asyncio
async def test_duckduckgo_search():
    query1 = 'Why http://127.0.0.1:8000/ is down, Unexpected status code: 404'
    # query2 = "Python KeyError"
    response1 = await duckduckgo_search(query1)
    # response2 = await duckduckgo_search(query2)

    print('Response1: ', response1)
    # print('Response2: ', response2)
    assert response1[0].get('title') != ''
    assert response1[0].get('href') != ''
    assert response1[0].get('snippet') != ''


@pytest.mark.asyncio
async def test_ai_analyze_issue_timeout(mock_redis):
    mock_search_results = [
       {'title': 'HTTP 404 - Wikipedia',
        'href': 'https://en.wikipedia.org/wiki/HTTP_404',
        'snippet': '2 weeks ago - In HTTP, the 404 response status code indicates that a web client (i.e. browser) was able to communicate with a server, but the server could not provide the requested resource . The server may not have the resource or it may not wish to disclose whether it has the resource.'},
       {'title': 'List of HTTP status codes - Wikipedia',
        'href': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes',
        'snippet': '1 week ago - Indicates that the resource is accessible via an alternate URL indicated in the Location header field . The HTTP/1.0 specification (which used reason phrase "Moved Temporarily") required the client to redirect with the same method, but popular ...'},
       {'title': '404 Not Found - HTTP | MDN',
        'href': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/404',
        'snippet': 'The HTTP 404 Not Found client error response status code indicates that the server cannot find the requested resource . Links that lead to a 404 page are often called broken or dead links and can be subject to link rot.'},
       {'title': 'What is a 404 Error Code? What It Means and How to Fix It',
        'href': 'https://www.techtarget.com/whatis/definition/404-status-code',
        'snippet': 'This definition explains what 404 errors are and what website users can do to find and fix these errors. Also examine several custom 404 error messages.'},
       {'title': 'HTTP/1.1: Status Code Definitions',
        'href': 'https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html',
        'snippet': 'If the request method was not HEAD and the server wishes to make public why the request has not been fulfilled, it SHOULD describe the reason for the refusal in the entity. If the server does not wish to make this information available to the client , the status code 404 (Not Found) can be used ...'}
    ]

    mock_ai_response = """
    ANALYSIS:
    The error "Unexpected status code: 404" indicates the server cannot find the requested resource at http://127.0.0.1:8000/. This is a standard HTTP 404 Not Found error. The server is running but the specific endpoint or resource does not exist. Common causes include incorrect URL, missing route configuration, or the resource being moved/deleted.

    RESOLUTION:
    1. Verify the URL is correct and the endpoint exists
    2. Check server route configuration
    3. Ensure the resource/file exists on the server
    4. Test with a different HTTP client
    5. Review server logs for more details
    """

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    with patch("backend.app.services.ai_analysis.redis", mock_redis), \
            patch("backend.app.services.duckduckgo.duckduckgo_search",
                  AsyncMock(return_value=mock_search_results)), \
            patch("backend.app.services.ai_analysis.call_gemini",
                  AsyncMock(return_value=mock_ai_response)):

        analysis, resolution = await ai_analyze_issue(
            url="http://127.0.0.1:8000/",
            error_message="Unexpected status code: 404",
            ddg_results=mock_search_results
        )

        print(f"Analysis: {analysis}")
        print(f"Resolution: {resolution}")

        assert isinstance(analysis, str)
        assert isinstance(resolution, str)
        assert "404" in analysis or "not found" in analysis.lower()
        assert len(resolution.split('\n')) >= 3  # Должны быть шаги
