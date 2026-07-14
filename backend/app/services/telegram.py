"""Verify Telegram Mini App `initData`.

Telegram signs the launch parameters with a key derived from the bot token.
We recompute that signature and compare it in constant time; only then do we
trust the embedded user object.

Reference: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
import hashlib
import hmac
import json
import re
import time
from urllib.parse import parse_qsl

from app.core.config import settings

_HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class TelegramAuthError(Exception):
    """Raised when initData is missing, malformed, forged, or expired."""


def verify_init_data(init_data: str) -> dict:
    """Validate `initData` and return the decoded Telegram `user` dict.

    Raises TelegramAuthError on any problem.
    """
    if not settings.bot_token:
        raise TelegramAuthError("Telegram login is not configured (no BOT_TOKEN)")
    if not init_data:
        raise TelegramAuthError("Empty init data")

    # parse_qsl URL-decodes values, which is what the signature is computed over.
    # keep_blank_values=True so empty-valued signed fields aren't dropped (they
    # are part of what Telegram signed, so omitting them would fail valid logins).
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("Missing hash")
    # Reject a malformed hash up front: compare_digest raises TypeError on
    # non-ASCII input, which would otherwise surface as a 500.
    if not _HASH_RE.match(received_hash):
        raise TelegramAuthError("Malformed hash")

    secret_key = hmac.new(
        b"WebAppData", settings.bot_token.encode(), hashlib.sha256
    ).digest()

    def _hash_matches(fields: dict) -> bool:
        dcs = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
        calc = hmac.new(secret_key, dcs.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(calc, received_hash)

    # Per the Telegram spec the check string is every received field except
    # `hash`. Newer clients also send a separate `signature` (Ed25519) field;
    # try the spec-literal form (signature kept) first, then drop it as a
    # fallback so we validate correctly regardless of client version.
    ok = _hash_matches(parsed)
    if not ok and "signature" in parsed:
        ok = _hash_matches({k: v for k, v in parsed.items() if k != "signature"})
    if not ok:
        raise TelegramAuthError("Signature mismatch")

    # Replay protection: fail closed if auth_date is absent or unparseable.
    if settings.telegram_auth_max_age > 0:
        try:
            auth_date = int(parsed["auth_date"])
        except (KeyError, ValueError):
            raise TelegramAuthError("Missing or invalid auth_date")
        if (time.time() - auth_date) > settings.telegram_auth_max_age:
            raise TelegramAuthError("Init data expired")

    user_raw = parsed.get("user")
    if not user_raw:
        raise TelegramAuthError("Missing user")
    try:
        user = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise TelegramAuthError("Malformed user object") from exc

    if not user.get("id"):
        raise TelegramAuthError("User has no id")
    return user
