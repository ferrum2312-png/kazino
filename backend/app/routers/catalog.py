from fastapi import APIRouter

router = APIRouter(prefix="/catalog", tags=["catalog"])

# Static catalog powering the home screen cards.
GAMES = [
    {
        "slug": "raffles",
        "title": "РОЗЫГРЫШИ",
        "subtitle": "Ежедневные призы",
        "live": False,
        "playable": False,
        "accent": "#3ddc84",
    },
    {
        "slug": "ralph-arena",
        "title": "VAVADA АРЕНА",
        "subtitle": "Сражайся за джекпот",
        "live": True,
        "playable": False,
        "accent": "#8a5cff",
    },
    {
        "slug": "duel",
        "title": "ПВП ДУЭЛЬ",
        "subtitle": "1 на 1",
        "live": True,
        "playable": False,
        "accent": "#ff5ca8",
    },
    {
        "slug": "crash",
        "title": "КРАШ",
        "subtitle": "Успей забрать до взрыва",
        "live": True,
        "playable": True,
        "accent": "#ff7a3d",
    },
    {
        "slug": "mines",
        "title": "МИНЫ",
        "subtitle": "Обходи бомбы",
        "live": False,
        "playable": True,
        "accent": "#2ecc71",
    },
]


@router.get("/games")
async def list_games():
    return {"games": GAMES}


@router.get("/banner")
async def banner():
    return {
        "title": "Выбей 777",
        "subtitle": "и получи NFT подарок",
        "cta": "Играть",
    }
