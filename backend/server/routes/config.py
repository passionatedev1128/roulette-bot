"""Configuration-related API routes."""

from typing import List

from fastapi import APIRouter, HTTPException, status

from ..bot_manager import bot_manager
from ..schemas import (
    ConfigResponse,
    ConfigUpdateRequest,
    ErrorResponse,
    PresetCreateRequest,
    PresetSummary,
)


router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    """Retrieve the current bot configuration."""

    return ConfigResponse(config=bot_manager.get_config())


@router.put("/", response_model=ConfigResponse, responses={400: {"model": ErrorResponse}})
def update_config(payload: ConfigUpdateRequest) -> ConfigResponse:
    """Update the bot configuration."""

    if not isinstance(payload.config, dict):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid configuration payload")

    bot_manager.update_config(payload.config, persist=payload.persist)
    return ConfigResponse(config=bot_manager.get_config())


@router.post("/preset", status_code=status.HTTP_201_CREATED)
def save_preset(payload: PresetCreateRequest) -> PresetSummary:
    """Persist a configuration preset."""

    preset = bot_manager.save_preset(payload.name, payload.config)
    return PresetSummary(name=preset["name"], slug=preset["slug"], created_at=preset["created_at"])


@router.get("/presets", response_model=List[PresetSummary])
def list_presets() -> List[PresetSummary]:
    """List stored configuration presets."""

    presets = bot_manager.list_presets()
    return [
        PresetSummary(name=item["name"], slug=item["slug"], created_at=item.get("created_at"))
        for item in presets
    ]


@router.get("/preset/{slug}", response_model=ConfigResponse, responses={404: {"model": ErrorResponse}})
def load_preset(slug: str) -> ConfigResponse:
    """Load preset configuration by slug."""

    try:
        preset = bot_manager.load_preset(slug)
    except FileNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ConfigResponse(config=preset.get("config", {}))


