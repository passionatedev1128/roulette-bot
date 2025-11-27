"""
Fix Template Inversion Issue
Tests if templates need to be inverted to match ROI
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


def test_template_inversion(roi: np.ndarray, template: np.ndarray, detector: ScreenDetector) -> Dict:
    """Test if template needs to be inverted."""
    results = {}
    
    # Convert ROI to grayscale
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    
    h_t, w_t = template.shape
    h_roi, w_roi = roi_gray.shape
    
    # Test 1: Standard approach (current)
    roi_processed = detector._preprocess_badge_image(roi_gray)
    roi_resized = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
    result = cv2.matchTemplate(roi_resized, template, cv2.TM_CCOEFF_NORMED)
    score_standard = float(result[0][0])
    results['standard'] = score_standard
    
    # Test 2: Invert ROI
    roi_inverted = cv2.bitwise_not(roi_gray)
    roi_inv_processed = detector._preprocess_badge_image(roi_inverted)
    roi_inv_resized = cv2.resize(roi_inv_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
    result = cv2.matchTemplate(roi_inv_resized, template, cv2.TM_CCOEFF_NORMED)
    score_roi_inverted = float(result[0][0])
    results['roi_inverted'] = score_roi_inverted
    
    # Test 3: Invert template
    template_inverted = cv2.bitwise_not(template)
    result = cv2.matchTemplate(roi_resized, template_inverted, cv2.TM_CCOEFF_NORMED)
    score_template_inverted = float(result[0][0])
    results['template_inverted'] = score_template_inverted
    
    # Test 4: Invert both
    result = cv2.matchTemplate(roi_inv_resized, template_inverted, cv2.TM_CCOEFF_NORMED)
    score_both_inverted = float(result[0][0])
    results['both_inverted'] = score_both_inverted
    
    # Test 5: No preprocessing, standard
    roi_raw_resized = cv2.resize(roi_gray, (w_t, h_t), interpolation=cv2.INTER_AREA)
    result = cv2.matchTemplate(roi_raw_resized, template, cv2.TM_CCOEFF_NORMED)
    score_raw = float(result[0][0])
    results['raw'] = score_raw
    
    # Test 6: No preprocessing, ROI inverted
    roi_inv_raw_resized = cv2.resize(roi_inverted, (w_t, h_t), interpolation=cv2.INTER_AREA)
    result = cv2.matchTemplate(roi_inv_raw_resized, template, cv2.TM_CCOEFF_NORMED)
    score_raw_roi_inv = float(result[0][0])
    results['raw_roi_inverted'] = score_raw_roi_inv
    
    # Test 7: No preprocessing, template inverted
    result = cv2.matchTemplate(roi_raw_resized, template_inverted, cv2.TM_CCOEFF_NORMED)
    score_raw_template_inv = float(result[0][0])
    results['raw_template_inverted'] = score_raw_template_inv
    
    return results


def fix_templates_inversion(templates_dir: Path, output_dir: Optional[Path] = None) -> bool:
    """Invert all templates and save them."""
    if output_dir is None:
        output_dir = templates_dir / 'inverted'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    template_files = list(templates_dir.glob("*.png"))
    if not template_files:
        print(" No template files found")
        return False
    
    print(f"\nInverting {len(template_files)} templates...")
    
    for template_file in template_files:
        img = cv2.imread(str(template_file), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        
        # Invert
        img_inverted = cv2.bitwise_not(img)
        
        # Save
        output_path = output_dir / template_file.name
        cv2.imwrite(str(output_path), img_inverted)
        print(f"    {template_file.name}  {output_path.name}")
    
    print(f"\n Inverted templates saved to: {output_dir}")
    return True


def main():
    """Main function."""
    print("=" * 80)
    print("FIXING TEMPLATE INVERSION ISSUE")
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
    
    # Get a frame and ROI
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(" Cannot open video")
        return
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(" Cannot read frame")
        return
    
    roi = frame[y:y+h, x:x+w]
    if roi.size == 0:
        print(" ROI is empty")
        return
    
    print(f"\n Extracted ROI: {roi.shape}")
    
    # Test with first template
    first_template_num, first_template = detector.winning_templates[0]
    print(f"\nTesting with template number {first_template_num}...")
    
    # Test inversion
    print("\n" + "=" * 80)
    print("TESTING TEMPLATE INVERSION")
    print("=" * 80)
    
    inversion_results = test_template_inversion(roi, first_template, detector)
    
    print(f"\nTest Results:")
    print(f"   1. Standard (current): {inversion_results['standard']:.3f}")
    print(f"   2. ROI inverted: {inversion_results['roi_inverted']:.3f}")
    print(f"   3. Template inverted: {inversion_results['template_inverted']:.3f}")
    print(f"   4. Both inverted: {inversion_results['both_inverted']:.3f}")
    print(f"   5. Raw (no preprocessing): {inversion_results['raw']:.3f}")
    print(f"   6. Raw, ROI inverted: {inversion_results['raw_roi_inverted']:.3f}")
    print(f"   7. Raw, template inverted: {inversion_results['raw_template_inverted']:.3f}")
    
    # Find best approach
    best_method = max(inversion_results.items(), key=lambda x: x[1])
    best_score = best_method[1]
    best_name = best_method[0]
    
    print(f"\n" + "=" * 80)
    print("BEST APPROACH")
    print("=" * 80)
    print(f"Best method: {best_name}")
    print(f"Best score: {best_score:.3f}")
    
    if best_score > 0.5:
        print(f" Excellent match found!")
    elif best_score > 0.3:
        print(f"  Good match found")
    elif best_score > 0:
        print(f"  Weak match found")
    else:
        print(f" All scores negative - inversion is not the issue")
    
    # Recommendations
    print(f"\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if 'template_inverted' in best_name or 'both_inverted' in best_name:
        print(f" Templates need to be inverted!")
        print(f"\nOption 1: Invert templates and save")
        templates_dir = Path(detection_config.get('winning_templates_dir', 'winning-number_templates/'))
        if not templates_dir.is_absolute():
            templates_dir = Path.cwd() / templates_dir
        
        response = input(f"\nInvert templates in {templates_dir}? (y/n): ")
        if response.lower() == 'y':
            # Backup originals
            backup_dir = templates_dir / 'original_backup'
            backup_dir.mkdir(exist_ok=True)
            for template_file in templates_dir.glob("*.png"):
                import shutil
                shutil.copy(template_file, backup_dir / template_file.name)
            print(f" Backed up originals to {backup_dir}")
            
            # Invert and overwrite
            for template_file in templates_dir.glob("*.png"):
                img = cv2.imread(str(template_file), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img_inverted = cv2.bitwise_not(img)
                    cv2.imwrite(str(template_file), img_inverted)
                    print(f"    Inverted {template_file.name}")
            
            print(f"\n Templates inverted! Re-run detection to test.")
        else:
            print(f"\n To invert templates manually:")
            print(f"   1. Load each template")
            print(f"   2. Apply cv2.bitwise_not()")
            print(f"   3. Save back")
    
    elif 'roi_inverted' in best_name:
        print(f"  ROI needs to be inverted (unusual)")
        print(f"   This might indicate a color space issue")
        print(f"   Check if ROI extraction is correct")
    
    elif best_score > 0.3:
        print(f" Good match found with method: {best_name}")
        print(f"   Consider updating detection code to use this method")
    
    else:
        print(f" Inversion is not the issue")
        print(f"   All scores are negative")
        print(f"   Check if ROI actually contains the winning number")
        print(f"   Verify templates match the video style")
    
    # Save comparison images
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    roi_inverted = cv2.bitwise_not(roi_gray)
    template_inverted = cv2.bitwise_not(first_template)
    
    cv2.imwrite('inversion_test_roi_original.png', roi_gray)
    cv2.imwrite('inversion_test_roi_inverted.png', roi_inverted)
    cv2.imwrite('inversion_test_template_original.png', first_template)
    cv2.imwrite('inversion_test_template_inverted.png', template_inverted)
    
    # Create comparison
    h_t, w_t = first_template.shape
    roi_resized = cv2.resize(roi_gray, (w_t, h_t))
    comparison = np.hstack([
        roi_resized,
        cv2.bitwise_not(roi_resized),
        first_template,
        template_inverted
    ])
    cv2.imwrite('inversion_test_comparison.png', comparison)
    
    print(f"\n Saved comparison images:")
    print(f"   - inversion_test_comparison.png (shows all variations)")
    print(f"   - Check these images to see which matches best")


if __name__ == '__main__':
    main()

