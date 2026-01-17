from unittest.mock import patch

import pytest

from app.services.billing import BillingService


@pytest.mark.asyncio
async def test_billing_service_mock():
    with patch("app.services.billing.settings") as mock_settings:
        mock_settings.STRIPE_API_KEY = None
        service = BillingService()
        res = await service.create_checkout_session("cust_123", "price_123")
        assert res["url"] == "http://mock-stripe-url"


@pytest.mark.asyncio
async def test_billing_service_stripe():
    with patch("app.services.billing.settings") as mock_settings:
        mock_settings.STRIPE_API_KEY = "sk_test_123"
        service = BillingService()
        with patch("stripe.checkout.Session.create") as mock_create:
            mock_create.return_value = {
                "id": "sess_123",
                "url": "https://stripe.com/sess",
            }
            res = await service.create_checkout_session("cust_123", "price_123")
            assert res["url"] == "https://stripe.com/sess"
