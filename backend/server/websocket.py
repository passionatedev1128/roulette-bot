"""WebSocket endpoint for real-time bot events."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .bot_manager import bot_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/events")
async def events_socket(websocket: WebSocket) -> None:
    """Stream bot events to the client."""

    # Accept the WebSocket connection
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    # Register for events
    queue = bot_manager.event_dispatcher.register()
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "payload": {"status": "connected"}
        })
        
        # Stream events
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        bot_manager.event_dispatcher.unregister(queue)
        logger.info("WebSocket client unregistered")


