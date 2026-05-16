import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import POSTGRES_DATABASE_URL
from app.core.exceptions import ConfigurationError, DatabaseError
from app.db.postgres import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def get_postgres_db():
    if not POSTGRES_DATABASE_URL:
        raise ConfigurationError("Database URL is not configured")

    try:
        async with AsyncSessionLocal() as db:
            try:
                yield db
            except SQLAlchemyError as exc:
                await db.rollback()
                logger.exception("Database session error during request")
                raise DatabaseError() from exc
            except Exception:
                await db.rollback()
                raise
    except SQLAlchemyError as exc:
        logger.exception("Failed to open database session")
        raise DatabaseError() from exc
