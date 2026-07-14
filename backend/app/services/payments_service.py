"""Credit off-chain payments (Stars, Crypto Bot) exactly once."""
from sqlalchemy import select
from sqlalchemy.exc import DataError, IntegrityError

from app.db.session import AsyncSessionLocal
from app.models.deposit import Payment
from app.models.transaction import TransactionType
from app.models.user import User
from app.services.wallet import apply_transaction


async def credit_payment(
    provider: str,
    external_id: str,
    user_id: int,
    stars: int,
    amount: float,
    asset: str | None,
) -> bool:
    """Idempotently credit `stars` to a user for a payment. Returns True if a
    new credit was applied, False if it was a duplicate / invalid."""
    if stars <= 0:
        return False
    async with AsyncSessionLocal() as db:
        exists = await db.execute(
            select(Payment.id).where(
                Payment.provider == provider, Payment.external_id == str(external_id)
            )
        )
        if exists.scalar_one_or_none():
            return False  # already credited

        user = await db.get(User, user_id)
        if user is None:
            return False

        await apply_transaction(
            db, user, stars, TransactionType.DEPOSIT, game=provider,
            ref=f"{provider}:{external_id}"[:64],
        )
        db.add(
            Payment(
                provider=provider,
                external_id=str(external_id),
                user_id=user_id,
                stars=stars,
                amount=amount,
                asset=asset,
            )
        )
        try:
            await db.commit()
            print(f"[pay:{provider}] user {user_id} +{stars} ★ ({amount} {asset or ''})")
            return True
        except (IntegrityError, DataError):
            await db.rollback()
            return False
