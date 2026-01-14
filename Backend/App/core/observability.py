from prometheus_client import Counter, Gauge, Histogram

REQUEST_RISK = Histogram("accessguard_request_risk", "Risk score for evaluated requests")
DECISIONS = Counter("accessguard_decisions_total", "Counts of access decisions", ["decision"])


def record_decision(decision: str, risk: int):
    try:
        DECISIONS.labels(decision=decision).inc()
        REQUEST_RISK.observe(risk)
    except Exception:
        pass
