from datetime import datetime, timedelta

from fastapi import HTTPException, APIRouter, Depends
from typing import List

from sqlalchemy import func, desc
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select

from user.jwt_bearer import JwtBearer, get_current_user
from task import schemas, models
from db import get_session, get_db, SessionLocal

task_router = APIRouter(prefix="/task", tags=["task"])


@task_router.post("/", response_model=schemas.TaskRead, dependencies=[Depends(JwtBearer())])
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_session), user: get_current_user = Depends()):
    count_last_task = await db.execute(select(models.Task).filter(models.Task.title == task.title) \
        .filter(models.Task.create_date.between(datetime.utcnow() - timedelta(minutes=1), datetime.utcnow())))
    count_last_task = count_last_task.all()

    if not bool(count_last_task):
        db_task = models.Task(title=task.title, description=task.description, owner=user["user_id"])
        db.add(db_task)
        db_status_task = models.StatusTask(status="Невыполнено", task=db_task)
        db.add(db_status_task)
        await db.commit()
        db.refresh(db_task)
        return db_task
    else:
        raise HTTPException(422, {'msg': "Can not create: time cool down"})


@task_router.get("/{id}/", response_model=schemas.TaskRead, dependencies=[Depends(JwtBearer())])
async def get_retrieve_task(id: int, db: AsyncSession = Depends(get_session), user: get_current_user = Depends()):
    db_task = await db.execute(select(models.Task).filter(models.Task.owner == user["user_id"]).filter(models.Task.id == id))
    db_task = db_task.scalars().first()
    if db_task:
        return db_task
    else:
        raise HTTPException(status_code=404, detail="Task is not found")


@task_router.get("/", response_model=List[schemas.TaskReadList], dependencies=[Depends(JwtBearer())])
async def get_task_list(db: AsyncSession = Depends(get_session), order_by: str = None,
                        limit: int = None, is_complete: bool = None, date_from: datetime = None,
                        date_by: datetime = None, user: get_current_user = Depends()):
    id_current_user = user["user_id"]

    query = select(models.Task).filter(models.Task.owner == id_current_user).limit(limit)

    if order_by is not None:
        query = query.order_by(desc(order_by))
    if is_complete is not None:
        query = query.filter(models.Task.is_complete == is_complete)
    if date_from is not None:
        query = query.filter(func.date(models.Task.create_date) >= date_from)
    if date_by is not None:
        query = query.filter(func.date(models.Task.create_date) <= date_by)
    db_task_list = await db.execute(query)   
    db_task_list = db_task_list.scalars().all()
    return db_task_list


@task_router.put("/update/{id}/", response_model=schemas.TaskRead, dependencies=[Depends(JwtBearer())])
async def update_task(id: int, task: schemas.TaskUpdate,
                      db: AsyncSession = Depends(get_session), user: get_current_user = Depends()):
    db_task = await db.execute(select(models.Task).filter(models.Task.owner == user["user_id"]).filter(models.Task.id == id))
    db_task = db_task.scalars().first()
    if db_task:
        for var, value in vars(task).items():
            setattr(db_task, var, value) if value else None
        await db.commit()
        new_task = await db.execute(select(models.Task).where(models.Task.id == id))
        return new_task.scalars().first()
    else:
        raise HTTPException(status_code=404, detail="Task is not found")


@task_router.put("/update-status/{id}/", response_model=schemas.TaskRead, dependencies=[Depends(JwtBearer())])
async def update_status_task(id: int, status_task: schemas.StatusTaskCreate, db: AsyncSession = Depends(get_session)):
    db_task = await db.execute(select(models.Task).filter(models.Task.id == id).options(joinedload(models.Task.status_task)))
    db_task = db_task.scalars().first()
    db_status_task = models.StatusTask(status=status_task.status, task=db_task)
    db.add(db_status_task)
    await db.commit()
    return db_task


@task_router.delete("/remove/{id}/", dependencies=[Depends(JwtBearer())], status_code=200)
async def delete_task(id: int, db: AsyncSession = Depends(get_session), user: get_current_user = Depends()):
    query = sqlalchemy_delete(models.Task).filter(models.Task.id == id).filter(models.Task.owner == user["user_id"])
    await db.execute(query)
    await db.commit()
    return {}
