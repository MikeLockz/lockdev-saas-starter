from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.communications import Notification
from src.models.users import User
from src.schemas.notifications import (
    NotificationListResponse,
    NotificationRead,
    UnreadCountResponse,
)
from src.security.auth import get_current_user
from src.services.notifications import notification_service

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_read: bool | None = None,
    type: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the current user."""
    query = select(Notification).where(Notification.user_id == current_user.id)

    if is_read is not None:
        query = query.where(Notification.is_read == is_read)

    if type:
        query = query.where(Notification.type == type)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get page items
    # Sort by created_at desc (newest first)
    query = query.order_by(Notification.created_at.desc())
    query = query.limit(size).offset((page - 1) * size)

    result = await db.execute(query)
    items = result.scalars().all()

    # Get unread count
    unread_count = await notification_service.get_unread_count(db, current_user.id)

    return NotificationListResponse(
        items=items,
        total=total,
        unread_count=unread_count,
        page=page,
        size=size,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the number of unread notifications."""
    count = await notification_service.get_unread_count(db, current_user.id)
    return UnreadCountResponse(count=count)


@router.patch("/{notification_id}/read", response_model=NotificationRead)
async def mark_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id).where(Notification.user_id == current_user.id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(notification)

    return notification


@router.patch("/{notification_id}/unread", response_model=NotificationRead)
async def mark_as_unread(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as unread."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id).where(Notification.user_id == current_user.id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.is_read:
        notification.is_read = False
        notification.read_at = None
        await db.commit()
        await db.refresh(notification)

    return notification


@router.post("/mark-all-read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read for the current user."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)  # noqa: E712
        .values(is_read=True, read_at=datetime.now(UTC))
    )
    await db.commit()


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a notification."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id).where(Notification.user_id == current_user.id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.delete(notification)
    await db.commit()
