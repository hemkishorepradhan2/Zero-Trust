from collections import defaultdict
from . import redis_client

_counts = defaultdict(int)


def increment_request_count(user_id: str, endpoint: str) -> int:
	key = f"{user_id}:{endpoint}"
	try:
		# Try Redis first (sliding window semantics can be added)
		val = redis_client.increment_counter("cnt:" + key, 1, expire_seconds=60 * 60)
		return val
	except Exception:
		_counts[key] += 1
		return _counts[key]


def get_request_count(user_id: str, endpoint: str) -> int:
	key = f"{user_id}:{endpoint}"
	try:
		return redis_client.get_counter("cnt:" + key)
	except Exception:
		return _counts.get(key, 0)
