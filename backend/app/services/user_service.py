from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.user_dao import UserDAO


class UserService:
    @staticmethod
    async def get_current_user(db: AsyncSession, user_id: str):
        return await UserDAO.get_user_by_id(db, user_id)
