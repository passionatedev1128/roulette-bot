"""
Comprehensive Detection Diagnostic Script
Systematically checks all aspects of detection to identify issues.
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
    mock_pyautogui = sys.modules['pyautogui']
    mock_pyautogui.screenshot = MagicMock(return_value=None)
    mock_pyautogui.moveTo = MagicMock()
    mock_pyautogui.click = MagicMock()
    mock_pyautogui.write = MagicMock()
    mock_pyautogui.press = MagicMock()
    mock_pyautogui.PAUSE = 0.1
    mock_pyautogui.FAILSAFE = False

sys.path.insert(0, os.path.abspath('.'))

from backend.app.config_loader import ConfigLoader
from backend.app.detection.frame_detector import FrameDetector
from backend.app.detection.screen_detector import ScreenDetector


def check_templates(config: Dict) -> Tuple[bool, List[str]]:
    """Check if templates are loading correctly."""
    print("\n" + "=" * 80)
    print("STEP 1: CHECKING TEMPLATES")
    print("=" * 80)
    
    issues = []
    detector = ScreenDetector(config)
    
    templates_dir = config.get('detection', {}).get('winning_templates_dir', 'winning-number_templates/')
    print(f"Templates directory: {templates_dir}")
    print(f"Current working directory: {Path.cwd()}")
    
    template_path = Path(templates_dir)
    if not template_path.is_absolute():
        # Try multiple locations
        possible_paths = [
            template_path,
            Path.cwd() / template_path,
        ]
        current = Path.cwd()
        for parent in [current] + list(current.parents)[:3]:
            possible_paths.append(parent / template_path)
        
        found = False
        for path in possible_paths:
            if path.exists() and path.is_dir():
                template_path = path
                found = True
                print(f" Found templates directory at: {template_path.absolute()}")
                break
        
        if not found:
            print(f" Templates directory NOT FOUND!")
            print(f"   Tried locations:")
            for p in possible_paths[:5]:
                print(f"      - {p.absolute()}")
            issues.append("Templates directory not found")
            return False, issues
    else:
        if not template_path.exists():
            print(f" Templates directory NOT FOUND at: {template_path}")
            issues.append("Templates directory not found")
            return False, issues
        print(f" Templates directory exists: {template_path}")
    
    # Check templates loaded
    print(f"\nTemplates loaded by detector: {len(detector.winning_templates)}")
    if len(detector.winning_templates) == 0:
        print(" No templates loaded!")
        issues.append("No templates loaded by detector")
        
        # Check if files exist
        template_files = list(template_path.glob("*.png"))
        print(f"   Template files found in directory: {len(template_files)}")
        if template_files:
            print(f"   Examples: {[f.name for f in template_files[:5]]}")
            issues.append("Templates exist but not loaded - check file naming or format")
        else:
            issues.append("No template files found in directory")
        return False, issues
    else:
        template_numbers = sorted([t[0] for t in detector.winning_templates])
        print(f" Templates loaded: {len(detector.winning_templates)}")
        print(f"   Template numbers: {template_numbers}")
        return True, issues


def check_video_and_roi(video_path: str, config: Dict, start_frame: int = 690) -> Tuple[bool, Optional[np.ndarray], Dict]:
    """Check video and extract ROI."""
    print("\n" + "=" * 80)
    print("STEP 2: CHECKING VIDEO AND ROI")
    print("=" * 80)
    
    issues = []
    
    if not Path(video_path).exists():
        print(f" Video file not found: {video_path}")
        issues.append("Video file not found")
        return False, None, {'issues': issues}
    
    print(f" Video file found: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f" Cannot open video file")
        issues.append("Cannot open video file")
        return False, None, {'issues': issues}
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f" Video opened successfully")
    print(f"   Total frames: {total_frames}")
    print(f"   FPS: {fps:.2f}")
    print(f"   Resolution: {width}x{height}")
    print(f"   Start frame: {start_frame}")
    
    if start_frame >= total_frames:
        print(f"  Start frame ({start_frame}) >= total frames ({total_frames})")
        start_frame = 0
        print(f"   Using frame 0 instead")
    
    # Set frame position
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    # Read frame
    ret, frame = cap.read()
    if not ret:
        print(f" Cannot read frame {start_frame}")
        issues.append("Cannot read frame from video")
        cap.release()
        return False, None, {'issues': issues}
    
    print(f" Frame {start_frame} read successfully: {frame.shape}")
    
    # Check screen region
    screen_region = config.get('detection', {}).get('screen_region', [])
    print(f"\nScreen region: {screen_region}")
    print(f"   Format: [x, y, width, height]")
    
    if not screen_region or len(screen_region) != 4:
        print(f" Screen region not configured or invalid")
        issues.append("Screen region not configured")
        cap.release()
        return False, frame, {'issues': issues}
    
    x, y, w, h = screen_region
    print(f"   Coordinates: x={x}, y={y}, width={w}, height={h}")
    
    # Check if region is within frame bounds
    if x < 0 or y < 0 or x + w > width or y + h > height:
        print(f"  WARNING: Screen region extends beyond frame bounds!")
        print(f"   Frame bounds: 0-{width} (width), 0-{height} (height)")
        print(f"   Region bounds: {x}-{x+w} (width), {y}-{y+h} (height)")
        issues.append("Screen region out of bounds")
    
    # Extract ROI
    roi = frame[y:y+h, x:x+w]
    print(f" ROI extracted: {roi.shape}")
    
    # Check ROI quality
    if roi.size == 0:
        print(f" ROI is empty!")
        issues.append("ROI is empty")
        cap.release()
        return False, frame, {'issues': issues}
    
    # Check ROI variance (empty regions have low variance)
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    variance = np.var(roi_gray)
    print(f"   ROI variance: {variance:.1f}")
    
    if variance < 100:
        print(f"  WARNING: ROI variance is very low - region might be empty/blank")
        issues.append("ROI variance too low")
    
    # Save ROI for inspection
    roi_path = 'diagnostic_roi.png'
    cv2.imwrite(roi_path, roi)
    print(f" ROI saved to: {roi_path}")
    print(f"   👀 CHECK THIS IMAGE - Does it show the winning number?")
    
    # Save full frame with ROI marked
    frame_marked = frame.copy()
    cv2.rectangle(frame_marked, (x, y), (x+w, y+h), (0, 255, 0), 2)
    frame_path = 'diagnostic_frame_with_roi.png'
    cv2.imwrite(frame_path, frame_marked)
    print(f" Full frame with ROI marked saved to: {frame_path}")
    
    cap.release()
    
    return True, frame, {
        'roi': roi,
        'roi_path': roi_path,
        'frame_path': frame_path,
        'frame_shape': frame.shape,
        'roi_shape': roi.shape,
        'roi_variance': variance,
        'issues': issues
    }


def test_template_matching(roi: np.ndarray, detector: ScreenDetector, threshold: float) -> Dict:
    """Test template matching on ROI."""
    print("\n" + "=" * 80)
    print("STEP 3: TESTING TEMPLATE MATCHING")
    print("=" * 80)
    
    if len(detector.winning_templates) == 0:
        print(" No templates available for matching")
        return {'success': False, 'best_match': None, 'best_score': 0, 'all_scores': {}}
    
    print(f"Testing {len(detector.winning_templates)} templates...")
    
    # Preprocess ROI
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    roi_processed = detector._preprocess_badge_image(roi_gray)
    
    # Try matching all templates
    all_scores = {}
    best_match = None
    best_score = -1.0
    
    for number, template in detector.winning_templates:
        h_t, w_t = template.shape
        roi_resized = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
        
        try:
            result = cv2.matchTemplate(roi_resized, template, cv2.TM_CCOEFF_NORMED)
            score = float(result[0][0])
            all_scores[number] = score
            
            if score > best_score:
                best_score = score
                best_match = number
        except Exception as e:
            print(f"     Error matching template {number}: {e}")
            all_scores[number] = -1.0
    
    # Show results
    print(f"\nTemplate Matching Results:")
    print(f"   Best match: {best_match} (score: {best_score:.3f})")
    print(f"   Threshold: {threshold}")
    
    if best_match is not None:
        if best_score >= threshold:
            print(f"    Match above threshold!")
        else:
            print(f"    Match below threshold!")
            print(f"    Try lowering threshold to {best_score:.2f}")
        
        # Show top 5 matches
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        print(f"\n   Top 5 matches:")
        for i, (num, score) in enumerate(sorted_scores[:5], 1):
            marker = "" if score >= threshold else "  "
            print(f"   {marker} {i}. Number {num}: {score:.3f}")
    
    return {
        'success': best_match is not None,
        'best_match': best_match,
        'best_score': best_score,
        'all_scores': all_scores,
        'above_threshold': best_score >= threshold if best_match is not None else False
    }


def test_ocr(roi: np.ndarray, detector: ScreenDetector) -> Dict:
    """Test OCR on ROI."""
    print("\n" + "=" * 80)
    print("STEP 4: TESTING OCR FALLBACK")
    print("=" * 80)
    
    if not detector.enable_ocr_fallback:
        print("  OCR fallback is DISABLED")
        return {'success': False, 'enabled': False, 'reason': 'OCR disabled'}
    
    print(f"OCR fallback: ENABLED")
    print(f"OCR confidence threshold: {detector.ocr_confidence_threshold}")
    
    # Try OCR
    number = detector.detect_number_ocr(roi)
    
    if number is not None:
        print(f" OCR detected number: {number}")
        return {'success': True, 'number': number, 'enabled': True}
    else:
        print(f" OCR did not detect a number")
        print(f"   This could mean:")
        print(f"   - ROI is empty/blank")
        print(f"   - OCR cannot read the number")
        print(f"   - Confidence below threshold ({detector.ocr_confidence_threshold})")
        return {'success': False, 'number': None, 'enabled': True}


def test_multiple_frames(video_path: str, config: Dict, start_frame: int = 690, num_frames: int = 20) -> Dict:
    """Test detection on multiple frames."""
    print("\n" + "=" * 80)
    print("STEP 5: TESTING MULTIPLE FRAMES")
    print("=" * 80)
    
    detector = ScreenDetector(config)
    frame_detector = FrameDetector(config, video_path)
    frame_detector.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    detections = []
    frame_numbers = []
    
    print(f"Testing {num_frames} frames starting from frame {start_frame}...")
    
    for i in range(num_frames):
        frame = frame_detector.capture_screen()
        if frame is None:
            break
        
        frame_num = start_frame + i
        detection = detector.detect_result(frame)
        
        if detection and detection.get('number') is not None:
            detections.append(detection)
            frame_numbers.append(frame_num)
            print(f"   Frame {frame_num}:  Detected {detection.get('number')} "
                  f"(method: {detection.get('method')}, confidence: {detection.get('confidence', 0):.2f})")
        else:
            if i < 5:  # Show first 5 failures
                print(f"   Frame {frame_num}:  No detection")
    
    frame_detector.release()
    
    success_rate = len(detections) / num_frames * 100 if num_frames > 0 else 0
    print(f"\nDetection Results:")
    print(f"   Successful: {len(detections)}/{num_frames}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    if detections:
        methods = {}
        for d in detections:
            method = d.get('method', 'unknown')
            methods[method] = methods.get(method, 0) + 1
        print(f"   Methods used: {methods}")
    
    return {
        'total_frames': num_frames,
        'successful': len(detections),
        'success_rate': success_rate,
        'detections': detections,
        'frame_numbers': frame_numbers
    }


def main():
    """Run comprehensive diagnostic."""
    print("=" * 80)
    print("COMPREHENSIVE DETECTION DIAGNOSTIC")
    print("=" * 80)
    
    # Configuration
    config_path = 'config/default_config.json'
    video_path = 'roleta_brazileria.mp4'
    start_frame = 690
    
    # Find video file
    if not Path(video_path).exists():
        video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov'))]
        if video_files:
            video_path = video_files[0]
            print(f"Using video: {video_path}")
        else:
            print(f" No video file found!")
            return
    
    # Load config
    if not Path(config_path).exists():
        print(f" Config file not found: {config_path}")
        return
    
    config = ConfigLoader.load_config(config_path)
    detection_config = config.get('detection', {})
    threshold = detection_config.get('winning_template_threshold', 0.65)
    
    print(f"\nConfiguration:")
    print(f"   Config: {config_path}")
    print(f"   Video: {video_path}")
    print(f"   Start frame: {start_frame}")
    print(f"   Template threshold: {threshold}")
    print(f"   OCR fallback: {detection_config.get('enable_ocr_fallback', True)}")
    print(f"   OCR threshold: {detection_config.get('ocr_confidence_threshold', 70.0)}")
    
    # Step 1: Check templates
    templates_ok, template_issues = check_templates(config)
    
    # Step 2: Check video and ROI
    video_ok, frame, video_info = check_video_and_roi(video_path, config, start_frame)
    
    if not video_ok or frame is None:
        print("\n Cannot proceed - video or ROI check failed")
        return
    
    # Step 3: Test template matching
    if templates_ok and 'roi' in video_info:
        template_results = test_template_matching(video_info['roi'], ScreenDetector(config), threshold)
    else:
        template_results = {'success': False, 'reason': 'Templates not loaded or ROI invalid'}
    
    # Step 4: Test OCR
    if 'roi' in video_info:
        ocr_results = test_ocr(video_info['roi'], ScreenDetector(config))
    else:
        ocr_results = {'success': False, 'reason': 'ROI invalid'}
    
    # Step 5: Test multiple frames
    multi_frame_results = test_multiple_frames(video_path, config, start_frame, num_frames=20)
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    print(f"\n Templates: {'OK' if templates_ok else 'ISSUES FOUND'}")
    if template_issues:
        for issue in template_issues:
            print(f"   - {issue}")
    
    print(f"\n Video/ROI: {'OK' if video_ok else 'ISSUES FOUND'}")
    if 'issues' in video_info and video_info['issues']:
        for issue in video_info['issues']:
            print(f"   - {issue}")
    
    print(f"\n Template Matching: {'OK' if template_results.get('above_threshold') else 'BELOW THRESHOLD'}")
    if template_results.get('best_match') is not None:
        print(f"   Best match: {template_results['best_match']} "
              f"(score: {template_results['best_score']:.3f}, threshold: {threshold})")
    
    print(f"\n OCR: {'OK' if ocr_results.get('success') else 'FAILED'}")
    if ocr_results.get('number') is not None:
        print(f"   Detected: {ocr_results['number']}")
    
    print(f"\n Multiple Frames Test: {multi_frame_results['success_rate']:.1f}% success rate")
    print(f"   Successful: {multi_frame_results['successful']}/{multi_frame_results['total_frames']}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    if not templates_ok:
        recommendations.append("1. Fix template loading - check directory path and file names")
    
    if 'issues' in video_info and video_info['issues']:
        if 'Screen region out of bounds' in video_info['issues']:
            recommendations.append("2. Fix screen_region coordinates in config - region is out of frame bounds")
        if 'ROI variance too low' in video_info['issues']:
            recommendations.append("3. Check screen_region - ROI appears empty/blank")
    
    if template_results.get('best_match') is not None:
        if not template_results.get('above_threshold'):
            recommendations.append(f"4. Lower winning_template_threshold from {threshold} to {template_results['best_score']:.2f}")
    
    if not ocr_results.get('success') and ocr_results.get('enabled'):
        recommendations.append("5. OCR is failing - check if ROI shows readable number")
        recommendations.append("6. Try lowering ocr_confidence_threshold or improving ROI quality")
    
    if multi_frame_results['success_rate'] < 10:
        recommendations.append("7. Very low detection rate - try different start_frame")
        recommendations.append("8. Verify video contains roulette game at specified frame")
    
    if not recommendations:
        recommendations.append(" All checks passed! If detection still fails, try:")
        recommendations.append("   - Different start_frame values")
        recommendations.append("   - Lowering thresholds")
        recommendations.append("   - Recreating templates from this video")
    
    for rec in recommendations:
        print(f"   {rec}")
    
    print("\n" + "=" * 80)
    print("Check the saved images:")
    if 'roi_path' in video_info:
        print(f"   - {video_info['roi_path']} (ROI extracted)")
    if 'frame_path' in video_info:
        print(f"   - {video_info['frame_path']} (Full frame with ROI marked)")
    print("=" * 80)


if __name__ == '__main__':
    main()

