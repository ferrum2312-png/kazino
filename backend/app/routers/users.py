from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.deps import get_current_user
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.user import BalanceResponse, UserPublic
from app.services.wallet import apply_transaction

router = APIRouter(prefix="/users", tags=["users"])


class DepositRequest(BaseModel):
    amount: float = Field(gt=0, le=100_000)


@router.get("/me", response_model=UserPublic)
async def get_me(current: User = Depends(get_current_user)):
    return current


@router.get("/me/balance", response_model=BalanceResponse)
async def get_balance(current: User = Depends(get_current_user)):
    return BalanceResponse(balance=float(current.balance))


@router.post("/me/deposit", response_model=BalanceResponse)
async def deposit(
    payload: DepositRequest,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Demo top-up (no real payment provider wired in)."""
    balance = await apply_transaction(
        db, current, payload.amount, TransactionType.DEPOSIT, game=None
    )
    await db.commit()
    return BalanceResponse(balance=balance)


@router.get("/me/transactions")
async def transactions(
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current.id)
        .order_by(desc(Transaction.id))
        .limit(min(limit, 200))
    )
    rows = result.scalars().all()
    return [
        {
            "id": t.id,
            "type": t.type.value,
            "amount": float(t.amount),
            "balance_after": float(t.balance_after),
            "game": t.game,
            "created_at": t.created_at,
        }
        for t in rows
    ]
