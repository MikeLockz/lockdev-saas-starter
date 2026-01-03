"""
Billing API Tests

Tests for organization billing endpoints with mocked Stripe calls.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models.organizations import Organization, OrganizationMember


@pytest.fixture
async def test_org_with_stripe(db_session):
    """Create a test organization with Stripe customer ID."""
    org = Organization(
        name="Billing Test Org",
        stripe_customer_id="cus_test123",
        subscription_status="ACTIVE",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    yield org
    await db_session.delete(org)
    await db_session.commit()


@pytest.fixture
async def test_org_without_stripe(db_session):
    """Create a test organization without Stripe customer ID."""
    org = Organization(
        name="New Billing Test Org",
        stripe_customer_id=None,
        subscription_status=None,
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    yield org
    await db_session.delete(org)
    await db_session.commit()


@pytest.fixture
async def admin_member(db_session, test_user, test_org_with_stripe):
    """Create an admin member for the test org."""
    member = OrganizationMember(
        organization_id=test_org_with_stripe.id,
        user_id=test_user.id,
        role="ADMIN",
    )
    db_session.add(member)
    await db_session.commit()
    yield member
    await db_session.delete(member)
    await db_session.commit()


@pytest.mark.asyncio
async def test_create_checkout_session(db_session, test_org_with_stripe, admin_member, auth_headers):
    """Test creating a checkout session returns Stripe URL."""
    mock_session = AsyncMock()
    mock_session.session_id = "cs_test_session"
    mock_session.checkout_url = "https://checkout.stripe.com/test"

    with patch(
        "src.api.billing.create_checkout_session",
        return_value=mock_session,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            response = await client.post(
                f"/api/v1/organizations/{test_org_with_stripe.id}/billing/checkout",
                json={"price_id": "price_test123"},
                headers=auth_headers,
            )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "cs_test_session"
    assert data["checkout_url"] == "https://checkout.stripe.com/test"


@pytest.mark.asyncio
async def test_create_checkout_creates_customer(
    db_session, test_org_without_stripe, test_user, auth_headers
):
    """Test that checkout creates Stripe customer if none exists."""
    # Create admin membership
    member = OrganizationMember(
        organization_id=test_org_without_stripe.id,
        user_id=test_user.id,
        role="ADMIN",
    )
    db_session.add(member)
    await db_session.commit()

    mock_session = AsyncMock()
    mock_session.session_id = "cs_test_new"
    mock_session.checkout_url = "https://checkout.stripe.com/new"

    with patch(
        "src.api.billing.create_customer",
        return_value="cus_new123",
    ) as mock_create_customer, patch(
        "src.api.billing.create_checkout_session",
        return_value=mock_session,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            response = await client.post(
                f"/api/v1/organizations/{test_org_without_stripe.id}/billing/checkout",
                json={"price_id": "price_test123"},
                headers=auth_headers,
            )

    assert response.status_code == 200
    mock_create_customer.assert_called_once()

    # Cleanup
    await db_session.delete(member)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_subscription_status(db_session, test_org_with_stripe, admin_member, auth_headers):
    """Test getting subscription status."""
    mock_subscriptions = [
        {
            "id": "sub_test123",
            "status": "active",
            "plan_id": "price_test",
            "current_period_end": 1735689600,
            "cancel_at_period_end": False,
        }
    ]

    with patch(
        "src.api.billing.get_customer_subscriptions",
        return_value=mock_subscriptions,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            response = await client.get(
                f"/api/v1/organizations/{test_org_with_stripe.id}/billing/subscription",
                headers=auth_headers,
            )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACTIVE"
    assert data["plan_id"] == "price_test"


@pytest.mark.asyncio
async def test_get_subscription_no_customer(
    db_session, test_org_without_stripe, test_user, auth_headers
):
    """Test subscription status for org without Stripe customer."""
    # Create admin membership
    member = OrganizationMember(
        organization_id=test_org_without_stripe.id,
        user_id=test_user.id,
        role="ADMIN",
    )
    db_session.add(member)
    await db_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        response = await client.get(
            f"/api/v1/organizations/{test_org_without_stripe.id}/billing/subscription",
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NONE"
    assert data["plan_id"] is None

    # Cleanup
    await db_session.delete(member)
    await db_session.commit()


@pytest.mark.asyncio
async def test_create_portal_session(db_session, test_org_with_stripe, admin_member, auth_headers):
    """Test creating a billing portal session."""
    mock_portal = AsyncMock()
    mock_portal.portal_url = "https://billing.stripe.com/portal/test"

    with patch(
        "src.api.billing.create_portal_session",
        return_value=mock_portal,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            response = await client.post(
                f"/api/v1/organizations/{test_org_with_stripe.id}/billing/portal",
                headers=auth_headers,
            )

    assert response.status_code == 200
    data = response.json()
    assert data["portal_url"] == "https://billing.stripe.com/portal/test"


@pytest.mark.asyncio
async def test_portal_requires_stripe_customer(
    db_session, test_org_without_stripe, test_user, auth_headers
):
    """Test that portal requires existing Stripe customer."""
    # Create admin membership
    member = OrganizationMember(
        organization_id=test_org_without_stripe.id,
        user_id=test_user.id,
        role="ADMIN",
    )
    db_session.add(member)
    await db_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        response = await client.post(
            f"/api/v1/organizations/{test_org_without_stripe.id}/billing/portal",
            headers=auth_headers,
        )

    assert response.status_code == 400
    assert "no active subscription" in response.json()["detail"].lower()

    # Cleanup
    await db_session.delete(member)
    await db_session.commit()


@pytest.mark.asyncio
async def test_billing_requires_admin_role(db_session, test_org_with_stripe, test_user, auth_headers):
    """Test that billing endpoints require ADMIN role."""
    # Create member with MEMBER role (not ADMIN)
    member = OrganizationMember(
        organization_id=test_org_with_stripe.id,
        user_id=test_user.id,
        role="MEMBER",
    )
    db_session.add(member)
    await db_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        response = await client.get(
            f"/api/v1/organizations/{test_org_with_stripe.id}/billing/subscription",
            headers=auth_headers,
        )

    assert response.status_code == 403

    # Cleanup
    await db_session.delete(member)
    await db_session.commit()
