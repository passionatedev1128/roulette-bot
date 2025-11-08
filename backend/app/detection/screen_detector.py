"""
Screen Detection Module
Captures roulette table and detects winning number, color, and zero position.
"""

import cv2
import numpy as np
import pytesseract
import pyautogui
from PIL import Image
import logging
from typing import Dict, Optional, Tuple
import time

logger = logging.getLogger(__name__)


class ScreenDetector:
    """Detects roulette results from screen/video frames."""
    
    def __init__(self, config: Dict):
        """
        Initialize screen detector.
        
        Args:
            config: Configuration dictionary with detection settings
        """
        self.config = config
        self.screen_region = config.get('detection', {}).get('screen_region', None)
        self.color_ranges = config.get('detection', {}).get('color_ranges', {})
        
        # Initialize color ranges if not provided
        if not self.color_ranges:
            self._initialize_default_color_ranges()
        
        # Detection history for validation
        self.detection_history = []
        self.max_history = 10
        
        logger.info("ScreenDetector initialized")
    
    def _initialize_default_color_ranges(self):
        """Initialize default HSV color ranges for red, black, and green."""
        # HSV color ranges (Hue, Saturation, Value)
        self.color_ranges = {
            'red': [
                # Red range 1 (0-10 degrees)
                ([0, 100, 100], [10, 255, 255]),
                # Red range 2 (170-180 degrees)
                ([170, 100, 100], [180, 255, 255])
            ],
            'black': [
                ([0, 0, 0], [180, 255, 30])  # Low value = dark/black
            ],
            'green': [
                ([50, 100, 100], [70, 255, 255])  # Green on roulette wheel
            ]
        }
    
    def capture_screen(self) -> np.ndarray:
        """
        Capture screen or video frame.
        
        Returns:
            Frame as numpy array
        """
        try:
            if self.screen_region:
                # Capture specific region
                screenshot = pyautogui.screenshot(region=self.screen_region)
            else:
                # Capture full screen
                screenshot = pyautogui.screenshot()
            
            # Convert PIL to OpenCV format
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            logger.debug("Screen captured successfully")
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
            raise
    
    def detect_number_ocr(self, frame: np.ndarray, region: Optional[Tuple] = None) -> Optional[int]:
        """
        Detect number using OCR.
        
        Args:
            frame: Input frame
            region: Optional region (x, y, w, h) to focus OCR on
            
        Returns:
            Detected number (0-36) or None
        """
        try:
            # Check if pytesseract is available
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                logger.debug("Tesseract OCR not available, skipping OCR detection")
                return None
            
            if region:
                x, y, w, h = region
                roi = frame[y:y+h, x:x+w]
            else:
                roi = frame
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR configuration
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(thresh, config=custom_config)
            
            # Extract number
            number = None
            for char in text.strip():
                if char.isdigit():
                    number = int(char)
                    if number >= 0 and number <= 36:
                        return number
            
            logger.debug(f"OCR detected text: '{text}', extracted number: {number}")
            return number
            
        except Exception as e:
            logger.debug(f"OCR detection failed: {e}")
            return None
    
    def detect_number_template(self, frame: np.ndarray, templates_dir: str = "templates") -> Optional[int]:
        """
        Detect number using template matching.
        More reliable than OCR for stylized numbers.
        
        Args:
            frame: Input frame
            templates_dir: Directory containing number templates
            
        Returns:
            Detected number (0-36) or None
        """
        try:
            # Check if templates directory exists
            from pathlib import Path
            template_path_obj = Path(templates_dir)
            if not template_path_obj.exists():
                logger.debug(f"Templates directory not found: {templates_dir}")
                return None
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            best_match = None
            best_confidence = -1.0  # Start with -1 to find actual best match
            second_best_confidence = -1.0  # Track second best for validation
            confidence_threshold = 0.75  # Minimum confidence threshold
            
            # Store all matches for validation
            all_matches = []
            templates_found = 0
            
            # Try to match templates for numbers 0-36
            for num in range(37):
                template_path = template_path_obj / f"number_{num}.png"
                try:
                    if not template_path.exists():
                        continue
                    
                    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                    if template is None:
                        continue
                    
                    templates_found += 1
                    
                    # Check if template is larger than frame (would cause error)
                    if template.shape[0] > gray.shape[0] or template.shape[1] > gray.shape[1]:
                        logger.debug(f"Template {num} ({template.shape[1]}x{template.shape[0]}) larger than frame ({gray.shape[1]}x{gray.shape[0]})")
                        continue
                    
                    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    all_matches.append((num, max_val))
                    
                    # Track best and second best
                    if max_val > best_confidence:
                        second_best_confidence = best_confidence
                        best_confidence = max_val
                        best_match = num
                    elif max_val > second_best_confidence:
                        second_best_confidence = max_val
                        
                except Exception as e:
                    logger.debug(f"Template {num} error: {e}")
                    continue
            
            # Log if no templates found
            if templates_found == 0:
                logger.debug(f"No templates found in {templates_dir}")
                return None
            
            # Validate result
            if best_match is not None:
                # Check if confidence meets threshold
                if best_confidence < confidence_threshold:
                    logger.debug(f"Best match {best_match} confidence {best_confidence:.2f} below threshold {confidence_threshold}")
                    return None
                
                # Check if best match is significantly better than second best (prevents false positives)
                # If second best is close, might be ambiguous
                if second_best_confidence > 0 and (best_confidence - second_best_confidence) < 0.1:
                    logger.debug(f"Best match {best_match} ({best_confidence:.2f}) too close to second best ({second_best_confidence:.2f}) - ambiguous")
                    return None
                
                # Additional check: If multiple templates match with high confidence, might be matching betting grid
                # Count how many templates match above threshold
                high_conf_matches = [m for m in all_matches if m[1] >= confidence_threshold]
                if len(high_conf_matches) > 5:  # If more than 5 templates match, probably matching grid
                    logger.debug(f"Too many templates match ({len(high_conf_matches)}), likely matching betting grid instead of result display")
                    return None
                
                logger.debug(f"Template matching found number {best_match} with confidence {best_confidence:.2f}")
                return best_match
            
            logger.debug(f"No valid template match found (best: {best_confidence:.2f}, threshold: {confidence_threshold})")
            return None
            
        except Exception as e:
            logger.warning(f"Template matching failed: {e}")
            return None
    
    def detect_color_hsv(self, frame: np.ndarray, region: Optional[Tuple] = None) -> Optional[str]:
        """
        Detect color using HSV color space.
        
        Args:
            frame: Input frame
            region: Optional region (x, y, w, h) to check
            
        Returns:
            Color string ('red', 'black', 'green') or None
        """
        try:
            if region:
                x, y, w, h = region
                roi = frame[y:y+h, x:x+w]
            else:
                roi = frame
            
            # Convert to HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Calculate average color
            avg_hsv = np.mean(hsv.reshape(-1, 3), axis=0)
            h, s, v = avg_hsv
            
            # Check against color ranges
            color_scores = {}
            
            for color_name, ranges in self.color_ranges.items():
                for lower, upper in ranges:
                    lower = np.array(lower, dtype=np.uint8)
                    upper = np.array(upper, dtype=np.uint8)
                    
                    # Check if average color is in range
                    if np.all(lower <= avg_hsv) and np.all(avg_hsv <= upper):
                        color_scores[color_name] = color_scores.get(color_name, 0) + 1
            
            # Return color with highest score
            if color_scores:
                detected_color = max(color_scores, key=color_scores.get)
                
                # Map roulette colors
                if detected_color == 'green':
                    return 'green'
                elif detected_color == 'red':
                    return 'red'
                elif detected_color == 'black':
                    return 'black'
            
            # Fallback: determine color from number if detected
            # Red: 1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
            # Black: 2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35
            # Green: 0
            
            logger.debug(f"Color detection: average HSV = ({h:.1f}, {s:.1f}, {v:.1f})")
            return None
            
        except Exception as e:
            logger.warning(f"Color detection failed: {e}")
            return None
    
    def get_color_from_number(self, number: int) -> str:
        """
        Get color from roulette number.
        
        Args:
            number: Roulette number (0-36)
            
        Returns:
            Color string ('red', 'black', 'green')
        """
        if number == 0:
            return 'green'
        
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        
        if number in red_numbers:
            return 'red'
        elif number in black_numbers:
            return 'black'
        else:
            return 'green'
    
    def detect_zero_position(self, frame: np.ndarray) -> bool:
        """
        Detect if zero (0) is the winning number.
        
        Args:
            frame: Input frame
            
        Returns:
            True if zero detected, False otherwise
        """
        # Try to detect number 0
        number = self.detect_result(frame).get('number')
        return number == 0
    
    def detect_result(self, frame: Optional[np.ndarray] = None) -> Dict:
        """
        Main detection method - detects number, color, and zero.
        Uses hybrid approach: template matching preferred, OCR as fallback.
        
        Args:
            frame: Optional frame (if None, captures screen)
            
        Returns:
            Dictionary with detection results:
            {
                "number": int (0-36),
                "color": str ("red", "black", "green"),
                "zero": bool,
                "confidence": float (0-1),
                "method": str ("template", "ocr", "color_fallback")
            }
        """
        if frame is None:
            frame = self.capture_screen()
        
        result = {
            "number": None,
            "color": None,
            "zero": False,
            "confidence": 0.0,
            "method": None
        }
        
        # Try template matching first (more reliable)
        # Only use screen_region if specified in config
        if self.screen_region:
            x, y, w, h = self.screen_region
            roi = frame[y:y+h, x:x+w]
            number = self.detect_number_template(roi)
        else:
            number = self.detect_number_template(frame)
        
        if number is not None:
            result["number"] = number
            result["color"] = self.get_color_from_number(number)
            result["zero"] = (number == 0)
            result["confidence"] = 0.9
            result["method"] = "template"
        
        # Fallback to OCR
        if result["number"] is None:
            number = self.detect_number_ocr(frame)
            if number is not None:
                result["number"] = number
                result["color"] = self.get_color_from_number(number)
                result["zero"] = (number == 0)
                result["confidence"] = 0.7
                result["method"] = "ocr"
        
        # If still no number, try color detection only
        if result["number"] is None:
            color = self.detect_color_hsv(frame)
            if color:
                result["color"] = color
                result["confidence"] = 0.5
                result["method"] = "color_fallback"
                result["zero"] = (color == 'green')
        
        # Validate result
        if result["number"] is not None:
            # Validate number is in valid range
            if result["number"] < 0 or result["number"] > 36:
                logger.warning(f"Invalid number detected: {result['number']}")
                result["number"] = None
                result["confidence"] = 0.0
        
        # Store in history for validation
        if result["number"] is not None:
            self.detection_history.append(result)
            if len(self.detection_history) > self.max_history:
                self.detection_history.pop(0)
        
        logger.info(f"Detection result: {result}")
        return result
    
    def validate_result(self, result: Dict) -> bool:
        """
        Validate detection result against history.
        
        Args:
            result: Detection result dictionary
            
        Returns:
            True if result seems valid, False otherwise
        """
        if result["number"] is None:
            return False
        
        # Check confidence threshold
        if result["confidence"] < 0.5:
            return False
        
        # Check if result is consistent with recent history
        if len(self.detection_history) > 1:
            # Should not have same number twice in a row (unless very confident)
            if result["number"] == self.detection_history[-1].get("number"):
                if result["confidence"] < 0.9:
                    logger.warning("Same number detected twice - may be error")
                    return False
        
        return True

