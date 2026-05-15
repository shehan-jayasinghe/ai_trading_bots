from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import AUTH_SECRET, JWT_ALGORITHM
from app.db.dependencies import get_postgres_db
from app.services.user_service import UserService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_postgres_db),
):
    if not AUTH_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Server auth is not configured",
        )
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            AUTH_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
            )

        user = await UserService.get_current_user(db, str(user_id))
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
            )
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )
