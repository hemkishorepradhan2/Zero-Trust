from typing import List


SENSITIVITY_MAP = {
    "/admin/logs": 30,
    "/admin/users": 30,
    "/admin/reports": 30,
    "/user/settings": 10,
}


def calculate_risk(user_role: str, endpoint: str, request_count: int = 0, required_roles: List[str] = None) -> int:
    """Calculate a 0-100 risk score for a request.

    - Base risk: 5
    - Role mismatch: +40 if user's role not in required_roles
    - Endpoint sensitivity: from SENSITIVITY_MAP
    - Behavior: request_count thresholds add risk
    """
    risk_score = 5  # base risk

    # Role mismatch risk
    if required_roles and user_role not in required_roles:
        risk_score += 40

    # Endpoint sensitivity
    sensitivity = SENSITIVITY_MAP.get(endpoint, 0)
    risk_score += sensitivity

    # Behavior risk based on frequency
    if request_count > 20:
        risk_score += 30
    elif request_count > 10:
        risk_score += 20
    elif request_count > 5:
        risk_score += 10

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
