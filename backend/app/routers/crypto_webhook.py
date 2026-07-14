import json

from fastapi import APIRouter, Header, Request

from app.services import crypto_pay
from app.services.payments_service import credit_payment

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.post("/webhook")
async def webhook(
    request: Request,
    crypto_pay_api_signature: str | None = Header(default=None),
):
    body = await request.body()
    if not crypto_pay.verify_webhook(body, crypto_pay_api_signature or ""):
        return {"ok": False}

    try:
        update = json.loads(body)
    except json.JSONDecodeError:
        return {"ok": False}

    if update.get("update_type") != "invoice_paid":
        return {"ok": True}

    inv = update.get("payload") or {}
    our_payload = inv.get("payload") or ""  # "cb:<userId>"
    parts = our_payload.split(":")
    if len(parts) == 2 and parts[0] == "cb":
        try:
            user_id = int(parts[1])
        except ValueError:
            return {"ok": True}
        asset = inv.get("asset") or ""
        amount = float(inv.get("amount") or 0)
        stars = await crypto_pay.asset_to_stars(asset, amount)
        await credit_payment(
            provider="cryptobot",
            external_id=str(inv.get("invoice_id")),
            user_id=user_id,
            stars=stars,
            amount=amount,
            asset=asset,
        )
    return {"ok": True}
