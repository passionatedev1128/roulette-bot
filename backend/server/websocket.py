"""WebSocket endpoint for real-time bot events."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .bot_manager import bot_manager


router = APIRouter()


@router.websocket("/ws/events")
async def events_socket(websocket: WebSocket) -> None:
    """Stream bot events to the client."""

    await websocket.accept()
    queue = bot_manager.event_dispatcher.register()
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        bot_manager.event_dispatcher.unregister(queue)


