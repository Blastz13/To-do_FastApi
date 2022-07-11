from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from db import Base
import datetime


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    create_date = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    status_task = relationship('StatusTask', backref='task', cascade="all, delete-orphan")
    owner = Column(Integer, ForeignKey('user.id'))


class StatusTask(Base):
    __tablename__ = 'status_task'
    id = Column(Integer, primary_key=True)
    status = Column(String)
    create_date = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    task_id = Column(Integer, ForeignKey('task.id', ondelete='CASCADE'))
