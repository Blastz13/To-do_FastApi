import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True


class UserRead(BaseModel):
    id: int
    username: str
    password: str
    create_date: datetime.datetime

    class Config:
        orm_mode = True


class UserLogin(UserCreate):
    pass
