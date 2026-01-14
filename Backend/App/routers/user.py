from fastapi import APIRouter, Depends
from App.dependencies import require_roles

router = APIRouter(prefix="/user")

@router.get("/profile")
def profile(user=Depends(require_roles("user", "admin"))):
    return {"message": "User profile", "user": user}

@router.get("/settings")
def settings(user=Depends(require_roles("user", "admin"))):
    return {"message": "User settings", "user": user}

@router.get("/history")
def history(user=Depends(require_roles("user", "admin"))):
    return {"message": "User history", "user": user}

@router.get("/notifications")
def notifications(user=Depends(require_roles("user", "admin"))):
    return {"message": "User notifications", "user": user}

@router.get("/messages")
def messages(user=Depends(require_roles("user", "admin"))):
    return {"message": "User messages", "user": user}
