"""
Deep Analysis of Detection Issues
Analyzes every aspect of the detection pipeline to find the root cause.
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Colab compatibility
try:
    import pyautogui
except (ImportError, OSError, KeyError, RuntimeError):
    from unittest.mock import MagicMock
    sys.modules['pyautogui'] = MagicMock()

sys.path.insert(0, os.path.abspath('.'))

from backend.app.config_loader import ConfigLoader
from backend.app.detection.frame_detector import FrameDetector
from backend.app.detection.screen_detector import ScreenDetector


def analyze_preprocessing(roi: np.ndarray, template: np.ndarray, detector: ScreenDetector) -> Dict:
    """Analyze preprocessing steps and their effects."""
    print("\n" + "=" * 80)
    print("ANALYZING PREPROCESSING PIPELINE")
    print("=" * 80)
    
    results = {}
    
    # Original ROI
    print(f"\n1. Original ROI:")
    print(f"   Shape: {roi.shape}")
    print(f"   Dtype: {roi.dtype}")
    print(f"   Min/Max: {roi.min()}/{roi.max()}")
    if len(roi.shape) == 3:
        print(f"   Channels: {roi.shape[2]} (BGR)")
    else:
        print(f"   Grayscale")
    
    # Convert to grayscale if needed
    if len(roi.shape) == 3:
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        print(f"\n2. After BGR to Grayscale:")
        print(f"   Shape: {roi_gray.shape}")
        print(f"   Min/Max: {roi_gray.min()}/{roi_gray.max()}")
        print(f"   Mean: {roi_gray.mean():.1f}, Std: {roi_gray.std():.1f}")
    else:
        roi_gray = roi.copy()
        print(f"\n2. Already grayscale")
    
    # Apply preprocessing (same as detector)
    roi_processed = detector._preprocess_badge_image(roi_gray)
    print(f"\n3. After preprocessing (equalizeHist + GaussianBlur):")
    print(f"   Shape: {roi_processed.shape}")
    print(f"   Min/Max: {roi_processed.min()}/{roi_processed.max()}")
    print(f"   Mean: {roi_processed.mean():.1f}, Std: {roi_processed.std():.1f}")
    
    # Template info
    print(f"\n4. Template:")
    print(f"   Shape: {template.shape}")
    print(f"   Dtype: {template.dtype}")
    print(f"   Min/Max: {template.min()}/{template.max()}")
    print(f"   Mean: {template.mean():.1f}, Std: {template.std():.1f}")
    
    # Check size compatibility
    h_roi, w_roi = roi_processed.shape
    h_t, w_t = template.shape
    
    print(f"\n5. Size Analysis:")
    print(f"   ROI size: {w_roi}x{h_roi}")
    print(f"   Template size: {w_t}x{h_t}")
    
    if w_roi == w_t and h_roi == h_t:
        print(f"    Same size - no resize needed")
        needs_resize = False
    else:
        print(f"     Different sizes - resize needed")
        print(f"   Aspect ratio ROI: {w_roi/h_roi:.2f}")
        print(f"   Aspect ratio Template: {w_t/h_t:.2f}")
        if abs((w_roi/h_roi) - (w_t/h_t)) > 0.1:
            print(f"     WARNING: Aspect ratios differ significantly!")
            print(f"      Resize will distort the image!")
        needs_resize = True
    
    # Test resize
    if needs_resize:
        roi_resized = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
        print(f"\n6. After resize to template size:")
        print(f"   Shape: {roi_resized.shape}")
        print(f"   Min/Max: {roi_resized.min()}/{roi_resized.max()}")
        print(f"   Mean: {roi_resized.mean():.1f}, Std: {roi_resized.std():.1f}")
        
        # Check if resize caused issues
        if roi_resized.std() < 5:
            print(f"     WARNING: Very low std after resize - image might be too uniform")
    else:
        roi_resized = roi_processed
    
    # Save intermediate images for inspection
    cv2.imwrite('deep_analysis_roi_original.png', roi)
    cv2.imwrite('deep_analysis_roi_gray.png', roi_gray)
    cv2.imwrite('deep_analysis_roi_processed.png', roi_processed)
    if needs_resize:
        cv2.imwrite('deep_analysis_roi_resized.png', roi_resized)
    cv2.imwrite('deep_analysis_template.png', template)
    
    # Create side-by-side comparison
    if needs_resize:
        comparison = np.hstack([roi_processed, cv2.resize(roi_processed, (w_t, h_t)), template])
        cv2.imwrite('deep_analysis_comparison.png', comparison)
        print(f"\n Saved comparison image: deep_analysis_comparison.png")
        print(f"   Left: ROI processed, Middle: ROI resized, Right: Template")
    
    results['roi_original'] = roi
    results['roi_processed'] = roi_processed
    results['roi_resized'] = roi_resized if needs_resize else roi_processed
    results['template'] = template
    results['needs_resize'] = needs_resize
    
    return results


def test_template_matching_variations(roi: np.ndarray, template: np.ndarray, detector: ScreenDetector) -> Dict:
    """Test different template matching approaches."""
    print("\n" + "=" * 80)
    print("TESTING TEMPLATE MATCHING VARIATIONS")
    print("=" * 80)
    
    results = {}
    
    # Standard approach (current)
    roi_processed = detector._preprocess_badge_image(roi)
    h_t, w_t = template.shape
    roi_resized = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
    
    # Test different interpolation methods
    interpolation_methods = {
        'INTER_AREA': cv2.INTER_AREA,
        'INTER_LINEAR': cv2.INTER_LINEAR,
        'INTER_CUBIC': cv2.INTER_CUBIC,
        'INTER_NEAREST': cv2.INTER_NEAREST,
    }
    
    print(f"\n1. Testing different resize interpolation methods:")
    resize_scores = {}
    for name, method in interpolation_methods.items():
        roi_resized_var = cv2.resize(roi_processed, (w_t, h_t), interpolation=method)
        result = cv2.matchTemplate(roi_resized_var, template, cv2.TM_CCOEFF_NORMED)
        score = float(result[0][0])
        resize_scores[name] = score
        marker = "" if score > 0.3 else "" if score > 0 else ""
        print(f"   {marker} {name}: {score:.3f}")
    
    best_resize_method = max(resize_scores, key=resize_scores.get)
    best_resize_score = resize_scores[best_resize_method]
    results['best_resize_method'] = best_resize_method
    results['best_resize_score'] = best_resize_score
    
    # Test different template matching methods
    print(f"\n2. Testing different template matching methods:")
    matching_methods = {
        'TM_CCOEFF_NORMED': cv2.TM_CCOEFF_NORMED,
        'TM_CCORR_NORMED': cv2.TM_CCORR_NORMED,
        'TM_SQDIFF_NORMED': cv2.TM_SQDIFF_NORMED,
    }
    
    match_scores = {}
    for name, method in matching_methods.items():
        result = cv2.matchTemplate(roi_resized, template, method)
        if method == cv2.TM_SQDIFF_NORMED:
            score = 1.0 - float(result[0][0])  # Invert for SQDIFF
        else:
            score = float(result[0][0])
        match_scores[name] = score
        marker = "" if score > 0.3 else "" if score > 0 else ""
        print(f"   {marker} {name}: {score:.3f}")
    
    best_match_method = max(match_scores, key=match_scores.get)
    best_match_score = match_scores[best_match_method]
    results['best_match_method'] = best_match_method
    results['best_match_score'] = best_match_score
    
    # Test without preprocessing
    print(f"\n3. Testing without preprocessing:")
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    roi_no_preprocess = cv2.resize(roi_gray, (w_t, h_t), interpolation=cv2.INTER_AREA)
    result = cv2.matchTemplate(roi_no_preprocess, template, cv2.TM_CCOEFF_NORMED)
    score_no_preprocess = float(result[0][0])
    marker = "" if score_no_preprocess > 0.3 else "" if score_no_preprocess > 0 else ""
    print(f"   {marker} Without preprocessing: {score_no_preprocess:.3f}")
    results['score_no_preprocess'] = score_no_preprocess
    
    # Test with different preprocessing
    print(f"\n4. Testing alternative preprocessing:")
    
    # No equalization
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    roi_no_eq = cv2.GaussianBlur(roi_gray, (3, 3), 0)
    roi_no_eq_resized = cv2.resize(roi_no_eq, (w_t, h_t), interpolation=cv2.INTER_AREA)
    result = cv2.matchTemplate(roi_no_eq_resized, template, cv2.TM_CCOEFF_NORMED)
    score_no_eq = float(result[0][0])
    marker = "" if score_no_eq > 0.3 else "" if score_no_eq > 0 else ""
    print(f"   {marker} Without equalizeHist: {score_no_eq:.3f}")
    results['score_no_eq'] = score_no_eq
    
    # No blur
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    roi_no_blur = cv2.equalizeHist(roi_gray)
    roi_no_blur_resized = cv2.resize(roi_no_blur, (w_t, h_t), interpolation=cv2.INTER_AREA)
    result = cv2.matchTemplate(roi_no_blur_resized, template, cv2.TM_CCOEFF_NORMED)
    score_no_blur = float(result[0][0])
    marker = "" if score_no_blur > 0.3 else "" if score_no_blur > 0 else ""
    print(f"   {marker} Without GaussianBlur: {score_no_blur:.3f}")
    results['score_no_blur'] = score_no_blur
    
    # No preprocessing at all
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    roi_raw_resized = cv2.resize(roi_gray, (w_t, h_t), interpolation=cv2.INTER_AREA)
    result = cv2.matchTemplate(roi_raw_resized, template, cv2.TM_CCOEFF_NORMED)
    score_raw = float(result[0][0])
    marker = "" if score_raw > 0.3 else "" if score_raw > 0 else ""
    print(f"   {marker} Raw (no preprocessing): {score_raw:.3f}")
    results['score_raw'] = score_raw
    
    return results


def analyze_template_quality(template_path: Path) -> Dict:
    """Analyze template image quality."""
    print("\n" + "=" * 80)
    print("ANALYZING TEMPLATE QUALITY")
    print("=" * 80)
    
    img = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f" Cannot load template: {template_path}")
        return {}
    
    print(f"\nTemplate: {template_path.name}")
    print(f"   Size: {img.shape[1]}x{img.shape[0]}")
    print(f"   Min/Max: {img.min()}/{img.max()}")
    print(f"   Mean: {img.mean():.1f}, Std: {img.std():.1f}")
    
    # Check if template is too uniform
    if img.std() < 10:
        print(f"     WARNING: Very low std ({img.std():.1f}) - template might be too uniform")
    
    # Check contrast
    contrast = img.max() - img.min()
    print(f"   Contrast: {contrast}")
    if contrast < 50:
        print(f"     WARNING: Low contrast - template might not be clear")
    
    # Check if mostly black or white
    black_pixels = np.sum(img < 50)
    white_pixels = np.sum(img > 200)
    total_pixels = img.size
    black_ratio = black_pixels / total_pixels
    white_ratio = white_pixels / total_pixels
    
    print(f"   Black pixels (<50): {black_ratio*100:.1f}%")
    print(f"   White pixels (>200): {white_ratio*100:.1f}%")
    
    if black_ratio > 0.8:
        print(f"     WARNING: Template is mostly black")
    if white_ratio > 0.8:
        print(f"     WARNING: Template is mostly white")
    
    return {
        'size': img.shape,
        'std': img.std(),
        'contrast': contrast,
        'black_ratio': black_ratio,
        'white_ratio': white_ratio
    }


def main():
    """Run deep analysis."""
    print("=" * 80)
    print("DEEP DETECTION ANALYSIS")
    print("=" * 80)
    
    config_path = 'config/default_config.json'
    video_path = 'roleta_brazileria.mp4'
    start_frame = 690
    
    # Find video
    if not Path(video_path).exists():
        video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov'))]
        if video_files:
            video_path = video_files[0]
    
    # Load config
    config = ConfigLoader.load_config(config_path)
    detection_config = config.get('detection', {})
    screen_region = detection_config.get('screen_region', [])
    
    if not screen_region or len(screen_region) != 4:
        print(" Screen region not configured")
        return
    
    x, y, w, h = screen_region
    
    # Initialize detector
    detector = ScreenDetector(config)
    
    if len(detector.winning_templates) == 0:
        print(" No templates loaded")
        return
    
    print(f"\nLoaded {len(detector.winning_templates)} templates")
    template_numbers = [t[0] for t in detector.winning_templates]
    print(f"Template numbers: {template_numbers}")
    
    # Get a frame
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f" Cannot open video")
        return
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    ret, frame = cap.read()
    if not ret:
        print(f" Cannot read frame")
        cap.release()
        return
    
    # Extract ROI
    roi = frame[y:y+h, x:x+w]
    if roi.size == 0:
        print(f" ROI is empty")
        cap.release()
        return
    
    print(f"\n Extracted ROI: {roi.shape}")
    cap.release()
    
    # Get first template for analysis
    first_template_num, first_template = detector.winning_templates[0]
    print(f"\nUsing template number {first_template_num} for analysis")
    
    # Analyze preprocessing
    preprocess_results = analyze_preprocessing(roi, first_template, detector)
    
    # Test template matching variations
    matching_results = test_template_matching_variations(roi, first_template, detector)
    
    # Analyze template quality
    templates_dir = Path(detection_config.get('winning_templates_dir', 'winning-number_templates/'))
    if not templates_dir.is_absolute():
        templates_dir = Path.cwd() / templates_dir
    
    template_files = list(templates_dir.glob(f"*{first_template_num}*.png"))
    if template_files:
        template_quality = analyze_template_quality(template_files[0])
    
    # Summary
    print("\n" + "=" * 80)
    print("DEEP ANALYSIS SUMMARY")
    print("=" * 80)
    
    print(f"\nBest resize method: {matching_results.get('best_resize_method')} "
          f"(score: {matching_results.get('best_resize_score', 0):.3f})")
    print(f"Best match method: {matching_results.get('best_match_method')} "
          f"(score: {matching_results.get('best_match_score', 0):.3f})")
    print(f"Without preprocessing: {matching_results.get('score_no_preprocess', 0):.3f}")
    print(f"Raw (no preprocessing): {matching_results.get('score_raw', 0):.3f}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    best_score = max([
        matching_results.get('best_resize_score', -1),
        matching_results.get('best_match_score', -1),
        matching_results.get('score_no_preprocess', -1),
        matching_results.get('score_raw', -1)
    ])
    
    if best_score > 0.5:
        print(f" Found good match! Score: {best_score:.3f}")
        print(f"   Consider using the method that achieved this score")
    elif best_score > 0.3:
        print(f"  Moderate match. Score: {best_score:.3f}")
        print(f"   Lower threshold or improve preprocessing")
    elif best_score > 0:
        print(f"  Weak match. Score: {best_score:.3f}")
        print(f"   Templates might not match video style")
        print(f"   Consider recreating templates from this video")
    else:
        print(f" All scores negative or very low")
        print(f"   Critical issue - templates don't match ROI at all")
        print(f"   Possible causes:")
        print(f"   1. ROI doesn't contain the winning number")
        print(f"   2. Templates from different video/game")
        print(f"   3. Preprocessing is destroying the match")
        print(f"   4. Size/aspect ratio mismatch causing distortion")
    
    print("\n" + "=" * 80)
    print("Check saved images for visual analysis:")
    print("  - deep_analysis_comparison.png (ROI vs Template)")
    print("  - deep_analysis_roi_processed.png (Processed ROI)")
    print("  - deep_analysis_template.png (Template)")
    print("=" * 80)


if __name__ == '__main__':
    main()

