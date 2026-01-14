from fastapi import FastAPI, Depends, Response
from core.security import create_access_token
from routers import users, admin
from core.middleware import AccessGuardMiddleware
from database import redis_client
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="AccessGuard")

# Initialize optional Redis client (silently continue if unavailable)
try:
	redis_client.init_redis()
except Exception:
	pass

app.add_middleware(AccessGuardMiddleware)

app.include_router(users.router)
app.include_router(admin.router)


@app.post("/login")
def login(username: str, role: str):
	"""Return a simple JWT for testing purposes."""
	token = create_access_token({"sub": username, "role": role})
	return {"access_token": token, "token_type": "bearer"}


@app.get("/health")
def health():
	return {"status": "ok"}


@app.get("/metrics")
def metrics():
	data = generate_latest()
	return Response(content=data, media_type=CONTENT_TYPE_LATEST)
