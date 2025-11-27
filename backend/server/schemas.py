"""Pydantic schemas used by the web interface backend API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ConfigResponse(BaseModel):
    """Represents the full bot configuration payload."""

    config: Dict[str, Any] = Field(..., description="Complete configuration dictionary")


class ConfigUpdateRequest(BaseModel):
    """Payload for updating configuration."""

    config: Dict[str, Any]
    persist: bool = Field(default=True, description="If true, write config to disk")


class PresetCreateRequest(BaseModel):
    """Request body for saving configuration presets."""

    name: str = Field(..., description="Human readable preset name", min_length=1)
    config: Dict[str, Any]

    @validator("name")
    def _strip_name(cls, value: str) -> str:  # noqa: D401,N805
        """Trim whitespace and ensure non-empty."""

        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Preset name cannot be empty")
        return cleaned


class PresetSummary(BaseModel):
    """Metadata for stored presets."""

    name: str
    slug: str
    created_at: datetime


class StatusResponse(BaseModel):
    """Represents bot status information."""

    running: bool
    status: str
    mode: str
    last_activity: Optional[datetime]
    spin_number: int
    process_time_seconds: Optional[int] = None


class BalanceResponse(BaseModel):
    """Balance and performance metrics."""

    current_balance: float
    initial_balance: float
    profit_loss: float
    today_profit_loss: float
    total_bets: int
    wins: int
    losses: int


class ResultItem(BaseModel):
    """Represents a roulette result entry."""

    spin_number: int
    number: Optional[int]
    color: Optional[str]
    zero: bool = False
    timestamp: Optional[datetime]


class ResultsResponse(BaseModel):
    """Collection of recent results."""

    results: List[ResultItem]


class ActiveBet(BaseModel):
    """Current active bet details."""

    bet_type: str
    bet_amount: float
    placed_at: datetime
    gale_step: Optional[int]


class BetHistoryItem(BaseModel):
    """Historical bet entry."""

    spin_number: int
    bet_type: Optional[str]
    bet_amount: float
    result: str
    profit_loss: float
    balance_after: float
    timestamp: datetime


class BetHistoryResponse(BaseModel):
    """Collection of historical bets."""

    bets: List[BetHistoryItem]


class BotControlRequest(BaseModel):
    """Start bot request payload."""

    mode: Optional[str] = Field(default=None, description="Desired bot mode")
    test_mode: bool = Field(default=False, description="Run bot in simulation/test mode")


class ModeChangeRequest(BaseModel):
    """Update bot mode request body."""

    mode: str


class DailyStats(BaseModel):
    """Stats aggregated per day."""

    date: str
    spins: int
    bets: int
    wins: int
    losses: int
    profit_loss: float


class StrategyStats(BaseModel):
    """Stats aggregated per strategy."""

    strategy: str
    bets: int
    wins: int
    losses: int
    win_rate: float
    profit_loss: float


class GaleStats(BaseModel):
    """Stats aggregated by gale step."""

    gale_step: int
    occurrences: int
    wins: int
    losses: int
    profit_loss: float


class DailyStatsResponse(BaseModel):
    """Response for daily statistics."""

    stats: List[DailyStats]


class StrategyStatsResponse(BaseModel):
    """Response for strategy statistics."""

    stats: List[StrategyStats]


class GaleStatsResponse(BaseModel):
    """Response for gale statistics."""

    stats: List[GaleStats]


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str


