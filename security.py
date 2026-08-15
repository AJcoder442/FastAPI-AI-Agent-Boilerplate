from passlib.context import CryptContext
from datetime import datetime , timedelta, timezone
from jose import jwt,JWTError
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer


from config import settings
pwd_context=CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
 )
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(
        plain_password:str,
        hashed_password:str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def create_access_token(data: dict):
    to_encode=data.copy()

    expire=datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login"
)
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session =Depends(get_db)):
        try:
            payload=jwt.decode(
                 token,
                 settings.SECRET_KEY,
                 algorithms=[settings.ALGORITHM]
            )
            email=payload.get("sub")

            if email is None:
                 raise HTTPException(
                      status_code=status.HTTP_401_UNAUTHORIZED,
                      detail= "Could not validate Credentials"

                 )
        except JWTError:
             raise HTTPException(
                  status_code=status.HTTP_401_UNAUTHORIZED,
                  detail= "Could not validate credential"
             )
        user=db.scalar(
             select(User).where(User.email==email)
        )

        if user is None:
             raise HTTPException(
                  status_code=status.HTTP_401_UNAUTHORIZED,
                  detail= "Could not validate credentials"
             )
        return user
def required_admin(current_user:User=Depends(get_current_user)):
     if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

     return current_user
     
 