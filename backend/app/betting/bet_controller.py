"""
Action/Automation Module
Places bets using mouse automation (pyautogui).
"""

import pyautogui
import time
import random
import logging
from typing import Dict, Optional, Tuple
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class BetController:
    """Handles automated betting using mouse clicks."""
    
    def __init__(self, config: Dict):
        """
        Initialize bet controller.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.betting_config = config.get('betting', {})
        self.betting_areas = self.betting_config.get('betting_areas', {})
        self.human_delays = self.betting_config.get('human_delays', {'min': 0.1, 'max': 0.5})
        
        # Adaptive chip selection
        self.adaptive_chip_selection = self.betting_config.get('adaptive_chip_selection', False)
        self.chip_sizes = self.betting_config.get('chip_sizes', [0.5, 1.0, 2.5, 5.0, 10.0])
        self.chip_rules = self.betting_config.get('chip_selection_rules', {})
        self.chip_coords = self.betting_config.get('chip_selection_coordinates', {})
        
        # State tracking
        self.last_bet_time = None
        self.bet_placed_flag = False
        self.last_bet_details = None
        
        # Safety settings
        pyautogui.PAUSE = 0.1  # Small pause between actions
        pyautogui.FAILSAFE = True  # Enable failsafe (move mouse to corner to stop)
        
        logger.info("BetController initialized")
        if self.adaptive_chip_selection:
            logger.info("Adaptive chip selection enabled")
    
    def _random_delay(self):
        """Add random human-like delay."""
        delay = random.uniform(
            self.human_delays.get('min', 0.1),
            self.human_delays.get('max', 0.5)
        )
        time.sleep(delay)
    
    def find_betting_area(self, bet_type: str) -> Optional[Tuple[int, int]]:
        """
        Find betting area coordinates for bet type.
        
        Args:
            bet_type: 'red', 'black', 'green', 'even', 'odd', or 'number'
            
        Returns:
            Tuple of (x, y) coordinates or None
        """
        if bet_type in self.betting_areas:
            coords = self.betting_areas[bet_type]
            if isinstance(coords, list) and len(coords) >= 2:
                return (coords[0], coords[1])
        
        logger.warning(f"Betting area not found for {bet_type}")
        return None
    
    def check_existing_bet(self) -> bool:
        """
        Check if a bet is already placed.
        
        Uses screen detection to check for existing bet indicators.
        
        Returns:
            True if bet exists, False otherwise
        """
        try:
            # Capture screen area where bet confirmation appears
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Look for indicators of existing bet
            # This is platform-specific and may need calibration
            # For now, return False (assume no bet)
            # TODO: Implement actual bet detection based on platform UI
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking existing bet: {e}")
            return False
    
    def click_with_delay(self, x: int, y: int, clicks: int = 1):
        """
        Click at coordinates with human-like delay.
        
        Args:
            x: X coordinate
            y: Y coordinate
            clicks: Number of clicks (default: 1)
        """
        try:
            pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))
            self._random_delay()
            pyautogui.click(x, y, clicks=clicks)
            self._random_delay()
            logger.debug(f"Clicked at ({x}, {y})")
        except Exception as e:
            logger.error(f"Error clicking at ({x}, {y}): {e}")
            raise
    
    def enter_amount(self, amount: float):
        """
        Enter bet amount.
        
        Args:
            amount: Bet amount to enter
        """
        try:
            # Type amount
            pyautogui.write(str(amount), interval=random.uniform(0.05, 0.15))
            self._random_delay()
            logger.debug(f"Entered amount: {amount}")
        except Exception as e:
            logger.error(f"Error entering amount: {e}")
            raise
    
    def confirm_bet(self):
        """Confirm bet placement."""
        try:
            # Look for confirm button in config
            confirm_area = self.betting_config.get('confirm_button')
            if confirm_area:
                x, y = confirm_area[0], confirm_area[1]
                self.click_with_delay(x, y)
            else:
                # Default: press Enter
                pyautogui.press('enter')
                self._random_delay()
            
            logger.debug("Bet confirmed")
        except Exception as e:
            logger.error(f"Error confirming bet: {e}")
            raise
    
    def select_chip(self, bet_amount: float, streak_length: Optional[int] = None, 
                    gale_step: Optional[int] = None) -> Tuple[float, Optional[Tuple[int, int]]]:
        """
        Select appropriate chip size based on bet amount, streak length, and gale step.
        
        Args:
            bet_amount: Desired bet amount
            streak_length: Current streak length (for entry bets)
            gale_step: Current gale step (0 = entry, 1+ = gale progression)
            
        Returns:
            Tuple of (selected_chip_value, chip_coordinates) or (bet_amount, None) if no chip selection
        """
        if not self.adaptive_chip_selection:
            # If adaptive selection disabled, return bet_amount as-is
            return bet_amount, None
        
        # Determine chip size based on rules
        chip_value = None
        
        # Priority 1: Gale step rules (for recovery bets)
        if gale_step is not None:
            if gale_step == 0:
                chip_value = self.chip_rules.get('gale_step_0')
            elif gale_step == 1:
                chip_value = self.chip_rules.get('gale_step_1')
            elif gale_step == 2:
                chip_value = self.chip_rules.get('gale_step_2')
            elif gale_step >= 3:
                chip_value = self.chip_rules.get('gale_step_3')
        
        # Priority 2: Streak length rules (for entry bets)
        if chip_value is None and streak_length is not None:
            if streak_length == 6:
                chip_value = self.chip_rules.get('entry_streak_6')
            elif streak_length == 7:
                chip_value = self.chip_rules.get('entry_streak_7')
            elif streak_length == 8:
                chip_value = self.chip_rules.get('entry_streak_8')
            elif streak_length >= 9:
                chip_value = self.chip_rules.get('entry_streak_9+')
        
        # Fallback: Find closest chip size to bet_amount
        if chip_value is None:
            # Find closest chip size
            chip_value = min(self.chip_sizes, key=lambda x: abs(x - bet_amount))
            # Ensure chip is not larger than bet_amount
            if chip_value > bet_amount:
                chip_value = max([c for c in self.chip_sizes if c <= bet_amount], default=self.chip_sizes[0])
        
        # Get chip coordinates
        chip_coords = None
        if chip_value in self.chip_coords:
            coords = self.chip_coords[chip_value]
            if isinstance(coords, list) and len(coords) >= 2:
                chip_coords = (coords[0], coords[1])
        
        # Calculate number of chips needed
        num_chips = int(bet_amount / chip_value) if chip_value > 0 else 1
        actual_bet = chip_value * num_chips
        
        logger.debug(
            f"Chip selection: bet_amount={bet_amount}, chip_value={chip_value}, "
            f"num_chips={num_chips}, actual_bet={actual_bet}, "
            f"streak={streak_length}, gale_step={gale_step}"
        )
        
        return chip_value, chip_coords
    
    def select_chip_and_place(self, chip_value: float, chip_coords: Optional[Tuple[int, int]], 
                              num_chips: int):
        """
        Select chip and place it on betting area.
        
        Args:
            chip_value: Chip value to select
            chip_coords: Coordinates of chip selection area
            num_chips: Number of chips to place
        """
        if chip_coords:
            # Click on chip selection area
            self.click_with_delay(chip_coords[0], chip_coords[1])
            self._random_delay()
            logger.debug(f"Selected chip: {chip_value}")
        
        # If multiple chips needed, click multiple times
        # (This depends on platform - some require selecting chip then clicking betting area multiple times)
        # For now, we'll assume one click per chip
        return num_chips
    
    def verify_bet_placed(self, timeout: int = 5) -> bool:
        """
        Verify that bet was placed successfully.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            True if bet verified, False otherwise
        """
        try:
            # Wait for bet confirmation
            time.sleep(1)  # Wait for UI to update
            
            # Check for confirmation indicator
            # This is platform-specific
            # For now, assume success if no error
            # TODO: Implement actual verification based on platform UI
            
            return True
            
        except Exception as e:
            logger.warning(f"Error verifying bet: {e}")
            return False
    
    def place_bet(self, bet_type: str, bet_amount: float, 
                  streak_length: Optional[int] = None,
                  gale_step: Optional[int] = None) -> Dict:
        """
        Place a bet on the table.
        
        Args:
            bet_type: 'red', 'black', 'green', 'even', 'odd', or number string
            bet_amount: Amount to bet
            
        Returns:
            Dictionary with bet placement result:
            {
                "success": bool,
                "bet_type": str,
                "bet_amount": float,
                "timestamp": float,
                "error": str (if failed)
            }
        """
        result = {
            "success": False,
            "bet_type": bet_type,
            "bet_amount": bet_amount,
            "timestamp": time.time(),
            "error": None
        }
        
        try:
            # Check if bet already exists
            if self.check_existing_bet():
                logger.warning("Bet already exists, skipping")
                result["error"] = "Bet already exists"
                return result
            
            # Find betting area
            betting_coords = self.find_betting_area(bet_type)
            if not betting_coords:
                result["error"] = f"Betting area not found for {bet_type}"
                logger.error(result["error"])
                return result
            
            x, y = betting_coords
            
            # Select chip if adaptive selection enabled
            chip_value = bet_amount
            chip_coords = None
            num_chips = 1
            
            if self.adaptive_chip_selection:
                chip_value, chip_coords = self.select_chip(bet_amount, streak_length, gale_step)
                num_chips = int(bet_amount / chip_value) if chip_value > 0 else 1
                actual_bet = chip_value * num_chips
                
                # Select chip first
                if chip_coords:
                    self.select_chip_and_place(chip_value, chip_coords, num_chips)
                    logger.info(f"Selected chip: {chip_value} (x{num_chips} = {actual_bet})")
            
            # Place bet
            logger.info(f"Placing bet: {bet_type} - {bet_amount} (using chip: {chip_value} x {num_chips})")
            
            # Click on betting area (multiple times if multiple chips)
            for _ in range(num_chips):
                self.click_with_delay(x, y)
                if num_chips > 1:
                    self._random_delay()  # Small delay between multiple chip placements
            
            # Enter bet amount (if needed - for platforms that require manual entry)
            # Some platforms may require amount entry, others may have fixed chips
            # This depends on platform - may need to be configured
            if self.betting_config.get('requires_amount_entry', False):
                self.enter_amount(bet_amount)
            
            # Confirm bet
            self.confirm_bet()
            
            # Verify bet was placed
            if self.verify_bet_placed():
                result["success"] = True
                self.bet_placed_flag = True
                self.last_bet_time = time.time()
                self.last_bet_details = {
                    "type": bet_type,
                    "amount": bet_amount,
                    "time": result["timestamp"]
                }
                logger.info(f"Bet placed successfully: {bet_type} - {bet_amount}")
            else:
                result["error"] = "Bet verification failed"
                logger.warning(result["error"])
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error placing bet: {e}")
        
        return result
    
    def reset_bet_flag(self):
        """Reset bet placed flag (call after round completes)."""
        self.bet_placed_flag = False
        self.last_bet_details = None

