from core.risk_engine import evaluate_request


def test_low_risk():
    ctx = {
        "user_role": "user",
        "required_role": "user",
        "endpoint": "/users",
        "request_count": 1,
        "suspicious": False,
    }
    res = evaluate_request(ctx)
    assert res["risk"] <= 30
    assert res["decision"] == "allow"


def test_role_mismatch_high_risk():
    ctx = {
        "user_role": "user",
        "required_role": "admin",
        "endpoint": "/admin",
        "request_count": 200,
        "suspicious": True,
        "ip_reputation": 80,
-    }
+    }
+    res = evaluate_request(ctx)
+    assert res["risk"] >= 60
+    assert res["decision"] in ("allow_log", "deny")
