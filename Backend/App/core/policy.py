from typing import Dict, Any


def evaluate_policy(user_attrs: Dict[str, Any], resource_attrs: Dict[str, Any], env: Dict[str, Any]) -> Dict[str, Any]:
    """Simple ABAC evaluator. Returns dict with 'allow':bool and optional 'reasons'.

    This is an extension point to add richer policy expressions or a policy language.
    """
    reasons = []
    # Example: deny if user's department doesn't match resource and resource is sensitive
    user_dept = user_attrs.get("department")
    res_dept = resource_attrs.get("department")
    sensitive = resource_attrs.get("sensitive", False)

    if sensitive and user_dept and res_dept and user_dept != res_dept:
        reasons.append("department_mismatch_on_sensitive_resource")
        return {"allow": False, "reasons": reasons}

    # Default allow
    return {"allow": True, "reasons": reasons}
