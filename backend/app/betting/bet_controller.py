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
        
        # Chip selection coordinates
        self.chip_selection_coords = self.betting_config.get('chip_selection_coordinates', {})
        # Fallback to single chip_selection if chip_selection_coordinates not available
        if not self.chip_selection_coords:
            single_chip = self.betting_config.get('chip_selection')
            if single_chip:
                # Use single chip coordinate for all chip values (legacy support)
                self.chip_selection_coords = {
                    '0.5': single_chip,
                    '1': single_chip,
                    '2.5': single_chip,
                    '5': single_chip,
                    '20': single_chip,
                    '50': single_chip
                }
                logger.info("Using single chip_selection coordinate for all chip values")
        
        # State tracking
        self.last_bet_time = None
        self.bet_placed_flag = False
        self.last_bet_details = None
        self.last_selected_chip = None
        
        # Safety settings
        pyautogui.PAUSE = 0.1  # Small pause between actions
        pyautogui.FAILSAFE = True  # Enable failsafe (move mouse to corner to stop)
        
        logger.info("BetController initialized")
        if self.chip_selection_coords:
            logger.info(f"Chip selection coordinates available for: {list(self.chip_selection_coords.keys())}")
    
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
    
    def select_chip(self, chip_value: float) -> bool:
        """
        Select a chip value before placing bet.
        
        Args:
            chip_value: Chip value to select (0.5, 1, 2.5, 5, 20, or 50)
            
        Returns:
            True if chip selected successfully, False otherwise
        """
        try:
            # Convert chip value to string key
            chip_key = str(chip_value)
            
            # Check if we have coordinates for this chip
            if chip_key not in self.chip_selection_coords:
                logger.warning(f"Chip selection coordinates not found for {chip_value}")
                # Try to find closest available chip
                available_chips = [float(k) for k in self.chip_selection_coords.keys()]
                if available_chips:
                    closest_chip = min(available_chips, key=lambda x: abs(x - chip_value))
                    chip_key = str(closest_chip)
                    logger.info(f"Using closest available chip: {closest_chip} instead of {chip_value}")
                else:
                    logger.warning("No chip selection coordinates available")
                    return False
            
            # Get coordinates for this chip
            chip_coords = self.chip_selection_coords[chip_key]
            if not isinstance(chip_coords, list) or len(chip_coords) < 2:
                logger.error(f"Invalid chip coordinates for {chip_value}: {chip_coords}")
                return False
            
            x, y = chip_coords[0], chip_coords[1]
            
            # Only select chip if it's different from last selected
            if self.last_selected_chip != chip_value:
                logger.info(f"Selecting chip: {chip_value} at ({x}, {y})")
                self.click_with_delay(x, y)
                self.last_selected_chip = chip_value
                self._random_delay()  # Wait for chip selection to register
                logger.debug(f"Chip {chip_value} selected successfully")
            else:
                logger.debug(f"Chip {chip_value} already selected, skipping")
            
            return True
            
        except Exception as e:
            logger.error(f"Error selecting chip {chip_value}: {e}")
            return False
    
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
    
    def place_bet(self, bet_type: str, bet_amount: float, chip_value: Optional[float] = None) -> Dict:
        """
        Place a bet on the table.
        
        Args:
            bet_type: 'red', 'black', 'green', 'even', 'odd', or number string
            bet_amount: Amount to bet
            chip_value: Optional chip value to use (0.5, 1, 2.5, 5, 20, or 50).
                       If not provided, will use closest available chip.
            
        Returns:
            Dictionary with bet placement result:
            {
                "success": bool,
                "bet_type": str,
                "bet_amount": float,
                "chip_value": float,
                "timestamp": float,
                "error": str (if failed)
            }
        """
        result = {
            "success": False,
            "bet_type": bet_type,
            "bet_amount": bet_amount,
            "chip_value": chip_value,
            "timestamp": time.time(),
            "error": None
        }
        
        try:
            # Check if bet already exists
            if self.check_existing_bet():
                logger.warning("Bet already exists, skipping")
                result["error"] = "Bet already exists"
                return result
            
            # Determine chip value to use
            if chip_value is None:
                # Find best chip value based on bet amount
                available_chips = [float(k) for k in self.chip_selection_coords.keys()]
                if available_chips:
                    # Use largest chip that fits into bet amount
                    suitable_chips = [c for c in available_chips if c <= bet_amount]
                    if suitable_chips:
                        chip_value = max(suitable_chips)
                    else:
                        chip_value = min(available_chips)
                    logger.info(f"Auto-selected chip: {chip_value} for bet amount: {bet_amount}")
                else:
                    logger.warning("No chip selection coordinates available, proceeding without chip selection")
            
            # Select chip if chip selection coordinates are available
            if self.chip_selection_coords and chip_value:
                if not self.select_chip(chip_value):
                    logger.warning(f"Failed to select chip {chip_value}, proceeding anyway")
                result["chip_value"] = chip_value
            
            # Find betting area
            betting_coords = self.find_betting_area(bet_type)
            if not betting_coords:
                result["error"] = f"Betting area not found for {bet_type}"
                logger.error(result["error"])
                logger.error(f"Available betting areas: {list(self.betting_areas.keys())}")
                return result
            
            x, y = betting_coords
            
            # Calculate number of clicks needed
            num_clicks = 1
            if chip_value and chip_value > 0:
                num_clicks = int(bet_amount / chip_value)
                if num_clicks < 1:
                    num_clicks = 1
                logger.info(f"Bet amount: {bet_amount}, Chip: {chip_value}, Clicks needed: {num_clicks}")
            
            # Place bet
            logger.info(f"Placing bet: {bet_type} - {bet_amount}")
            if chip_value:
                logger.info(f"Using chip: {chip_value} x {num_clicks}")
            logger.info(f"Moving mouse to betting area: ({x}, {y})")
            
            # Click on betting area (multiple times if needed)
            for click_num in range(num_clicks):
                self.click_with_delay(x, y)
                if click_num < num_clicks - 1:
                    self._random_delay()  # Small delay between multiple clicks
            logger.info(f" Mouse moved and clicked {num_clicks} time(s) at ({x}, {y})")
            
            # Enter bet amount (if needed)
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

