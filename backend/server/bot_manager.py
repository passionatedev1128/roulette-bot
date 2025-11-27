"""Bot manager responsible for orchestrating the Roulette Bot for the web API."""

from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from backend.app.bot import RouletteBot
from backend.app.config_loader import ConfigLoader
from backend.app.detection.frame_detector import FrameDetector

from .events import EventDispatcher


class BotManager:
    """High-level controller coordinating the bot, config, and realtime state."""

    def __init__(self, config_path: str = "config/default_config.json") -> None:
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = ConfigLoader.load_config(str(self.config_path))

        self._lock = threading.RLock()
        self._bot: Optional[RouletteBot] = None
        self._bot_thread: Optional[threading.Thread] = None
        self._running = False
        self._status = "idle"
        self._mode = "Full Auto Mode"
        self._test_mode = False
        self._last_activity: Optional[datetime] = None
        self._last_error: Optional[str] = None
        self._start_time: Optional[datetime] = None

        self._initial_balance = float(self._config.get("risk", {}).get("initial_balance", 0.0))
        self._current_balance = self._initial_balance
        self._wins = 0
        self._losses = 0
        self._total_bets = 0

        self._spin_records: List[Dict[str, Any]] = []
        self._bet_history: List[Dict[str, Any]] = []
        self._active_bet: Dict[str, Any] = None

        self._preset_dir = Path("config/presets")
        self._preset_dir.mkdir(parents=True, exist_ok=True)

        self.event_dispatcher = EventDispatcher()

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------

    def initialize(self, loop) -> None:
        """Bind the asyncio event loop for websocket publishing."""

        self.event_dispatcher.bind_loop(loop)

    def _state_callback(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Receive state updates from the bot and update caches."""

        with self._lock:
            self._last_activity = datetime.now(timezone.utc)

            if event_type == "status_change":
                self._status = payload.get("status", self._status)
                self._mode = payload.get("mode", self._mode)
                if payload.get("error"):
                    self._last_error = payload["error"]

            elif event_type == "new_result":
                spin = payload.get("spin_data", {})
                if spin:
                    self._spin_records.append(spin)
                    self._spin_records = self._spin_records[-100:]

                bet_decision = payload.get("bet_decision")
                if bet_decision:
                    # Use timestamp from spin_data if available, otherwise use current time
                    spin_data = payload.get("spin_data", {})
                    timestamp = spin_data.get("timestamp")
                    if not timestamp:
                        timestamp = datetime.now(timezone.utc).isoformat()
                    self._active_bet = {
                        "bet_type": bet_decision.get("bet_type"),
                        "bet_amount": bet_decision.get("bet_amount", 0.0),
                        "gale_step": payload.get("gale_step"),
                        "timestamp": timestamp,
                    }

            elif event_type == "bet_placed":
                self._total_bets += 1
                # Use timestamp from payload if available, otherwise use current time
                timestamp = payload.get("timestamp")
                if not timestamp:
                    timestamp = datetime.now(timezone.utc).isoformat()
                self._active_bet = {
                    "bet_type": payload.get("bet_type"),
                    "bet_amount": payload.get("bet_amount", 0.0),
                    "gale_step": payload.get("gale_step"),
                    "timestamp": timestamp,
                }

            elif event_type == "bet_resolved":
                result = payload.get("result")
                if result == "win":
                    self._wins += 1
                elif result == "loss":
                    self._losses += 1

                self._current_balance = payload.get("balance", self._current_balance)

                history_entry = {
                    "spin_number": payload.get("spin_number", 0),
                    "bet_type": payload.get("bet_type"),
                    "bet_amount": payload.get("bet_amount", 0.0),
                    "result": result or "unknown",
                    "profit_loss": payload.get("profit_loss", 0.0),
                    "balance_after": self._current_balance,
                    "timestamp": payload.get("timestamp", datetime.now(timezone.utc).isoformat()),
                }
                self._bet_history.append(history_entry)
                self._bet_history = self._bet_history[-200:]
                self._active_bet = None

            elif event_type == "balance_update":
                self._current_balance = payload.get("balance", self._current_balance)

            elif event_type == "error":
                self._last_error = payload.get("message")

    def _create_bot(self) -> RouletteBot:
        """Instantiate a RouletteBot with current configuration."""
        
        logger = logging.getLogger(__name__)
        
        bot = RouletteBot(
            str(self.config_path),
            event_dispatcher=self.event_dispatcher,
            state_callback=self._state_callback,
            test_mode=self._test_mode,
            mode=self._mode,  # Pass the mode to the bot
        )
        
        # Replace detector with FrameDetector ONLY if explicitly configured via environment variable
        # By default, use ScreenDetector (desktop screen capture) for production use
        video_path = os.environ.get('BOT_VIDEO_PATH')
        
        # Only use video file if explicitly set via environment variable
        # Do NOT auto-detect video files - use screen capture by default
        if video_path and Path(video_path).exists():
            # Start from frame 1000 by default
            start_frame = int(os.environ.get('BOT_START_FRAME', '1000'))
            frame_detector = FrameDetector(self._config, video_path, start_frame=start_frame)
            bot.detector = frame_detector
            logger.info(f"Using video file for input: {video_path} (start_frame={start_frame})")
            logger.info("Note: Video file mode is enabled. Bot will read from video file, not desktop screen.")
        else:
            # Default: Use ScreenDetector (desktop screen capture)
            logger.info("Using screen capture (ScreenDetector) - bot will detect from desktop screen")
            logger.info(f"Screen region: {self._config.get('detection', {}).get('screen_region', 'full screen')}")
            logger.info("To use video file instead, set BOT_VIDEO_PATH environment variable.")
        
        return bot

    def start_bot(self, mode: Optional[str] = None, test_mode: bool = False) -> None:
        """Start the bot in a background thread."""

        with self._lock:
            if self._running:
                raise RuntimeError("Bot is already running")

            # Clear bet history when starting bot (but keep dailyStats and galeStats)
            self._bet_history = []
            self._spin_records = []
            self._active_bet = None
            # Reset counters but keep daily/gale stats (they are calculated from logs, not stored here)
            self._wins = 0
            self._losses = 0
            self._total_bets = 0
            self._current_balance = self._initial_balance

            self._mode = mode or self._mode
            self._test_mode = test_mode
            self._bot = self._create_bot()

            self._bot_thread = threading.Thread(target=self._run_bot_thread, name="RouletteBotThread", daemon=True)
            self._running = True
            self._status = "running"
            self._start_time = datetime.now(timezone.utc)

            self.event_dispatcher.publish("status_change", {"status": self._status, "mode": self._mode})

            self._bot_thread.start()

    def _run_bot_thread(self) -> None:
        """Internal method running in the bot thread."""

        try:
            if self._bot:
                self._bot.run()
        except Exception as exc:  # pragma: no cover - defensive guard
            with self._lock:
                self._status = "error"
                self._last_error = str(exc)
                self._running = False
            self.event_dispatcher.publish(
                "error",
                {"message": str(exc)},
            )
            self.event_dispatcher.publish("status_change", {"status": "error", "mode": self._mode, "error": str(exc)})
        finally:
            with self._lock:
                self._running = False
                if self._status != "error":
                    self._status = "idle"
            self.event_dispatcher.publish("status_change", {"status": self._status, "mode": self._mode})

    def stop_bot(self) -> None:
        """Stop the bot if it is running."""

        with self._lock:
            if not self._running or not self._bot:
                return

            self._bot.stop()
            self._start_time = None  # Reset start time when bot stops

        if self._bot_thread:
            self._bot_thread.join(timeout=10)

        with self._lock:
            self._running = False
            self._start_time = None  # Reset start time when bot stops
            self._status = "idle"
            self.event_dispatcher.publish("status_change", {"status": self._status, "mode": self._mode})

    def set_mode(self, mode: str) -> None:
        """Update the bot's operating mode."""

        with self._lock:
            self._mode = mode
        self.event_dispatcher.publish("status_change", {"status": self._status, "mode": mode})

    # ------------------------------------------------------------------
    # Configuration management
    # ------------------------------------------------------------------

    def get_config(self) -> Dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._config))  # deep copy

    def update_config(self, config: Dict[str, Any], persist: bool = True) -> None:
        with self._lock:
            self._config = config
            if persist:
                ConfigLoader.save_config(config, str(self.config_path))
            # Refresh initial balance reference
            self._initial_balance = float(config.get("risk", {}).get("initial_balance", self._initial_balance))
            if not self._running and self._bot is not None:
                # Recreate bot with new config when idle
                self._bot = self._create_bot()

    def save_preset(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        slug = self._slugify(name)
        preset_path = self._preset_dir / f"{slug}.json"
        preset_data = {
            "name": name,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "config": config,
        }
        preset_path.write_text(json.dumps(preset_data, indent=2), encoding="utf-8")
        return {"name": name, "slug": slug, "created_at": preset_data["saved_at"]}

    def list_presets(self) -> List[Dict[str, Any]]:
        presets = []
        for file in self._preset_dir.glob("*.json"):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                presets.append(
                    {
                        "name": data.get("name", file.stem),
                        "slug": file.stem,
                        "created_at": data.get("saved_at"),
                        "config": data.get("config"),
                    }
                )
            except json.JSONDecodeError:
                continue
        presets.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        return presets

    def load_preset(self, slug: str) -> Dict[str, Any]:
        preset_path = self._preset_dir / f"{slug}.json"
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {slug}")
        data = json.loads(preset_path.read_text(encoding="utf-8"))
        return data

    # ------------------------------------------------------------------
    # Data accessors
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            # Calculate process time if bot is running
            process_time_seconds = None
            if self._running and self._start_time:
                elapsed = datetime.now(timezone.utc) - self._start_time
                process_time_seconds = int(elapsed.total_seconds())
            
            return {
                "running": self._running,
                "status": self._status,
                "mode": self._mode,
                "last_activity": self._last_activity.isoformat() if self._last_activity else None,
                "spin_number": getattr(self._bot, "spin_number", 0),
                "process_time_seconds": process_time_seconds,
            }

    def get_balance(self) -> Dict[str, Any]:
        with self._lock:
            current_balance = self._current_balance
            if self._bot:
                current_balance = getattr(self._bot, "current_balance", current_balance)
            profit_loss = current_balance - self._initial_balance
            return {
                "current_balance": round(current_balance, 2),
                "initial_balance": round(self._initial_balance, 2),
                "profit_loss": round(profit_loss, 2),
                "today_profit_loss": round(self._calculate_today_profit(), 2),
                "total_bets": self._total_bets,
                "wins": self._wins,
                "losses": self._losses,
            }

    def get_recent_results(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._spin_records[-limit:])

    def get_active_bet(self) -> Dict[str, Any]:
        with self._lock:
            return self._active_bet.copy() if self._active_bet else None

    def get_bet_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._bet_history[-limit:])

    def get_daily_stats(self) -> List[Dict[str, Any]]:
        df = self._load_log_dataframe()
        if df is None or df.empty:
            return []

        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        grouped = df.groupby("date")
        stats = []
        for date, group in grouped:
            # Check if bet_type column exists before filtering
            if "bet_type" in group.columns:
                bets = group[group["bet_type"].notna()]
            else:
                bets = group  # If no bet_type column, consider all rows as bets
            
            wins = len(group[group["result"] == "win"]) if "result" in group.columns else 0
            losses = len(group[group["result"] == "loss"]) if "result" in group.columns else 0
            profit_series = group["profit_loss"] if "profit_loss" in group.columns else pd.Series(dtype=float)
            stats.append(
                {
                    "date": date.isoformat(),
                    "spins": int(len(group)),
                    "bets": int(len(bets)),
                    "wins": int(wins),
                    "losses": int(losses),
                    "profit_loss": float(profit_series.sum()) if not profit_series.empty else 0.0,
                }
            )
        stats.sort(key=lambda item: item["date"], reverse=True)
        return stats

    def get_strategy_stats(self) -> List[Dict[str, Any]]:
        df = self._load_log_dataframe()
        if df is None or df.empty:
            return []
        
        if "strategy" not in df.columns:
            return []

        grouped = df.groupby("strategy")
        stats = []
        for strategy, group in grouped:
            # Check if bet_type column exists before filtering
            if "bet_type" in group.columns:
                bets = group[group["bet_type"].notna()]
            else:
                bets = group  # If no bet_type column, consider all rows as bets
            
            wins = len(group[group["result"] == "win"]) if "result" in group.columns else 0
            losses = len(group[group["result"] == "loss"]) if "result" in group.columns else 0
            total_bets = len(bets)
            win_rate = (wins / total_bets * 100) if total_bets else 0.0
            profit_loss = group["profit_loss"].sum() if "profit_loss" in group.columns else 0.0
            stats.append(
                {
                    "strategy": strategy,
                    "bets": int(total_bets),
                    "wins": int(wins),
                    "losses": int(losses),
                    "win_rate": round(win_rate, 2),
                    "profit_loss": float(profit_loss),
                }
            )
        stats.sort(key=lambda item: item["bets"], reverse=True)
        return stats

    def get_gale_stats(self) -> List[Dict[str, Any]]:
        df = self._load_log_dataframe()
        if df is None or df.empty or "gale_step" not in df.columns:
            return []

        grouped = df.groupby("gale_step")
        stats = []
        for gale_step, group in grouped:
            wins = len(group[group["result"] == "win"]) if "result" in group.columns else 0
            losses = len(group[group["result"] == "loss"]) if "result" in group.columns else 0
            profit_loss = group["profit_loss"].sum() if "profit_loss" in group.columns else 0.0
            stats.append(
                {
                    "gale_step": int(gale_step) if pd.notna(gale_step) else 0,
                    "occurrences": int(len(group)),
                    "wins": int(wins),
                    "losses": int(losses),
                    "profit_loss": float(profit_loss),
                }
            )
        stats.sort(key=lambda item: item["gale_step"])
        return stats

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_log_dataframe(self) -> Optional[pd.DataFrame]:
        log_file = None
        with self._lock:
            if self._bot and getattr(self._bot, "logger", None):
                log_file = getattr(self._bot.logger, "csv_file", None)

        if not log_file:
            # Try latest log from logs dir
            logs_dir = Path(self._config.get("logging", {}).get("logs_dir", "logs"))
            if logs_dir.exists():
                csv_files = sorted(logs_dir.glob("roulette_log_*.csv"), reverse=True)
                if csv_files:
                    log_file = csv_files[0]

        if not log_file or not Path(log_file).exists():
            return None

        try:
            df = pd.read_csv(log_file)
            if "timestamp" not in df.columns:
                return None
            return df
        except Exception:  # pragma: no cover - defensive guard
            return None

    def _calculate_today_profit(self) -> float:
        df = self._load_log_dataframe()
        if df is None or df.empty or "timestamp" not in df.columns:
            return 0.0

        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        today = datetime.now().date()
        today_rows = df[df["date"] == today]
        if "profit_loss" not in today_rows.columns:
            return 0.0
        return float(today_rows["profit_loss"].sum())

    @staticmethod
    def _slugify(name: str) -> str:
        slug = name.strip().lower().replace(" ", "-")
        return "".join(ch for ch in slug if ch.isalnum() or ch == "-")


# Singleton manager used throughout the API
bot_manager = BotManager()


