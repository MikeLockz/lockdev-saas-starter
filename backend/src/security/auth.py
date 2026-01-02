import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.config import settings
from src.database import get_db, user_id_ctx, tenant_id_ctx
from src.models import User

# Initialize Firebase
try:
    firebase_admin.get_app()
except ValueError:
    try:
        # In production, use explicit credentials or Application Default
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    except Exception:
        # In local dev without Google Creds, we might skip init but verify_token will fail unless mocked
        pass

security = HTTPBearer()

async def verify_token(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    # Mock for local dev testing without real Firebase token
    if settings.ENVIRONMENT == "local" and token.credentials.startswith("mock_"):
        # Format: mock_EMAIL
        email = token.credentials.split("_")[1]
        return {"uid": "mock_uid", "email": email}

    try:
        decoded_token = auth.verify_id_token(token.credentials, check_revoked=True)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    decoded_token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
) -> User:
    email = decoded_token.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token: Email missing")

    # Fetch user from DB
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    # Set RLS context with DB UUID
    user_id_ctx.set(str(user.id))
    
    return user
