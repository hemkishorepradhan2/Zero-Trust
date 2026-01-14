from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Support running as a package (recommended) and as a script
try:
	from .routers import auth, admin, user, public
except Exception:
	import sys
	from pathlib import Path

	# When running `python main.py` the parent of the `App` package
	# may not be on sys.path. Add the package parent so absolute
	# imports like `from App.routers import ...` work.
	pkg_root = Path(__file__).resolve().parent.parent
	if str(pkg_root) not in sys.path:
		sys.path.insert(0, str(pkg_root))
	from App.routers import auth, admin, user, public


app = FastAPI(title="AccessGuard Zero-Trust API")

# Allow frontend development servers to access the API
origins = [
	"http://localhost:5173",
	"http://localhost:3000",
	"http://127.0.0.1:5173",
	"http://127.0.0.1:3000",
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  # during dev allow all; restrict in production
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(public.router)


from App.database.models import Base
from App.database.session import engine


@app.on_event("startup")
def startup_event():
	# Ensure database tables exist when the app starts
	Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("App.main:app", host="127.0.0.1", port=8000, reload=True)
	



