from fastapi import APIRouter, Depends
from src.schemas.users import UserRead
from src.security.auth import get_current_user
from src.models import User

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user
