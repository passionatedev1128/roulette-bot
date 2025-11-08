"""
Martingale Strategy
Doubles bet after each loss, resets to base bet after win.
"""

from typing import Dict, List, Optional
import logging
from .base_strategy import StrategyBase

logger = logging.getLogger(__name__)


class MartingaleStrategy(StrategyBase):
    """Martingale betting strategy."""
    
    def __init__(self, config: Dict):
        """Initialize Martingale strategy."""
        super().__init__(config)
        self.multiplier = config.get('multiplier', 2.0)  # Default: double after loss
        
        logger.info(f"Martingale strategy initialized: base_bet={self.base_bet}, multiplier={self.multiplier}")
    
    def calculate_bet(self, history: List[Dict], current_balance: float, last_result: Dict) -> Optional[Dict]:
        """
        Calculate Martingale bet.
        
        Strategy:
        - After loss: bet = previous_bet * multiplier
        - After win: bet = base_bet
        - Bet on opposite color of last result
        """
        if not history:
            # First bet - bet on red (or configure default)
            bet_type = "red"
            bet_amount = self.base_bet
        else:
            last_color = last_result.get('color')
            
            # Bet on opposite color
            if last_color == 'red':
                bet_type = 'black'
            elif last_color == 'black':
                bet_type = 'red'
            else:  # green/zero
                # Default to red after zero
                bet_type = 'red'
            
            # Calculate bet amount based on gale progression
            bet_amount = self.get_bet_amount()
        
        # Check if we can place bet
        if not self.should_place_bet(current_balance, bet_amount):
            logger.warning(f"Insufficient funds: balance={current_balance}, bet={bet_amount}")
            return None
        
        # Check max gale limit
        if self.is_gale_max_reached():
            logger.warning("Maximum gale steps reached")
            return None
        
        return {
            "bet_type": bet_type,
            "bet_amount": bet_amount,
            "strategy": "martingale",
            "reason": f"Martingale step {self.gale_step}, betting {bet_type} after {self.consecutive_losses} losses"
        }
    
    def get_bet_amount(self) -> float:
        """
        Calculate bet amount based on Martingale progression.
        
        Returns:
            Bet amount
        """
        if self.gale_step == 0:
            return self.base_bet
        
        # Calculate: base_bet * (multiplier ^ gale_step)
        bet_amount = self.base_bet * (self.multiplier ** self.gale_step)
        return bet_amount
    
    def handle_zero(self, history: List[Dict], current_balance: float) -> Dict:
        """
        Handle zero result in Martingale strategy.
        
        Options:
        - Continue sequence (treat as loss)
        - Reset to base bet
        - Skip bet
        """
        zero_rule = self.zero_handling.get('rule', 'continue_sequence')
        
        if zero_rule == 'continue_sequence':
            # Treat zero as loss, continue gale
            logger.info("Zero detected: continuing Martingale sequence (treating as loss)")
            return {
                "action": "continue",
                "gale_step": self.gale_step + 1,
                "consecutive_losses": self.consecutive_losses + 1
            }
        elif zero_rule == 'reset':
            # Reset to base bet
            logger.info("Zero detected: resetting Martingale to base bet")
            self.reset_gale()
            return {
                "action": "reset",
                "gale_step": 0,
                "consecutive_losses": 0
            }
        else:  # skip
            # Skip this bet
            logger.info("Zero detected: skipping bet")
            return {
                "action": "skip",
                "gale_step": self.gale_step,
                "consecutive_losses": self.consecutive_losses
            }

