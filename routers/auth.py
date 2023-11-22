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

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/auth", tags=["auth"], responses={404: {"user": "Nort Authorized"}})

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def http_exception():
    raise HTTPException(status_code=404, detail="Item not found")

def get_password_hash(password):
    return bcrypt_context.hash(password)


async def authenticate_user (username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.UsersModel).filter(models.UsersModel.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return user

async def create_access_token(username:str, user_id : int, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"sub": username,"id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            get_user_exception()
    except JWTError:
        get_user_exception()
    user = db.query(models.UsersModel).filter(models.UsersModel.username == username).first()
    if user is None:
        get_user_exception()
    return user

@router.post("/create/user")
async def create_new_user(user: CreateUser, db: Session = Depends(get_db) ):
    try:
        user_model = models.UsersModel()
        user_model.username = user.username
        user_model.email = user.email
        user_model.first_name = user.first_name
        user_model.last_name = user.last_name
        user_model.hashed_password = get_password_hash(user.password)
        db.add(user_model)
        db.commit()
        db.refresh(user_model)
    except:
        raise HTTPException(status_code=400, detail="User already exists")
    return user_model

@router.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user =await authenticate_user(form_data.username, form_data.password,db)
    if not user:
        token_exception()
    token = await create_access_token(user.username, user.id)
    u = await get_current_user(token, db)
    return {"access_token": token, "token_type": "bearer", "user": u}



#Exception Handling


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status. HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status. HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response