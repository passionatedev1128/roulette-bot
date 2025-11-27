"""FastAPI application setup for the Roulette Bot web interface."""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .bot_manager import bot_manager
from .routes import config, control, results, stats, status
from .websocket import router as websocket_router

# Setup server-level logging
def _setup_server_logging():
    """Setup logging for the server to save all logs to a file."""
    # Create backend directory if it doesn't exist
    backend_dir = Path(__file__).parent.parent
    backend_dir.mkdir(exist_ok=True)
    
    # Create logs directory in backend
    logs_dir = backend_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"server_log_{timestamp}.txt"
    
    # Configure root logger to capture all logs
    root_logger = logging.getLogger()
    
    # Check if a file handler for this specific file already exists
    log_file_str = str(log_file)
    has_file_handler = any(
        isinstance(h, logging.FileHandler) and 
        hasattr(h, 'baseFilename') and 
        log_file_str in h.baseFilename 
        for h in root_logger.handlers
    )
    
    if not has_file_handler:
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create a custom handler that flushes immediately for real-time logging
        class ImmediateFlushHandler(logging.FileHandler):
            def emit(self, record):
                super().emit(record)
                self.flush()
        
        # File handler with immediate flushing - captures all logs and errors
        file_handler = ImmediateFlushHandler(log_file, encoding='utf-8', mode='a')
        file_handler.setLevel(logging.DEBUG)  # Capture all levels in file
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Ensure root logger level is set to capture all logs
        if root_logger.level > logging.DEBUG:
            root_logger.setLevel(logging.DEBUG)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Server logging configured: Logs saved to {log_file}")

# Setup logging on module import
_setup_server_logging()


def _get_cors_origins() -> List[str]:
    """
    Get CORS allowed origins from environment variable.
    Default includes local development origins.
    For production, set ROULETTE_WEB_CORS with your Vercel domain, e.g.:
    ROULETTE_WEB_CORS="https://your-app.vercel.app,http://localhost:3000"
    """
    default_origins = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    origins = os.getenv("ROULETTE_WEB_CORS", default_origins).split(",")
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


