"""Provably-fair randomness.

Each round has a server seed (secret until reveal), a client seed and a nonce.
The HMAC-SHA256 of "clientSeed:nonce" keyed by the server seed is a deterministic
hash the player can verify after the fact.
"""
import hashlib
import hmac
import math
import secrets

from app.core.config import settings


def new_server_seed() -> str:
    return secrets.token_hex(32)


def server_seed_hash(server_seed: str) -> str:
    """Public commitment shown to the player before the round."""
    return hashlib.sha256(server_seed.encode()).hexdigest()


def _hmac_hex(server_seed: str, client_seed: str, nonce: int) -> str:
    msg = f"{client_seed}:{nonce}".encode()
    return hmac.new(server_seed.encode(), msg, hashlib.sha256).hexdigest()


def hmac_float(server_seed: str, client_seed: str, nonce: int) -> float:
    """Uniform float in [0, 1) derived from the first 52 bits of the hash."""
    digest = _hmac_hex(server_seed, client_seed, nonce)
    # Use 13 hex chars = 52 bits for a clean double.
    return int(digest[:13], 16) / float(1 << 52)


def crash_point(server_seed: str, client_seed: str, nonce: int) -> float:
    """Return the multiplier at which a crash round busts.

    Uses the well-known Bustabit-style distribution: a house-edge slice of
    rounds bust instantly at 1.00x, and the rest follow a heavy-tailed inverse
    distribution. Minimum non-instant result is 1.00x.
    """
    r = int(_hmac_hex(server_seed, client_seed, nonce)[:13], 16)  # 52-bit int
    e = 1 << 52

    # House edge: a slice of rounds crash at exactly 1.00x.
    if r % round(1 / settings.crash_house_edge) == 0:
        return 1.00

    # (100 * e - r) / (e - r), floored to 2 decimals.
    point = (100 * e - r) / (e - r)
    return math.floor(point) / 100


def mine_positions(
    server_seed: str, client_seed: str, nonce: int, size: int, mines: int
) -> list[int]:
    """Deterministically pick `mines` unique tile indices in [0, size)."""
    positions: list[int] = []
    counter = 0
    while len(positions) < mines:
        digest = _hmac_hex(server_seed, client_seed, nonce * 10_000 + counter)
        idx = int(digest[:13], 16) % size
        if idx not in positions:
            positions.append(idx)
        counter += 1
    return positions
