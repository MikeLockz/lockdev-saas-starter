from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database import get_db
from src.security.org_access import get_current_org_member 
from src.security.auth import get_current_user # If needed for enrichment, but org member has user_id
from src.models import OrganizationMember, User
from src.models.operations import Call
from src.schemas.operations import CallCreate, CallRead, CallUpdate

router = APIRouter()

@router.get("/", response_model=List[CallRead])
async def list_calls(
    org_id: UUID, 
    current_member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    agent_id: Optional[UUID] = Query(None, description="Filter by agent"),
    date_from: Optional[datetime] = Query(None, description="Filter by start date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by start date to"),
    skip: int = 0,
    limit: int = 50,
):
    query = select(Call).where(Call.organization_id == org_id)
    
    if status:
        query = query.where(Call.status == status)
    if agent_id:
        query = query.where(Call.agent_id == agent_id)
    if date_from:
        query = query.where(Call.started_at >= date_from)
    if date_to:
        query = query.where(Call.started_at <= date_to)
        
    # Join for names (optional enhancement, here we just load)
    # query = query.options(joinedload(Call.agent), joinedload(Call.patient))
    
    query = query.order_by(desc(Call.started_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    calls = result.scalars().all()
    
    # Enrichment could happen here if we query users/patients explicitly or via join
    return calls

@router.post("/", response_model=CallRead)
async def create_call(
    org_id: UUID,
    call_in: CallCreate,
    current_member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    Log a new call. Automatically sets status to IN_PROGRESS and started_at to now.
    """
    call = Call(
        organization_id=org_id,
        agent_id=current_member.user_id,
        direction=call_in.direction,
        status="IN_PROGRESS",
        phone_number=call_in.phone_number,
        patient_id=call_in.patient_id,
        notes=call_in.notes,
        outcome=call_in.outcome,
        started_at=datetime.now(timezone.utc)
    )
    db.add(call)
    await db.commit()
    await db.refresh(call)
    return call

@router.patch("/{call_id}", response_model=CallRead)
async def update_call(
    org_id: UUID,
    call_id: UUID,
    call_in: CallUpdate,
    current_member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    query = select(Call).where(Call.id == call_id, Call.organization_id == org_id)
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
        
    update_data = call_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(call, field, value)
        
    # Auto-set ended_at if completed and not provided
    if call.status == "COMPLETED" and not call.ended_at:
        call.ended_at = datetime.now(timezone.utc)
        if call.started_at:
             delta = call.ended_at - call.started_at
             call.duration_seconds = int(delta.total_seconds())

    db.add(call)
    await db.commit()
    await db.refresh(call)
    return call
