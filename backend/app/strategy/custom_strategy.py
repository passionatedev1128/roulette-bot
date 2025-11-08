"""
Custom Strategy
User-defined betting sequence and rules.
"""

from typing import Dict, List, Optional
import logging
from .base_strategy import StrategyBase

logger = logging.getLogger(__name__)


class CustomStrategy(StrategyBase):
    """Custom betting strategy with user-defined sequence."""
    
    def __init__(self, config: Dict):
        """Initialize Custom strategy."""
        super().__init__(config)
        
        # Get custom sequence from config
        self.custom_sequence = config.get('custom_sequence', [10, 20, 40, 80, 160])
        self.sequence_index = 0
        self.bet_color_pattern = config.get('bet_color_pattern', 'opposite')  # 'opposite', 'same', 'alternate'
        
        logger.info(f"Custom strategy initialized: sequence={self.custom_sequence}")
    
    def calculate_bet(self, history: List[Dict], current_balance: float, last_result: Dict) -> Optional[Dict]:
        """
        Calculate custom strategy bet.
        
        Uses user-defined sequence for bet amounts.
        """
        if not history:
            bet_type = "red"
        else:
            last_color = last_result.get('color')
            
            # Determine bet color based on pattern
            if self.bet_color_pattern == 'opposite':
                if last_color == 'red':
                    bet_type = 'black'
                elif last_color == 'black':
                    bet_type = 'red'
                else:
                    bet_type = 'red'
            elif self.bet_color_pattern == 'same':
                bet_type = last_color if last_color != 'green' else 'red'
            else:  # alternate
                # Alternate between red and black
                if len(history) % 2 == 0:
                    bet_type = 'red'
                else:
                    bet_type = 'black'
        
        # Get bet amount from custom sequence
        if self.sequence_index < len(self.custom_sequence):
            bet_amount = self.custom_sequence[self.sequence_index]
        else:
            # Use last value in sequence
            bet_amount = self.custom_sequence[-1]
        
        # Check if we can place bet
        if not self.should_place_bet(current_balance, bet_amount):
            logger.warning(f"Insufficient funds: balance={current_balance}, bet={bet_amount}")
            return None
        
        # Check max gale limit
        if self.sequence_index >= self.max_gales:
            logger.warning("Maximum custom sequence reached")
            return None
        
        return {
            "bet_type": bet_type,
            "bet_amount": bet_amount,
            "strategy": "custom",
            "reason": f"Custom sequence step {self.sequence_index}, betting {bet_amount} on {bet_type}"
        }
    
    def update_after_bet(self, bet_result: Dict):
        """Update custom sequence index after bet."""
        super().update_after_bet(bet_result)
        
        if bet_result.get('result') == 'loss':
            # Move forward in sequence
            self.sequence_index = min(self.sequence_index + 1, len(self.custom_sequence) - 1)
        else:
            # Reset to start after win
            self.sequence_index = 0
        
        logger.debug(f"Custom sequence index updated: {self.sequence_index}")
    
    def handle_zero(self, history: List[Dict], current_balance: float) -> Dict:
        """Handle zero result in Custom strategy."""
        zero_rule = self.zero_handling.get('rule', 'continue_sequence')
        
        if zero_rule == 'continue_sequence':
            logger.info("Zero detected: continuing custom sequence")
            self.sequence_index = min(self.sequence_index + 1, len(self.custom_sequence) - 1)
            return {
                "action": "continue",
                "sequence_index": self.sequence_index
            }
        elif zero_rule == 'reset':
            logger.info("Zero detected: resetting custom sequence")
            self.sequence_index = 0
            return {
                "action": "reset",
                "sequence_index": 0
            }
        else:
            logger.info("Zero detected: skipping bet")
            return {
                "action": "skip",
                "sequence_index": self.sequence_index
            }

