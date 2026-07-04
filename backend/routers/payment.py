import stripe
import os
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services.supabase_service import SupabaseDB

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

payment_router = APIRouter(
    prefix="/payment",
    tags=["payment"]
)

class CheckoutRequest(BaseModel):
    user_id: str

@payment_router.post('/create-checkout-session')
async def checkout(request: CheckoutRequest):
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": os.getenv("STRIPE_PRICE_ID"), "quantity": 1}],
            client_reference_id=request.user_id,
            success_url=f"{os.getenv('FRONTEND_URL')}/?payment=success",
            cancel_url=f"{os.getenv('FRONTEND_URL')}/?payment=cancelled",
        )
        return {"url": session.url}
    except Exception as e:
        raise e

@payment_router.post('/webhook')
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except stripe.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        clerk_user_id = getattr(session, "client_reference_id", None)
        stripe_customer_id = getattr(session, "customer", None)

        if clerk_user_id:
            try:
                db = SupabaseDB()
                db.upsert_user(clerk_user_id, stripe_customer_id)
                print(f"Upserted user: {clerk_user_id} with plan: pro")
            except Exception as e:
                print(f"Supabase error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}
