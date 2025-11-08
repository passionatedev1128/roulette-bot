"""
Base Strategy Class
All betting strategies inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class StrategyBase(ABC):
    """Abstract base class for all betting strategies."""
    
    def __init__(self, config: Dict):
        """
        Initialize strategy.
        
        Args:
            config: Strategy configuration dictionary
        """
        self.config = config
        self.strategy_type = config.get('type', 'unknown')
        self.base_bet = config.get('base_bet', 10.0)
        self.max_gales = config.get('max_gales', 5)
        self.zero_handling = config.get('zero_handling', {})
        
        # Betting history
        self.bet_history: List[Dict] = []
        self.current_balance = config.get('initial_balance', 1000.0)
        self.gale_step = 0
        self.consecutive_losses = 0
        
        logger.info(f"Strategy {self.strategy_type} initialized")
    
    @abstractmethod
    def calculate_bet(self, history: List[Dict], current_balance: float, last_result: Dict) -> Optional[Dict]:
        """
        Calculate next bet based on strategy.
        
        Args:
            history: List of previous results
            current_balance: Current account balance
            last_result: Last roulette result
            
        Returns:
            Bet decision dictionary:
            {
                "bet_type": str ("red", "black", "green", "number"),
                "bet_amount": float,
                "strategy": str,
                "reason": str
            }
            or None if no bet should be placed
        """
        pass
    
    @abstractmethod
    def handle_zero(self, history: List[Dict], current_balance: float) -> Dict:
        """
        Handle zero (0) result according to strategy rules.
        
        Args:
            history: List of previous results
            current_balance: Current account balance
            
        Returns:
            Updated strategy state or bet decision
        """
        pass
    
    def should_place_bet(self, current_balance: float, bet_amount: float) -> bool:
        """
        Check if bet should be placed (sufficient funds).
        
        Args:
            current_balance: Current balance
            bet_amount: Proposed bet amount
            
        Returns:
            True if bet can be placed
        """
        return current_balance >= bet_amount
    
    def update_after_bet(self, bet_result: Dict):
        """
        Update strategy state after bet is resolved.
        
        Args:
            bet_result: Result of bet (win/loss)
        """
        self.current_balance = bet_result.get('balance_after', self.current_balance)
        
        if bet_result.get('result') == 'loss':
            self.consecutive_losses += 1
            self.gale_step += 1
        else:
            self.consecutive_losses = 0
            self.gale_step = 0
        
        self.bet_history.append(bet_result)
        logger.debug(f"Strategy updated: balance={self.current_balance}, losses={self.consecutive_losses}, gale_step={self.gale_step}")
    
    def get_bet_amount(self) -> float:
        """
        Get current bet amount based on gale progression.
        
        Returns:
            Bet amount
        """
        return self.base_bet
    
    def reset_gale(self):
        """Reset gale progression."""
        self.gale_step = 0
        self.consecutive_losses = 0
        logger.info("Gale progression reset")
    
    def is_gale_max_reached(self) -> bool:
        """
        Check if maximum gale steps reached.
        
        Returns:
            True if max gale reached
        """
        return self.gale_step >= self.max_gales
    
    def get_strategy_info(self) -> Dict:
        """
        Get current strategy state information.
        
        Returns:
            Dictionary with strategy information
        """
        return {
            "type": self.strategy_type,
            "base_bet": self.base_bet,
            "current_balance": self.current_balance,
            "gale_step": self.gale_step,
            "consecutive_losses": self.consecutive_losses,
            "max_gales": self.max_gales
        }

