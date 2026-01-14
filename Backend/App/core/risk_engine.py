from typing import List


SENSITIVITY_MAP = {
    "/admin/logs": 35,
    "/admin/users": 35,
    "/admin/reports": 35,
    "/user/settings": 10,
    "/user/profile": 5,
}


def calculate_risk(
    user_role: str,
    endpoint: str,
    request_count: int = 0,
    required_roles: List[str] = None,
    failed_login_count: int = 0,
    token_age_seconds: int = 0,
    token_reuse_count: int = 0,
    ip_change: bool = False,
    ua_change: bool = False,
) -> int:
    """Calculate a 0-100 risk score for a request using multiple signals.

    Signals considered:
    - Role mismatch: high risk
    - Endpoint sensitivity: per-endpoint mapping
    - Request frequency: behavior
    - Failed login attempts (recent): strong indicator of brute force
    - Token reuse count: strong indicator of token theft
    - IP/UA changes: medium indicators
    - Token age: older tokens slightly increase risk
    """
    risk_score = 5  # base risk

    # Role mismatch risk
    if required_roles and user_role not in required_roles:
        risk_score += 40

    # Endpoint sensitivity
    sensitivity = SENSITIVITY_MAP.get(endpoint, 0)
    risk_score += sensitivity

    # Behavior risk based on frequency
    if request_count > 50:
        risk_score += 30
    elif request_count > 20:
        risk_score += 20
    elif request_count > 5:
        risk_score += 10

    # Failed login attempts indicate brute-force attempts
    if failed_login_count >= 20:
        risk_score += 50
    elif failed_login_count >= 10:
        risk_score += 35
    elif failed_login_count >= 5:
        risk_score += 20

    # Token reuse (same jti seen from multiple IPs) — high risk
    if token_reuse_count >= 3:
        risk_score += 50
    elif token_reuse_count == 2:
        risk_score += 30
    elif token_reuse_count == 1:
        risk_score += 15

    # IP / UA changes
    if ip_change:
        risk_score += 15
    if ua_change:
        risk_score += 5

    # Token age (older tokens slightly more risky)
    if token_age_seconds > 60 * 60 * 24 * 7:  # older than 7 days
        risk_score += 10
    elif token_age_seconds > 60 * 60 * 24:  # older than 1 day
        risk_score += 5

    # cap between 0 and 100
    risk_score = max(0, min(100, risk_score))
    return risk_score


def evaluate_risk_score(risk_score: int) -> str:
    if risk_score <= 30:
        return "allow"
    elif 31 <= risk_score <= 60:
        return "allow+log"
    else:
        return "deny"
