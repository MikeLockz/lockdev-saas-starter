from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.communications import MessageThread, Message, MessageParticipant
from src.models.users import User


class MessagingService:
    @staticmethod
    async def create_thread(
        db: AsyncSession,
        organization_id: UUID,
        creator_id: UUID,
        subject: str,
        initial_message: str,
        participant_ids: list[UUID],
        patient_id: UUID | None = None,
    ) -> MessageThread:
        """Create a new message thread."""
        # Create thread
        thread = MessageThread(
            organization_id=organization_id,
            subject=subject,
            patient_id=patient_id,
        )
        db.add(thread)
        await db.flush()  # Get thread ID

        # Add creator as participant
        creator_participant = MessageParticipant(
            thread_id=thread.id,
            user_id=creator_id,
            last_read_at=datetime.now(timezone.utc),
        )
        db.add(creator_participant)

        # Add other participants
        # Ensure creator is not added twice
        unique_participants = set(participant_ids) - {creator_id}
        for uid in unique_participants:
            participant = MessageParticipant(
                thread_id=thread.id,
                user_id=uid,
            )
            db.add(participant)

        # Add initial message
        message = Message(
            thread_id=thread.id,
            sender_id=creator_id,
            body=initial_message,
        )
        db.add(message)
        
        await db.commit()
        await db.refresh(thread)
        return thread

    @staticmethod
    async def create_message(
        db: AsyncSession,
        thread_id: UUID,
        sender_id: UUID,
        body: str,
    ) -> Message:
        """Add a message to a thread."""
        message = Message(
            thread_id=thread_id,
            sender_id=sender_id,
            body=body,
        )
        db.add(message)
        
        # Update thread updated_at
        stmt = select(MessageThread).where(MessageThread.id == thread_id)
        result = await db.execute(stmt)
        thread = result.scalar_one()
        thread.updated_at = datetime.now(timezone.utc)
        
        # Update sender's last_read_at
        # Check if sender is participant (should be)
        part_stmt = select(MessageParticipant).where(
            MessageParticipant.thread_id == thread_id,
            MessageParticipant.user_id == sender_id
        )
        part_result = await db.execute(part_stmt)
        participant = part_result.scalar_one_or_none()
        if participant:
            participant.last_read_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_user_threads(
        db: AsyncSession,
        user_id: UUID,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[MessageThread], int]:
        """Get threads for a user."""
        # Find threads where user is a participant
        query = (
            select(MessageThread)
            .join(MessageParticipant)
            .where(MessageParticipant.user_id == user_id)
            .options(
                selectinload(MessageThread.participants).selectinload(MessageParticipant.user),
                selectinload(MessageThread.messages).selectinload(Message.sender),
            )
            .order_by(MessageThread.updated_at.desc())
        )

        # Count
        count_query = (
            select(func.count())
            .select_from(MessageThread)
            .join(MessageParticipant)
            .where(MessageParticipant.user_id == user_id)
        )
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Pagination
        query = query.limit(size).offset((page - 1) * size)
        
        result = await db.execute(query)
        threads = result.scalars().all()
        
        return list(threads), total

    @staticmethod
    async def mark_thread_read(
        db: AsyncSession,
        thread_id: UUID,
        user_id: UUID,
    ) -> None:
        """Mark thread as read for user."""
        stmt = select(MessageParticipant).where(
            MessageParticipant.thread_id == thread_id,
            MessageParticipant.user_id == user_id
        )
        result = await db.execute(stmt)
        participant = result.scalar_one_or_none()
        
        if participant:
            participant.last_read_at = datetime.now(timezone.utc)
            await db.commit()


messaging_service = MessagingService()
