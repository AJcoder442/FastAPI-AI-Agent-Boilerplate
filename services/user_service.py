import secrets
from datetime import datetime, timedelta, timezone
from config import settings
from fastapi import HTTPException,status
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import User, RefreshSession
from schemas import UserCreate, UserLogin, UserUpdate, PasswordChange, TokenRefreshRequest, LogoutRequest
from fastapi.security import OAuth2PasswordRequestForm
from security import (
    hash_password,
    verify_password,
    create_access_token 
)


def register_user(user:UserCreate,db:Session):
 existing_user=db.scalar(
    select(User).where(User.email == user.email)

 )

 if existing_user:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already exits "
    )
 db_user=User(
    username=user.username,
    email=user.email,
    hashed_password=hash_password(user.password),
    is_active=True,
    role="user"
 )

 db.add(db_user)
 db.commit()
 db.refresh(db_user)


 return db_user

def login_user(form_data:OAuth2PasswordRequestForm, db: Session):
  user=db.scalar(select(User).where(User.email==form_data.username))

  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail= "Invalid email or password"
    )
  if not verify_password(
    form_data.password,
    user.hashed_password
  ):
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail= "Invalid email or password"
    ) 
  access_token= create_access_token(
    data={"sub": user.email}
  )

  # Generate refresh token
  refresh_token = secrets.token_urlsafe(32)
  expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

  db_session = RefreshSession(
      user_id=user.id,
      refresh_token=refresh_token,
      expires_at=expires_at
  )
  db.add(db_session)
  db.commit()

  return {
     "access_token" : access_token,
     "token_type": "bearer",
     "refresh_token": refresh_token
  }

def refresh_access_token(payload: TokenRefreshRequest, db: Session):
    session = db.scalar(
        select(RefreshSession).where(RefreshSession.refresh_token == payload.refresh_token)
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    if datetime.now(timezone.utc) > session.expires_at:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    
    user = session.user
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    new_access_token = create_access_token(data={"sub": user.email})
    
    new_refresh_token = secrets.token_urlsafe(32)
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    session.refresh_token = new_refresh_token
    session.expires_at = new_expires_at
    db.commit()
    db.refresh(session)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }

def logout_user(payload: LogoutRequest, db: Session):
    session = db.scalar(
        select(RefreshSession).where(RefreshSession.refresh_token == payload.refresh_token)
    )
    if session:
        db.delete(session)
        db.commit()
    return {"message": "Logged out successfully"}

def update_user_profile(user_id: int, update_data: UserUpdate, db: Session):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if update_data.username is not None:
        if update_data.username != user.username:
            existing = db.scalar(select(User).where(User.username == update_data.username))
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
        user.username = update_data.username
        
    if update_data.email is not None:
        if update_data.email != user.email:
            existing = db.scalar(select(User).where(User.email == update_data.email))
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        user.email = update_data.email
        
    db.commit()
    db.refresh(user)
    return user

def change_user_password(user_id: int, pw_data: PasswordChange, db: Session):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_password(pw_data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
        
    user.hashed_password = hash_password(pw_data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}