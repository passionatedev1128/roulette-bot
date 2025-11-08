"""
Fibonacci Strategy
Uses Fibonacci sequence for bet progression: 1, 1, 2, 3, 5, 8, 13, 21...
"""

from typing import Dict, List, Optional
import logging
from .base_strategy import StrategyBase

logger = logging.getLogger(__name__)


class FibonacciStrategy(StrategyBase):
    """Fibonacci betting strategy."""
    
    def __init__(self, config: Dict):
        """Initialize Fibonacci strategy."""
        super().__init__(config)
        self.fibonacci_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        self.sequence_index = 0
        
        logger.info(f"Fibonacci strategy initialized: base_bet={self.base_bet}")
    
    def get_fibonacci_value(self, index: int) -> int:
        """
        Get Fibonacci value at index.
        
        Args:
            index: Sequence index
            
        Returns:
            Fibonacci number
        """
        if index < len(self.fibonacci_sequence):
            return self.fibonacci_sequence[index]
        else:
            # Generate if beyond sequence
            a, b = self.fibonacci_sequence[-2], self.fibonacci_sequence[-1]
            for _ in range(index - len(self.fibonacci_sequence) + 1):
                a, b = b, a + b
            return b
    
    def calculate_bet(self, history: List[Dict], current_balance: float, last_result: Dict) -> Optional[Dict]:
        """
        Calculate Fibonacci bet.
        
        Strategy:
        - After loss: move forward in Fibonacci sequence
        - After win: move back 2 steps in sequence
        """
        if not history:
            bet_type = "red"
            fib_value = self.fibonacci_sequence[0]
            bet_amount = self.base_bet * fib_value
        else:
            last_color = last_result.get('color')
            
            # Bet on opposite color
            if last_color == 'red':
                bet_type = 'black'
            elif last_color == 'black':
                bet_type = 'red'
            else:
                bet_type = 'red'
            
            # Use Fibonacci value for bet amount
            fib_value = self.get_fibonacci_value(self.sequence_index)
            bet_amount = self.base_bet * fib_value
        
        # Check if we can place bet
        if not self.should_place_bet(current_balance, bet_amount):
            logger.warning(f"Insufficient funds: balance={current_balance}, bet={bet_amount}")
            return None
        
        # Check max gale limit
        if self.sequence_index >= self.max_gales:
            logger.warning("Maximum Fibonacci sequence reached")
            return None
        
        return {
            "bet_type": bet_type,
            "bet_amount": bet_amount,
            "strategy": "fibonacci",
            "reason": f"Fibonacci step {self.sequence_index}, value={fib_value}, betting {bet_type}"
        }
    
    def update_after_bet(self, bet_result: Dict):
        """Update Fibonacci sequence index after bet."""
        super().update_after_bet(bet_result)
        
        if bet_result.get('result') == 'loss':
            # Move forward in sequence
            self.sequence_index = min(self.sequence_index + 1, len(self.fibonacci_sequence) - 1)
        else:
            # Move back 2 steps after win
            self.sequence_index = max(0, self.sequence_index - 2)
        
        logger.debug(f"Fibonacci index updated: {self.sequence_index}")
    
    def handle_zero(self, history: List[Dict], current_balance: float) -> Dict:
        """Handle zero result in Fibonacci strategy."""
        zero_rule = self.zero_handling.get('rule', 'continue_sequence')
        
        if zero_rule == 'continue_sequence':
            # Treat zero as loss, advance sequence
            logger.info("Zero detected: continuing Fibonacci sequence")
            self.sequence_index = min(self.sequence_index + 1, len(self.fibonacci_sequence) - 1)
            return {
                "action": "continue",
                "sequence_index": self.sequence_index
            }
        elif zero_rule == 'reset':
            logger.info("Zero detected: resetting Fibonacci sequence")
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

