from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.deps import get_current_user
from app.models.deposit import TonDeposit
from app.models.user import User
from app.services import ton_rates

router = APIRouter(prefix="/payments", tags=["payments"])


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
