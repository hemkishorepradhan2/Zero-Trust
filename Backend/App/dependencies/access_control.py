from fastapi import Depends, Request, HTTPException
from dependencies.auth import get_current_user
from core.risk_engine import evaluate_request
from database.session import increment_request_count
from core.audit import log_event
from dependencies.mfa import trigger_step_up
from core.observability import record_decision


def require_access(required_role: str):
	"""Factory returning a dependency that enforces role + risk-based decision."""
	def dependency(request: Request, user=Depends(get_current_user)):
		endpoint = request.url.path
		user_id = user.get("user_id")
		role = user.get("role")

		# Increment per-user per-endpoint counter (simple behavioral signal)
		count = increment_request_count(user_id, endpoint)

		# Simple heuristic for suspicious flag: header provided by client/tests
		suspicious = request.headers.get("X-Suspicious") == "1"

		context = {
			"user_role": role,
			"required_role": required_role,
			"endpoint": endpoint,
			"request_count": count,
			"suspicious": suspicious,
			# extension points
			"ip_reputation": int(request.headers.get("X-Ip-Reputation", 0)),
			"payload_anomaly_score": int(request.headers.get("X-Payload-Anomaly", 0)),
			"device_posture_score": int(request.headers.get("X-Device-Posture", 0)),
		}

		result = evaluate_request(context)
		risk = result["risk"]
		decision = result["decision"]

		if decision == "deny":
			log_event(user_id, role, endpoint, risk, "deny", details={"reasons": result.get("reasons")})
			record_decision("deny", risk)
			raise HTTPException(status_code=403, detail="Access denied by AccessGuard (risk too high)")

		# Medium risk: step-up authentication (MFA) hook
		if decision == "allow_log" and risk > 40:
			if not trigger_step_up(user_id):
				log_event(user_id, role, endpoint, risk, "deny_step_up_failed", details={"reasons": result.get("reasons")})
				record_decision("deny_step_up_failed", risk)
				raise HTTPException(status_code=403, detail="Step-up authentication required and failed")

		log_event(user_id, role, endpoint, risk, decision, details={"reasons": result.get("reasons")})
		record_decision(decision, risk)

		return {"user": user, "risk": risk, "decision": decision, "reasons": result.get("reasons", [])}

	return dependency
