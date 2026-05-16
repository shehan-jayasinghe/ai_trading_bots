import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import AUTH_SECRET, JWT_ALGORITHM
from app.core.exceptions import ConfigurationError, UnauthorizedError
from app.db.dependencies import get_postgres_db
from app.services.user_service import UserService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_postgres_db),
):
    if not AUTH_SECRET:
        raise ConfigurationError("AUTH_SECRET is not configured")

    try:
        payload = jwt.decode(
            credentials.credentials,
            AUTH_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except PyJWTError as exc:
        raise UnauthorizedError() from exc

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError()

    user = await UserService.get_current_user(db, str(user_id))
    if user is None:
        raise UnauthorizedError("User not found")

    return user
