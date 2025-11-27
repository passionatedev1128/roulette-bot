"""Utilities for broadcasting bot events to WebSocket subscribers."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, Optional, Set


class EventDispatcher:
    """Thread-safe event dispatcher used for WebSocket broadcasts."""

    def __init__(self) -> None:
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._subscribers: Set[asyncio.Queue] = set()
        self._lock = Lock()

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Bind the asyncio event loop used for dispatching events."""

        self._loop = loop

    def register(self) -> asyncio.Queue:
        """Register a new subscriber queue."""

        queue: asyncio.Queue = asyncio.Queue()
        with self._lock:
            self._subscribers.add(queue)
        return queue

    def unregister(self, queue: asyncio.Queue) -> None:
        """Remove a subscriber queue."""

        with self._lock:
            self._subscribers.discard(queue)

    def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Publish an event to all subscribers."""

        if not self._loop:
            return

        event = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }

        with self._lock:
            subscribers = list(self._subscribers)

        for queue in subscribers:
            self._loop.call_soon_threadsafe(queue.put_nowait, event)


