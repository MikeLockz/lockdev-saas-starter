from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.communications import Notification


class NotificationService:
    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: UUID,
        type: str,
        title: str,
        body: str | None = None,
        data: dict | None = None,
    ) -> Notification:
        """Create a new notification for a user."""
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            data_json=data,
            is_read=False,
        )
        db.add(notification)
        # We don't commit here to allow transaction grouping
        return notification

    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: UUID) -> int:
        """Get count of unread notifications for a user."""
        query = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
        result = await db.execute(query)
        return result.scalar() or 0


notification_service = NotificationService()
