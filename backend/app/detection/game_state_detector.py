"""
Game State Detection Module
Detects whether the roulette game is in betting phase, spinning, or showing results.
"""

import cv2
import numpy as np
import logging
from typing import Dict, Optional, Tuple
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Game state enumeration."""
    UNKNOWN = "unknown"
    BETTING_OPEN = "betting_open"  # Players can place bets
    SPINNING = "spinning"  # Wheel is spinning, no bets accepted
    RESULT_SHOWN = "result_shown"  # Result is displayed, waiting for next round
    PAUSED = "paused"  # Game is paused/maintenance


class GameStateDetector:
    """Detects the current state of the roulette game."""
    
    def __init__(self, config: Dict):
        """
        Initialize game state detector.
        
        Args:
            config: Configuration dictionary with game state detection settings
        """
        self.config = config
        detection_config = config.get('detection', {})
        
        # Game state detection regions (optional - can be configured)
        self.betting_indicator_region = detection_config.get('betting_indicator_region', None)
        self.spinning_indicator_region = detection_config.get('spinning_indicator_region', None)
        self.timer_region = detection_config.get('timer_region', None)
        
        # State detection method
        self.detection_method = detection_config.get('game_state_method', 'result_based')
        # Options: 'result_based' (infer from detection), 'template' (template matching), 'ocr' (read timer/text)
        
        # Templates for state detection (if using template method)
        self.state_templates_dir = detection_config.get('state_templates_dir', 'state-templates')
        self.state_templates = self._load_state_templates() if self.detection_method == 'template' else {}
        
        # State history for smoothing
        self.state_history = []
        self.max_history = 5
        
        logger.info(f"GameStateDetector initialized with method: {self.detection_method}")
    
    def _load_state_templates(self) -> Dict[str, np.ndarray]:
        """Load templates for state detection."""
        templates = {}
        template_dir = Path(self.state_templates_dir)
        if not template_dir.exists():
            logger.debug(f"State templates directory not found: {template_dir}")
            return templates
        
        for state_name in ['betting_open', 'spinning', 'result_shown', 'paused']:
            template_path = template_dir / f"{state_name}.png"
            if template_path.exists():
                img = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    templates[state_name] = img
                    logger.debug(f"Loaded state template: {state_name}")
        
        return templates
    
    def detect_state_from_result(self, detection_result: Optional[Dict]) -> GameState:
        """
        Infer game state from detection result.
        
        Args:
            detection_result: Result from ScreenDetector.detect_result()
            
        Returns:
            Detected game state
        """
        if detection_result is None:
            # No result detected - could be spinning or waiting
            return GameState.SPINNING
        
        if detection_result.get('number') is not None:
            # Result detected - game is showing result
            return GameState.RESULT_SHOWN
        
        # Fallback
        return GameState.UNKNOWN
    
    def detect_state_from_template(self, frame: np.ndarray) -> GameState:
        """
        Detect game state using template matching.
        
        Args:
            frame: Current frame from screen/video
            
        Returns:
            Detected game state
        """
        if not self.state_templates:
            return GameState.UNKNOWN
        
        # Extract region if configured
        if self.betting_indicator_region:
            x, y, w, h = self.betting_indicator_region
            roi = frame[y:y+h, x:x+w]
        else:
            roi = frame
        
        if roi.size == 0:
            return GameState.UNKNOWN
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        best_match = None
        best_score = 0.0
        
        for state_name, template in self.state_templates.items():
            if template.shape[0] > gray.shape[0] or template.shape[1] > gray.shape[1]:
                continue
            
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_score and max_val > 0.7:  # Threshold for template matching
                best_score = max_val
                best_match = state_name
        
        if best_match:
            state_map = {
                'betting_open': GameState.BETTING_OPEN,
                'spinning': GameState.SPINNING,
                'result_shown': GameState.RESULT_SHOWN,
                'paused': GameState.PAUSED
            }
            return state_map.get(best_match, GameState.UNKNOWN)
        
        return GameState.UNKNOWN
    
    def detect_state(self, frame: np.ndarray, detection_result: Optional[Dict] = None) -> GameState:
        """
        Detect current game state.
        
        Args:
            frame: Current frame from screen/video
            detection_result: Optional result from ScreenDetector (for result-based method)
            
        Returns:
            Detected game state
        """
        if self.detection_method == 'result_based':
            state = self.detect_state_from_result(detection_result)
        elif self.detection_method == 'template':
            state = self.detect_state_from_template(frame)
        else:
            # Default: result-based
            state = self.detect_state_from_result(detection_result)
        
        # Update history for smoothing
        self.state_history.append(state)
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
        
        # Return most common state from recent history (simple smoothing)
        if len(self.state_history) >= 3:
            from collections import Counter
            most_common = Counter(self.state_history[-3:]).most_common(1)[0][0]
            return most_common
        
        return state
    
    def is_betting_allowed(self, state: GameState) -> bool:
        """Check if betting is allowed in current state."""
        return state == GameState.BETTING_OPEN
    
    def is_result_ready(self, state: GameState) -> bool:
        """Check if result is ready to be processed."""
        return state == GameState.RESULT_SHOWN
    
    def get_current_state(self) -> Optional[GameState]:
        """Get the most recent detected state."""
        if self.state_history:
            return self.state_history[-1]
        return None

