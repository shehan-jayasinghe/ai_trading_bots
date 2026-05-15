from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User


class UserDAO:
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str):
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
