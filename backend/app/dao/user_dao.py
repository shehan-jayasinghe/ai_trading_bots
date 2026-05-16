import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseError
from app.models.user_model import User

logger = logging.getLogger(__name__)


class UserDAO:
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str):
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.exception("get_user_by_id failed user_id=%s", user_id)
            raise DatabaseError() from exc
