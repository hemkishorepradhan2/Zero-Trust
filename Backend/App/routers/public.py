from fastapi import APIRouter

router = APIRouter(prefix="/public")

@router.get("/info")
def info():
    return {"message": "Public info"}

@router.get("/status")
def status():
    return {"message": "Public status"}
