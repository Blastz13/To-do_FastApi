import datetime

from pydantic import BaseModel, root_validator, typing


class StatusTaskCreate(BaseModel):
    status: str

    class Config:
        orm_mode = True


class StatusTaskRead(BaseModel):
    status: str
    create_date: datetime.datetime

    class Config:
        orm_mode = True


class TaskUpdate(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True


class TaskRead(BaseModel):
    id: int
    owner: int
    title: str
    description: str
    create_date: datetime.datetime
    status_task: list[StatusTaskRead] = []

    @root_validator
    def compute_status(cls, values) -> typing.Dict:
        try:
            values["current_status"] = values["status_task"][-1].status
        except:
            pass
        return values

    class Config:
        orm_mode = True
        

class TaskReadList(BaseModel):
    id: int
    owner: int
    title: str
    description: str
    create_date: datetime.datetime

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True
