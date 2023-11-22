import sys
sys.path.append("..")

from fastapi import Depends, HTTPException, status, APIRouter
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from jose import JWTError, jwt

SECRET_KEY = "JijoNJohsnon"
ALGORITHM = "HS256"

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str

router = APIRouter(prefix="/user", tags=["user"], responses={404: {"message": "Not Found"}})

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)
def get_password_hash(password):
    return bcrypt_context.hash(password)

@router.get("/")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(models.UsersModel).all()
    return users

@router.post("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_bearer)):
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = db.query(models.UsersModel).filter(models.UsersModel.id == user_id).first()
    return user



@router.get("/query")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UsersModel).filter(models.UsersModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/reset_password")
async def reset_password(user_id: int, old_password: str, new_password: str, db: Session = Depends(get_db)):
    
    user = db.query(models.UsersModel).filter(models.UsersModel.id == user_id).first()
    # return user
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if verify_password(old_password, user.hashed_password):
        # return "Password matched"
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return db.query(models.UsersModel).filter(models.UsersModel.id == user_id).first()
    return "Password not matched"

@router.get("/update")
async def update_user():
    return "hello"

@router.post('/delete/{user_id}')
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UsersModel).filter(models.UsersModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {user_id: "deleted"}