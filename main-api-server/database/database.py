import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL_LOCAL')


engine = create_async_engine(DATABASE_URL, pool_size=200, max_overflow=100, pool_timeout=10, pool_recycle=35, echo=False)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# импорт моделей
#from auth.models import *
from src.users.models import *
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_models():
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
