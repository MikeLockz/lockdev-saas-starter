from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.security.auth import get_current_user
from src.models import User, SupportTicket, SupportMessage
from src.schemas.support import (
    TicketCreate,
    TicketRead,
    TicketUpdate,
    SupportMessageCreate,
    SupportMessageRead,
)

router = APIRouter()

@router.get("/tickets", response_model=List[TicketRead])
async def get_my_tickets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List user's support tickets.
    """
    stmt = (
        select(SupportTicket)
        .where(SupportTicket.user_id == current_user.id)
        .order_by(desc(SupportTicket.updated_at))
        .options(selectinload(SupportTicket.messages))
    )
    result = await db.execute(stmt)
    tickets = result.scalars().all()
    
    # Process tickets to count messages and filter internal messages if needed (though user messages are usually not internal)
    # The schema handles message_count if we compute it, or we can just let it rely on loaded messages len
    # For list view we might typically want just counts, but for now we'll return full objects per schema
    return tickets

@router.post("/tickets", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_in: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new support ticket with an initial message.
    """
    # Create Ticket
    new_ticket = SupportTicket(
        user_id=current_user.id,
        subject=ticket_in.subject,
        category=ticket_in.category,
        priority=ticket_in.priority,
        status="OPEN",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        # organization_id could be inferred if specific context is provided, maybe later
    )
    db.add(new_ticket)
    await db.flush() # get ID

    # Create Initial Message
    initial_message = SupportMessage(
        ticket_id=new_ticket.id,
        sender_id=current_user.id,
        body=ticket_in.initial_message,
        is_internal=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(initial_message)
    
    await db.commit()
    await db.refresh(new_ticket)
    # Explicitly load messages to ensure it's populated for the response
    await db.refresh(new_ticket, attribute_names=['messages'])
    
    return new_ticket

@router.get("/tickets/{ticket_id}", response_model=TicketRead)
async def get_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific ticket with messages.
    """
    stmt = (
        select(SupportTicket)
        .where(SupportTicket.id == ticket_id)
        .options(selectinload(SupportTicket.messages))
    )
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Access Control: User can only see their own tickets, Staff (Super Admin) can see all
    if ticket.user_id != current_user.id and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")

    # Filter internal messages for non-admin users
    if not current_user.is_super_admin:
        # We need to filter the messages list in the response. 
        # Since 'ticket.messages' is an instrumented list, we might cheat by returning a Pydantic model constructed manually
        # or relying on the schema. 
        # But SupportTicket SQLAlchemy object is attached to session.
        # Let's filter in python for the response
        visible_messages = [m for m in ticket.messages if not m.is_internal]
        # We can't easily modify ticket.messages without side effects if we are not careful, 
        # but for serialization purposes we might need to construct a response object if we strip data.
        # Actually, Pydantic's from_attributes=True will read attributes.
        # We can override the messages attribute on valid object before return? No, that's risky.
        # Better to return a constructed TicketRead
        
        return TicketRead(
            id=ticket.id,
            user_id=ticket.user_id,
            organization_id=ticket.organization_id,
            subject=ticket.subject,
            category=ticket.category,
            priority=ticket.priority,
            status=ticket.status,
            assigned_to_id=ticket.assigned_to_id,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            resolved_at=ticket.resolved_at,
            message_count=len(visible_messages),
            messages=visible_messages
        )

    return ticket

@router.post("/tickets/{ticket_id}/messages", response_model=SupportMessageRead)
async def add_message(
    ticket_id: UUID,
    message_in: SupportMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a message to a ticket.
    """
    stmt = select(SupportTicket).where(SupportTicket.id == ticket_id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.user_id != current_user.id and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not authorized to reply to this ticket")

    # Only admin can send internal messages
    is_internal = message_in.is_internal
    if is_internal and not current_user.is_super_admin:
         raise HTTPException(status_code=403, detail="Only admins can send internal nodes")

    new_message = SupportMessage(
        ticket_id=ticket.id,
        sender_id=current_user.id,
        body=message_in.body,
        is_internal=is_internal,
        created_at=datetime.now(timezone.utc),
    )
    db.add(new_message)
    
    # Auto-reopen if user replies
    if ticket.status == 'RESOLVED' and ticket.user_id == current_user.id:
        ticket.status = 'IN_PROGRESS'
        ticket.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(new_message)
    return new_message

# =============================================================================
# Admin / Staff Endpoints
# =============================================================================

@router.get("/admin/tickets", response_model=List[TicketRead])
async def get_all_tickets(
    status: Optional[str] = None,
    assigned_to_me: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Admin: List all tickets with optional filtering.
    """
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    stmt = select(SupportTicket).options(selectinload(SupportTicket.messages))
    
    if status:
        stmt = stmt.where(SupportTicket.status == status)
    
    if assigned_to_me:
        stmt = stmt.where(SupportTicket.assigned_to_id == current_user.id)
        
    stmt = stmt.order_by(desc(SupportTicket.updated_at))
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.patch("/admin/tickets/{ticket_id}", response_model=TicketRead)
async def update_ticket_status(
    ticket_id: UUID,
    update_in: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Admin: Update ticket status, priority, or assignment.
    """
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    stmt = (
        select(SupportTicket)
        .where(SupportTicket.id == ticket_id)
        .options(selectinload(SupportTicket.messages))
    )
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    update_data = update_in.model_dump(exclude_unset=True)
    if not update_data:
        return ticket
    
    current_status = ticket.status
        
    for field, value in update_data.items():
        setattr(ticket, field, value)
        
    # If resolving, set resolved_at
    if update_in.status == 'RESOLVED' and current_status != 'RESOLVED':
        ticket.resolved_at = datetime.now(timezone.utc)
    elif update_in.status and update_in.status != 'RESOLVED' and update_in.status != 'CLOSED':
        # Re-opened
        ticket.resolved_at = None

    ticket.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(ticket)
    return ticket

@router.patch("/admin/tickets/{ticket_id}/assign", response_model=TicketRead)
async def assign_ticket(
    ticket_id: UUID,
    assignee_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Admin: Assign ticket to a user (staff).
    """
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    stmt = (
        select(SupportTicket)
        .where(SupportTicket.id == ticket_id)
        .options(selectinload(SupportTicket.messages))
    )
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Verify assignee exists
    assignee_stmt = select(User).where(User.id == assignee_id)
    assignee_res = await db.execute(assignee_stmt)
    if not assignee_res.scalar_one_or_none():
         raise HTTPException(status_code=404, detail="Assignee user not found")

    ticket.assigned_to_id = assignee_id
    ticket.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(ticket)
    return ticket
