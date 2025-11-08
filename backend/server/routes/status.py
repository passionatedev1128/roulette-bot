"""Status endpoints."""

from datetime import datetime

from fastapi import APIRouter

from ..bot_manager import bot_manager
from ..schemas import BalanceResponse, StatusResponse


router = APIRouter(tags=["status"])


@router.get("/api/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    """Return bot runtime status."""

    data = bot_manager.get_status()
    last_activity = data.get("last_activity")
    return StatusResponse(
        running=data["running"],
        status=data["status"],
        mode=data["mode"],
        last_activity=datetime.fromisoformat(last_activity) if last_activity else None,
        spin_number=data.get("spin_number", 0),
    )


@router.get("/api/balance", response_model=BalanceResponse)
def get_balance() -> BalanceResponse:
    """Return balance and performance metrics."""

    data = bot_manager.get_balance()
    return BalanceResponse(**data)


