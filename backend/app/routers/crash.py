import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.crash_engine import engine

router = APIRouter(prefix="/games/crash", tags=["crash"])


@router.get("/history")
async def history():
    return {"history": await engine.history()}


@router.websocket("/ws")
async def crash_ws(ws: WebSocket):
    """Realtime crash socket.

    Client -> server messages:
      {"action": "auth", "token": "<jwt>"}
      {"action": "bet", "amount": 10, "auto_cashout": 2.0}
      {"action": "cashout"}
    """
    await engine.connect(ws)
    user_id: int | None = None
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"type": "error", "message": "bad json"}))
                continue

            action = msg.get("action")
            if action == "auth":
                user_id = await engine.authenticate(ws, msg.get("token", ""))
                await ws.send_text(
                    json.dumps(
                        {"type": "auth", "ok": user_id is not None}
                    )
                )
            elif action == "bet":
                if user_id is None:
                    await ws.send_text(
                        json.dumps({"type": "error", "message": "not authenticated"})
                    )
                    continue
                result = await engine.place_bet(
                    user_id,
                    float(msg.get("amount", 0)),
                    msg.get("auto_cashout"),
                )
                await ws.send_text(json.dumps(result))
            elif action == "cashout":
                if user_id is None:
                    await ws.send_text(
                        json.dumps({"type": "error", "message": "not authenticated"})
                    )
                    continue
                result = await engine.cash_out(user_id)
                await ws.send_text(json.dumps(result))
            elif action == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        engine.disconnect(ws)
    except Exception:
        engine.disconnect(ws)
