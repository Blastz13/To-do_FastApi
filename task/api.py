from datetime import datetime, timedelta

from fastapi import HTTPException, APIRouter, Depends
from typing import List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from user.jwt_bearer import JwtBearer, get_current_user
from task import schemas, models
from db import get_db

task_router = APIRouter(prefix="/task", tags=["task"])


@task_router.post("/", response_model=schemas.TaskRead, dependencies=[Depends(JwtBearer())])
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), user: get_current_user = Depends()):
    count_last_task = db.query(models.Task).filter(models.Task.title == task.title) \
        .filter(models.Task.create_date.between(datetime.utcnow() - timedelta(minutes=1), datetime.utcnow())).count()

    if count_last_task == 0:
        db_task = models.Task(title=task.title, description=task.description, owner=user["user_id"])
        db.add(db_task)
        db.commit()
        db_status_task = models.StatusTask(status="Невыполнено", task=db_task)
        db.add(db_status_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    else:
        raise HTTPException(422, {'msg': "Can not create: time cool down"})


@task_router.get("/{id}/", response_model=schemas.TaskRead, dependencies=[Depends(JwtBearer())])
async def get_retrieve_task(id: int, db: Session = Depends(get_db), user: get_current_user = Depends()):
    db_task = db.query(models.Task).filter(models.Task.owner == user["user_id"]).filter(models.Task.id == id)
    if bool(db_task.first()):
        return db_task.first()
    else:
        raise HTTPException(status_code=404, detail="Task is not found")


@task_router.get("/", response_model=List[schemas.TaskRead], dependencies=[Depends(JwtBearer())])
async def get_task_list(db: Session = Depends(get_db), order_by: str = None,
                        limit: int = None, is_complete: bool = None, date_from: datetime = None,
                        date_by: datetime = None, user: get_current_user = Depends()):
    id_current_user = user["user_id"]
    db = db.query(models.Task).filter(models.Task.owner == id_current_user).limit(limit)
    if order_by is not None:
        db = db.order_by(desc(order_by))
    if is_complete is not None:
        db = db.filter(models.Task.is_complete == is_complete)
    if date_from is not None:
        db = db.filter(func.date(models.Task.create_date) >= date_from)
    if date_by is not None:
        db = db.filter(func.date(models.Task.create_date) <= date_by)
    return db.all()


@task_router.put("/update/{id}/", response_model=schemas.TaskRead, dependencies=[Depends(JwtBearer())])
async def update_task(id: int, task: schemas.TaskUpdate,
                      db: Session = Depends(get_db), user: get_current_user = Depends()):
    db_task = db.query(models.Task).filter(models.Task.owner == user["user_id"]).filter(models.Task.id == id)
    if db_task.count() > 0:
        for var, value in vars(task).items():
            setattr(db_task.first(), var, value) if value else None
        db.commit()
        return db.query(models.Task).get(id)
    else:
        raise HTTPException(status_code=404, detail="Task is not found")


@task_router.put("/update-status/{id}/", response_model=schemas.TaskRead, dependencies=[Depends(JwtBearer())])
async def update_status_task(id: int, status_task: schemas.StatusTaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).get(id)
    db_status_task = models.StatusTask(status=status_task.status, task=db_task)
    db.add(db_status_task)
    db.commit()
    return db_task


@task_router.delete("/remove/{id}/", dependencies=[Depends(JwtBearer())], status_code=200)
async def delete_task(id: int, db: Session = Depends(get_db), user: get_current_user = Depends()):
    db.query(models.Task).filter(models.Task.id == id).filter(models.Task.owner == user["user_id"]).delete()
    db.commit()
    return {}
