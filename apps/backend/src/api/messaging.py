from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models.communications import Message, MessageParticipant, MessageThread
from src.models.users import User
from src.schemas.messaging import (
    MessageCreate,
    MessageRead,
    ParticipantRead,
    ThreadCreate,
    ThreadDetail,
    ThreadListResponse,
    ThreadRead,
)
from src.security.auth import get_current_user
from src.services.messaging import messaging_service

router = APIRouter()


async def _validate_thread_participant_access(
    db: AsyncSession,
    patient_id: UUID,
    participant_ids: list[UUID],
    organization_id: UUID,
) -> None:
    """
    HIPAA: Ensure all participants have legitimate access to the patient.
    This prevents unauthorized users from being added to PHI discussions.
    """
    from src.models.assignments import PatientProxyAssignment
    from src.models.care_teams import CareTeamAssignment
    from src.models.organizations import OrganizationMember
    from src.models.profiles import Patient, Provider, Proxy

    # Get patient to check user_id
    patient_stmt = select(Patient).where(Patient.id == patient_id)
    patient_result = await db.execute(patient_stmt)
    patient = patient_result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    for user_id in participant_ids:
        # Check 1: User IS the patient
        if patient.user_id == user_id:
            continue

        # Check 2: User is org Staff/Admin/Provider (can access all patients)
        member_stmt = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
            .where(OrganizationMember.user_id == user_id)
            .where(OrganizationMember.deleted_at.is_(None))
        )
        member_result = await db.execute(member_stmt)
        member = member_result.scalar_one_or_none()

        if member and member.role in ("STAFF", "ADMIN", "PROVIDER"):
            continue

        # Check 3: User is authorized proxy with messaging permission
        proxy_stmt = select(Proxy).where(Proxy.user_id == user_id).where(Proxy.deleted_at.is_(None))
        proxy_result = await db.execute(proxy_stmt)
        proxy = proxy_result.scalar_one_or_none()

        if proxy:
            from datetime import UTC, datetime

            now = datetime.now(UTC)
            assignment_stmt = (
                select(PatientProxyAssignment)
                .where(PatientProxyAssignment.proxy_id == proxy.id)
                .where(PatientProxyAssignment.patient_id == patient_id)
                .where(PatientProxyAssignment.can_message_providers == True)  # noqa: E712
                .where(PatientProxyAssignment.revoked_at.is_(None))
                .where(PatientProxyAssignment.deleted_at.is_(None))
                .where((PatientProxyAssignment.expires_at.is_(None)) | (PatientProxyAssignment.expires_at > now))
            )
            assignment_result = await db.execute(assignment_stmt)
            if assignment_result.scalar_one_or_none():
                continue

        # Check 4: User is on patient's care team
        care_team_stmt = (
            select(CareTeamAssignment)
            .join(Provider, CareTeamAssignment.provider_id == Provider.id)
            .where(Provider.user_id == user_id)
            .where(CareTeamAssignment.patient_id == patient_id)
            .where(CareTeamAssignment.removed_at.is_(None))
        )
        care_team_result = await db.execute(care_team_stmt)
        if care_team_result.scalar_one_or_none():
            continue

        # User failed all authorization checks
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to participate in discussions about this patient",
        )


@router.get("", response_model=ThreadListResponse)
async def list_threads(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List message threads for the current user."""
    threads, total = await messaging_service.get_user_threads(db, current_user.id, page, size)

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
    # HIPAA: If thread is about a patient, validate all participants have access
    if data.patient_id:
        await _validate_thread_participant_access(
            db=db,
            patient_id=data.patient_id,
            participant_ids=data.participant_ids,
            organization_id=data.organization_id,
        )

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
        MessageParticipant.thread_id == thread_id, MessageParticipant.user_id == current_user.id
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
