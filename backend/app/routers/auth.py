from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.deps import (
    get_current_user,
    get_user_by_telegram_id,
    get_user_by_username,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest, TelegramAuthRequest, TokenResponse
from app.schemas.user import UserPublic
from app.services.telegram import TelegramAuthError, verify_init_data

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=TokenResponse)
async def telegram_login(
    payload: TelegramAuthRequest, db: AsyncSession = Depends(get_db)
):
    """Authenticate a Telegram Mini App user from signed initData.

    Verifies the signature, then finds-or-creates the user by their Telegram id
    and returns a JWT. No password involved.
    """
    try:
        tg_user = verify_init_data(payload.init_data)
    except TelegramAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        )

    tg_id = int(tg_user["id"])
    avatar = (
        tg_user.get("photo_url")
        or f"https://api.dicebear.com/7.x/thumbs/svg?seed=tg{tg_id}"
    )
    user = await get_user_by_telegram_id(db, tg_id)

    if user is None:
        # Use the TG @username only if it's free; otherwise leave it null.
        uname = tg_user.get("username")
        if uname and await get_user_by_username(db, uname):
            uname = None
        user = User(
            telegram_id=tg_id,
            username=uname,
            first_name=tg_user.get("first_name"),
            avatar_url=avatar,
        )
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
        except IntegrityError:
            # Concurrent first login (e.g. StrictMode fires the request twice,
            # or a username collision) hit a unique constraint. Roll back and
            # reuse the row the other request created.
            await db.rollback()
            user = await get_user_by_telegram_id(db, tg_id)
            if user is None:
                # The clash was on username, not telegram_id — insert without it.
                user = User(
                    telegram_id=tg_id,
                    first_name=tg_user.get("first_name"),
                    avatar_url=avatar,
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
    else:
        # Keep profile fields fresh on each launch.
        if tg_user.get("first_name"):
            user.first_name = tg_user["first_name"]
        if tg_user.get("photo_url"):
            user.avatar_url = tg_user["photo_url"]
        await db.commit()

    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        avatar_url=f"https://api.dicebear.com/7.x/thumbs/svg?seed={payload.username}",
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already taken",
        )
    await db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_username(db, form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserPublic)
async def me(current: User = Depends(get_current_user)):
    return current
