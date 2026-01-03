from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.security.org_access import get_current_org_member
from src.security.auth import get_current_user
from src.models import OrganizationMember, User
from src.models.operations import Task
from src.schemas.operations import TaskCreate, TaskRead, TaskUpdate

router = APIRouter()
user_tasks_router = APIRouter()

@router.get("/", response_model=List[TaskRead])
async def list_org_tasks(
    org_id: UUID, 
    current_member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    assignee_id: Optional[UUID] = Query(None, description="Filter by assignee"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    skip: int = 0,
    limit: int = 50,
):
    query = select(Task).where(Task.organization_id == org_id)
    
    if status:
        query = query.where(Task.status == status)
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)
    if priority:
        query = query.where(Task.priority == priority)
        
    query = query.order_by(desc(Task.due_date), desc(Task.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks

@router.post("/", response_model=TaskRead)
async def create_task(
    org_id: UUID,
    task_in: TaskCreate,
    current_member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    task = Task(
        organization_id=org_id,
        created_by_id=current_member.user_id,
        patient_id=task_in.patient_id,
        assignee_id=task_in.assignee_id,
        title=task_in.title,
        description=task_in.description,
        status="TODO",
        priority=task_in.priority,
        due_date=task_in.due_date
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    org_id: UUID,
    task_id: UUID,
    task_in: TaskUpdate,
    current_member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).where(Task.id == task_id, Task.organization_id == org_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = task_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
        
    if task.status == "DONE" and not task.completed_at and task_in.status == "DONE":
         task.completed_at = datetime.now()
         
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    org_id: UUID,
    task_id: UUID,
    current_member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    # Only allow creator or admin to delete? For now, any member can.
    query = select(Task).where(Task.id == task_id, Task.organization_id == org_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    await db.delete(task)
    await db.commit()
    return

# --- My Tasks (Cross-Org or Current User Context) ---
# Note: Since the plan put this here, I'll add an endpoint that requires user authent (not necessarily org scoping in URL, but logical scoping)
# However, usually we want strict org scoping. A "/users/me/tasks" endpoint implies searching across orgs OR just tasks assigned to me anywhere.
# If we stick to org-scoped tasks, the frontend might just query list_calls with assignee_id=me.
# But for a top-level "My Tasks" view spanning orgs, we use this:

@user_tasks_router.get("/me/all", response_model=List[TaskRead], description="Get all tasks assigned to current user across all organizations")
async def list_my_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
):
    query = select(Task).where(Task.assignee_id == current_user.id)
    
    if status:
        query = query.where(Task.status == status)
        
    query = query.order_by(desc(Task.due_date)).offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks
