from fastapi import APIRouter, Depends
from schemas import LoginRequest,UserResponse
from dependencies import get_current_user,admin_only
router=APIRouter(
    prefix="/auth",tags=["Auth"]
)

@router.post("/login")
def login(data:LoginRequest):
    return{
        "message":f"User { data.username} logged in successfully."
    }

@router.get("/me" ,response_model=UserResponse)
def get_profile(user=Depends(get_current_user)):
    return user

@router.get("/user/{user_id}")
def get_user_by_id(user_id:int):
    return {
        "user_id":user_id
    }

@router.get("/search")
def search_users(role:str="USER"):
    return {
        "filter_role":role
    }
#admin only

@router.get("/admin")
def admin_dashboard(user=Depends(admin_only)):
    return {
        "Message":"Welcome Admin"
    }


