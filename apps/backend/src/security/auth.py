"""
Authentication and session tracking module.

Handles:
- Firebase token verification
- Session creation/tracking
- RLS context setup
"""

import logging

# Initialize Firebase
import os
from datetime import UTC, datetime

import firebase_admin
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db, user_id_ctx
from src.models import User
from src.models.sessions import UserSession

_firebase_logger = logging.getLogger(__name__)

try:
    firebase_admin.get_app()
except ValueError:
    _firebase_initialized = False

    # Try explicit credentials file first (for local development)
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and os.path.exists(creds_path):
        try:
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            _firebase_logger.info(f"Firebase initialized with credentials from: {creds_path}")
        except Exception as e:
            _firebase_logger.warning(f"Failed to initialize Firebase with certificate: {e}")

    # Fall back to Application Default Credentials (for cloud deployment)
    if not _firebase_initialized:
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            _firebase_logger.info("Firebase initialized with Application Default Credentials")
        except Exception as e:
            _firebase_logger.warning(
                f"Firebase not initialized: {e}. Mock authentication will be used in local environment."
            )

security = HTTPBearer()


async def verify_token(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Firebase JWT token."""
    import logging

    logger = logging.getLogger(__name__)

    # SECURITY: Explicitly reject mock tokens in non-local environments
    # This is defense-in-depth - even if someone misconfigures ENVIRONMENT,
    # we log the attempt and reject it explicitly.
    if token.credentials.startswith("mock_"):
        if settings.ENVIRONMENT != "local":
            # Log security event - someone attempted mock auth in non-local env
            logger.warning(
                f"SECURITY: Mock token rejected in {settings.ENVIRONMENT} environment. "
                f"Client IP: {request.client.host if request.client else 'unknown'}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mock authentication is not allowed in this environment",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Local environment - allow mock auth for development/testing
        email = token.credentials.split("_", 1)[1]
        logger.info(f"Mock auth used for: {email}")
        return {"uid": "mock_uid", "email": email}

    # Real Firebase token verification
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
    session = result.scalars().first()  # Use .first() to handle multiple sessions gracefully

    now = datetime.now(UTC)

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
    request: Request, decoded_token: dict = Depends(verify_token), db: AsyncSession = Depends(get_db)
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

    # Ensure DB session has the correct context set (since transaction started before ctx was set)
    await db.execute(text("SELECT set_config('app.current_user_id', :uid, false)"), {"uid": str(user.id)})

    # Get or create session for tracking
    firebase_uid = decoded_token.get("uid", "unknown")
    session = await get_or_create_session(user, firebase_uid, request, db)

    # Store session ID in request state for API endpoints
    request.state.session_id = session.id

    return user
