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
import warnings
from typing import Dict, Optional, Tuple
import time
import re
from pathlib import Path

try:
    import easyocr  # type: ignore

    # easyocr internally sets pin_memory=True on its DataLoader which emits a warning on CPU-only hosts.
    # Filter the warning to avoid noisy console output when no accelerator is available.
    warnings.filterwarnings(
        "ignore",
        message=".*'pin_memory' argument is set as true but no accelerator is found.*",
        category=UserWarning,
    )

    # Performance optimization: Initialize EasyOCR reader lazily (only when needed)
    # This prevents loading the model into memory if OCR is never used
    _EASY_OCR_READER = None
    _EASY_OCR_INITIALIZED = False
    
    def _get_easyocr_reader():
        """Lazy initialization of EasyOCR reader to save memory."""
        global _EASY_OCR_READER, _EASY_OCR_INITIALIZED
        if not _EASY_OCR_INITIALIZED:
            try:
                _EASY_OCR_READER = easyocr.Reader(["en"], gpu=False, verbose=False)
                _EASY_OCR_INITIALIZED = True
                logger.info("EasyOCR reader initialized (lazy loading)")
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {e}")
                _EASY_OCR_INITIALIZED = True  # Mark as attempted to avoid retrying
        return _EASY_OCR_READER
except Exception:  # pragma: no cover - optional dependency
    _EASY_OCR_READER = None
    _EASY_OCR_INITIALIZED = False
    
    def _get_easyocr_reader():
        return None

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
        detection_config = config.get('detection', {})
        self.screen_region = detection_config.get('screen_region', None)
        self.color_ranges = detection_config.get('color_ranges', {})
        self.ocr_debug = bool(detection_config.get('ocr_debug', False))
        # Get template directory path and resolve it (handle both relative and absolute paths)
        template_dir_raw = detection_config.get('winning_templates_dir', 'winning-number_templates')
        # Remove trailing slash if present
        template_dir_raw = template_dir_raw.rstrip('/').rstrip('\\')
        # Try to resolve as absolute path first, then relative to current working directory
        template_dir_path = Path(template_dir_raw)
        if not template_dir_path.is_absolute():
            # Try relative to current working directory
            template_dir_path = Path.cwd() / template_dir_path
            # If not found, try relative to config file location (if available)
            if not template_dir_path.exists():
                # Try relative to project root (common case)
                project_root = Path(__file__).parent.parent.parent.parent
                template_dir_path = project_root / template_dir_raw
        self.winning_templates_dir = str(template_dir_path)
        
        self.winning_template_threshold = float(detection_config.get('winning_template_threshold', 0.75))
        self.ocr_confidence_threshold = float(detection_config.get('ocr_confidence_threshold', 0.9))
        
        # Initialize color ranges if not provided
        if not self.color_ranges:
            self._initialize_default_color_ranges()
        
        # Detection history for validation
        self.detection_history = []
        self.max_history = 10
        
        # Temporal validation: track recent detections to identify isolated false positives
        self.recent_detections = []  # Track recent detections with frame info
        self.max_recent_detections = 5  # Track last 5 detections for temporal validation

        self.winning_templates = self._load_winning_number_templates()
        
        # Performance optimization: cache for processed ROIs to avoid redundant processing
        self._roi_cache = None
        self._roi_cache_frame_hash = None
        self._roi_cache_max_age = 5  # Cache valid for 5 frames
        self._roi_cache_age = 0
        
        logger.info(f"ScreenDetector initialized with winning templates dir: {self.winning_templates_dir}")
        logger.info(f"Loaded {len(self.winning_templates)} winning number templates")

    def _preprocess_badge_image(self, image: np.ndarray) -> np.ndarray:
        """Convert badge image to normalized grayscale for comparison."""
        # Check if image is empty or invalid
        if image is None or image.size == 0 or image.shape[0] == 0 or image.shape[1] == 0:
            raise ValueError("Cannot preprocess empty image")
        
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
        
        logger.debug(f"Looking for winning templates in: {template_dir.absolute()}")
        
        if not template_dir.exists():
            logger.warning(
                "Winning templates directory not found: %s (absolute: %s)",
                template_dir,
                template_dir.absolute()
            )
            # Try alternative locations
            alternative_paths = [
                Path.cwd() / "winning-number_templates",
                Path(__file__).parent.parent.parent.parent / "winning-number_templates",
                Path.cwd() / "winning-number_templates" / "",
            ]
            for alt_path in alternative_paths:
                if alt_path.exists():
                    logger.info(f"Found templates in alternative location: {alt_path.absolute()}")
                    template_dir = alt_path
                    break
            else:
                logger.warning("No winning templates found in any location")
                return templates

        template_files = list(template_dir.glob("*.png"))
        logger.debug(f"Found {len(template_files)} PNG files in template directory")
        
        for path in sorted(template_files):
            match = re.search(r'(\d+)', path.stem)
            if not match:
                logger.debug(f"Skipping template file (no number found): {path.name}")
                continue
            number = int(match.group(1))
            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                logger.warning(f"Failed to load template image: {path}")
                continue
            processed = self._preprocess_badge_image(img)
            templates.append((number, processed))
            logger.debug(f"Loaded template for number {number} from {path.name}")

        if templates:
            logger.info("Loaded %d winning number templates from %s", len(templates), template_dir.absolute())
            # Log which numbers were loaded
            numbers_loaded = sorted([num for num, _ in templates])
            logger.debug(f"Template numbers loaded: {numbers_loaded}")
        else:
            logger.warning("No winning number templates loaded from %s", template_dir.absolute())
        return templates

    def detect_winning_number_template(self, roi: np.ndarray) -> Optional[Tuple[int, float]]:
        """Try to match ROI against cached winning-number templates."""
        if not self.winning_templates:
            logger.debug("No winning templates available for matching")
            return None

        # Check if ROI is empty or invalid
        if roi is None or roi.size == 0 or (hasattr(roi, 'shape') and (roi.shape[0] == 0 or roi.shape[1] == 0)):
            logger.debug("ROI is empty, cannot match templates")
            return None

        try:
            processed = self._preprocess_badge_image(roi)
        except (ValueError, cv2.error) as e:
            logger.warning(f"Template matching failed: {e}")
            return None
        best_number = None
        best_score = -1.0
        all_scores = {}  # Track all scores for debugging

        logger.debug(f"Matching ROI (shape: {roi.shape}) against {len(self.winning_templates)} templates")

        # Performance optimization: early exit if ROI is too small for any template
        min_template_h = min(t.shape[0] for _, t in self.winning_templates)
        min_template_w = min(t.shape[1] for _, t in self.winning_templates)
        if processed.shape[0] < min_template_h or processed.shape[1] < min_template_w:
            logger.debug(f"ROI too small for any template: ROI={processed.shape}, min_template=({min_template_h}, {min_template_w})")
            return None

        for number, template in self.winning_templates:
            h, w = template.shape
            # Check if ROI is too small
            if processed.shape[0] < h or processed.shape[1] < w:
                logger.debug(f"ROI too small for template {number}: ROI={processed.shape}, template={template.shape}")
                continue
            
            try:
                # Performance optimization: skip if ROI is too small for this template
                if processed.shape[0] < h or processed.shape[1] < w:
                    continue
                
                # If ROI is much larger than template, do sliding window search
                # Otherwise, resize ROI to template size for direct comparison
                if processed.shape[0] > h * 2 or processed.shape[1] > w * 2:
                    # ROI is large - do sliding window template matching
                    result = cv2.matchTemplate(processed, template, cv2.TM_CCOEFF_NORMED)
                    # Get the best match score
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)
                    score = float(max_val)
                else:
                    # ROI is similar size to template - resize and compare directly
                    resized = cv2.resize(processed, (w, h), interpolation=cv2.INTER_AREA)
                    result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
                    score = float(result[0][0])
                
                # Early exit optimization: if we find a very high confidence match, return immediately
                # BUT: Only if score is significantly above threshold to avoid false positives
                if score >= 0.98 and score >= self.winning_template_threshold + 0.15:
                    logger.debug(f"Early exit: found very high confidence match {number} with score {score:.3f}")
                    return (number, score)
                
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
                    "Template match below threshold: best=%d (%.3f), threshold=%.3f. Top 5 scores: %s",
                    best_number, best_score, self.winning_template_threshold,
                    {k: f"{v:.3f}" for k, v in sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:5]}
                )
                return None  # Reject if below threshold
            else:
                # Check if there are multiple high-scoring matches (potential ambiguity)
                sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
                if len(sorted_scores) >= 2:
                    second_best_number, second_best_score = sorted_scores[1]
                    # If second-best is also above threshold and close to best, be more cautious
                    if second_best_score >= self.winning_template_threshold:
                        score_gap = best_score - second_best_score
                        # Relaxed ambiguity checks for better detection rate:
                        # If gap is very small (< 0.03), require good confidence (>= 0.90)
                        # If gap is small (0.03-0.04), require reasonable confidence (>= 0.85)
                        # If gap is >= 0.04, accept any score above threshold
                        if score_gap < 0.03:
                            # Very ambiguous - require good confidence (relaxed from 0.95)
                            if best_score < 0.90:
                                logger.warning(
                                    "Ambiguous template match: best=%d (%.3f) vs second=%d (%.3f), gap=%.3f < 0.03. "
                                    "Best score %.3f < 0.90, rejecting ambiguous match.",
                                    best_number, best_score, second_best_number, second_best_score,
                                    score_gap, best_score
                                )
                                return None
                        elif score_gap < 0.04:
                            # Somewhat ambiguous - require reasonable confidence (relaxed from 0.94)
                            if best_score < 0.85:
                                logger.warning(
                                    "Ambiguous template match: best=%d (%.3f) vs second=%d (%.3f), gap=%.3f < 0.04. "
                                    "Best score %.3f < 0.85, rejecting ambiguous match.",
                                    best_number, best_score, second_best_number, second_best_score,
                                    score_gap, best_score
                                )
                                return None
                        elif score_gap < 0.05:
                            logger.info(
                                "Template match SUCCESS (ambiguous but high confidence): number=%d, confidence=%.3f, "
                                "second_best=%d (%.3f), gap=%.3f",
                                best_number, best_score, second_best_number, second_best_score, score_gap
                            )
                        else:
                            logger.info(
                                "Template match SUCCESS: number=%d, confidence=%.3f (threshold=%.3f)",
                                best_number, best_score, self.winning_template_threshold
                            )
                else:
                    logger.info(
                        "Template match SUCCESS: number=%d, confidence=%.3f (threshold=%.3f)",
                        best_number, best_score, self.winning_template_threshold
                    )
            # Final validation: ensure score meets threshold and we have a valid number
            if best_score >= self.winning_template_threshold and best_number is not None and 0 <= best_number <= 36:
                return best_number, best_score
            else:
                logger.debug(
                    f"Template match rejected: best_number={best_number}, best_score={best_score:.3f}, "
                    f"threshold={self.winning_template_threshold}, valid_number={best_number is not None and 0 <= best_number <= 36}"
                )
        else:
            logger.debug("No template match found (no templates matched)")
        
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
        Capture screen or video frame with retry logic for better reliability.
        
        When running in background thread (through backend), frame capture can be less reliable
        due to timing/threading issues. This method adds retry logic and quality checks.
        
        Returns:
            Frame as numpy array
        """
        max_retries = 3
        retry_delay = 0.05  # 50ms delay between retries
        
        for attempt in range(max_retries):
            try:
                if self.screen_region:
                    # Capture specific region
                    screenshot = pyautogui.screenshot(region=self.screen_region)
                else:
                    # Capture full screen
                    screenshot = pyautogui.screenshot()
                
                # Convert PIL to OpenCV format
                # Performance optimization: use array view instead of copy when possible
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Clean up PIL image to free memory immediately
                del screenshot
                
                # Quality check: ensure frame is valid and not empty
                if frame is None or frame.size == 0:
                    if attempt < max_retries - 1:
                        logger.debug(f"Frame capture returned empty frame (attempt {attempt + 1}/{max_retries}), retrying...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error("Frame capture returned empty frame after all retries")
                        raise ValueError("Frame capture returned empty frame")
                
                # Validate frame dimensions
                if frame.shape[0] == 0 or frame.shape[1] == 0:
                    if attempt < max_retries - 1:
                        logger.warning(f"Frame capture returned invalid dimensions (attempt {attempt + 1}/{max_retries}), retrying...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error("Frame capture returned invalid dimensions after all retries")
                        raise ValueError("Frame capture returned invalid dimensions")
                
                # Additional quality check: ensure frame has reasonable brightness (not completely black)
                # This helps catch cases where window is minimized or not visible
                if self.screen_region:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
                    mean_brightness = np.mean(gray)
                    if mean_brightness < 5:  # Very dark frame (likely window not visible)
                        if attempt < max_retries - 1:
                            logger.debug(f"Frame capture returned very dark frame (brightness={mean_brightness:.1f}, attempt {attempt + 1}/{max_retries}), retrying...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            logger.warning(f"Frame capture returned very dark frame (brightness={mean_brightness:.1f}) - window may not be visible or screen region may be incorrect")
                
                if attempt > 0:
                    logger.debug(f"Screen captured successfully on attempt {attempt + 1} (shape: {frame.shape})")
                else:
                    logger.debug(f"Screen captured successfully (shape: {frame.shape})")
                return frame
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error capturing screen (attempt {attempt + 1}/{max_retries}): {e}, retrying...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Error capturing screen after {max_retries} attempts: {e}")
                    raise
    
    def detect_number_ocr(self, frame: np.ndarray, region: Optional[Tuple] = None) -> Optional[Tuple[int, float]]:
        """
        Detect number using OCR.
        
        Args:
            frame: Input frame
            region: Optional region (x, y, w, h) to focus OCR on
            
        Returns:
            Tuple of (detected number (0-36), confidence (0-1)) or None
            Only returns if confidence >= ocr_confidence_threshold (default 0.9)
        """
        try:
            tesseract_available = True
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                tesseract_available = False
                easyocr_reader = _get_easyocr_reader() if '_get_easyocr_reader' in globals() else None
            if easyocr_reader is None and not tesseract_available:
                    logger.debug("No OCR backend available (tesseract missing, easyocr not installed)")
                    return None
            
            # Validate frame is not empty
            if frame is None or frame.size == 0 or (hasattr(frame, 'shape') and (frame.shape[0] == 0 or frame.shape[1] == 0)):
                logger.debug("Frame is empty, cannot detect number with OCR")
                return None
            
            if region:
                x, y, w, h = region
                roi = frame[y:y + h, x:x + w]
                # Validate ROI is not empty
                if roi is None or roi.size == 0 or (hasattr(roi, 'shape') and (roi.shape[0] == 0 or roi.shape[1] == 0)):
                    logger.debug("ROI is empty, cannot detect number with OCR")
                    return None
            else:
                roi = frame

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Performance optimization: limit upscaling for very large ROIs
            max_roi_size = 200  # Maximum dimension before reducing upscale factor
            if roi.shape[0] > max_roi_size or roi.shape[1] > max_roi_size:
                # For large ROIs, use smaller upscale factor to reduce processing time
                upscale_factor = 2
            else:
                upscale_factor = 4
            
            gray = cv2.equalizeHist(gray)

            # Upscale and blur for better readability
            scaled = cv2.resize(gray, None, fx=upscale_factor, fy=upscale_factor, interpolation=cv2.INTER_CUBIC)
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

                for variant_name, image_variant in variants:
                    for cfg in ocr_configs:
                        # Get both text and confidence
                        try:
                            data = pytesseract.image_to_data(image_variant, config=cfg, output_type=pytesseract.Output.DICT)
                            # Extract text and confidence
                            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                            texts = [text for text in data['text'] if text.strip()]
                            
                            if texts and confidences:
                                # Get the best confidence score
                                max_confidence = max(confidences) / 100.0  # Convert to 0-1 scale
                                text = ' '.join(texts)
                                digits = "".join(filter(str.isdigit, text))
                                
                                if digits and max_confidence >= self.ocr_confidence_threshold:
                                    try:
                                        number = int(digits)
                                        if 0 <= number <= 36:
                                            logger.debug(
                                                "OCR detected %s from text '%s' with confidence %.2f (variant=%s, cfg=%s)",
                                                number,
                                                text.strip(),
                                                max_confidence,
                                                variant_name,
                                                cfg,
                                            )
                                            return (number, max_confidence)
                                    except ValueError:
                                        continue
                        except Exception as e:
                            # Fallback to simple text extraction if confidence extraction fails
                            logger.debug(f"OCR confidence extraction failed, trying simple method: {e}")
                            try:
                                text = pytesseract.image_to_string(image_variant, config=cfg)
                                digits = "".join(filter(str.isdigit, text))
                                if digits:
                                    try:
                                        number = int(digits)
                                        if 0 <= number <= 36:
                                            # If we can't get confidence, assume low confidence and reject
                                            logger.debug(
                                                "OCR detected %s but confidence unavailable - rejecting (requires >= %.2f)",
                                                number,
                                                self.ocr_confidence_threshold
                                            )
                                            continue
                                    except ValueError:
                                        continue
                            except Exception:
                                continue

            # Use lazy-loaded EasyOCR reader
            easyocr_reader = _get_easyocr_reader() if '_get_easyocr_reader' in globals() else None
            if easyocr_reader is not None:
                # Bypass detector by providing full bounding box
                rgb_scaled = cv2.cvtColor(scaled, cv2.COLOR_GRAY2RGB)
                h, w = rgb_scaled.shape[:2]
                bbox = [[0, 0, w, 0, w, h, 0, h]]
                try:
                    # Try to get detailed results with confidence
                    results = easyocr_reader.readtext(
                        rgb_scaled,
                        detail=1,  # Get confidence scores
                        paragraph=False,
                        allowlist="0123456789",
                    )
                    for result in results:
                        if isinstance(result, (list, tuple)) and len(result) >= 3:
                            # EasyOCR format: (bbox, text, confidence)
                            bbox_coords = result[0]
                            text = result[1]
                            confidence = float(result[2]) / 100.0  # Convert to 0-1 scale
                            
                            if confidence >= self.ocr_confidence_threshold:
                                digits = "".join(filter(str.isdigit, text))
                                if digits:
                                    try:
                                        number = int(digits)
                                        if 0 <= number <= 36:
                                            logger.debug(
                                                "EasyOCR detected %s from text '%s' with confidence %.2f",
                                                number,
                                                text.strip(),
                                                confidence
                                            )
                                            return (number, confidence)
                                    except ValueError:
                                        continue
                        else:
                            # Fallback for detail=0 format
                            text = result if isinstance(result, str) else str(result)
                            digits = "".join(filter(str.isdigit, text))
                            if digits:
                                try:
                                    number = int(digits)
                                    if 0 <= number <= 36:
                                        # Without confidence, reject (requires >= 0.9)
                                        logger.debug(
                                            "EasyOCR detected %s but confidence unavailable - rejecting (requires >= %.2f)",
                                            number,
                                            self.ocr_confidence_threshold
                                        )
                                        continue
                                except ValueError:
                                    continue
                except TypeError:
                    # Fallback to standard readtext if API signature differs
                    try:
                        results = easyocr_reader.readtext(
                            rgb_scaled,
                            detail=1,
                            paragraph=False,
                            allowlist="0123456789",
                        )
                        for result in results:
                            if isinstance(result, (list, tuple)) and len(result) >= 3:
                                # EasyOCR format: (bbox, text, confidence)
                                bbox_coords = result[0]
                                text = result[1]
                                confidence = float(result[2]) / 100.0  # Convert to 0-1 scale
                                
                                if confidence >= self.ocr_confidence_threshold:
                                    digits = "".join(filter(str.isdigit, text))
                                    if digits:
                                        try:
                                            number = int(digits)
                                            if 0 <= number <= 36:
                                                logger.debug(
                                                    "EasyOCR detected %s with confidence %.2f",
                                                    number,
                                                    confidence
                                                )
                                                return (number, confidence)
                                        except ValueError:
                                            continue
                    except Exception as e:
                        logger.debug(f"EasyOCR fallback failed: {e}")

            logger.debug("OCR failed to extract valid number from snapshot.")
            return None
            
        except Exception as e:
            logger.debug(f"OCR detection failed: {e}")
            return None
    
    def detect_number_template(self, frame: np.ndarray, templates_dir: str = "betting-number_templates") -> Optional[int]:
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
            # Validate frame is not empty
            if frame is None or frame.size == 0 or (hasattr(frame, 'shape') and (frame.shape[0] == 0 or frame.shape[1] == 0)):
                logger.debug("Frame is empty, cannot detect number template")
                return None
            
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
            
            # Performance optimization: pre-check frame size to avoid loading templates that won't fit
            frame_h, frame_w = gray.shape[:2]
            
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
                    if template.shape[0] > frame_h or template.shape[1] > frame_w:
                        logger.debug(f"Template {num} ({template.shape[1]}x{template.shape[0]}) larger than frame ({frame_w}x{frame_h})")
                        continue
                    
                    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    # Early exit optimization: if we find a very high confidence match, return immediately
                    if max_val >= 0.95:
                        logger.debug(f"Early exit: found very high confidence template match {num} with score {max_val:.3f}")
                        return num
                    
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
            # Validate frame is not empty
            if frame is None or frame.size == 0 or (hasattr(frame, 'shape') and (frame.shape[0] == 0 or frame.shape[1] == 0)):
                logger.debug("Frame is empty, cannot detect color")
                return None
            
            if region:
                x, y, w, h = region
                roi = frame[y:y+h, x:x+w]
                # Validate ROI is not empty
                if roi is None or roi.size == 0 or (hasattr(roi, 'shape') and (roi.shape[0] == 0 or roi.shape[1] == 0)):
                    logger.debug("ROI is empty, cannot detect color")
                    return None
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
            try:
                frame = self.capture_screen()
            except Exception as e:
                logger.error(f"Frame capture failed in detect_result: {e}")
                return {
                    "number": None,
                    "color": None,
                    "zero": False,
                    "confidence": 0.0,
                    "method": None
                }
        
        # Check if frame is None (video ended or capture failed)
        if frame is None:
            logger.warning("Frame capture returned None (video may have ended or capture failed)")
            return {
                "number": None,
                "color": None,
                "zero": False,
                "confidence": 0.0,
                "method": None
            }
        
        result = {
            "number": None,
            "color": None,
            "zero": False,
            "confidence": 0.0,
            "method": None
        }
        
        # Determine region of interest (winning badge)
        # Note: If screen_region is set, capture_screen() already returns only that region
        # So we use the frame directly as ROI (no need to crop again)
        
        # Check if this is a video frame (FrameDetector)
        is_video_frame = hasattr(self, 'cap') and hasattr(self, 'video_path')
        
        if self.screen_region:
            if is_video_frame:
                # For video frames, extract screen_region from the full frame
                # screen_region format: [x, y, width, height]
                x, y, w, h = self.screen_region
                frame_h, frame_w = frame.shape[:2]
                # Validate coordinates
                if x >= 0 and y >= 0 and x + w <= frame_w and y + h <= frame_h:
                    roi = frame[y:y + h, x:x + w]
                    logger.debug(f"Extracted screen_region ROI from video frame: ({x}, {y}, {w}, {h}) from frame shape {frame.shape}")
                else:
                    logger.warning(
                        f"Invalid screen_region coordinates: ({x}, {y}, {w}, {h}) for frame shape {frame.shape}, using full frame"
                    )
                    roi = frame
            else:
                # For real-time screen capture, frame is already cropped to screen_region by capture_screen()
                # Use it directly as ROI
                roi = frame
        elif is_video_frame:
            # Video frame - extract ROI using video_roi config or try full frame with auto-scaling
            video_roi = self.config.get('detection', {}).get('video_roi')
            if video_roi:
                # Extract ROI from config
                x = video_roi.get('x', 0)
                y = video_roi.get('y', 0)
                w = video_roi.get('width', frame.shape[1])
                h = video_roi.get('height', frame.shape[0])
                # Validate coordinates
                if x >= 0 and y >= 0 and x + w <= frame.shape[1] and y + h <= frame.shape[0]:
                    roi = frame[y:y + h, x:x + w]
                    logger.debug(f"Extracted video ROI: ({x}, {y}, {w}, {h}) from frame shape {frame.shape}")
                else:
                    logger.warning(f"Invalid video_roi coordinates: ({x}, {y}, {w}, {h}) for frame shape {frame.shape}, using center region")
                    # Fallback: use center region (typical badge location)
                    center_x = frame.shape[1] // 2
                    center_y = frame.shape[0] // 2
                    roi_w = min(400, frame.shape[1])
                    roi_h = min(200, frame.shape[0])
                    roi = frame[center_y - roi_h//2:center_y + roi_h//2, center_x - roi_w//2:center_x + roi_w//2]
            else:
                # No video_roi config - try to use center/upper region where badge typically appears
                # For most roulette games, the winning badge is in the center-upper area
                frame_h, frame_w = frame.shape[:2]
                # Extract a reasonable ROI from center-upper region (where badges usually are)
                roi_w = min(600, frame_w)
                roi_h = min(300, frame_h)
                roi_x = (frame_w - roi_w) // 2
                roi_y = max(0, frame_h // 4)  # Upper quarter, but allow some margin
                roi = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
                logger.debug(f"Using default video ROI (center-upper): ({roi_x}, {roi_y}, {roi_w}, {roi_h}) from frame shape {frame.shape}")
        else:
            # Full screen capture - use frame as-is
            roi = frame

        # Try dedicated winning-number templates first
        # Only use template matching if we have templates loaded
        # CRITICAL: Only use winning-number templates, never use betting-number templates
        # This prevents false positives from matching betting grid numbers
        if self.winning_templates:
            badge_match = self.detect_winning_number_template(roi)
            if badge_match is not None:
                number, confidence = badge_match
                # Additional validation: ensure confidence is high enough and number is valid
                # Also verify that this number actually has a template (prevent false matches)
                if confidence >= self.winning_template_threshold and 0 <= number <= 36:
                    # Verify the detected number has a template in our loaded templates
                    template_numbers = [num for num, _ in self.winning_templates]
                    if number in template_numbers:
                        result["number"] = number
                        result["color"] = self.get_color_from_number(number)
                        result["zero"] = (number == 0)
                        result["confidence"] = float(confidence)
                        result["method"] = "template_badge"
                        logger.info(f"Template badge match: number={number}, confidence={confidence:.3f}, template verified")
                    else:
                        logger.warning(
                            f"Template match rejected: number {number} detected but no template exists. "
                            f"Available templates: {sorted(template_numbers)}"
                        )

        # If video frame and ROI matching failed, try full frame with scaled templates
        # BUT: Only if we have templates and ROI matching didn't find anything
        # CRITICAL: Only use winning-number templates, verify template exists
        if result["number"] is None and is_video_frame and roi.shape != frame.shape and self.winning_templates:
            logger.debug("ROI-based template matching failed, trying full frame with scaled search")
            badge_match_full = self.detect_winning_number_template(frame)
            if badge_match_full is not None:
                number, confidence = badge_match_full
                # Additional validation: ensure confidence is high enough and number is valid
                # Also verify that this number actually has a template (prevent false matches)
                if confidence >= self.winning_template_threshold and 0 <= number <= 36:
                    # Verify the detected number has a template in our loaded templates
                    template_numbers = [num for num, _ in self.winning_templates]
                    if number in template_numbers:
                        result["number"] = number
                        result["color"] = self.get_color_from_number(number)
                        result["zero"] = (number == 0)
                        result["confidence"] = float(confidence)
                        result["method"] = "template_badge_fullframe"
                        logger.info(f"Template badge fullframe match: number={number}, confidence={confidence:.3f}, template verified")
                    else:
                        logger.warning(
                            f"Template fullframe match rejected: number {number} detected but no template exists. "
                            f"Available templates: {sorted(template_numbers)}"
                        )

        # DO NOT use generic betting-number templates for winning number detection
        # These templates are from the betting grid and will cause false positives
        # Only use winning-number templates (from winning-number_templates/)
        # If winning templates don't match, we should not detect a number
        # This prevents false positives like detecting number 1 when no template exists
        
        # Fallback to OCR (only if winning templates failed)
        # CRITICAL: Only use OCR if we have no winning templates OR if templates failed
        # Also verify OCR result matches available templates to prevent false positives
        if result["number"] is None:
            ocr_result = self.detect_number_ocr(roi)
            if ocr_result is not None:
                number, confidence = ocr_result
                # Only accept OCR if confidence >= threshold (default 0.9)
                # AND if we have templates, verify the number has a template
                if confidence >= self.ocr_confidence_threshold:
                    # If we have winning templates, verify OCR result matches available template
                    if self.winning_templates:
                        template_numbers = [num for num, _ in self.winning_templates]
                        if number not in template_numbers:
                            logger.warning(
                                f"OCR detection rejected: number {number} detected but no winning template exists. "
                                f"Available templates: {sorted(template_numbers)}. OCR confidence: {confidence:.2f}"
                            )
                        else:
                            result["number"] = number
                            result["color"] = self.get_color_from_number(number)
                            result["zero"] = (number == 0)
                            result["confidence"] = confidence
                            result["method"] = "ocr"
                            logger.info(f"OCR detection accepted: number={number}, confidence={confidence:.2f}, template verified")
                    else:
                        # No templates available, accept OCR if confidence is high
                        result["number"] = number
                        result["color"] = self.get_color_from_number(number)
                        result["zero"] = (number == 0)
                        result["confidence"] = confidence
                        result["method"] = "ocr"
                        logger.info(f"OCR detection accepted (no templates): number={number}, confidence={confidence:.2f}")
                else:
                    logger.debug(
                        f"OCR detection rejected: number={number}, confidence={confidence:.2f} < threshold={self.ocr_confidence_threshold}"
                    )
        
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
            self.detection_history.append(result.copy())  # Store copy to avoid reference issues
            if len(self.detection_history) > self.max_history:
                self.detection_history.pop(0)
            
            # Track recent detections for temporal validation
            self.recent_detections.append({
                "number": result["number"],
                "confidence": result.get("confidence", 0.0),
                "method": result.get("method")
            })
            if len(self.recent_detections) > self.max_recent_detections:
                self.recent_detections.pop(0)
        
        # Performance optimization: clear ROI cache after processing
        self._roi_cache = None
        self._roi_cache_frame_hash = None
        self._roi_cache_age = 0
        
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
        
        # For OCR results, require confidence >= 0.9 (strict requirement)
        if result.get("method") == "ocr":
            if result["confidence"] < self.ocr_confidence_threshold:
                logger.warning(
                    f"OCR result rejected: confidence {result['confidence']:.2f} < threshold {self.ocr_confidence_threshold}"
                )
                return False
        
        # Check confidence threshold (general minimum)
        if result["confidence"] < 0.5:
            return False
        
        # Check if result is consistent with recent history
        if len(self.detection_history) > 1:
            # Should not have same number twice in a row (unless very confident)
            last_number = self.detection_history[-1].get("number")
            if result["number"] == last_number:
                # Reject if confidence is below threshold
                if result["confidence"] < 0.9:
                    logger.warning(
                        "Same number detected twice - may be error. "
                        f"Number: {result['number']}, Confidence: {result['confidence']:.2f} < 0.9"
                    )
                    return False
                else:
                    # Even with high confidence, log it for awareness
                    logger.debug(
                        f"Same number detected twice but high confidence ({result['confidence']:.2f}) - accepting"
                    )
        
        # Temporal validation: reject isolated single-frame detections (likely false positives)
        # This catches cases like frame 5533 where number 8 was detected incorrectly
        # Check if this detection appears isolated (different from previous detection, not seen in recent history)
        if len(self.recent_detections) >= 1:
            current_number = result["number"]
            current_method = result.get("method")
            current_confidence = result.get("confidence", 0.0)
            
            # Get previous detection
            prev_detection = self.recent_detections[-1] if len(self.recent_detections) > 0 else None
            prev_number = prev_detection.get("number") if prev_detection else None
            
            # If this is a template_badge detection that's different from the previous detection
            # and this number doesn't appear in recent history, it might be isolated (false positive)
            if (current_method == "template_badge" and 
                prev_number is not None and 
                current_number != prev_number):
                
                # Check if this number appears in recent detection history (excluding current)
                same_number_in_history = any(
                    d.get("number") == current_number 
                    for d in self.recent_detections
                )
                
                # If this number doesn't appear in recent history (isolated detection),
                # require higher confidence (>= 0.95) to prevent false positives
                # Example: Frame 5533 detected 8 with 0.9335 confidence - this would be rejected
                if not same_number_in_history and current_confidence < 0.95:
                    logger.warning(
                        f"Isolated detection rejected: number {current_number} not seen in recent {len(self.recent_detections)} detections. "
                        f"Confidence {current_confidence:.2f} < 0.95 (required for isolated template_badge detections). "
                        f"Previous detection: {prev_number}"
                    )
                    return False
        
        return True

