try:
    import redis
except Exception:
    redis = None

from typing import Optional

_client = None

def init_redis(url: str = "redis://localhost:6379/0"):
    global _client
    if redis is None:
        _client = None
        return None
    _client = redis.Redis.from_url(url)
    try:
        _client.ping()
    except Exception:
        _client = None
    return _client


def increment_counter(key: str, amount: int = 1, expire_seconds: Optional[int] = None) -> int:
    """Increment counter and return new value. If Redis is not available, raise RuntimeError."""
    global _client
    if _client is None:
        raise RuntimeError("Redis client not initialized")

    val = _client.incrby(key, amount)
    if expire_seconds:
        _client.expire(key, expire_seconds)
    return int(val)


def get_counter(key: str) -> int:
    global _client
    if _client is None:
        raise RuntimeError("Redis client not initialized")
    v = _client.get(key)
    return int(v or 0)
