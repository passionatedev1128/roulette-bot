"""
Screen Detection Module
Captures roulette table and detects winning number, color, and zero position.
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
from typing import Dict, Optional, Tuple
import time
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy import pyautogui - only needed for screen capture, not for frame mode
try:
    import pyautogui
    _PYAUTOGUI_AVAILABLE = True
except (ImportError, OSError, KeyError, RuntimeError) as e:
    # Handle headless environments (like Colab) gracefully
    # KeyError can occur when DISPLAY env var is missing (Colab)
    _PYAUTOGUI_AVAILABLE = False
    logger.debug(f"pyautogui not available (headless environment?): {e}")

try:
    import easyocr  # type: ignore
    _EASY_OCR_READER = easyocr.Reader(["en"], gpu=False, verbose=False)
except Exception:  # pragma: no cover - optional dependency
    _EASY_OCR_READER = None


class ScreenDetector:
    """Detects roulette results from screen/video frames."""
    
    def __init__(self, config: Dict):
        """
        Initialize screen detector.
        
        Args:
            config: Configuration dictionary with detection settings
        """
        self.config = config
        detection_config = config.get('detection', {})
        self.screen_region = detection_config.get('screen_region', None)
        self.color_ranges = detection_config.get('color_ranges', {})
        self.ocr_debug = bool(detection_config.get('ocr_debug', False))
        self.winning_templates_dir = detection_config.get('winning_templates_dir', 'winning-numbers')
        self.winning_template_threshold = float(detection_config.get('winning_template_threshold', 0.75))
        self.enable_ocr_fallback = bool(detection_config.get('enable_ocr_fallback', True))
        self.ocr_confidence_threshold = float(detection_config.get('ocr_confidence_threshold', 30.0))
        self.ocr_only_if_no_templates = bool(detection_config.get('ocr_only_if_no_templates', False))
        
        # Initialize color ranges if not provided
        if not self.color_ranges:
            self._initialize_default_color_ranges()
        
        # Detection history for validation
        self.detection_history = []
        self.max_history = 10

        self.winning_templates = self._load_winning_number_templates()
        
        logger.info("ScreenDetector initialized")

    def _preprocess_badge_image(self, image: np.ndarray) -> np.ndarray:
        """Convert badge image to normalized grayscale for comparison."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        return gray

    def _load_winning_number_templates(self):
        """Load winning number templates from disk."""
        templates = []
        template_dir = Path(self.winning_templates_dir)
        if not template_dir.exists():
            logger.info("Winning templates directory not found: %s", template_dir)
            return templates

        for path in sorted(template_dir.glob("*.png")):
            match = re.search(r'(\d+)', path.stem)
            if not match:
                continue
            number = int(match.group(1))
            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            processed = self._preprocess_badge_image(img)
            templates.append((number, processed))

        if templates:
            logger.info("Loaded %d winning number templates from %s", len(templates), template_dir)
        else:
            logger.warning("No winning number templates loaded from %s", template_dir)
        return templates

    def detect_winning_number_template(self, roi: np.ndarray) -> Optional[Tuple[int, float]]:
        """Try to match ROI against cached winning-number templates."""
        if not self.winning_templates:
            return None

        processed = self._preprocess_badge_image(roi)
        best_number = None
        best_score = -1.0
        all_scores = {}  # Track all scores for debugging

        for number, template in self.winning_templates:
            h, w = template.shape
            resized = cv2.resize(processed, (w, h), interpolation=cv2.INTER_AREA)
            try:
                result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
                score = float(result[0][0])
                all_scores[number] = score
                if score > best_score:
                    best_score = score
                    best_number = number
            except cv2.error as e:
                logger.debug("Template match error for %s: %s", number, e)
                continue

        # Log all scores if best score is below threshold (for debugging)
        if best_number is not None:
            if best_score < self.winning_template_threshold:
                logger.debug(
                    "Template match below threshold: best=%d (%.3f), threshold=%.3f. All scores: %s",
                    best_number, best_score, self.winning_template_threshold,
                    {k: f"{v:.3f}" for k, v in sorted(all_scores.items(), key=lambda x: x[1], reverse=True)}
                )
            if best_score >= self.winning_template_threshold:
                return best_number, best_score
        
        return None
    
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
        if not _PYAUTOGUI_AVAILABLE:
            raise RuntimeError(
                "pyautogui not available. Cannot capture screen in headless environment. "
                "Use --mode frame for video file processing instead."
            )
        
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
    
    def _is_region_likely_empty(self, roi: np.ndarray) -> bool:
        """
        Check if region is likely empty (no number present).
        Helps prevent OCR false positives.
        More strict checks to catch empty regions.
        
        Args:
            roi: Region of interest image
            
        Returns:
            True if region appears empty, False if likely contains content
        """
        try:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
            
            # Check variance - empty regions have low variance
            variance = np.var(gray)
            if variance < 200:  # Increased threshold - more strict
                logger.debug(f"Region appears empty (variance={variance:.1f} < 200)")
                return True
            
            # Check edge density - numbers have edges
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            if edge_density < 0.08:  # Increased threshold - more strict (8% instead of 5%)
                logger.debug(f"Region appears empty (edge_density={edge_density:.3f} < 0.08)")
                return True
            
            # Check if image is mostly uniform (single color)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_normalized = hist / hist.sum()
            max_bin_ratio = hist_normalized.max()
            if max_bin_ratio > 0.75:  # More strict - 75% instead of 80%
                logger.debug(f"Region appears uniform/empty (max_bin_ratio={max_bin_ratio:.3f} > 0.75)")
                return True
            
            # Additional check: standard deviation
            std_dev = np.std(gray)
            if std_dev < 15:  # Very low standard deviation = likely uniform/empty
                logger.debug(f"Region appears empty (std_dev={std_dev:.1f} < 15)")
                return True
            
            # Check contrast - numbers need contrast
            min_val = np.min(gray)
            max_val = np.max(gray)
            contrast = max_val - min_val
            if contrast < 30:  # Very low contrast = likely empty
                logger.debug(f"Region appears empty (contrast={contrast:.1f} < 30)")
                return True
            
            return False
        except Exception as e:
            logger.debug(f"Error checking if region is empty: {e}")
            return False  # If check fails, assume not empty (conservative)
    
    def _validate_ocr_result(self, roi: np.ndarray, detected_number: int) -> bool:
        """
        Post-OCR validation: Double-check if OCR result makes sense.
        Additional validation after OCR detects a number.
        
        Args:
            roi: Region of interest image
            detected_number: Number detected by OCR
            
        Returns:
            True if result seems valid, False if likely false positive
        """
        try:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
            
            # Re-check if region is empty (more strict check)
            if self._is_region_likely_empty(roi):
                logger.debug(f"OCR result {detected_number} rejected - region appears empty on re-check")
                return False
            
            # Check if we have enough text-like features
            # Numbers should have clear edges and structure
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # If edge density is very low, OCR probably hallucinated
            if edge_density < 0.10:  # Less than 10% edges = suspicious
                logger.debug(f"OCR result {detected_number} rejected - low edge density ({edge_density:.3f})")
                return False
            
            # Check variance - real numbers have variance
            variance = np.var(gray)
            if variance < 300:  # Very low variance = suspicious
                logger.debug(f"OCR result {detected_number} rejected - low variance ({variance:.1f})")
                return False
            
            return True
        except Exception as e:
            logger.debug(f"Error validating OCR result: {e}")
            return True  # If validation fails, accept result (conservative)
    
    def detect_number_ocr(self, frame: np.ndarray, region: Optional[Tuple] = None) -> Optional[int]:
        """
        Detect number using OCR.
        More conservative - validates region has content before trusting OCR.
        
        Args:
            frame: Input frame
            region: Optional region (x, y, w, h) to focus OCR on
            
        Returns:
            Detected number (0-36) or None
        """
        try:
            tesseract_available = True
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                tesseract_available = False
                if _EASY_OCR_READER is None:
                    logger.debug("No OCR backend available (tesseract missing, easyocr not installed)")
                    return None
            
            if region:
                x, y, w, h = region
                roi = frame[y:y + h, x:x + w]
            else:
                roi = frame

            # Check if region is likely empty before trying OCR
            if self._is_region_likely_empty(roi):
                logger.debug("Skipping OCR - region appears empty")
                return None

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            # Upscale and blur for better readability
            scaled = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            blur = cv2.GaussianBlur(scaled, (3, 3), 0)

            variants = [
                ("adaptive_inv", cv2.adaptiveThreshold(
                    blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 3)),
                ("adaptive", cv2.adaptiveThreshold(
                    blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 3)),
            ]

            # also consider the raw scaled image only if not blank
            variants.append(("raw_scaled", scaled))

            if self.ocr_debug:
                debug_dir = Path("ocr_debug")
                debug_dir.mkdir(exist_ok=True)
                for name, img in variants:
                    cv2.imwrite(str(debug_dir / f"{name}.png"), img)

            if tesseract_available:
                ocr_configs = [
                    r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',
                    r'--oem 1 --psm 6 -c tessedit_char_whitelist=0123456789',
                ]

                # Track best OCR result with confidence
                best_result = None
                best_confidence = 0.0
                
                for variant_name, image_variant in variants:
                    for cfg in ocr_configs:
                        try:
                            # Get OCR data with confidence
                            ocr_data = pytesseract.image_to_data(image_variant, config=cfg, output_type=pytesseract.Output.DICT)
                            text = pytesseract.image_to_string(image_variant, config=cfg)
                            
                            # Extract digits and check confidence
                            digits = "".join(filter(str.isdigit, text))
                            if digits:
                                # Calculate average confidence for detected text
                                confidences = [int(conf) for conf, txt in zip(ocr_data.get('conf', []), ocr_data.get('text', [])) 
                                             if txt.strip() and txt.strip().isdigit()]
                                
                                if confidences:
                                    avg_confidence = sum(confidences) / len(confidences)
                                    # Only accept if confidence meets threshold
                                    if avg_confidence >= self.ocr_confidence_threshold:
                                        try:
                                            number = int(digits)
                                            if 0 <= number <= 36:
                                                if avg_confidence > best_confidence:
                                                    best_confidence = avg_confidence
                                                    best_result = number
                                                    logger.debug(
                                                        "OCR detected %s from text '%s' (confidence=%.1f, variant=%s, cfg=%s)",
                                                        number,
                                                        text.strip(),
                                                        avg_confidence,
                                                        variant_name,
                                                        cfg,
                                                    )
                                        except ValueError:
                                            continue
                                else:
                                    # Fallback: if no confidence data, be more strict
                                    # Only accept single digit results (less likely to be false positive)
                                    if len(digits) == 1:
                                        try:
                                            number = int(digits)
                                            if 0 <= number <= 36:
                                                # Lower confidence for results without confidence data
                                                if 0.5 > best_confidence:
                                                    best_confidence = 0.5
                                                    best_result = number
                                                    logger.debug(
                                                        "OCR detected %s from text '%s' (no confidence data, variant=%s)",
                                                        number,
                                                        text.strip(),
                                                        variant_name,
                                                    )
                                        except ValueError:
                                            continue
                        except Exception as e:
                            logger.debug(f"OCR error with variant {variant_name}: {e}")
                            continue
                
                # Only return if we have a reasonably confident result AND it passes validation
                if best_result is not None and best_confidence >= self.ocr_confidence_threshold:
                    # Additional validation: check if result makes sense
                    if self._validate_ocr_result(roi, best_result):
                        return best_result
                    else:
                        logger.debug(f"OCR result {best_result} rejected - failed post-validation")
                elif best_result is not None:
                    logger.debug(f"OCR result {best_result} rejected (confidence {best_confidence:.1f} < {self.ocr_confidence_threshold})")

            if _EASY_OCR_READER is not None:
                # Bypass detector by providing full bounding box
                rgb_scaled = cv2.cvtColor(scaled, cv2.COLOR_GRAY2RGB)
                h, w = rgb_scaled.shape[:2]
                bbox = [[0, 0, w, 0, w, h, 0, h]]
                try:
                    # Try to get detailed results with confidence
                    try:
                        results = _EASY_OCR_READER.readtext(
                            rgb_scaled,
                            detail=1,  # Get confidence scores
                            paragraph=False,
                            allowlist="0123456789",
                        )
                    except TypeError:
                        # Fallback if detail parameter not supported
                        results = _EASY_OCR_READER.readtext(
                            rgb_scaled,
                            detail=0,
                            paragraph=False,
                            allowlist="0123456789",
                        )
                    
                    best_result = None
                    best_confidence = 0.0
                    
                    for item in results:
                        if isinstance(item, tuple) and len(item) >= 2:
                            # Format: (bbox, text, confidence)
                            text = item[1] if len(item) > 1 else str(item[0])
                            confidence = item[2] if len(item) > 2 else 0.5
                        else:
                            # Format: just text
                            text = str(item)
                            confidence = 0.5  # Default confidence if not provided
                        
                        digits = "".join(filter(str.isdigit, text))
                        if digits:
                            try:
                                number = int(digits)
                                if 0 <= number <= 36:
                                    # Only accept if confidence is reasonable (>= 0.3 for EasyOCR)
                                    if confidence >= 0.3 and confidence > best_confidence:
                                        best_confidence = confidence
                                        best_result = number
                                        logger.debug(
                                            "EasyOCR detected %s from text '%s' (confidence=%.2f)",
                                            number,
                                            text.strip(),
                                            confidence
                                        )
                            except ValueError:
                                continue
                    
                    # Only return if we have a reasonably confident result AND it passes validation
                    if best_result is not None and best_confidence >= 0.3:
                        # Additional validation: check if result makes sense
                        if self._validate_ocr_result(roi, best_result):
                            return best_result
                        else:
                            logger.debug(f"EasyOCR result {best_result} rejected - failed post-validation")
                    elif best_result is not None:
                        logger.debug(f"EasyOCR result {best_result} rejected (confidence {best_confidence:.2f} < 0.3)")
                        
                except Exception as e:
                    logger.debug(f"EasyOCR error: {e}")
                    pass

            logger.debug("OCR failed to extract valid number from snapshot.")
            return None
            
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
        
        # Determine region of interest (winning badge)
        if self.screen_region:
            x, y, w, h = self.screen_region
            roi = frame[y:y+h, x:x+w]
        else:
            roi = frame

        # Try dedicated winning-number templates first
        badge_match = self.detect_winning_number_template(roi)
        if badge_match is not None:
            number, confidence = badge_match
            result["number"] = number
            result["color"] = self.get_color_from_number(number)
            result["zero"] = (number == 0)
            result["confidence"] = float(confidence)
            result["method"] = "template_badge"

        # Fall back to generic grid templates if needed
        if result["number"] is None:
            number = self.detect_number_template(roi if self.screen_region else frame)
            if number is not None:
                result["number"] = number
                result["color"] = self.get_color_from_number(number)
                result["zero"] = (number == 0)
                result["confidence"] = 0.9
                result["method"] = "template"
        
        # Fallback to OCR (only if enabled)
        if result["number"] is None and self.enable_ocr_fallback:
            # If ocr_only_if_no_templates is True, only use OCR if we have no templates at all
            if self.ocr_only_if_no_templates and len(self.winning_templates) > 0:
                logger.debug("Skipping OCR - templates available and ocr_only_if_no_templates is enabled")
            else:
                number = self.detect_number_ocr(roi)
                if number is not None:
                    result["number"] = number
                    result["color"] = self.get_color_from_number(number)
                    result["zero"] = (number == 0)
                    result["confidence"] = 0.7
                    result["method"] = "ocr"
        
        # If still no number, try color detection only
        if result["number"] is None:
            color = self.detect_color_hsv(roi)
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

