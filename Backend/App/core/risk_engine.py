import datetime
from typing import Dict, Any, Optional

# Sensitivity mapping (pluggable)
ENDPOINT_SENSITIVITY = {
    "/admin": 40,
    "/users": 20,
    "/health": 5
}


def _clamp(n: int) -> int:
    return max(0, min(100, n))


def calculate_risk_factors(context: Dict[str, Any]) -> Dict[str, Any]:
    """Return a breakdown of contributing risks and a combined score.

    context keys: user_role, required_role, endpoint, request_count, suspicious,
    ip_reputation (0-100), token_age_minutes, payload_anomaly_score (0-100), device_posture_score (0-100)
    """
    score = 10  # base risk
    reasons = []

    user_role = context.get("user_role")
    required_role = context.get("required_role")
    endpoint = context.get("endpoint")
    request_count = int(context.get("request_count", 0))
    suspicious = bool(context.get("suspicious", False))

    # Role mismatch
    if user_role != required_role:
        score += 30
        reasons.append("role_mismatch")

    # Endpoint sensitivity
    sensitivity = ENDPOINT_SENSITIVITY.get(endpoint, 10)
    score += sensitivity
    reasons.append(f"endpoint_sensitivity={sensitivity}")

    # Behavior: request frequency
    if request_count > 100:
        score += 30
        reasons.append("very_high_rate")
    elif request_count > 50:
        score += 15
        reasons.append("high_rate")

    # Suspicious flag
    if suspicious:
        score += 25
        reasons.append("suspicious_flag")

    # IP reputation (higher value == worse)
    ip_rep = int(context.get("ip_reputation", 0))
    if ip_rep > 0:
        ip_risk = min(20, ip_rep // 5)
        score += ip_risk
        reasons.append(f"ip_reputation={ip_rep}")

    # Token age: older tokens may be risky if extremely old
    token_age = int(context.get("token_age_minutes", 0))
    if token_age and token_age > 60 * 24 * 7:
        score += 15
        reasons.append("stale_token")
    elif token_age and token_age > 60 * 24:
        score += 5
        reasons.append("old_token")

    # Payload anomaly
    payload_score = int(context.get("payload_anomaly_score", 0))
    if payload_score > 0:
        payload_risk = min(30, payload_score // 3)
        score += payload_risk
        reasons.append(f"payload_anomaly={payload_score}")

    # Device posture (0 good - 100 bad)
    device_score = int(context.get("device_posture_score", 0))
    if device_score > 0:
        dev_risk = min(20, device_score // 5)
        score += dev_risk
        reasons.append(f"device_posture={device_score}")

    # ML anomaly scorer hook (stub): allow pluggable model to add risk
    ml_score = int(context.get("ml_anomaly_score", 0))
    if ml_score > 0:
        ml_risk = min(40, ml_score // 2)
        score += ml_risk
        reasons.append(f"ml_anomaly={ml_score}")

    final = _clamp(score)

    return {
        "risk": final,
        "score_components": score,
        "reasons": reasons,
        "computed_at": datetime.datetime.utcnow().isoformat()
    }


def map_decision(risk: int) -> str:
    if risk <= 30:
        return "allow"
    if risk <= 60:
        return "allow_log"
    return "deny"


def evaluate_request(context: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate request based on provided context dict.

    Returns: {risk:int, decision:str, reasons:[...], details: {...}}
    """
    factors = calculate_risk_factors(context)
    decision = map_decision(factors["risk"])
    return {
        "risk": factors["risk"],
        "decision": decision,
        "reasons": factors["reasons"],
        "details": factors
    }
