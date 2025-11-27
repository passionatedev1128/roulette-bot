"""Routes for results and betting data."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter

from ..bot_manager import bot_manager
from ..schemas import (
    ActiveBet,
    BetHistoryItem,
    BetHistoryResponse,
    ResultItem,
    ResultsResponse,
)


router = APIRouter(tags=["results"])


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@router.get("/api/results/latest", response_model=ResultsResponse)
def get_latest_results(limit: int = 20) -> ResultsResponse:
    """Return latest roulette results."""

    records = bot_manager.get_recent_results(limit)
    items: List[ResultItem] = []
    for record in records:
        items.append(
            ResultItem(
                spin_number=int(record.get("spin_number", 0)),
                number=record.get("outcome_number"),
                color=record.get("outcome_color"),
                zero=bool(record.get("outcome_number") == 0 or record.get("outcome_color") == "green"),
                timestamp=_parse_timestamp(record.get("timestamp")),
            )
        )
    return ResultsResponse(results=items)


@router.get("/api/bets/active", response_model=Optional[ActiveBet])
def get_active_bet() -> Optional[ActiveBet]:
    """Return active bet information, if any."""

    active = bot_manager.get_active_bet()
    if not active:
        return None

    return ActiveBet(
        bet_type=active.get("bet_type", ""),
        bet_amount=float(active.get("bet_amount", 0.0)),
        gale_step=active.get("gale_step"),
        placed_at=_parse_timestamp(active.get("timestamp")) or datetime.now(),
    )


@router.get("/api/bets/history", response_model=BetHistoryResponse)
def get_bet_history(limit: int = 50) -> BetHistoryResponse:
    """Return bet history entries."""

    history = bot_manager.get_bet_history(limit)
    items: List[BetHistoryItem] = []
    for item in history:
        items.append(
            BetHistoryItem(
                spin_number=int(item.get("spin_number", 0)),
                bet_type=item.get("bet_type"),
                bet_amount=float(item.get("bet_amount", 0.0)),
                result=item.get("result", "unknown"),
                profit_loss=float(item.get("profit_loss", 0.0)),
                balance_after=float(item.get("balance_after", 0.0)),
                timestamp=_parse_timestamp(item.get("timestamp")) or datetime.now(),
            )
        )
    return BetHistoryResponse(bets=items)


