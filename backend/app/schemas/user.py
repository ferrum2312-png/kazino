from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int | None
    username: str | None
    first_name: str | None
    email: str | None
    avatar_url: str | None
    balance: float
    is_admin: bool
    created_at: datetime


class BalanceResponse(BaseModel):
    balance: float
