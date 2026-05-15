from sqlalchemy.ext.asyncio import (
create_async_engine,
async_sessionmaker
)

from sqlalchemy.orm import declarative_base
from app.core.config import POSTGRES_DATABASE_URL

DATABASE_URL = (
     POSTGRES_DATABASE_URL
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True                         )

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()