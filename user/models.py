from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from db import Base
import datetime


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    create_date = Column(DateTime, default=datetime.datetime.now())
    tasks = relationship('Task', backref='user')
