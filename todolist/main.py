from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uvicorn
from database import SessionLocal, engine
import models
import schemas
import crud


# Создание всех таблиц в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=" ToDoList")

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Маршрут для создания новой задачи
@app.post("/tasks/", response_model=schemas.Task)
def create_task(user_id:int, task: Annotated[schemas.TaskCreate, Depends()], db: Session = Depends(get_db)):
    return crud.create_user_task(db=db, task=task, user_id=user_id)

# Маршрут для получения списка задач
@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)
