import contextlib
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
    SubscriptionStatusResponse,
    TransactionListResponse,
    TransactionResponse,
)
from src.security.auth import get_current_user
from src.services import billing as billing_service
from src.services import billing_access

router = APIRouter()


@router.get("/managed-patients/billing", response_model=list[dict])
async def list_managed_patient_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """
    List all patients managed by the current proxy user and their subscription status.
    """
    # Find all patients where this user is the assigned billing manager
    query = select(Patient).where(Patient.billing_manager_id == current_user.id)
    result = await db.execute(query)
    patients = result.scalars().all()

    managed_patients = []
    for patient in patients:
        # Verify active proxy relationship
        is_active = await billing_access.validate_proxy_relationship_active(db, patient.id, current_user.id)
        if not is_active:
            continue

        # Get subscription status
        status_info = {"status": "NONE"}
        if patient.stripe_customer_id:
            with contextlib.suppress(Exception):
                status_info = await billing_service.get_subscription_status(patient.stripe_customer_id)

        managed_patients.append(
            {
                "patient_id": patient.id,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "subscription": status_info,
            }
        )

    return managed_patients


@router.get("/managed-patients/{patient_id}/billing/subscription", response_model=SubscriptionStatusResponse)
async def get_managed_patient_subscription(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubscriptionStatusResponse:
    """
    Get subscription status for a specific managed patient.
    """
    # Verify access
    if not await billing_access.can_manage_billing(db, patient_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage billing for this patient",
        )

    patient = await db.get(Patient, patient_id)
    if not patient or not patient.stripe_customer_id:
        return SubscriptionStatusResponse(status="NONE")

    status_data = await billing_service.get_subscription_status(patient.stripe_customer_id)
    return SubscriptionStatusResponse(**status_data)


@router.post("/managed-patients/{patient_id}/billing/checkout", response_model=CheckoutSessionResponse)
async def create_managed_patient_checkout(
    patient_id: UUID,
    request: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CheckoutSessionResponse:
    """
    Create a checkout session for a managed patient.
    """
    # Verify access
    if not await billing_access.can_manage_billing(db, patient_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage billing for this patient",
        )

    # Get or create Stripe customer for the PATIENT
    customer_id = await billing_service.get_or_create_patient_customer(db, patient_id)

    # Create checkout session
    try:
        session = await billing_service.create_checkout_session(
            customer_id=customer_id,
            price_id=request.price_id,
            success_url=f"{settings.FRONTEND_URL}/proxy/managed-patients-billing/success",
            cancel_url=f"{settings.FRONTEND_URL}/proxy/managed-patients-billing",
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/managed-patients/{patient_id}/billing/cancel", response_model=SubscriptionStatusResponse)
async def cancel_managed_patient_subscription(
    patient_id: UUID,
    request: CancelSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Cancel a managed patient's subscription.
    """
    # Verify access
    if not await billing_access.can_manage_billing(db, patient_id, current_user.id):
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


@router.get("/managed-patients/{patient_id}/billing/transactions", response_model=TransactionListResponse)
async def get_managed_patient_transactions(
    patient_id: UUID,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionListResponse:
    """
    Get billing history for a managed patient.
    """
    # Verify access
    if not await billing_access.can_manage_billing(db, patient_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage billing for this patient",
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
