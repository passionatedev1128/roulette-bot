"""Statistics endpoints."""

from fastapi import APIRouter

from ..bot_manager import bot_manager
from ..schemas import DailyStatsResponse, GaleStatsResponse, StrategyStatsResponse


router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/daily", response_model=DailyStatsResponse)
def get_daily_stats() -> DailyStatsResponse:
    """Return daily aggregate statistics."""

    stats = bot_manager.get_daily_stats()
    return DailyStatsResponse(stats=stats)


@router.get("/strategy", response_model=StrategyStatsResponse)
def get_strategy_stats() -> StrategyStatsResponse:
    """Return strategy-level stats."""

    stats = bot_manager.get_strategy_stats()
    return StrategyStatsResponse(stats=stats)


@router.get("/gale", response_model=GaleStatsResponse)
def get_gale_stats() -> GaleStatsResponse:
    """Return gale progression stats."""

    stats = bot_manager.get_gale_stats()
    return GaleStatsResponse(stats=stats)


