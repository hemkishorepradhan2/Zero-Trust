from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core.security import decode_token, token_age_minutes
from core.risk_engine import evaluate_request
from core.audit import log_event
from database.session import get_request_count
from core.observability import record_decision


class AccessGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Leave health and login open
        if path in ("/health", "/login", "/metrics"):
            return await call_next(request)

        # Try to decode token (if present)
        auth_header = request.headers.get("authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        payload = None
        user_id = "anonymous"
        role = "anonymous"
        token_age = 0
        if token:
            payload = decode_token(token)
            if payload:
                user_id = payload.get("sub") or user_id
                role = payload.get("role") or role
                token_age = token_age_minutes(payload)

        # Behavioral signal
        try:
            count = get_request_count(user_id, path)
        except Exception:
            count = 0

        suspicious = request.headers.get("X-Suspicious") == "1"

        context = {
            "user_role": role,
            "required_role": request.scope.get("route", {}).get("path_params", {}).get("role") if request.scope.get("route") else None,
            "endpoint": path,
            "request_count": count,
            "suspicious": suspicious,
            "ip_reputation": 0,
            "token_age_minutes": token_age,
            "payload_anomaly_score": 0,
            "device_posture_score": 0,
            "ml_anomaly_score": 0,
        }

        result = evaluate_request(context)
        risk = result["risk"]
        decision = result["decision"]

        # Log decision and record metrics
        log_event(user_id, role, path, risk, decision, details={"reasons": result.get("reasons")})
        record_decision(decision, risk)

        # Enforce decision
        if decision == "deny":
            return Response(status_code=403, content="Access denied by AccessGuard (risk too high)")

        # For allow_log, add header for downstream handlers and continue
        if decision == "allow_log":
            response = await call_next(request)
            response.headers["X-AccessGuard-Risk"] = str(risk)
            response.headers["X-AccessGuard-Decision"] = decision
            return response

        return await call_next(request)
