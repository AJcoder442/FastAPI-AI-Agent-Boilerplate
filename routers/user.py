from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from schemas import UserCreate, UserResponse, Token, UserUpdate, PasswordChange, TokenRefreshRequest, LogoutRequest
from security import get_current_user
from models import User

from services import user_service

router= APIRouter(prefix="/users",tags=["Users"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
def register_user(
    user: UserCreate,
    db: Session=Depends(get_db)
):
    return user_service.register_user(user,db)
@router.post("/login", response_model=Token)
def login_user(
     form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return user_service.login_user(form_data, db)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return user_service.update_user_profile(current_user.id, update_data, db)

@router.put("/me/change-password")
def change_password(
    pw_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return user_service.change_user_password(current_user.id, pw_data, db)

@router.post("/refresh", response_model=Token)
def refresh_token(
    payload: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    return user_service.refresh_access_token(payload, db)

@router.post("/logout")
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db)
):
    return user_service.logout_user(payload, db)