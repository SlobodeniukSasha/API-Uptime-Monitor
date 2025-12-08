import hashlib


def prompt_cache_key(url: str, error: str) -> str:
    """
    Generate a persistent cache key for identical incidents.
    Useful for Redis or in-memory caching.
    """
    normalized_error = " ".join(error.lower().split()[:10])
    payload = f"{url}:{normalized_error}"
    return hashlib.md5(payload.encode()).hexdigest()
