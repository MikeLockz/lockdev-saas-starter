import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import current_user_id
from app.core.db import get_db
from app.models.user import User

# Initialize Firebase
try:
    firebase_app = firebase_admin.get_app()
except ValueError:
    # In local dev without credentials, this will use mock or fail gracefully
    try:
        firebase_app = firebase_admin.initialize_app()
    except Exception:
        # Fallback for environments without any GCP credentials
        firebase_app = None

security = HTTPBearer()


async def verify_token(res: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if not firebase_app:
        # Development bypass if firebase not configured?
        # Better to mock or use a dummy token.
        # For now, we expect real tokens or mock them in tests.
        raise HTTPException(status_code=500, detail="Firebase not initialized")

    try:
        return auth.verify_id_token(res.credentials)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e!s}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: dict = Depends(verify_token), db: AsyncSession = Depends(get_db)
) -> User:
    email = token.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Token missing email")

    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Set contextvar for RLS
    current_user_id.set(user.id)

    return user


def require_mfa(token: dict = Depends(verify_token)):
    """
    Dependency to enforce MFA for sensitive routes.
    GCIP tokens have 'amr' claim if MFA was used.
    """
    # 'amr' (Authentication Methods References) should contain 'mfa' or 'second_factor'
    amr = token.get("amr", [])
    if "mfa" not in amr and "second_factor" not in amr:
        # Also check auth_time if needed
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MFA required for this action",
        )
    return True
