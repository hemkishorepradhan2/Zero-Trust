from fastapi import Depends, HTTPException

def get_current_user():
    return {
        "username":"Hem",
        "role":"ADMIN"
    }

def admin_only(user=Depends(get_current_user)):
    if user["role"] !="ADMIN":
        raise HTTPException(status_code=403,detail="Admin only")
    return user
