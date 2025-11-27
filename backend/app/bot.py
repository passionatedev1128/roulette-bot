"""
Main Bot Orchestrator
Coordinates all modules to run the roulette bot.
"""

import time
import sys
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np

# Import standard library logging before local logging module to avoid circular import
# Use importlib to get standard library logging directly
import importlib
import sys as _sys

# Temporarily remove local logging from path to import standard library
_original_modules = {}
if 'logging' in _sys.modules:
    _original_modules['logging'] = _sys.modules.pop('logging')

# Import standard library logging
std_logging = importlib.import_module('logging')

# Restore original modules
_sys.modules.update(_original_modules)

from .detection import ScreenDetector
from .detection.game_state_detector import GameStateDetector, GameState
from .strategy import StrategyBase, MartingaleStrategy, FibonacciStrategy, CustomStrategy, EvenOddStrategy
from .betting import BetController
from .logging import RouletteLogger
from .config_loader import ConfigLoader

logger = std_logging.getLogger(__name__)


def calculate_required_bankroll(base_bet: float, max_gales: int, multiplier: float = 2.0) -> Dict:
    """
    Calculate the maximum required bankroll for a given strategy configuration.
    
    This is an informational pre-check to estimate the maximum bankroll needed
    if all gales in a cycle are used (worst-case scenario).
    
    Args:
        base_bet: Base stake amount
        max_gales: Maximum number of gales allowed
        multiplier: Multiplier for gale progression (default: 2.0 for doubling)
        
    Returns:
        Dictionary with bankroll information:
        {
            "base_bet": float,
            "max_gales": int,
            "multiplier": float,
            "gale_sequence": List[float],  # Bet amounts for each gale step
            "total_required": float,  # Sum of all bets in worst-case cycle
            "recommended_bankroll": float  # Recommended bankroll (total + buffer)
        }
    """
    gale_sequence = []
    total = 0.0
    
    for step in range(max_gales + 1):  # Include initial bet (step 0)
        bet_amount = base_bet * (multiplier ** step)
        gale_sequence.append(bet_amount)
        total += bet_amount
    
    # Recommended bankroll includes a 20% buffer for safety
    recommended = total * 1.2
    
    return {
        "base_bet": base_bet,
        "max_gales": max_gales,
        "multiplier": multiplier,
        "gale_sequence": gale_sequence,
        "total_required": round(total, 2),
        "recommended_bankroll": round(recommended, 2),
        "note": "This is the worst-case scenario if all gales are used in a single cycle"
    }


class RouletteBot:
    """Main bot orchestrator."""
    
    def __init__(
        self,
        config_path: str,
        event_dispatcher: Optional[object] = None,
        state_callback: Optional[Callable[[str, Dict], None]] = None,
        test_mode: bool = False,
        mode: str = "Full Auto Mode",
    ):
        """
        Initialize roulette bot.
        
        Args:
            config_path: Path to configuration file
            event_dispatcher: Optional event dispatcher for WebSocket events
            state_callback: Optional callback for state updates
            test_mode: If True, run in test mode (still places bets but logs more)
            mode: Operating mode - "Full Auto Mode" (places bets) or "Detection Only Mode" (no betting)
        """
        # Load configuration
        self.config = ConfigLoader.load_config(config_path)
        
        # Initialize modules
        self.detector = ScreenDetector(self.config)
        self.strategy = self._create_strategy()
        self.bet_controller = BetController(self.config)
        self.logger = RouletteLogger(self.config)
        detection_settings = self.config.get('detection', {})
        self.min_result_gap_seconds = float(detection_settings.get('min_result_gap_seconds', 3.0))
        # Frame gap: if same number appears for 60-90 frames, ignore it (default: 90)
        self.min_result_gap_frames = int(detection_settings.get('min_result_gap_frames', 90))
        self.last_result_signature: Optional[Tuple[Optional[int], Optional[str]]] = None
        self.last_result_time: float = 0.0
        self.last_result_frame_index: Optional[int] = None
        self.last_processed_result: Optional[Tuple[Optional[int], Optional[str]]] = None  # Track last actually processed result
        self.first_detection_processed: bool = False  # Track if first detection has been processed
        
        # Initialize game state detector (optional)
        enable_game_state = self.config.get('detection', {}).get('enable_game_state', False)
        if enable_game_state:
            self.game_state_detector = GameStateDetector(self.config)
        else:
            self.game_state_detector = None
        
        # Bot state
        self.running = False
        self.spin_number = 0
        self.result_history: List[Dict] = []
        self.current_balance = self.config.get('risk', {}).get('initial_balance', 1000.0)
        self.initial_balance = self.current_balance
        self.last_maintenance_bet_time = time.time()
        
        # Track pending bet (bet placed but not yet resolved)
        self.pending_bet: Optional[Dict] = None
        
        # Frame skipping configuration
        self.frame_skip_interval = self.config.get('detection', {}).get('frame_skip_interval', 30)
        self.video_frame_skip_interval = self.config.get('detection', {}).get('video_frame_skip_interval', 30)
        self.frame_counter = 0  # Track frames to determine when to process
        
        # Performance optimization settings
        detection_settings = self.config.get('detection', {})
        self.loop_delay_no_detection = float(detection_settings.get('loop_delay_no_detection', 0.1))  # Sleep when no detection
        self.loop_delay_after_detection = float(detection_settings.get('loop_delay_after_detection', 0.05))  # Sleep after detection
        self.loop_delay_duplicate = float(detection_settings.get('loop_delay_duplicate', 0.2))  # Sleep when duplicate detected
        self.consecutive_no_detection = 0  # Track consecutive failures for adaptive delays
        
        # Stop conditions tracking
        self.winning_rounds = 0
        self.losing_rounds = 0
        self.keepalive_bets_count = 0
        self.stop_trigger_info = None  # Track which stop condition was triggered
        
        # Events / callbacks
        self.event_dispatcher = event_dispatcher
        self.state_callback = state_callback
        self.test_mode = test_mode
        self.mode = mode  # "Full Auto Mode" or "Detection Only Mode"

        # Setup logging
        self._setup_logging()
        
        # Log bankroll information (informational only)
        if isinstance(self.strategy, EvenOddStrategy):
            bankroll_info = calculate_required_bankroll(
                self.strategy.base_bet,
                self.strategy.max_gales,
                self.strategy.multiplier
            )
            logger.info(
                f"Bankroll estimate: Required={bankroll_info['total_required']}, "
                f"Recommended={bankroll_info['recommended_bankroll']} "
                f"(base_bet={self.strategy.base_bet}, max_gales={self.strategy.max_gales})"
            )
        
        logger.info("RouletteBot initialized")
        logger.info(f"Bot mode: {self.mode}")
        if self.test_mode:
            logger.info("RouletteBot running in test mode")
        if self.mode == "Detection Only Mode":
            logger.info("  Detection Only Mode: Bot will detect numbers but will NOT place bets or move mouse")

    def _emit_event(self, event_type: str, payload: Dict):
        """Emit events to dispatcher and state callback."""

        if self.state_callback:
            try:
                self.state_callback(event_type, payload)
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.debug(f"State callback error for {event_type}: {exc}")

        if self.event_dispatcher:
            try:
                self.event_dispatcher.publish(event_type, payload)
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.debug(f"Event dispatcher error for {event_type}: {exc}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('logging', {}).get('log_level', 'INFO')
        
        # Create backend directory if it doesn't exist
        backend_dir = Path(__file__).parent.parent
        backend_dir.mkdir(exist_ok=True)
        
        # Create logs directory in backend
        logs_dir = backend_dir / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"bot_log_{timestamp}.txt"
        
        # Configure root logger to capture all logs
        root_logger = std_logging.getLogger()
        formatter = std_logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Check if a file handler for this specific file already exists
        log_file_str = str(log_file)
        has_file_handler = any(
            isinstance(h, std_logging.FileHandler) and 
            hasattr(h, 'baseFilename') and 
            log_file_str in h.baseFilename 
            for h in root_logger.handlers
        )

        if not has_file_handler:
            # Create a custom handler that flushes immediately for real-time logging
            class ImmediateFlushHandler(std_logging.FileHandler):
                def emit(self, record):
                    super().emit(record)
                    self.flush()
            
            # File handler with immediate flushing - captures all logs and errors
            immediate_handler = ImmediateFlushHandler(log_file, encoding='utf-8', mode='a')
            immediate_handler.setLevel(std_logging.DEBUG)  # Capture all levels in file
            immediate_handler.setFormatter(formatter)
            root_logger.addHandler(immediate_handler)

        # Set root logger level (but don't clear existing handlers)
        root_logger.setLevel(getattr(std_logging, log_level))

        # Ensure a dedicated console handler exists so bot logs are always visible in terminal output
        console_handler_name = "bot_console_handler"
        has_console_handler = any(
            isinstance(h, std_logging.StreamHandler) and getattr(h, "name", "") == console_handler_name
            for h in root_logger.handlers
        )
        if not has_console_handler:
            console_handler = std_logging.StreamHandler(stream=sys.stdout)
            console_handler.setLevel(getattr(std_logging, log_level))
            console_handler.setFormatter(formatter)
            console_handler.set_name(console_handler_name)
            root_logger.addHandler(console_handler)
        
        logger.info(f"Bot logging configured: Logs saved to {log_file}")
    
    def _create_strategy(self) -> StrategyBase:
        """Create strategy instance based on configuration."""
        strategy_type = self.config.get('strategy', {}).get('type', 'martingale')
        strategy_config = self.config.get('strategy', {})
        
        if strategy_type == 'martingale':
            return MartingaleStrategy(strategy_config)
        elif strategy_type == 'fibonacci':
            return FibonacciStrategy(strategy_config)
        elif strategy_type == 'custom':
            return CustomStrategy(strategy_config)
        elif strategy_type == 'even_odd':
            return EvenOddStrategy(strategy_config)
        else:
            logger.warning(f"Unknown strategy type: {strategy_type}, using Martingale")
            return MartingaleStrategy(strategy_config)
    
    def detect_result(self, frame: Optional[np.ndarray] = None) -> Optional[Dict]:
        """
        Detect current roulette result.
        
        Args:
            frame: Optional frame to use for detection. If None, detector will capture its own.
        
        Returns:
            Detection result or None if failed
        """
        try:
            result = self.detector.detect_result(frame)
            
            # Validate result
            if self.detector.validate_result(result):
                return result
            else:
                logger.warning("Detection result validation failed")
                return None
                
        except Exception as e:
            logger.error(f"Error detecting result: {e}")
            self.logger.log_error({
                "error": str(e),
                "type": "detection_error",
                "context": {"spin_number": self.spin_number}
            })
            return None
    
    def check_maintenance_bet(self) -> bool:
        """
        Check if maintenance bet is needed.
        
        Returns:
            True if maintenance bet should be placed
        """
        # For Even/Odd strategy, use 29 minutes; others use configured interval
        if isinstance(self.strategy, EvenOddStrategy):
            interval = 1740  # 29 minutes in seconds
        else:
            interval = self.config.get('session', {}).get('maintenance_bet_interval', 1800)  # 30 minutes
        
        elapsed = time.time() - self.last_maintenance_bet_time
        
        return elapsed >= interval
    
    def place_maintenance_bet(self):
        """Place maintenance bet to keep session active."""
        try:
            # If using Even/Odd strategy, use its keepalive method
            if isinstance(self.strategy, EvenOddStrategy):
                keepalive_bet = self.strategy.get_keepalive_bet()
                if keepalive_bet is None:
                    logger.debug("Keepalive skipped: cycle is active")
                    return
                
                bet_result = self.bet_controller.place_bet(
                    keepalive_bet['bet_type'],
                    keepalive_bet['bet_amount']
                )
                
                if bet_result['success']:
                    self.last_maintenance_bet_time = time.time()
                    self.keepalive_bets_count += 1
                    logger.info(f"Keepalive bet placed: {keepalive_bet['bet_amount']} on {keepalive_bet['bet_type']} (total keepalive bets: {self.keepalive_bets_count})")
                else:
                    logger.warning(f"Keepalive bet failed: {bet_result.get('error')}")
            else:
                # For other strategies, use traditional maintenance bet
                min_bet = self.config.get('session', {}).get('min_bet_amount', 1.0)
                
                # Place minimum bet on red (or alternate)
                bet_result = self.bet_controller.place_bet('red', min_bet)
                
                if bet_result['success']:
                    self.last_maintenance_bet_time = time.time()
                    logger.info(f"Maintenance bet placed: {min_bet} on red")
                else:
                    logger.warning(f"Maintenance bet failed: {bet_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error placing maintenance bet: {e}")
    
    def process_spin(self, result: Dict) -> Dict:
        """
        Process a complete spin: detect result, calculate bet, place bet.
        
        Args:
            result: Detection result
            
        Returns:
            Spin processing result
        """
        self.spin_number += 1
        
        # Update history
        self.result_history.append(result)
        if len(self.result_history) > 100:  # Keep last 100 results
            self.result_history.pop(0)
        
        # Handle zero if needed
        if result.get('zero', False):
            zero_handling = self.strategy.handle_zero(self.result_history, self.current_balance)
            logger.info(f"Zero detected, handling: {zero_handling}")
        
        # Log current strategy state before calculating bet (for Even/Odd strategy)
        if isinstance(self.strategy, EvenOddStrategy):
            logger.info(
                f"Before bet calculation: Even streak={self.strategy.current_even_streak}, "
                f"Odd streak={self.strategy.current_odd_streak}, "
                f"streak_length required={self.strategy.streak_length}, "
                f"cycle_active={self.strategy.cycle_active}, number={result.get('number')}"
            )
        
        # Calculate bet (strategy will update streaks internally)
        bet_decision = self.strategy.calculate_bet(
            self.result_history,
            self.current_balance,
            result
        )
        
        # Log why bet decision was made or not
        if bet_decision:
            logger.info(
                f"Bet decision: {bet_decision.get('bet_type')} for {bet_decision.get('bet_amount')} "
                f"(reason: {bet_decision.get('reason', 'N/A')})"
            )
        else:
            if isinstance(self.strategy, EvenOddStrategy):
                logger.info(
                    f"No bet decision: Even streak={self.strategy.current_even_streak}, "
                    f"Odd streak={self.strategy.current_odd_streak}, "
                    f"streak_length required={self.strategy.streak_length}, "
                    f"cycle_active={self.strategy.cycle_active}"
                )
            else:
                logger.info("No bet decision made by strategy")
        
        # Place bet if decision made
        bet_result = None
        if bet_decision:
            bet_type = bet_decision.get('bet_type')
            bet_amount = bet_decision.get('bet_amount')
            
            # Check if betting is allowed based on mode
            if self.mode == "Detection Only Mode":
                logger.info(f"  Bet decision made: {bet_type} - {bet_amount}, but skipping bet placement (Detection Only Mode)")
                logger.info(f"   Betting is disabled in Detection Only Mode. Switch to 'Full Auto Mode' to enable betting.")
                # Still emit event to show what bet would have been placed
                self._emit_event("bet_decision_made", {
                    "bet_type": bet_type,
                    "bet_amount": bet_amount,
                    "gale_step": self.strategy.gale_step,
                    "spin_number": self.spin_number,
                    "skipped": True,
                    "reason": "Detection Only Mode"
                })
                bet_result = {
                    "success": False,
                    "bet_type": bet_type,
                    "bet_amount": bet_amount,
                    "error": "Betting disabled in Detection Only Mode"
                }
            else:
                # Log coordinates for debugging
                betting_coords = self.bet_controller.find_betting_area(bet_type)
                if betting_coords:
                    logger.info(f" Betting coordinates found: {betting_coords} for bet_type={bet_type}")
                else:
                    logger.error(f" No coordinates found for bet_type={bet_type}")
                    logger.error(f"   Available betting areas: {list(self.bet_controller.betting_areas.keys())}")
                
                logger.info(f"  Moving mouse to place bet: {bet_type} - {bet_amount}")
                
                bet_result = self.bet_controller.place_bet(bet_type, bet_amount)
            
            if bet_result['success']:
                logger.info(f" Bet placed successfully: {bet_type} - {bet_amount}")
                logger.info(f" Mouse moved and clicked at betting coordinates")
                self._emit_event("bet_placed", {
                    "bet_type": bet_type,
                    "bet_amount": bet_amount,
                    "gale_step": self.strategy.gale_step,
                    "spin_number": self.spin_number,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            else:
                error_msg = bet_result.get('error', 'Unknown error')
                logger.error(f" Bet placement failed: {error_msg}")
                logger.error(f"   Bet type: {bet_type}, Amount: {bet_amount}")
                logger.error(f"   Coordinates: {betting_coords}")
                self._emit_event("error", {
                    "message": f"Bet placement failed: {error_msg}",
                    "context": {"spin_number": self.spin_number, "bet_type": bet_type}
                })
        else:
            logger.info("No bet decision made - skipping bet placement")
        
        # Determine result (win/loss) - this would need to be determined after round completes
        # For now, we'll log what we know
        # Determine bet category (strategy/maintenance/gale) and bet color
        bet_category = None
        bet_color = None
        if bet_decision:
            # bet_type from strategy is actually the color (red/black/green)
            bet_color = bet_decision.get('bet_type')
            # Determine category based on context
            if self.strategy.gale_step > 0:
                bet_category = "gale"
            elif bet_decision.get('strategy') == 'maintenance':
                bet_category = "maintenance"
            else:
                bet_category = "strategy"
        
        # Get table name from config
        table_name = self.config.get('table', {}).get('name', 'Roleta Brasileira')
        
        # Get cycle and streak info from strategy if available
        cycle_number = None
        streak_length = None
        is_keepalive = False
        
        if isinstance(self.strategy, EvenOddStrategy):
            # Get cycle number - use from bet_decision if available, otherwise from strategy
            if bet_decision and bet_decision.get('cycle_number') is not None:
                cycle_number = bet_decision.get('cycle_number')
            else:
                cycle_number = self.strategy.cycle_number if self.strategy.cycle_active else None
            streak_length = max(self.strategy.current_even_streak, self.strategy.current_odd_streak)
            if bet_decision:
                is_keepalive = bet_decision.get('is_keepalive', False)
        
        spin_data = {
            "spin_number": self.spin_number,
            "table": table_name,
            "outcome_number": result.get('number'),
            "outcome_color": result.get('color'),
            "bet_category": bet_category,
            "bet_color": bet_color,
            "bet_amount": bet_decision.get('bet_amount') if bet_decision else 0.0,
            "stake": bet_decision.get('bet_amount') if bet_decision else 0.0,  # Same as bet_amount for now
            "balance_before": self.current_balance,
            "balance_after": self.current_balance,  # Will be updated after round
            "result": "pending",  # Will be updated after round completes
            "profit_loss": 0.0,
            "strategy": self.strategy.strategy_type,
            "cycle_number": cycle_number,
            "gale_step": self.strategy.gale_step,
            "streak_length": streak_length,
            "is_keepalive": is_keepalive,
            "detection_confidence": result.get('confidence', 0.0),
            "detection_method": result.get('method', 'unknown'),
            "errors": None
        }
        
        # Log spin
        self.logger.log_spin(spin_data)
        
        self._emit_event("new_result", {
            "spin_number": self.spin_number,
            "result": result,
            "bet_decision": bet_decision,
            "bet_result": bet_result,
            "spin_data": spin_data,
            "gale_step": self.strategy.gale_step,
        })

        return {
            "spin_number": self.spin_number,
            "result": result,
            "bet_decision": bet_decision,
            "bet_result": bet_result,
            "spin_data": spin_data
        }
    
    def _determine_bet_result(self, bet_type: str, result_number: int) -> bool:
        """
        Determine if a bet won based on bet type and result number.
        
        Args:
            bet_type: 'red', 'black', 'green', 'even', 'odd', or number string
            result_number: The winning number (0-36)
            
        Returns:
            True if bet won, False if lost
        """
        if bet_type is None:
            return False
            
        # Even/Odd bets
        if bet_type == 'even':
            # Even numbers: 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36
            even_numbers = {2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36}
            return result_number in even_numbers
            
        if bet_type == 'odd':
            # Odd numbers: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35
            odd_numbers = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35}
            return result_number in odd_numbers
        
        # Color bets
        red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
        
        if bet_type == 'red':
            return result_number in red_numbers
        if bet_type == 'black':
            return result_number in black_numbers
        if bet_type == 'green':
            return result_number == 0
        
        # Number bets
        try:
            bet_number = int(bet_type)
            return result_number == bet_number
        except (ValueError, TypeError):
            logger.warning(f"Unknown bet type: {bet_type}")
            return False
    
    def update_after_round(self, spin_result: Dict, result_number: Optional[int] = None):
        """
        Update bot state after round completes.
        
        Args:
            spin_result: Result from process_spin (or minimal dict with spin_number when resolving pending bet)
            result_number: The winning number (0-36). If None, uses spin_result data.
        """
        # Handle case where spin_data might not exist (e.g., when resolving pending bet)
        spin_data = spin_result.get('spin_data', {})
        
        # Get bet information - try spin_data first, then bet_decision, then pending_bet
        bet_amount = spin_data.get('bet_amount', 0.0)
        if bet_amount == 0.0:
            bet_amount = spin_result.get('bet_decision', {}).get('bet_amount', 0.0)
        if bet_amount == 0.0 and self.pending_bet:
            bet_amount = self.pending_bet.get('bet_amount', 0.0)
        
        bet_type = spin_data.get('bet_color') or spin_result.get('bet_decision', {}).get('bet_type')
        if not bet_type and self.pending_bet:
            bet_type = self.pending_bet.get('bet_type')
        
        # Get result number
        if result_number is None:
            result_number = spin_result.get('result', {}).get('number')
            if result_number is None:
                result_number = spin_data.get('outcome_number')
        
        # Determine if bet won
        if bet_type and result_number is not None:
            won = self._determine_bet_result(bet_type, result_number)
        else:
            # Fallback: if we can't determine, assume loss (conservative)
            logger.warning(f"Cannot determine bet result: bet_type={bet_type}, result_number={result_number}")
            won = False
        
        if won:
            profit = bet_amount  # Assuming 1:1 payout
            self.current_balance += profit
            result = "win"
            self.winning_rounds += 1
        else:
            profit = -bet_amount
            self.current_balance -= bet_amount
            result = "loss"
            self.losing_rounds += 1
        
        # Update strategy
        self.strategy.update_after_bet({
            "result": result,
            "balance_after": self.current_balance,
            "profit_loss": profit
        })
        
        # Reset bet controller
        self.bet_controller.reset_bet_flag()
        
        # Update spin data in CSV log with final result
        spin_number_for_update = spin_result.get('spin_number', self.spin_number)
        self.logger.update_spin_result(
            spin_number=spin_number_for_update,
            result=result,
            profit_loss=profit,
            balance_after=self.current_balance
        )
        logger.info(f"Round completed: {result}, Balance: {self.current_balance}, Bet: {bet_type}, Result: {result_number}")

        # Get gale step from spin data or strategy for stats
        gale_step = spin_data.get('gale_step')
        if gale_step is None:
            gale_step = self.strategy.gale_step
        
        self._emit_event("bet_resolved", {
            "spin_number": spin_result.get('spin_number', self.spin_number),
            "bet_type": bet_type,
            "bet_amount": bet_amount,
            "result": result,
            "result_number": result_number,
            "profit_loss": profit,
            "balance": self.current_balance,
            "gale_step": gale_step,  # Include for gale stats calculation
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self._emit_event("balance_update", {"balance": self.current_balance})
    
    def check_stop_conditions(self) -> bool:
        """
        Check if bot should stop (StopLoss or StopWin).
        
        Returns:
            True if should stop, False otherwise
        """
        risk_config = self.config.get('risk', {})
        
        # StopLoss by money
        stop_loss_money = risk_config.get('stop_loss', 0.0)
        if stop_loss_money > 0 and self.current_balance <= stop_loss_money:
            logger.warning(f"StopLoss (money) reached: balance={self.current_balance}, stop_loss={stop_loss_money}")
            self.stop_trigger_info = {
                "triggered": True,
                "type": "stop_loss_money",
                "value": self.current_balance,
                "threshold": stop_loss_money
            }
            return True
        
        # StopLoss by count
        stop_loss_count = risk_config.get('stop_loss_count', None)
        if stop_loss_count is not None and self.losing_rounds >= stop_loss_count:
            logger.warning(f"StopLoss (count) reached: losing_rounds={self.losing_rounds}, threshold={stop_loss_count}")
            self.stop_trigger_info = {
                "triggered": True,
                "type": "stop_loss_count",
                "value": self.losing_rounds,
                "threshold": stop_loss_count
            }
            return True
        
        # StopWin by money
        stop_win_money = risk_config.get('stop_win', None)
        if stop_win_money is not None:
            net_pnl = self.current_balance - self.initial_balance
            if net_pnl >= stop_win_money:
                logger.warning(f"StopWin (money) reached: net_pnl={net_pnl}, stop_win={stop_win_money}")
                self.stop_trigger_info = {
                    "triggered": True,
                    "type": "stop_win_money",
                    "value": net_pnl,
                    "threshold": stop_win_money
                }
                return True
        
        # StopWin by count
        stop_win_count = risk_config.get('stop_win_count', None)
        if stop_win_count is not None and self.winning_rounds >= stop_win_count:
            logger.warning(f"StopWin (count) reached: winning_rounds={self.winning_rounds}, threshold={stop_win_count}")
            self.stop_trigger_info = {
                "triggered": True,
                "type": "stop_win_count",
                "value": self.winning_rounds,
                "threshold": stop_win_count
            }
            return True
        
        # Max gale reached (only stop if not in a cycle that should complete)
        if self.strategy.is_gale_max_reached():
            # For Even/Odd strategy, this is handled in cycle management
            if not isinstance(self.strategy, EvenOddStrategy):
                logger.warning("Maximum gale steps reached")
                return True
        
        return False
    
    def run(self):
        """Main bot loop."""
        logger.info("Starting roulette bot...")
        self.running = True
        
        # Reset duplicate detection tracking when bot starts
        self.last_result_signature = None
        self.last_result_time = 0.0
        self.last_result_frame_index = None
        self.last_processed_result = None
        self.first_detection_processed = False
        logger.info("Duplicate detection tracking reset - ready for new detections")

        self._emit_event("status_change", {"status": "running"})
        
        # Check if video has frames (if using FrameDetector)
        if hasattr(self.detector, 'cap') and hasattr(self.detector, 'video_path'):
            test_frame = self.detector.capture_screen()
            if test_frame is None:
                logger.error(
                    "Cannot start bot: Video file has no readable frames. "
                    "Please verify the video file is valid: %s",
                    getattr(self.detector, 'video_path', 'unknown')
                )
                self.running = False
                self._emit_event("status_change", {"status": "error", "error": "Video file has no frames"})
                return
            # Reset to beginning after test
            if hasattr(self.detector, 'restart_video'):
                self.detector.restart_video()
        
        # Check if using video frames (FrameDetector) vs real-time screen capture
        is_video_mode = hasattr(self.detector, 'cap') and hasattr(self.detector, 'video_path')
        
        # Performance-optimized processing with adaptive delays
        # Game cycle timing (updated):
        # - Wheel spins: 14 seconds
        # - Winning number displays: 2-3 seconds (appears 15 seconds after wheel starts)
        # - Total cycle: 15 seconds
        # - Detection: Every 30 frames (1 second intervals at 30fps)
        
        if is_video_mode:
            logger.info(f"Video frame mode detected - processing every {self.video_frame_skip_interval} frames (1 second intervals), starting from frame 1000")
            logger.info(f"Game cycle: 15 seconds. Duplicate detections within {self.min_result_gap_seconds}s will be ignored.")
        else:
            logger.info(f"Real-time mode - processing with optimized delays (delay_no_detection={self.loop_delay_no_detection}s, frame_skip={self.frame_skip_interval})")
        
        try:
            while self.running:
                # Check stop conditions
                if self.check_stop_conditions():
                    logger.warning("Stop conditions met, shutting down")
                    break
                
                # Check maintenance bet
                if self.check_maintenance_bet():
                    self.place_maintenance_bet()
                
                # Process frames immediately without any delay
                
                # Capture frame (needed for both game state detection and result detection)
                frame = None
                try:
                    frame = self.detector.capture_screen()
                    if frame is None:
                        logger.info("Video ended or frame capture failed. Stopping bot.")
                        break
                except Exception as e:
                    logger.error(f"Failed to capture frame: {e}")
                    break
                
                # Frame skipping: process every Nth frame based on mode
                # Video mode: process every 30 frames (1 second at 30fps) for optimal performance
                # Real-time mode: process every Nth frame based on config
                # When running through backend (in thread), use more frequent detection to improve reliability
                self.frame_counter += 1
                
                # Determine if running through backend (has event dispatcher = integrated mode)
                is_integrated_mode = self.event_dispatcher is not None
                
                # Use more frequent detection when running through backend to improve reliability
                # This compensates for potential timing/threading issues
                effective_frame_skip = self.frame_skip_interval
                if is_integrated_mode and not is_video_mode:
                    # Reduce frame skip by 10% when running through backend for better detection
                    # This helps catch frames that might be missed due to threading/timing issues
                    effective_frame_skip = max(1, int(self.frame_skip_interval * 0.1))
                    if self.frame_counter == 1:
                        logger.info(f"Integrated mode detected - using reduced frame skip interval: {effective_frame_skip} (was {self.frame_skip_interval}) for better detection reliability")
                
                if is_video_mode:
                    # Video mode: process every 30 frames (1 second intervals)
                    if self.frame_counter % self.video_frame_skip_interval != 0:
                        # Skip this frame - add small delay to prevent 100% CPU
                        time.sleep(self.loop_delay_no_detection)
                        result = None
                        # Continue to next iteration immediately
                        continue
                    else:
                        # Detect result using the captured frame (every 30 frames = 1 second)
                        result = self.detect_result(frame)
                else:
                    # Real-time mode: use effective frame skip interval (reduced in integrated mode)
                    if self.frame_counter % effective_frame_skip != 0:
                        # Skip this frame - add small delay to prevent 100% CPU
                        time.sleep(self.loop_delay_no_detection)
                        result = None
                        # Continue to next iteration immediately
                        continue
                    else:
                        # Detect result using the captured frame
                        result = self.detect_result(frame)
                
                # Detection completed, continue to process immediately

                # Determine frame index/context for logging
                frame_index: Optional[int] = None
                frame_context = ""
                if hasattr(self.detector, "get_current_frame_number"):
                    try:
                        frame_index = self.detector.get_current_frame_number()
                        if frame_index is not None and frame_index >= 0:
                            frame_context = f" (frame {frame_index})"
                    except Exception:  # pragma: no cover - best-effort logging
                        frame_context = ""
                        frame_index = None

                duplicate_detection = False
                if result:
                    result_signature = (result.get("number"), result.get("color"))
                    now_ts = time.time()
                    
                    # Check against last PROCESSED result (most strict - already sent to frontend)
                    # BUT: Only reject if within time gap (same cycle), allow if new cycle (15+ seconds passed)
                    if self.last_processed_result == result_signature:
                        # Check if enough time has passed for a new game cycle
                        time_since_last_processed = now_ts - self.last_result_time if self.last_result_time > 0 else float('inf')
                        if time_since_last_processed < self.min_result_gap_seconds:
                            # Same result within same cycle - reject as duplicate
                            duplicate_detection = True
                            logger.info(
                                f"Duplicate result ignored{frame_context}: "
                                f"result {result_signature} was already processed and sent to frontend "
                                f"(time gap: {time_since_last_processed:.2f}s < {self.min_result_gap_seconds}s)"
                            )
                        else:
                            # Same result but new cycle (15+ seconds passed) - allow it
                            logger.info(
                                f"Same result in new cycle{frame_context}: "
                                f"result {result_signature} detected again after {time_since_last_processed:.2f}s "
                                f"(new game cycle, allowing detection)"
                            )
                            # Update tracking to allow this detection
                            self.last_processed_result = None  # Reset to allow processing
                            self.last_result_signature = result_signature
                            self.last_result_time = now_ts
                            if frame_index is not None and frame_index >= 0:
                                self.last_result_frame_index = frame_index
                    # Check time/frame gaps for sequential detection
                    # Game cycle is 15 seconds: wheel spins 14s, then winning number shows for 2-3s (at 15s mark)
                    # If same number detected within 15 seconds, it's a duplicate from the same cycle
                    elif self.last_result_signature == result_signature and self.first_detection_processed:
                        # Use 15 second gap to match game cycle (one cycle = 15 seconds)
                        # In video mode with 30 frame skip (1 second intervals), 15 seconds = 15 detections
                        # Frame gap check: allow some tolerance for frame-based detection
                        # With 30 frame skip, 15 seconds = 15 detections, so use 15 as frame gap
                        effective_gap_frames = 15 if is_video_mode else self.min_result_gap_frames
                        within_time_gap = (now_ts - self.last_result_time) < self.min_result_gap_seconds

                        within_frame_gap = False
                        if (
                            frame_index is not None
                            and self.last_result_frame_index is not None
                            and frame_index >= 0
                            and self.last_result_frame_index >= 0
                        ):
                            frame_delta = frame_index - self.last_result_frame_index
                            if frame_delta < 0:
                                # Video restarted or frame counter reset - reset tracking
                                self.last_result_frame_index = frame_index
                                self.last_result_signature = result_signature
                                self.last_result_time = now_ts
                            else:
                                within_frame_gap = (
                                    frame_delta <= effective_gap_frames
                                )

                        if within_time_gap or within_frame_gap:
                            duplicate_detection = True
                            logger.info(
                                f"Duplicate detection ignored{frame_context}: "
                                f"same result {result_signature} detected again within {self.min_result_gap_seconds}s gap "
                                f"(time gap: {now_ts - self.last_result_time:.2f}s, "
                                f"frame gap: {frame_delta if frame_index is not None and self.last_result_frame_index is not None else 'N/A'}/{effective_gap_frames} frames) - NOT sent to frontend"
                            )
                        else:
                            # Same result but enough time/frames passed - treat as new result
                            logger.debug(f"Same result {result_signature} detected but enough time/frames passed ({frame_delta if frame_index is not None and self.last_result_frame_index is not None else 'N/A'} frames), processing as new")
                            self.last_result_signature = result_signature
                            self.last_result_time = now_ts
                            if frame_index is not None and frame_index >= 0:
                                self.last_result_frame_index = frame_index
                    else:
                        # Different result or first detection - always process
                        self.last_result_signature = result_signature
                        self.last_result_time = now_ts
                        if frame_index is not None and frame_index >= 0:
                            self.last_result_frame_index = frame_index
                        # Mark that we've processed at least one detection
                        if not self.first_detection_processed:
                            self.first_detection_processed = True
                            logger.info(f"First detection processed{frame_context}: {result_signature}")

                # CRITICAL: Skip all processing if duplicate detected - prevents events from being sent to frontend
                if duplicate_detection:
                    logger.debug(
                        "Duplicate detection detected%s; skipping ALL processing to avoid sending to frontend",
                        frame_context,
                    )
                    # Add delay for duplicates to reduce CPU usage
                    time.sleep(self.loop_delay_duplicate)
                    # Continue to next iteration immediately
                    continue

                if result:
                    # Reset consecutive no-detection counter on successful detection
                    self.consecutive_no_detection = 0
                    
                    detection_method = result.get("detection_method") or result.get("method") or "unknown"
                    detected_number = result.get("number")
                    # Enhanced logging for specific frames of interest
                    if frame_index is not None and (frame_index == 1004 or frame_index == 1003):
                        logger.info(
                            " DETECTION FOR FRAME %d%s: number=%s color=%s method=%s confidence=%s",
                            frame_index,
                            frame_context,
                            detected_number,
                            result.get("color"),
                            detection_method,
                            result.get("confidence"),
                        )
                    else:
                        # Reduce logging frequency for performance - log at info level
                        logger.info(
                            "Detection succeeded%s: number=%s color=%s method=%s confidence=%s",
                            frame_context,
                            detected_number,
                            result.get("color"),
                            detection_method,
                            result.get("confidence"),
                        )
                else:
                    # Increment consecutive no-detection counter for adaptive delays
                    self.consecutive_no_detection += 1
                    
                    # Log more detail when no result is detected, especially for specific frames
                    if frame_index is not None and (frame_index == 1004 or frame_index == 1003):
                        logger.warning(f"No detection result{frame_context}; frame {frame_index} - will retry. "
                                     f"Frame captured: {frame is not None}")
                    else:
                        logger.debug(f"No detection result{frame_context}; will retry")
                
                # Detect game state (if enabled) - but in video mode, skip game state filtering
                game_state = None
                if self.game_state_detector and frame is not None and not is_video_mode:
                    game_state = self.game_state_detector.detect_state(frame, result)
                    logger.debug(f"Game state: {game_state.value}")
                
                # Only process result if game state allows (or if state detection disabled or in video mode)
                # In video mode, process all results immediately without game state filtering
                if result and (is_video_mode or not self.game_state_detector or 
                              self.game_state_detector.is_result_ready(game_state)):
                    # First, resolve any pending bet from previous spin
                    if self.pending_bet:
                        # Use stored spin_result if available, otherwise create minimal dict
                        spin_result_for_resolution = self.pending_bet.get('spin_result', {
                            'spin_number': self.pending_bet.get('spin_number', self.spin_number)
                        })
                        self.update_after_round(
                            spin_result_for_resolution,
                            result.get('number')
                        )
                        self.pending_bet = None
                    
                    # Process spin (detect result, calculate bet, place bet)
                    spin_result = self.process_spin(result)
                    
                    # Store pending bet if one was placed
                    if spin_result.get('bet_decision') and spin_result.get('bet_decision').get('bet_amount', 0) > 0:
                        # Store full spin_result for proper resolution later
                        self.pending_bet = {
                            'spin_number': self.spin_number,
                            'bet_type': spin_result.get('bet_decision').get('bet_type'),
                            'bet_amount': spin_result.get('bet_decision').get('bet_amount'),
                            'gale_step': self.strategy.gale_step,
                            'spin_result': spin_result  # Store full result for resolution
                        }
                    
                    # Mark this result as processed to prevent duplicates
                    if result:
                        result_signature = (result.get("number"), result.get("color"))
                        self.last_processed_result = result_signature
                        # Update tracking variables
                        self.last_result_signature = result_signature
                        self.last_result_time = time.time()
                        if frame_index is not None and frame_index >= 0:
                            self.last_result_frame_index = frame_index
                        logger.info(f"Spin {self.spin_number} processed: number={result.get('number')}, color={result.get('color')}")
                    
                    # Detection continues after processing spin with small delay
                    # The bot will detect new results as they appear
                    time.sleep(self.loop_delay_after_detection)
                elif result and self.game_state_detector:
                    # Result detected but state not ready (e.g., still spinning)
                    logger.debug(f"Result detected but game state not ready: {game_state.value if game_state else 'unknown'}")
                    # Add delay when waiting for game state
                    time.sleep(self.loop_delay_no_detection)
                else:
                    logger.debug("No result detected yet, will retry")
                    # Adaptive delay: increase delay when no detection for many consecutive frames
                    # This prevents 100% CPU usage when nothing is happening
                    adaptive_delay = self.loop_delay_no_detection
                    if self.consecutive_no_detection > 10:
                        # After 10 consecutive failures, increase delay to reduce CPU
                        adaptive_delay = min(self.loop_delay_no_detection * 2, 0.5)
                    elif self.consecutive_no_detection > 50:
                        # After 50 consecutive failures, further increase delay
                        adaptive_delay = min(self.loop_delay_no_detection * 5, 1.0)
                    time.sleep(adaptive_delay)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error in bot loop: {e}")
            self.logger.log_error({
                "error": str(e),
                "type": "bot_error",
                "context": {"spin_number": self.spin_number}
            })
            self._emit_event("error", {"message": str(e), "context": {"spin_number": self.spin_number}})
        finally:
            self.running = False
            logger.info("Bot stopped")
            self._emit_event("status_change", {"status": "idle"})
    
    def stop(self):
        """Stop the bot."""
        logger.info("Stopping bot...")
        self.running = False
        
        # Generate final statistics
        stats = self.logger.get_statistics()
        logger.info(f"Final statistics: {stats}")
        
        # Prepare stop trigger info if not already set (manual stop)
        if self.stop_trigger_info is None:
            self.stop_trigger_info = {
                "triggered": True,
                "type": "manual",
                "value": None,
                "threshold": None
            }
        
        # Export summary with stop trigger info
        self.logger.export_summary(stop_triggers=self.stop_trigger_info)
        self._emit_event("status_change", {"status": "idle"})

