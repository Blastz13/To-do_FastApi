from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from user.api import user_router
from task.api import task_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(task_router)
