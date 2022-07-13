from fastapi import HTTPException, APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from werkzeug.security import generate_password_hash, check_password_hash

from fastapi.encoders import jsonable_encoder
from user.jwt_handler import sign_jwt

from .models import *
from .schemas import *
from db import get_session
from sqlalchemy.future import select

user_router = APIRouter(prefix="/auth", tags=["auth"])


@user_router.post('/signup')
async def sign_up(user: UserCreate, db: AsyncSession = Depends(get_session)):
    db_user = await db.execute(select(User).filter(User.username == user.username))
    db_user = db_user.first()
    if bool(db_user):
        raise HTTPException(status_code=400, detail="User with username already exists")
    db_user = User(username=user.username, password=generate_password_hash(user.password))
    db.add(db_user)
    await db.commit()
    return jsonable_encoder(sign_jwt(db_user.id))


@user_router.post('/login')
async def login(user: UserLogin, db: AsyncSession = Depends(get_session)):
    db_user = await db.execute(select(User).filter(User.username == user.username))
    db_user = db_user.scalars().first()
    if db_user is not None and check_password_hash(db_user.password, user.password):
        return jsonable_encoder(sign_jwt(db_user.id))
    else:
        raise HTTPException(status_code=400, detail="Invalid username or password")
