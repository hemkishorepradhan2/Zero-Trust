AccessGuard (Backend)
=====================

Run the demo FastAPI app locally:

1. Create and activate a virtualenv (optional)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Start the server

```powershell
uvicorn App.main:app --reload --port 8000
```

4. Get a token and call endpoints

Login (returns JWT):

```powershell
curl "http://localhost:8000/login?username=alice&role=user"
```

Call protected endpoint with `Authorization: Bearer <token>` header.

Advanced features added:

- Middleware: `AccessGuardMiddleware` evaluates every request and enforces allow/allow+log/deny decisions.
- Risk engine: extensible `core/risk_engine.py` with IP reputation, token age, payload anomaly and ML anomaly hooks.
- Redis support: optional `database/redis_client.py` for behavioral counters and rate signals (falls back to in-memory counters).
- ABAC policy stub: `core/policy.py` provides attribute-based policy evaluation extension points.
- Observability: Prometheus metrics endpoint `/metrics` and basic metrics in `core/observability.py`.
- Structured audit logs: JSON events written to `access.log` via `core/audit.py`.

To run tests:

```powershell
pip install -r requirements.txt
pytest -q
```
