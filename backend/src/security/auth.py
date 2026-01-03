"""
Authentication and session tracking module.

Handles:
- Firebase token verification
- Session creation/tracking
- RLS context setup
"""
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from datetime import datetime, timezone

from src.config import settings
from src.database import get_db, user_id_ctx, tenant_id_ctx
from src.models import User
from src.models.sessions import UserSession

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
    """Verify Firebase JWT token."""
    # Mock for local dev testing without real Firebase token
    if settings.ENVIRONMENT == "local" and token.credentials.startswith("mock_"):
        # Format: mock_EMAIL
        email = token.credentials.split("_", 1)[1]
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


async def get_or_create_session(
    user: User,
    firebase_uid: str,
    request: Request,
    db: AsyncSession,
) -> UserSession:
    """
    Get existing session or create a new one for this request.
    
    Sessions are keyed by firebase_uid to allow tracking across requests
    with the same token.
    """
    # Extract request info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Look for existing active session with this firebase_uid
    stmt = select(UserSession).where(
        UserSession.user_id == user.id,
        UserSession.firebase_uid == firebase_uid,
        UserSession.is_revoked == False,  # noqa: E712
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    now = datetime.now(timezone.utc)
    
    if session:
        # Update last_active_at
        session.last_active_at = now
        session.ip_address = ip_address
        if user_agent:
            session.user_agent = user_agent
    else:
        # Create new session
        session = UserSession(
            user_id=user.id,
            firebase_uid=firebase_uid,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info={
                "user_agent": user_agent,
                "ip_address": ip_address,
            },
            created_at=now,
            last_active_at=now,
        )
        db.add(session)
    
    await db.commit()
    await db.refresh(session)
    
    return session


async def get_current_user(
    request: Request,
    decoded_token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user and set up session/RLS context.
    """
    email = decoded_token.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token: Email missing")

    # Fetch user from DB
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check if user is soft-deleted
    if user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="Account has been deactivated")
    
    # Set RLS context with DB UUID
    user_id_ctx.set(str(user.id))
    
    # Get or create session for tracking
    firebase_uid = decoded_token.get("uid", "unknown")
    session = await get_or_create_session(user, firebase_uid, request, db)
    
    # Store session ID in request state for API endpoints
    request.state.session_id = session.id
    
    return user
