import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from .auth import get_current_user, get_user_exception
from routers import auth

router = APIRouter(prefix="/todos",tags=['todos'],responses={404: {"description": "Not found"}})

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6,description="Priority must be between 1 and 5")
    complete: bool = False

@router.get("/")
async def real_all(db: Session = Depends(get_db)):
    return db.query(models.TodoModel).all()

@router.get("/user")
async def read_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        get_user_exception()
    return db.query(models.TodoModel).filter(models.TodoModel.owner_id == user.id).all()

@router.get("/{todo_id}")
async def read_one(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        get_user_exception()
    todo_model = db.query(models.TodoModel)\
        .filter(models.TodoModel.id == todo_id)\
            .filter(models.TodoModel.owner_id == user.id)\
                .first()
    if todo_model is None:
        http_exception()
    return todo_model

@router.post("/")
def create(todo: Todo, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user is None:
        get_user_exception()
    todo_model = models.TodoModel()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.id
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return {
        "status": "201",
        "data": todo_model
    }

@router.put("/{user_id}")
async def update(user_id: int, todo: Todo, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user is None:
        get_user_exception()
    todo_model = db.query(models.TodoModel).filter(models.TodoModel.id == user_id).filter(models.TodoModel.owner_id == user.id).first()
    if todo_model is None:
        http_exception()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    db.commit()
    db.refresh(todo_model)
    return {
        "status": "200",
        "data": todo_model
    }
@router.delete("/{id}")
async def delete(id: int, db: Session = Depends(get_db),user: dict = Depends(get_current_user)):
    if user is None:
        get_user_exception()
    todo_model = db.query(models.TodoModel).filter(models.TodoModel.id == id).filter(models.TodoModel.owner_id == user.id).first()
    if todo_model is None:
        http_exception()
    db.delete(todo_model)
    db.commit()
    return {
        "status": "200",
        "data": todo_model
    }

def http_exception():
    raise HTTPException(status_code=404, detail="Todo not found", headers={"X-Error": "There goes my error"})