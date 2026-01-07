"""
Billing API

Organization billing endpoints for Stripe checkout, portal, and subscription management.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.organizations import Organization, OrganizationMember
from src.schemas.billing import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PortalSessionResponse,
    SubscriptionStatusResponse,
)
from src.security.org_access import require_org_admin
from src.services.billing import (
    CustomerType,
    create_checkout_session,
    create_customer,
    create_portal_session,
    get_customer_subscriptions,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout(
    org_id: UUID,
    request: CheckoutSessionRequest,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
) -> CheckoutSessionResponse:
    """
    Create a Stripe Checkout Session for subscription.

    Creates a Stripe customer for the organization if one doesn't exist,
    then creates a checkout session for the specified price.

    **Requires**: Organization ADMIN role.

    Returns:
        Checkout session with redirect URL for Stripe payment page.
    """
    # Get organization
    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Create or get Stripe customer
    stripe_customer_id = org.stripe_customer_id
    if not stripe_customer_id:
        # Need to create a customer - get admin user email for customer
        from src.models import User

        user_stmt = select(User).where(User.id == member.user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one()

        stripe_customer_id = await create_customer(
            owner_id=str(org.id),
            owner_type=CustomerType.ORGANIZATION,
            email=user.email,
            name=org.name,
        )

        # Update organization with customer ID
        await db.execute(
            update(Organization).where(Organization.id == org.id).values(stripe_customer_id=stripe_customer_id)
        )
        await db.commit()

        logger.info(
            "Created Stripe customer for organization",
            extra={
                "organization_id": str(org.id),
                "customer_id": stripe_customer_id,
            },
        )

    # Create checkout session
    session = await create_checkout_session(
        customer_id=stripe_customer_id,
        price_id=request.price_id,
        success_url=f"{settings.STRIPE_SUCCESS_URL}?org_id={org_id}",
        cancel_url=f"{settings.STRIPE_CANCEL_URL}?org_id={org_id}",
    )

    return CheckoutSessionResponse(
        session_id=session.session_id,
        checkout_url=session.checkout_url,
    )


@router.get("/subscription", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    org_id: UUID,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionStatusResponse:
    """
    Get current subscription status for the organization.

    **Requires**: Organization ADMIN role.

    Returns:
        Current subscription status including plan and billing period.
    """
    # Get organization
    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # If no Stripe customer, return no subscription
    if not org.stripe_customer_id:
        return SubscriptionStatusResponse(
            status="NONE",
            plan_id=None,
            current_period_end=None,
            cancel_at_period_end=False,
        )

    # Get subscription details from Stripe
    try:
        subscriptions = await get_customer_subscriptions(org.stripe_customer_id)
        if subscriptions:
            # Get the first active subscription
            active_sub = next(
                (s for s in subscriptions if s["status"] in ("active", "trialing")),
                subscriptions[0] if subscriptions else None,
            )
            if active_sub:
                return SubscriptionStatusResponse(
                    status=org.subscription_status or active_sub["status"].upper(),
                    plan_id=active_sub.get("plan_id"),
                    current_period_end=active_sub.get("current_period_end"),
                    cancel_at_period_end=active_sub.get("cancel_at_period_end", False),
                )
    except Exception as e:
        logger.warning(f"Failed to get Stripe subscriptions: {e}")

    # Fall back to database status
    return SubscriptionStatusResponse(
        status=org.subscription_status or "NONE",
        plan_id=None,
        current_period_end=None,
        cancel_at_period_end=False,
    )


@router.post("/portal", response_model=PortalSessionResponse)
async def create_billing_portal(
    org_id: UUID,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
) -> PortalSessionResponse:
    """
    Create a Stripe Customer Portal session.

    The portal allows customers to manage their subscription,
    update payment methods, and view invoices.

    **Requires**: Organization ADMIN role.

    Returns:
        Portal session with redirect URL.
    """
    # Get organization
    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if not org.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization has no active subscription",
        )

    # Create portal session
    session = await create_portal_session(
        customer_id=org.stripe_customer_id,
        return_url=f"{settings.FRONTEND_URL}/admin/billing",
    )

    return PortalSessionResponse(portal_url=session.portal_url)
