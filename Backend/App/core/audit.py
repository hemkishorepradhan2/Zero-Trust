import logging
import datetime
import json

logger = logging.getLogger("accessguard")
if not logger.handlers:
	handler = logging.FileHandler("access.log")
	formatter = logging.Formatter("%(asctime)s %(message)s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)

_in_memory = []


def log_event(user_id: str, role: str, endpoint: str, risk: int, decision: str, details: dict = None):
	event = {
		"user_id": user_id,
		"role": role,
		"endpoint": endpoint,
		"risk": risk,
		"decision": decision,
		"details": details or {},
		"timestamp": datetime.datetime.utcnow().isoformat()
	}
	_in_memory.append(event)
	# Write as structured JSON for easier ingestion by ELK/Graylog
	try:
		logger.info(json.dumps(event))
	except Exception:
		logger.info(str(event))


def get_audit_events():
	return list(_in_memory)
