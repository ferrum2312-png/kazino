from sqlalchemy import Float, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class TonDeposit(Base, TimestampMixin):
    __tablename__ = "ton_deposits"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable on-chain identifier so a deposit is credited exactly once.
    event_id: Mapped[str] = mapped_column(
        String(160), unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ton_amount: Mapped[float] = mapped_column(Float, nullable=False)
    stars: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)  # stars per GRAM at credit time
    sender: Mapped[str | None] = mapped_column(String(80), nullable=True)
