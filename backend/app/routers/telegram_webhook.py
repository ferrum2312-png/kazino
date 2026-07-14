import hmac

from fastapi import APIRouter, Header, Request

from app.services import telegram_bot
from app.services.payments_service import credit_payment

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    # Validate the secret (constant-time) so only Telegram can post here.
    if not hmac.compare_digest(
        x_telegram_bot_api_secret_token or "", telegram_bot.webhook_secret()
    ):
        return {"ok": False}

    update = await request.json()

    # 1) Pre-checkout: must be answered within 10s or the payment fails.
    pcq = update.get("pre_checkout_query")
    if pcq:
        await telegram_bot.answer_pre_checkout(pcq["id"], ok=True)
        return {"ok": True}

    # 2) Successful Stars payment -> credit the user.
    message = update.get("message") or {}
    sp = message.get("successful_payment")
    if sp and sp.get("currency") == "XTR":
        payload = sp.get("invoice_payload", "")  # "stars:<userId>:<stars>"
        parts = payload.split(":")
        if len(parts) == 3 and parts[0] == "stars":
            try:
                user_id = int(parts[1])
            except ValueError:
                return {"ok": True}
            stars = int(sp.get("total_amount") or 0)  # XTR amount == stars
            charge_id = sp.get("telegram_payment_charge_id") or payload
            await credit_payment(
                provider="stars",
                external_id=charge_id,
                user_id=user_id,
                stars=stars,
                amount=stars,
                asset="XTR",
            )
    return {"ok": True}
