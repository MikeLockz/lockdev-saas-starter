import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models.organizations import Organization
import uuid

# Mock Stripe Event
class MockStripeEvent:
    def __init__(self, type, data):
        self.type = type
        self.data = MagicMock()
        self.data.object = data

@pytest.mark.asyncio
async def test_stripe_webhook_checkout_completed(db_session):
    """
    Test that a 'checkout.session.completed' webhook event updates the 
    Organization's subscription_status to 'ACTIVE'.
    """
    # 1. Seed Data
    stripe_customer_id = f"cus_{uuid.uuid4()}"
    org = Organization(
        name="Test Org Billing",
        stripe_customer_id=stripe_customer_id,
        subscription_status="INCOMPLETE"
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    
    org_id = org.id

    # 2. Mock Stripe Webhook
    mock_event = MockStripeEvent(
        type="checkout.session.completed",
        data={"customer": stripe_customer_id, "subscription": "sub_123"}
    )

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        # Use AsyncClient to ensure we stay in the same event loop
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
            # 3. Send Webhook
            response = await client.post(
                "/api/v1/webhooks/stripe",
                json={"id": "evt_test", "object": "event"},
                headers={"Stripe-Signature": "t=123,v1=fake_sig"}
            )
            
    # 4. Verify Response
    assert response.status_code == 200
    assert response.json() == {"received": True, "event_type": "checkout.session.completed"}

    # 5. Verify DB Update
    # Need to expire/refresh to see changes from other session
    db_session.expire(org) 
    await db_session.refresh(org)
    assert org.subscription_status == "ACTIVE"

    # 6. Cleanup
    await db_session.delete(org)
    await db_session.commit()

@pytest.mark.asyncio
async def test_stripe_webhook_payment_failed(db_session):
    """
    Test that 'invoice.payment_failed' updates status to 'PAST_DUE'.
    """
    stripe_customer_id = f"cus_{uuid.uuid4()}"
    org = Organization(
        name="Test Org Failed Payment",
        stripe_customer_id=stripe_customer_id,
        subscription_status="ACTIVE"
    )
    db_session.add(org)
    await db_session.commit()
    
    mock_event = MockStripeEvent(
        type="invoice.payment_failed",
        data={"customer": stripe_customer_id, "attempt_count": 1}
    )

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
            response = await client.post(
                "/api/v1/webhooks/stripe",
                json={},
                headers={"Stripe-Signature": "fake"}
            )

    assert response.status_code == 200
    db_session.expire(org)
    await db_session.refresh(org)
    assert org.subscription_status == "PAST_DUE"

    # Cleanup
    await db_session.delete(org)
    await db_session.commit()

@pytest.mark.asyncio
async def test_stripe_webhook_invalid_signature():
    """
    Test that invalid signatures return 400 Bad Request.
    """
    with patch("stripe.Webhook.construct_event", side_effect=ValueError("Invalid signature")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
            response = await client.post(
                "/api/v1/webhooks/stripe",
                json={},
                headers={"Stripe-Signature": "bad_sig"}
            )
            
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid webhook signature"