from fastapi import APIRouter, Depends
from dependencies.access_control import require_access

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def stats(access=Depends(require_access("admin"))):
	return {"stats": {"users": 2, "uptime": "24h"}, "risk": access["risk"]}


@router.get("/secrets")
def secrets(access=Depends(require_access("admin"))):
	return {"secret": "42", "risk": access["risk"]}
