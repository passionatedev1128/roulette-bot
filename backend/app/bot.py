"""
Main Bot Orchestrator
Coordinates all modules to run the roulette bot.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional
from pathlib import Path

from .detection import ScreenDetector
from .detection.game_state_detector import GameStateDetector, GameState
from .strategy import StrategyBase, MartingaleStrategy, FibonacciStrategy, CustomStrategy, EvenOddStrategy
from .strategy.strategy_manager import StrategyManager
from .betting import BetController
from .logging import RouletteLogger
from .config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class RouletteBot:
    """Main bot orchestrator."""
    
    def __init__(
        self,
        config_path: str,
        event_dispatcher: Optional[object] = None,
        state_callback: Optional[Callable[[str, Dict], None]] = None,
        test_mode: bool = False,
    ):
        """
        Initialize roulette bot.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = ConfigLoader.load_config(config_path)
        
        # Initialize modules
        self.detector = ScreenDetector(self.config)
        
        # Use StrategyManager if navigation is enabled, otherwise use single strategy
        strategy_nav_config = self.config.get('strategy_navigation', {})
        if strategy_nav_config.get('enabled', False):
            self.strategy_manager = StrategyManager(self.config)
            self.strategy = self.strategy_manager.get_current_strategy()
            logger.info("Strategy navigation enabled - using StrategyManager")
        else:
            self.strategy = self._create_strategy()
            self.strategy_manager = None
            logger.info("Strategy navigation disabled - using single strategy")
        
        self.bet_controller = BetController(self.config)
        self.logger = RouletteLogger(self.config)
        
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
        
        # Stop conditions tracking
        self.winning_rounds = 0
        self.losing_rounds = 0
        
        # Events / callbacks
        self.event_dispatcher = event_dispatcher
        self.state_callback = state_callback
        self.test_mode = test_mode

        # Setup logging
        self._setup_logging()
        
        logger.info("RouletteBot initialized")
        if self.test_mode:
            logger.info("RouletteBot running in test mode")

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
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot.log'),
                logging.StreamHandler()
            ]
        )
    
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
    
    def detect_result(self) -> Optional[Dict]:
        """
        Detect current roulette result.
        
        Returns:
            Detection result or None if failed
        """
        try:
            result = self.detector.detect_result()
            
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
                    logger.info(f"Keepalive bet placed: {keepalive_bet['bet_amount']} on {keepalive_bet['bet_type']}")
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
        
        # Calculate bet (use strategy manager if enabled)
        if self.strategy_manager:
            bet_decision = self.strategy_manager.calculate_bet(
                self.result_history,
                self.current_balance,
                result
            )
            # Update current strategy reference
            self.strategy = self.strategy_manager.get_current_strategy()
        else:
            bet_decision = self.strategy.calculate_bet(
                self.result_history,
                self.current_balance,
                result
            )
        
        # Place bet if decision made
        bet_result = None
        if bet_decision:
            # Extract streak and gale info for adaptive chip selection
            streak_length = bet_decision.get('streak_length')
            gale_step = bet_decision.get('gale_step', self.strategy.gale_step)
            
            bet_result = self.bet_controller.place_bet(
                bet_decision['bet_type'],
                bet_decision['bet_amount'],
                streak_length=streak_length,
                gale_step=gale_step
            )
            
            if bet_result['success']:
                logger.info(f"Bet placed: {bet_decision['bet_type']} - {bet_decision['bet_amount']}")
                self._emit_event("bet_placed", {
                    "bet_type": bet_decision['bet_type'],
                    "bet_amount": bet_decision['bet_amount'],
                    "gale_step": self.strategy.gale_step,
                    "spin_number": self.spin_number,
                })
            else:
                logger.warning(f"Bet placement failed: {bet_result.get('error')}")
                self._emit_event("error", {
                    "message": bet_result.get('error', 'Bet placement failed'),
                    "context": {"spin_number": self.spin_number}
                })
        else:
            logger.info("No bet decision made")
        
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
        
        spin_data = {
            "spin_number": self.spin_number,
            "outcome_number": result.get('number'),
            "outcome_color": result.get('color'),
            "bet_category": bet_category,
            "bet_color": bet_color,
            "bet_amount": bet_decision.get('bet_amount') if bet_decision else 0.0,
            "balance_before": self.current_balance,
            "balance_after": self.current_balance,  # Will be updated after round
            "result": "pending",  # Will be updated after round completes
            "profit_loss": 0.0,
            "strategy": self.strategy.strategy_type,
            "gale_step": self.strategy.gale_step,
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
            spin_result: Result from process_spin
            result_number: The winning number (0-36). If None, uses spin_result data.
        """
        bet_amount = spin_result['spin_data'].get('bet_amount', 0.0)
        bet_type = spin_result['spin_data'].get('bet_color') or spin_result.get('bet_decision', {}).get('bet_type')
        
        # Get result number
        if result_number is None:
            result_number = spin_result.get('result', {}).get('number')
            if result_number is None:
                result_number = spin_result['spin_data'].get('outcome_number')
        
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
        # Update strategy (use strategy manager if enabled)
        bet_result_data = {
            "result": result,
            "balance_after": self.current_balance,
            "profit_loss": profit,
            "bet_amount": bet_amount,
            "cycle_ended": False  # Can be set based on strategy state
        }
        
        if self.strategy_manager:
            self.strategy_manager.update_after_bet(bet_result_data)
            # Update current strategy reference
            self.strategy = self.strategy_manager.get_current_strategy()
        else:
            self.strategy.update_after_bet(bet_result_data)
        
        # Reset bet controller
        self.bet_controller.reset_bet_flag()
        
        # Update spin data in log (would need to modify logger to support this)
        logger.info(f"Round completed: {result}, Balance: {self.current_balance}, Bet: {bet_type}, Result: {result_number}")

        self._emit_event("bet_resolved", {
            "spin_number": spin_result['spin_number'],
            "bet_type": bet_type,
            "bet_amount": spin_result['spin_data'].get('bet_amount', 0.0),
            "result": result,
            "result_number": result_number,
            "profit_loss": profit,
            "balance": self.current_balance,
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
            return True
        
        # StopLoss by count
        stop_loss_count = risk_config.get('stop_loss_count', None)
        if stop_loss_count is not None and self.losing_rounds >= stop_loss_count:
            logger.warning(f"StopLoss (count) reached: losing_rounds={self.losing_rounds}, threshold={stop_loss_count}")
            return True
        
        # StopWin by money
        stop_win_money = risk_config.get('stop_win', None)
        if stop_win_money is not None:
            net_pnl = self.current_balance - self.initial_balance
            if net_pnl >= stop_win_money:
                logger.warning(f"StopWin (money) reached: net_pnl={net_pnl}, stop_win={stop_win_money}")
                return True
        
        # StopWin by count
        stop_win_count = risk_config.get('stop_win_count', None)
        if stop_win_count is not None and self.winning_rounds >= stop_win_count:
            logger.warning(f"StopWin (count) reached: winning_rounds={self.winning_rounds}, threshold={stop_win_count}")
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

        self._emit_event("status_change", {"status": "running"})
        
        try:
            while self.running:
                # Check stop conditions
                if self.check_stop_conditions():
                    logger.warning("Stop conditions met, shutting down")
                    break
                
                # Check maintenance bet
                if self.check_maintenance_bet():
                    self.place_maintenance_bet()
                
                # Capture frame for game state detection (if enabled)
                frame = None
                if self.game_state_detector:
                    try:
                        frame = self.detector.capture_screen()
                    except Exception as e:
                        logger.debug(f"Failed to capture frame for state detection: {e}")
                
                # Detect result
                result = self.detect_result()
                
                # Detect game state (if enabled)
                game_state = None
                if self.game_state_detector and frame is not None:
                    game_state = self.game_state_detector.detect_state(frame, result)
                    logger.debug(f"Game state: {game_state.value}")
                
                # Only process result if game state allows (or if state detection disabled)
                if result and (not self.game_state_detector or 
                              self.game_state_detector.is_result_ready(game_state)):
                    # Process spin
                    spin_result = self.process_spin(result)
                    
                    # Wait for round to complete
                    # In real implementation, this would wait for next spin indicator
                    time.sleep(30)  # Placeholder - adjust based on game timing
                elif result and self.game_state_detector:
                    # Result detected but state not ready (e.g., still spinning)
                    logger.debug(f"Result detected but game state not ready: {game_state.value if game_state else 'unknown'}")
                    time.sleep(1)
                else:
                    logger.warning("Failed to detect result, retrying...")
                    time.sleep(5)
                
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
        
        # Export summary
        self.logger.export_summary()
        self._emit_event("status_change", {"status": "idle"})

