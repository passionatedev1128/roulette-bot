"""Bot control endpoints."""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from ..bot_manager import bot_manager
from ..schemas import BotControlRequest, ModeChangeRequest, StatusResponse

logger = logging.getLogger(__name__)


router = APIRouter(tags=["control"])


def _status_response() -> StatusResponse:
    data = bot_manager.get_status()
    last_activity = data.get("last_activity")
    return StatusResponse(
        running=data["running"],
        status=data["status"],
        mode=data["mode"],
        last_activity=datetime.fromisoformat(last_activity) if last_activity else None,
        spin_number=data.get("spin_number", 0),
    )


@router.post("/api/bot/start", response_model=StatusResponse, responses={400: {"description": "Bot already running"}})
def start_bot(payload: BotControlRequest) -> StatusResponse:
    """Start the bot."""

    try:
        bot_manager.start_bot(mode=payload.mode, test_mode=payload.test_mode)
    except RuntimeError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _status_response()


@router.post("/api/bot/stop", response_model=StatusResponse)
def stop_bot() -> StatusResponse:
    """Stop the bot."""
    logger.info("Stop bot endpoint called")
    try:
        bot_manager.stop_bot()
        logger.info("Bot stop command executed successfully")
        status_resp = _status_response()
        logger.info(f"Bot status after stop: running={status_resp.running}, status={status_resp.status}")
        return status_resp
    except Exception as e:
        logger.error(f"Error stopping bot: {e}", exc_info=True)
        raise


@router.post("/api/bot/mode", response_model=StatusResponse)
def change_mode(payload: ModeChangeRequest) -> StatusResponse:
    """Change operating mode."""

    bot_manager.set_mode(payload.mode)
    return _status_response()


