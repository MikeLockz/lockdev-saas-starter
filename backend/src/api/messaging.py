from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.security.auth import get_current_user
from src.models.users import User
from src.models.communications import MessageThread, Message, MessageParticipant
from src.schemas.messaging import (
    ThreadListResponse,
    ThreadRead,
    ThreadDetail,
    ThreadCreate,
    MessageRead,
    MessageCreate,
    ParticipantRead,
)
from src.services.messaging import messaging_service

router = APIRouter()


@router.get("", response_model=ThreadListResponse)
async def list_threads(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List message threads for the current user."""
    threads, total = await messaging_service.get_user_threads(
        db, current_user.id, page, size
    )

    items = []
    for thread in threads:
        # Calculate unread count and last message
        # Last message is the last one in the messages list (ordered by created_at)
        last_message_Read = None
        if thread.messages:
            last_msg = thread.messages[-1]
            last_message_Read = MessageRead.model_validate(last_msg)
            # Find sender name
            if last_msg.sender:
                last_message_Read.sender_name = last_msg.sender.display_name

        # Unread count: messages created after last_read_at
        unread = 0
        participant = next((p for p in thread.participants if p.user_id == current_user.id), None)
        if participant and participant.last_read_at:
            unread = sum(1 for m in thread.messages if m.created_at > participant.last_read_at)
        elif participant:
            # If never read, all messages are unread? Or maybe just new ones?
            # Assuming all for simplicity if joined_at is before messages
            unread = len(thread.messages)

        # Map participants
        participants_read = []
        for p in thread.participants:
            pread = ParticipantRead.model_validate(p)
            if p.user:
                pread.user_name = p.user.display_name
            participants_read.append(pread)

        thread_read = ThreadRead.model_validate(thread)
        thread_read.last_message = last_message_Read
        thread_read.unread_count = unread
        thread_read.participants = participants_read
        items.append(thread_read)

    return ThreadListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.post("", response_model=ThreadRead, status_code=status.HTTP_201_CREATED)
async def create_thread(
    data: ThreadCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new message thread."""
    thread = await messaging_service.create_thread(
        db,
        organization_id=data.organization_id,
        creator_id=current_user.id,
        subject=data.subject,
        initial_message=data.initial_message,
        participant_ids=data.participant_ids,
        patient_id=data.patient_id,
    )
    
    # Reload for response
    stmt = (
        select(MessageThread)
        .where(MessageThread.id == thread.id)
        .options(
            selectinload(MessageThread.participants).selectinload(MessageParticipant.user),
            selectinload(MessageThread.messages).selectinload(Message.sender),
        )
    )
    result = await db.execute(stmt)
    thread = result.scalar_one()

    # Map response (similar logic to list, extract to helper later if needed)
    last_message_Read = None
    if thread.messages:
        last_msg = thread.messages[-1]
        last_message_Read = MessageRead.model_validate(last_msg)
        if last_msg.sender:
            last_message_Read.sender_name = last_msg.sender.display_name

    participants_read = []
    for p in thread.participants:
        pread = ParticipantRead.model_validate(p)
        if p.user:
            pread.user_name = p.user.display_name
        participants_read.append(pread)

    thread_read = ThreadRead.model_validate(thread)
    thread_read.last_message = last_message_Read
    thread_read.unread_count = 0  # Creator reads it immediately
    thread_read.participants = participants_read

    return thread_read


@router.get("/{thread_id}", response_model=ThreadDetail)
async def get_thread(
    thread_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get thread details."""
    query = (
        select(MessageThread)
        .where(MessageThread.id == thread_id)
        .options(
            selectinload(MessageThread.participants).selectinload(MessageParticipant.user),
            selectinload(MessageThread.messages).selectinload(Message.sender),
        )
    )
    result = await db.execute(query)
    thread = result.scalar_one_or_none()
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Verify user is participant
    participant = next((p for p in thread.participants if p.user_id == current_user.id), None)
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")

    # Mark as read
    await messaging_service.mark_thread_read(db, thread_id, current_user.id)

    # Calculate unread count (should be 0 now)
    unread = 0

    last_message_Read = None
    if thread.messages:
        last_msg = thread.messages[-1]
        last_message_Read = MessageRead.model_validate(last_msg)
        if last_msg.sender:
            last_message_Read.sender_name = last_msg.sender.display_name

    participants_read = []
    for p in thread.participants:
        pread = ParticipantRead.model_validate(p)
        if p.user:
            pread.user_name = p.user.display_name
        participants_read.append(pread)
        
    messages_read = []
    for m in thread.messages:
        m_read = MessageRead.model_validate(m)
        if m.sender:
            m_read.sender_name = m.sender.display_name
        messages_read.append(m_read)

    thread_detail = ThreadDetail.model_validate(thread)
    thread_detail.last_message = last_message_Read
    thread_detail.unread_count = unread
    thread_detail.participants = participants_read
    thread_detail.messages = messages_read

    return thread_detail


@router.post("/{thread_id}/messages", response_model=MessageRead)
async def send_message(
    thread_id: UUID,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to a thread."""
    # Verify participation
    stmt = select(MessageParticipant).where(
        MessageParticipant.thread_id == thread_id,
        MessageParticipant.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a participant")

    message = await messaging_service.create_message(
        db,
        thread_id=thread_id,
        sender_id=current_user.id,
        body=data.body,
    )
    
    # Reload for relationships
    stmt = select(Message).where(Message.id == message.id).options(selectinload(Message.sender))
    result = await db.execute(stmt)
    message = result.scalar_one()
    
    msg_read = MessageRead.model_validate(message)
    if message.sender:
        msg_read.sender_name = message.sender.display_name
        
    return msg_read


@router.post("/{thread_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(
    thread_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark thread as read."""
    await messaging_service.mark_thread_read(db, thread_id, current_user.id)
