from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionType
from app.models.user import User


async def apply_transaction(
    db: AsyncSession,
    user: User,
    amount: float,
    tx_type: TransactionType,
    game: str | None = None,
    ref: str | None = None,
) -> float:
    """Mutate a user's balance and record a ledger entry.

    `amount` is positive for credits (win/deposit/bonus) and negative for
    debits (bet/withdraw). Raises 400 on insufficient funds. The caller is
    responsible for committing the surrounding transaction.

    The user row is locked FOR UPDATE so concurrent credits/bets can't clobber
    each other's balance write (read-modify-write race).
    """
    result = await db.execute(
        select(User).where(User.id == user.id).with_for_update()
    )
    locked = result.scalar_one()

    current = Decimal(str(locked.balance))
    delta = Decimal(str(amount))
    new_balance = current + delta

    if new_balance < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance",
        )

    locked.balance = new_balance
    if user is not locked:
        user.balance = new_balance
    db.add(
        Transaction(
            user_id=locked.id,
            type=tx_type,
            amount=delta,
            balance_after=new_balance,
            game=game,
            ref=ref,
        )
    )
    return float(new_balance)
