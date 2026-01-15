from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.billing import BillingTransaction
from src.models.profiles import Patient
from src.models.users import User
from src.schemas.billing import (
    CancelSubscriptionRequest,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PortalSessionResponse,
    SubscriptionStatusResponse,
    TransactionListResponse,
    TransactionResponse,
)
from src.security.auth import get_current_user
from src.services import billing as billing_service

router = APIRouter()


@router.post("/{patient_id}/billing/checkout", response_model=CheckoutSessionResponse)
async def create_patient_checkout(
    patient_id: UUID,
    request: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CheckoutSessionResponse:
    """
    Create a Stripe checkout session for a patient subscription.
    User must be the patient or an authorized proxy/staff.
    """
    from src.services.billing_access import can_manage_billing

    if not await can_manage_billing(db, patient_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage billing for this patient",
        )

    # Get or create Stripe customer
    customer_id = await billing_service.get_or_create_patient_customer(db, patient_id)

    # Create checkout session
    try:
        session = await billing_service.create_checkout_session(
            customer_id=customer_id,
            price_id=request.price_id,
            success_url=f"{settings.FRONTEND_URL}/patient/billing/success",
            cancel_url=f"{settings.FRONTEND_URL}/patient/billing",
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{patient_id}/billing/subscription", response_model=SubscriptionStatusResponse)
async def get_patient_subscription(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubscriptionStatusResponse:
    """
    Get patient's current subscription status.
    """
    from src.services.billing_access import can_manage_billing

    if not await can_manage_billing(db, patient_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view billing for this patient",
        )

    patient = await db.get(Patient, patient_id)
    if not patient or not patient.stripe_customer_id:
        return SubscriptionStatusResponse(status="NONE")

    status_data = await billing_service.get_subscription_status(patient.stripe_customer_id)
    return SubscriptionStatusResponse(**status_data)


@router.post("/{patient_id}/billing/portal", response_model=PortalSessionResponse)
async def create_patient_portal(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortalSessionResponse:
    """
    Create a Stripe billing portal session for the patient.
    """
    from src.services.billing_access import can_manage_billing

    if not await can_manage_billing(db, patient_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage billing for this patient",
        )

    patient = await db.get(Patient, patient_id)
    if not patient or not patient.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found for this patient")

    try:
        session = await billing_service.create_portal_session(
            customer_id=patient.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/patient/billing",
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{patient_id}/billing/transactions", response_model=TransactionListResponse)
async def get_patient_transactions(
    patient_id: UUID,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionListResponse:
    """
    Get patient's billing transaction history.
    """
    from src.services.billing_access import can_manage_billing

    if not await can_manage_billing(db, patient_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view billing for this patient",
        )

    # Query transactions
    offset = (page - 1) * page_size
    query = (
        select(BillingTransaction)
        .where(
            BillingTransaction.owner_id == patient_id,
            BillingTransaction.owner_type == "PATIENT",
        )
        .order_by(BillingTransaction.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    transactions = result.scalars().all()

    # Get total count
    count_query = (
        select(func.count())
        .select_from(BillingTransaction)
        .where(
            BillingTransaction.owner_id == patient_id,
            BillingTransaction.owner_type == "PATIENT",
        )
    )
    result_count = await db.execute(count_query)
    total = result_count.scalar() or 0

    return TransactionListResponse(
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
        total=total,
    )


@router.post("/{patient_id}/billing/cancel", response_model=SubscriptionStatusResponse)
async def cancel_patient_subscription(
    patient_id: UUID,
    request: CancelSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Cancel patient's subscription.
    """
    from src.services.billing_access import can_manage_billing

    if not await can_manage_billing(db, patient_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage billing for this patient",
        )

    patient = await db.get(Patient, patient_id)
    if not patient or not patient.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active billing account")

    try:
        result = await billing_service.cancel_subscription(
            customer_id=patient.stripe_customer_id,
            cancel_immediately=request.cancel_immediately,
        )

        return {
            "status": result["status"],
            "cancel_at_period_end": result["cancel_at_period_end"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")
