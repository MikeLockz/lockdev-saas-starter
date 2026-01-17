import stripe
from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import settings

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        return {"status": "ignored"}

    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        event["data"]["object"]
        # Handle completed checkout

    return {"status": "success"}
