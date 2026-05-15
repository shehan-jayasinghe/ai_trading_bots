from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.user_model import User
from app.schemas.user_schema import UserResponse

router = APIRouter(tags=["protected"])


@router.get("/hello/secure")
def secure_hello(user: User = Depends(get_current_user)):
    return {
        "message": "authenticated route",
        "user": UserResponse.model_validate(user),
    }
