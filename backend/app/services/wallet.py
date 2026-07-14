from decimal import Decimal

from fastapi import HTTPException, status
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
    """
    current = Decimal(str(user.balance))
    delta = Decimal(str(amount))
    new_balance = current + delta

    if new_balance < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance",
        )

    user.balance = new_balance
    db.add(
        Transaction(
            user_id=user.id,
            type=tx_type,
            amount=delta,
            balance_after=new_balance,
            game=game,
            ref=ref,
        )
    )
    return float(new_balance)
