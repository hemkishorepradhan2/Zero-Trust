from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.dependencies import require_roles
from App.database.session import get_db
from App.database.models import User
from App.schemas.user import UserCreate, UserOut
from App.core.security import hash_password

router = APIRouter(prefix="/admin")

@router.get("/data")
def get_data(user=Depends(require_roles("admin"))):
    return {"message": "Admin data", "user": user}

@router.get("/settings")
def get_settings(user=Depends(require_roles("admin"))):
    return {"message": "Admin settings", "user": user}

@router.get("/logs")
def get_logs(user=Depends(require_roles("admin"))):
    return {"message": "Admin logs", "user": user}

@router.get("/users")
def get_users(user=Depends(require_roles("admin"))):
    return {"message": "Admin users", "user": user}

@router.get("/reports")
def get_reports(user=Depends(require_roles("admin"))):
    return {"message": "Admin reports", "user": user}
@router.post("/users/create", response_model=UserOut)
def create_user(
    user_data: UserCreate,
    user=Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):

    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Hash password before saving
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user