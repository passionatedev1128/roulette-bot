"""FastAPI application setup for the Roulette Bot web interface."""

from __future__ import annotations

import asyncio
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .bot_manager import bot_manager
from .routes import config, control, results, stats, status
from .websocket import router as websocket_router


def _get_cors_origins() -> List[str]:
    origins = os.getenv("ROULETTE_WEB_CORS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    return [origin.strip() for origin in origins if origin.strip()]


def create_app() -> FastAPI:
    """Application factory."""

    app = FastAPI(
        title="Roulette Bot API",
        version="1.0.0",
        description="Backend API for the Roulette Bot web interface",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(config.router)
    app.include_router(status.router)
    app.include_router(results.router)
    app.include_router(control.router)
    app.include_router(stats.router)
    app.include_router(websocket_router)

    @app.on_event("startup")
    async def _startup() -> None:  # pragma: no cover - event hook
        loop = asyncio.get_running_loop()
        bot_manager.initialize(loop)

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


