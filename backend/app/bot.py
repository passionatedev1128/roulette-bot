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
from .strategy import StrategyBase, MartingaleStrategy, FibonacciStrategy, CustomStrategy
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
        self.strategy = self._create_strategy()
        self.bet_controller = BetController(self.config)
        self.logger = RouletteLogger(self.config)
        
        # Bot state
        self.running = False
        self.spin_number = 0
        self.result_history: List[Dict] = []
        self.current_balance = self.config.get('risk', {}).get('initial_balance', 1000.0)
        self.last_maintenance_bet_time = time.time()
        
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
        interval = self.config.get('session', {}).get('maintenance_bet_interval', 1800)  # 30 minutes
        elapsed = time.time() - self.last_maintenance_bet_time
        
        return elapsed >= interval
    
    def place_maintenance_bet(self):
        """Place maintenance bet to keep session active."""
        try:
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
        
        # Calculate bet
        bet_decision = self.strategy.calculate_bet(
            self.result_history,
            self.current_balance,
            result
        )
        
        # Place bet if decision made
        bet_result = None
        if bet_decision:
            bet_result = self.bet_controller.place_bet(
                bet_decision['bet_type'],
                bet_decision['bet_amount']
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
        spin_data = {
            "spin_number": self.spin_number,
            "outcome_number": result.get('number'),
            "outcome_color": result.get('color'),
            "bet_type": bet_decision.get('bet_type') if bet_decision else None,
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
    
    def update_after_round(self, spin_result: Dict, won: bool):
        """
        Update bot state after round completes.
        
        Args:
            spin_result: Result from process_spin
            won: True if bet won, False if lost
        """
        bet_amount = spin_result['spin_data'].get('bet_amount', 0.0)
        
        if won:
            profit = bet_amount  # Assuming 1:1 payout
            self.current_balance += profit
            result = "win"
        else:
            profit = -bet_amount
            self.current_balance -= bet_amount
            result = "loss"
        
        # Update strategy
        self.strategy.update_after_bet({
            "result": result,
            "balance_after": self.current_balance,
            "profit_loss": profit
        })
        
        # Reset bet controller
        self.bet_controller.reset_bet_flag()
        
        # Update spin data in log (would need to modify logger to support this)
        logger.info(f"Round completed: {result}, Balance: {self.current_balance}")

        self._emit_event("bet_resolved", {
            "spin_number": spin_result['spin_number'],
            "bet_type": spin_result['spin_data'].get('bet_type'),
            "bet_amount": spin_result['spin_data'].get('bet_amount', 0.0),
            "result": result,
            "profit_loss": profit,
            "balance": self.current_balance,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self._emit_event("balance_update", {"balance": self.current_balance})
    
    def check_stop_conditions(self) -> bool:
        """
        Check if bot should stop.
        
        Returns:
            True if should stop, False otherwise
        """
        stop_loss = self.config.get('risk', {}).get('stop_loss', 0.0)
        
        if self.current_balance <= stop_loss:
            logger.warning(f"Stop loss reached: balance={self.current_balance}, stop_loss={stop_loss}")
            return True
        
        if self.strategy.is_gale_max_reached():
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
                
                # Detect result
                result = self.detect_result()
                
                if result:
                    # Process spin
                    spin_result = self.process_spin(result)
                    
                    # Wait for round to complete
                    # In real implementation, this would wait for next spin indicator
                    time.sleep(30)  # Placeholder - adjust based on game timing
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

