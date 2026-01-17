import stripe

from app.core.config import settings

stripe.api_key = settings.STRIPE_API_KEY


class BillingService:
    def __init__(self):
        self.enabled = settings.STRIPE_API_KEY is not None

    async def create_checkout_session(self, customer_id: str, price_id: str):
        if not self.enabled:
            return {"url": "http://mock-stripe-url"}

        return stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
        )


billing_service = BillingService()
