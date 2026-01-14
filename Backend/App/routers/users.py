from fastapi import APIRouter, Depends
from dependencies.access_control import require_access

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def list_users(access=Depends(require_access("user"))):
	return {"users": ["alice", "bob"], "risk": access["risk"]}


@router.get("/me")
def me(access=Depends(require_access("user"))):
	return {"user": access["user"], "risk": access["risk"]}
