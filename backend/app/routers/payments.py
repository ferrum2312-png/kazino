from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.deps import get_current_user
from app.models.deposit import TonDeposit
from app.models.user import User
from app.services import crypto_pay, telegram_bot, ton_rates

router = APIRouter(prefix="/payments", tags=["payments"])


class StarsInvoiceRequest(BaseModel):
    amount: int = Field(ge=1, le=1_000_000)  # number of Stars


class CryptoInvoiceRequest(BaseModel):
    amount: float = Field(gt=0, le=1_000_000)
    asset: str = "TON"  # TON | USDT


@router.get("/rate")
async def rate():
    """Live GRAM/USD (KuCoin+Bybit avg) and stars-per-GRAM."""
    try:
        return await ton_rates.rate_info()
    except Exception:
        raise HTTPException(status_code=503, detail="Rate unavailable")


@router.get("/deposit-info")
async def deposit_info(current: User = Depends(get_current_user)):
    """Address + the comment the client must attach so the deposit is credited."""
    info = {
        "address": settings.ton_deposit_address,
        "comment": f"dep:{current.id}",
    }
    try:
        info.update(await ton_rates.rate_info())
    except Exception:
        pass
    return info


@router.post("/stars-invoice")
async def stars_invoice(
    payload: StarsInvoiceRequest, current: User = Depends(get_current_user)
):
    """Create a Telegram Stars (XTR) invoice link; the client opens it via
    Telegram.WebApp.openInvoice. Crediting happens on the successful_payment
    webhook."""
    if not settings.bot_token:
        raise HTTPException(status_code=503, detail="Stars payments not configured")
    try:
        link = await telegram_bot.create_stars_invoice_link(
            stars=payload.amount,
            payload=f"stars:{current.id}:{payload.amount}",
            title="Пополнение",
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Invoice failed: {exc}")
    return {"link": link}


@router.post("/cryptobot-invoice")
async def cryptobot_invoice(
    payload: CryptoInvoiceRequest, current: User = Depends(get_current_user)
):
    """Create a Crypto Pay invoice; the client opens the returned pay URL.
    Crediting happens on the Crypto Pay webhook / polling watcher."""
    if not settings.crypto_pay_token:
        raise HTTPException(status_code=503, detail="Crypto Bot not configured")
    asset = payload.asset.upper()
    if asset not in ("TON", "USDT"):
        raise HTTPException(status_code=400, detail="Unsupported asset")
    try:
        inv = await crypto_pay.create_invoice(
            asset=asset,
            amount=payload.amount,
            payload=f"cb:{current.id}",
            description="Пополнение баланса",
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Invoice failed: {exc}")
    return {
        "pay_url": inv.get("mini_app_invoice_url")
        or inv.get("bot_invoice_url")
        or inv.get("pay_url"),
        "invoice_id": inv.get("invoice_id"),
    }


@router.get("/my-deposits")
async def my_deposits(
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(
        select(TonDeposit)
        .where(TonDeposit.user_id == current.id)
        .order_by(desc(TonDeposit.id))
        .limit(20)
    )
    return [
        {
            "ton_amount": d.ton_amount,
            "stars": float(d.stars),
            "rate": d.rate,
            "created_at": d.created_at,
        }
        for d in rows.scalars().all()
    ]
