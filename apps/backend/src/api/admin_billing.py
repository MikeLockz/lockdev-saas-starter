"""
Admin Billing API

Endpoints for admin management of subscriptions, refunds, free grants, and billing managers.
Story 22.4 - Epic 22: Complete Billing & Subscription Management
"""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.billing import BillingTransaction
from src.models.organizations import Organization
from src.models.profiles import Patient
from src.models.users import User
from src.schemas.billing import (
    AssignBillingManagerRequest,
    BillingAnalytics,
    BillingManagerListResponse,
    BillingManagerResponse,
    CancelSubscriptionResponse,
    GrantFreeSubscriptionRequest,
    ManualCancelRequest,
    RefundResponse,
    RefundTransactionRequest,
    SubscriptionListItem,
    SubscriptionListResponse,
    SubscriptionOverrideResponse,
    TransactionListResponse,
    TransactionResponse,
)
from src.security.auth import get_current_user
from src.services import billing as billing_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["admin-billing"])


# =============================================================================
# Helper: Require Admin Role
# =============================================================================


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require admin or super admin role for billing management."""
    if not current_user.is_super_admin:
        # Check if user has admin role in any organization
        # For now, only super admins can access admin billing
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required for billing management",
        )
    return current_user


# =============================================================================
# Subscription Management Endpoints
# =============================================================================


@router.get("/subscriptions", response_model=SubscriptionListResponse)
async def list_all_subscriptions(
    status: str | None = Query(None, description="Filter by subscription status"),
    owner_type: str | None = Query(None, pattern="^(PATIENT|ORGANIZATION)$"),
    search: str | None = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> SubscriptionListResponse:
    """
    List all subscriptions across the platform.

    Requires super admin access.
    """
    subscriptions, total = await billing_service.get_all_subscriptions(
        db=db,
        status=status,
        owner_type=owner_type,
        search=search,
        page=page,
        page_size=page_size,
    )

    # Convert to response models
    items = [SubscriptionListItem(**sub) for sub in subscriptions]

    # Calculate total MRR
    total_mrr = sum(sub.mrr_cents for sub in items)

    return SubscriptionListResponse(
        subscriptions=items,
        total=total,
        page=page,
        page_size=page_size,
        total_mrr_cents=total_mrr,
    )


@router.get("/transactions", response_model=TransactionListResponse)
async def list_all_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> TransactionListResponse:
    """
    List all transactions across all customers.

    Requires super admin access.
    """
    offset = (page - 1) * page_size

    query = select(BillingTransaction).order_by(BillingTransaction.created_at.desc())

    if status_filter:
        query = query.where(BillingTransaction.status == status_filter)

    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    transactions = result.scalars().all()

    # Get total count
    count_query = select(func.count()).select_from(BillingTransaction)
    if status_filter:
        count_query = count_query.where(BillingTransaction.status == status_filter)
    total = await db.scalar(count_query) or 0

    return TransactionListResponse(
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
        total=total,
    )


@router.post("/transactions/{transaction_id}/refund", response_model=RefundResponse)
async def refund_transaction(
    transaction_id: UUID,
    request: RefundTransactionRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> RefundResponse:
    """
    Refund a transaction (full or partial).

    Requires super admin access.
    """
    try:
        result = await billing_service.refund_transaction(
            db=db,
            transaction_id=transaction_id,
            amount_cents=request.amount_cents,
            reason=request.reason,
            refunded_by=admin.id,
        )

        logger.info(
            "Admin refunded transaction",
            extra={
                "admin_id": str(admin.id),
                "transaction_id": str(transaction_id),
                "amount": result["amount_refunded"],
            },
        )

        return RefundResponse(
            success=True,
            refund_id=result["refund_id"],
            amount_refunded_cents=result["amount_refunded"],
            message="Refund processed successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Refund failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process refund",
        ) from e


@router.post("/grant-free", response_model=SubscriptionOverrideResponse)
async def grant_free_subscription(
    request: GrantFreeSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> SubscriptionOverrideResponse:
    """
    Grant a free subscription to a user.

    Requires super admin access.
    """
    try:
        override = await billing_service.grant_free_subscription(
            db=db,
            owner_id=request.owner_id,
            owner_type=request.owner_type,
            reason=request.reason,
            granted_by=admin.id,
            duration_months=request.duration_months,
        )

        logger.info(
            "Admin granted free subscription",
            extra={
                "admin_id": str(admin.id),
                "owner_id": str(request.owner_id),
                "owner_type": request.owner_type,
                "duration_months": request.duration_months,
            },
        )

        return SubscriptionOverrideResponse.model_validate(override)
    except Exception as e:
        logger.error(f"Grant free subscription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/subscriptions/{owner_type}/{owner_id}/cancel",
    response_model=CancelSubscriptionResponse,
)
async def admin_cancel_subscription(
    owner_type: str,
    owner_id: UUID,
    request: ManualCancelRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> CancelSubscriptionResponse:
    """
    Admin manually cancels a user's subscription.

    Requires super admin access.
    """
    # Get customer
    if owner_type == "PATIENT":
        owner = await db.get(Patient, owner_id)
    elif owner_type == "ORGANIZATION":
        owner = await db.get(Organization, owner_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid owner_type. Must be PATIENT or ORGANIZATION",
        )

    if not owner or not owner.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found or has no Stripe account",
        )

    try:
        result = await billing_service.cancel_subscription(
            customer_id=owner.stripe_customer_id,
            cancel_immediately=request.cancel_immediately,
        )

        logger.info(
            "Admin cancelled subscription",
            extra={
                "admin_id": str(admin.id),
                "owner_id": str(owner_id),
                "owner_type": owner_type,
                "reason": request.reason,
            },
        )

        cancelled_at = None
        if result.get("cancelled_at"):
            cancelled_at = datetime.fromtimestamp(result["cancelled_at"])

        return CancelSubscriptionResponse(
            success=True,
            cancelled_at=cancelled_at,
            cancels_at_period_end=result.get("cancel_at_period_end", False),
            message="Subscription cancelled by admin",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Cancel subscription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription",
        ) from e


@router.get("/analytics", response_model=BillingAnalytics)
async def get_billing_analytics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> BillingAnalytics:
    """
    Get billing analytics dashboard.

    Requires super admin access.
    """
    analytics = await billing_service.calculate_billing_analytics(db)
    return BillingAnalytics(**analytics)


# =============================================================================
# Billing Manager Management Endpoints
# =============================================================================


@router.get("/managers", response_model=BillingManagerListResponse)
async def list_billing_managers(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> BillingManagerListResponse:
    """
    List all billing manager relationships.

    Requires super admin access.
    """
    query = select(Patient).where(Patient.billing_manager_id.isnot(None))
    result = await db.execute(query)
    patients = result.scalars().all()

    relationships = []
    for patient in patients:
        manager = await db.get(User, patient.billing_manager_id)
        if manager:
            relationships.append(
                BillingManagerResponse(
                    patient_id=patient.id,
                    patient_name=f"{patient.first_name} {patient.last_name}",
                    billing_manager_id=manager.id,
                    billing_manager_name=manager.display_name or manager.email,
                    billing_manager_email=manager.email,
                    assigned_at=patient.billing_manager_assigned_at or patient.created_at,
                    assigned_by=patient.billing_manager_assigned_by,
                )
            )

    return BillingManagerListResponse(relationships=relationships, total=len(relationships))


# Patient billing manager endpoints (under /admin prefix)
patient_billing_router = APIRouter(prefix="/patients", tags=["admin-billing"])


@patient_billing_router.put("/{patient_id}/billing/manager")
async def admin_assign_billing_manager(
    patient_id: UUID,
    request: AssignBillingManagerRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    """
    Admin assigns a billing manager to a patient.

    This bypasses the proxy relationship check - admins can assign any user as billing manager.

    Requires super admin access.
    """
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    # Verify the proxy user exists
    proxy_user = await db.get(User, request.proxy_user_id)
    if not proxy_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proxy user not found",
        )

    patient.billing_manager_id = request.proxy_user_id
    patient.billing_manager_assigned_at = datetime.utcnow()
    patient.billing_manager_assigned_by = admin.id

    await db.commit()

    logger.info(
        "Admin assigned billing manager",
        extra={
            "admin_id": str(admin.id),
            "patient_id": str(patient_id),
            "billing_manager_id": str(request.proxy_user_id),
        },
    )

    return {"success": True, "message": "Billing manager assigned by admin"}


@patient_billing_router.delete("/{patient_id}/billing/manager")
async def admin_remove_billing_manager(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    """
    Admin removes a billing manager from a patient.

    Requires super admin access.
    """
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not patient.billing_manager_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient has no billing manager assigned",
        )

    old_manager_id = patient.billing_manager_id
    patient.billing_manager_id = None
    patient.billing_manager_assigned_at = None
    patient.billing_manager_assigned_by = None

    await db.commit()

    logger.info(
        "Admin removed billing manager",
        extra={
            "admin_id": str(admin.id),
            "patient_id": str(patient_id),
            "old_billing_manager_id": str(old_manager_id),
        },
    )

    return {"success": True, "message": "Billing manager removed by admin"}
