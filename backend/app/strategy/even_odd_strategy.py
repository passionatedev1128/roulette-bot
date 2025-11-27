"""
Even/Odd Counter-Sequence Strategy
Bets against streaks of Even or Odd outcomes.
Only enters when streak length N is reached.
"""

from typing import Dict, List, Optional, Tuple
import logging
import random
from .base_strategy import StrategyBase

logger = logging.getLogger(__name__)


class EvenOddStrategy(StrategyBase):
    """
    Even/Odd counter-sequence strategy.
    
    Strategy:
    - Monitors Even/Odd outcomes
    - Detects streaks (consecutive Even or Odd)
    - Enters when streak length N is reached
    - Bets against the streak (counter-sequence)
    - Applies Gale progression on losses
    """
    
    # Even numbers: 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36
    EVEN_NUMBERS = {2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36}
    # Odd numbers: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35
    ODD_NUMBERS = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35}
    
    def __init__(self, config: Dict):
        """Initialize Even/Odd strategy."""
        super().__init__(config)
        self.multiplier = config.get('multiplier', 2.0)  # Default: double after loss
        
        # Streak detection configuration
        self.streak_length = config.get('streak_length', 5)  # N consecutive to trigger entry
        
        # Zero handling policy
        self.zero_policy = config.get('zero_policy', 'count_as_loss')  # count_as_loss, neutral, reset
        
        # Streak tracking
        self.current_even_streak = 0
        self.current_odd_streak = 0
        self.last_even_odd = None  # 'even', 'odd', or None
        
        # Cycle management
        self.cycle_active = False  # True when in an active betting cycle
        self.cycle_number = 0
        
        # Keepalive configuration
        self.keepalive_stake = config.get('keepalive_stake', 1.0)
        
        logger.info(
            f"Even/Odd strategy initialized: "
            f"base_bet={self.base_bet}, streak_length={self.streak_length}, "
            f"max_gales={self.max_gales}, zero_policy={self.zero_policy}"
        )
    
    def _get_even_odd(self, number: int) -> Optional[str]:
        """
        Determine if number is Even, Odd, or Zero.
        
        Args:
            number: Roulette number (0-36)
            
        Returns:
            'even', 'odd', or None (for zero)
        """
        if number == 0:
            return None
        elif number in self.EVEN_NUMBERS:
            return 'even'
        elif number in self.ODD_NUMBERS:
            return 'odd'
        else:
            logger.warning(f"Unknown number: {number}")
            return None
    
    def _update_streaks(self, even_odd: Optional[str]):
        """
        Update streak counters based on outcome.
        
        Args:
            even_odd: 'even', 'odd', or None (zero)
        """
        if even_odd is None:  # Zero
            if self.zero_policy == 'reset':
                # Reset streaks on zero
                self.current_even_streak = 0
                self.current_odd_streak = 0
                self.last_even_odd = None
                logger.info("Zero detected: streaks reset")
            elif self.zero_policy == 'neutral':
                # Ignore zero for streak counting
                logger.info("Zero detected: ignored for streak counting")
                return
            # else: count_as_loss - handled in cycle logic, but don't update streaks
            return
        
        if even_odd == 'even':
            self.current_even_streak += 1
            self.current_odd_streak = 0  # Reset opposite streak
            self.last_even_odd = 'even'
        elif even_odd == 'odd':
            self.current_odd_streak += 1
            self.current_even_streak = 0  # Reset opposite streak
            self.last_even_odd = 'odd'
        
        logger.debug(
            f"Streaks updated: Even={self.current_even_streak}, "
            f"Odd={self.current_odd_streak}"
        )
    
    def _check_entry_condition(self) -> Optional[Tuple[str, str]]:
        """
        Check if entry condition is met (streak length reached).
        
        Returns:
            Tuple of (bet_type, streak_type) if entry condition met, else None
            bet_type: 'even' or 'odd'
            streak_type: 'even' or 'odd' (the streak that triggered entry)
        """
        # Check if we're already in a cycle
        if self.cycle_active:
            return None
        
        # Check Even streak
        if self.current_even_streak >= self.streak_length:
            logger.info(
                f"Entry condition met: {self.current_even_streak} consecutive Even  "
                f"Betting Odd"
            )
            return ('odd', 'even')
        
        # Check Odd streak
        if self.current_odd_streak >= self.streak_length:
            logger.info(
                f"Entry condition met: {self.current_odd_streak} consecutive Odd  "
                f"Betting Even"
            )
            return ('even', 'odd')
        
        return None
    
    def calculate_bet(self, history: List[Dict], current_balance: float, last_result: Dict) -> Optional[Dict]:
        """
        Calculate Even/Odd bet based on streak detection.
        
        Strategy:
        - If in active cycle: Continue gale progression
        - If not in cycle: Check for entry condition (streak N)
        - Bet against the streak (counter-sequence)
        
        Args:
            history: List of previous results
            current_balance: Current account balance
            last_result: Last roulette result
            
        Returns:
            Bet decision dictionary or None
        """
        number = last_result.get('number')
        if number is None:
            return None
        
        even_odd = self._get_even_odd(number)
        
        # Update streaks (unless zero with neutral policy)
        if not (even_odd is None and self.zero_policy == 'neutral'):
            self._update_streaks(even_odd)
        
        # If in active cycle, continue gale progression
        if self.cycle_active:
            # Get the bet type from the cycle (stored in strategy state)
            # For now, we'll determine it from the last bet or streak
            # In a full implementation, we'd store the cycle bet type
            
            # Calculate bet amount based on gale progression
            bet_amount = self.get_bet_amount()
            
            # Determine bet type: opposite of the streak that started the cycle
            # We need to track which streak triggered the cycle
            # For now, use a simple approach: bet opposite of last outcome
            if self.last_even_odd == 'even':
                bet_type = 'odd'
            elif self.last_even_odd == 'odd':
                bet_type = 'even'
            else:
                # Fallback: random (shouldn't happen in normal operation)
                bet_type = random.choice(['even', 'odd'])
                logger.warning("Using fallback bet type in cycle")
            
            # Check if we can place bet
            if not self.should_place_bet(current_balance, bet_amount):
                logger.warning(f"Insufficient funds: balance={current_balance}, bet={bet_amount}")
                return None
            
            # Check max gale limit
            if self.is_gale_max_reached():
                logger.warning("Maximum gale steps reached - ending cycle")
                self.cycle_active = False
                return None
            
            # Get current streak length for chip selection
            current_streak = max(self.current_even_streak, self.current_odd_streak)
            
            return {
                "bet_type": bet_type,
                "bet_amount": bet_amount,
                "strategy": "even_odd",
                "reason": f"Gale step {self.gale_step} in cycle {self.cycle_number}, "
                         f"betting {bet_type} after {self.consecutive_losses} losses",
                "cycle_number": self.cycle_number,
                "gale_step": self.gale_step,
                "streak_length": current_streak,  # Include for chip selection
                "is_keepalive": False
            }
        
        # Not in cycle - check for entry condition
        entry = self._check_entry_condition()
        if entry is None:
            # No entry condition met - don't bet
            return None
        
        bet_type, streak_type = entry
        
        # Start new cycle
        self.cycle_active = True
        self.cycle_number += 1
        self.gale_step = 0
        self.consecutive_losses = 0
        
        bet_amount = self.get_bet_amount()
        
        # Check if we can place bet
        if not self.should_place_bet(current_balance, bet_amount):
            logger.warning(f"Insufficient funds: balance={current_balance}, bet={bet_amount}")
            self.cycle_active = False  # Don't start cycle if can't bet
            return None
        
        logger.info(
            f"Starting cycle {self.cycle_number}: "
            f"Betting {bet_type} against {streak_type} streak "
            f"(streak length: {getattr(self, f'current_{streak_type}_streak')})"
        )
        
        return {
            "bet_type": bet_type,
            "bet_amount": bet_amount,
            "strategy": "even_odd",
            "reason": f"Entry triggered: {getattr(self, f'current_{streak_type}_streak')} "
                     f"consecutive {streak_type}  betting {bet_type}",
            "cycle_number": self.cycle_number,
            "gale_step": 0,
            "is_keepalive": False,
            "streak_type": streak_type,
            "streak_length": getattr(self, f'current_{streak_type}_streak')
        }
    
    def get_bet_amount(self) -> float:
        """
        Calculate bet amount based on Gale progression.
        
        Returns:
            Bet amount
        """
        if self.gale_step == 0:
            return self.base_bet
        
        # Calculate: base_bet * (multiplier ^ gale_step)
        bet_amount = self.base_bet * (self.multiplier ** self.gale_step)
        return bet_amount
    
    def update_after_bet(self, bet_result: Dict):
        """
        Update strategy state after bet is resolved.
        
        Args:
            bet_result: Result of bet (win/loss)
        """
        super().update_after_bet(bet_result)
        
        result = bet_result.get('result')
        
        if result == 'win':
            # Cycle ends successfully
            self.cycle_active = False
            logger.info(f"Cycle {self.cycle_number} ended with win")
        elif result == 'loss':
            # Continue cycle with gale progression
            if self.gale_step >= self.max_gales:
                # Max gale reached - cycle ends
                self.cycle_active = False
                logger.info(f"Cycle {self.cycle_number} ended: max gale reached")
            else:
                logger.debug(f"Cycle {self.cycle_number} continuing: gale step {self.gale_step}")
    
    def handle_zero(self, history: List[Dict], current_balance: float) -> Dict:
        """
        Handle zero (0) result according to zero policy.
        
        Args:
            history: List of previous results
            current_balance: Current balance
            
        Returns:
            Action dictionary
        """
        if self.zero_policy == 'count_as_loss':
            # Treat zero as loss, continue cycle if active
            logger.info("Zero detected: counting as loss, continuing cycle")
            if self.cycle_active:
                return {
                    "action": "continue",
                    "gale_step": self.gale_step + 1,
                    "consecutive_losses": self.consecutive_losses + 1
                }
            else:
                return {
                    "action": "ignore",
                    "gale_step": self.gale_step,
                    "consecutive_losses": self.consecutive_losses
                }
        elif self.zero_policy == 'neutral':
            # Ignore zero - don't affect cycle or streaks
            logger.info("Zero detected: treating as neutral (ignored)")
            return {
                "action": "ignore",
                "gale_step": self.gale_step,
                "consecutive_losses": self.consecutive_losses
            }
        elif self.zero_policy == 'reset':
            # Reset streaks (already handled in _update_streaks)
            logger.info("Zero detected: resetting streaks")
            if self.cycle_active:
                # End current cycle
                self.cycle_active = False
                self.reset_gale()
            return {
                "action": "reset",
                "gale_step": 0,
                "consecutive_losses": 0
            }
        else:
            # Default: count as loss
            logger.warning(f"Unknown zero policy: {self.zero_policy}, defaulting to count_as_loss")
            return {
                "action": "continue",
                "gale_step": self.gale_step + 1,
                "consecutive_losses": self.consecutive_losses + 1
            }
    
    def get_keepalive_bet(self) -> Optional[Dict]:
        """
        Generate a keepalive bet (random Even or Odd).
        
        Returns:
            Keepalive bet decision or None if cycle is active
        """
        # Don't place keepalive if cycle is active
        if self.cycle_active:
            logger.debug("Skipping keepalive: cycle is active")
            return None
        
        # Random pick: Even or Odd
        bet_type = random.choice(['even', 'odd'])
        
        logger.info(f"Keepalive bet: {bet_type} with stake {self.keepalive_stake}")
        
        return {
            "bet_type": bet_type,
            "bet_amount": self.keepalive_stake,
            "strategy": "even_odd",
            "reason": "Keepalive bet to prevent session pause",
            "is_keepalive": True,
            "cycle_number": None,
            "gale_step": None
        }
    
    def get_strategy_info(self) -> Dict:
        """
        Get current strategy state information.
        
        Returns:
            Dictionary with strategy information
        """
        info = super().get_strategy_info()
        info.update({
            "streak_length": self.streak_length,
            "current_even_streak": self.current_even_streak,
            "current_odd_streak": self.current_odd_streak,
            "cycle_active": self.cycle_active,
            "cycle_number": self.cycle_number,
            "zero_policy": self.zero_policy
        })
        return info

