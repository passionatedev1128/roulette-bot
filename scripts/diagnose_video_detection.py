"""
Diagnostic script to troubleshoot video detection issues.
Helps identify why detection isn't working with video.
"""

import cv2
import sys
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple

from backend.app.detection import ScreenDetector
from backend.app.detection.frame_detector import FrameDetector
from backend.app.config_loader import ConfigLoader


def check_templates(config: Dict) -> Dict:
    """Check if templates exist and are loaded."""
    detector = ScreenDetector(config)
    
    template_dir = Path(detector.winning_templates_dir)
    templates_loaded = len(detector.winning_templates)
    
    result = {
        "templates_dir": str(template_dir),
        "templates_dir_exists": template_dir.exists(),
        "templates_loaded": templates_loaded,
        "template_files": [],
        "template_numbers": []
    }
    
    if template_dir.exists():
        template_files = list(template_dir.glob("*.png"))
        result["template_files"] = [f.name for f in template_files]
        
        # Extract numbers from filenames
        import re
        numbers = []
        for f in template_files:
            match = re.search(r'(\d+)', f.stem)
            if match:
                numbers.append(int(match.group(1)))
        result["template_numbers"] = sorted(numbers)
    
    return result


def check_screen_region(video_path: str, config: Dict, frame_num: int = 0) -> Dict:
    """Check if screen_region is correct for the video."""
    detector = ScreenDetector(config)
    frame_detector = FrameDetector(config, video_path)
    
    # Go to specific frame
    frame_detector.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    frame = frame_detector.capture_screen()
    
    if frame is None:
        return {"error": "Could not read frame from video"}
    
    video_height, video_width = frame.shape[:2]
    screen_region = config.get('detection', {}).get('screen_region')
    
    result = {
        "video_resolution": [video_width, video_height],
        "screen_region": screen_region,
        "region_valid": False,
        "roi_size": None,
        "roi_preview_saved": False
    }
    
    if screen_region and len(screen_region) == 4:
        x, y, w, h = screen_region
        
        # Check if region is within video bounds
        if 0 <= x < video_width and 0 <= y < video_height:
            if x + w <= video_width and y + h <= video_height:
                result["region_valid"] = True
                result["roi_size"] = [w, h]
                
                # Extract ROI
                roi = frame[y:y+h, x:x+w]
                
                if roi.size > 0:
                    # Save ROI preview
                    roi_path = Path("diagnostic_roi.png")
                    cv2.imwrite(str(roi_path), roi)
                    result["roi_preview_saved"] = True
                    result["roi_path"] = str(roi_path)
                    
                    # Analyze ROI
                    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
                    result["roi_mean_brightness"] = float(np.mean(roi_gray))
                    result["roi_variance"] = float(np.var(roi_gray))
                    
                    # Check if ROI looks like it might contain a number
                    # (has some variation, not blank)
                    if result["roi_variance"] < 10:
                        result["roi_looks_blank"] = True
                    else:
                        result["roi_looks_blank"] = False
            else:
                result["error"] = f"Region extends beyond video bounds: x+w={x+w} > {video_width} or y+h={y+h} > {video_height}"
        else:
            result["error"] = f"Region starts outside video bounds: x={x} or y={y} invalid"
    else:
        result["error"] = "screen_region not configured or invalid format"
    
    frame_detector.release()
    return result


def test_template_matching(video_path: str, config: Dict, num_frames: int = 10) -> Dict:
    """Test template matching on multiple frames."""
    detector = ScreenDetector(config)
    frame_detector = FrameDetector(config, video_path)
    
    if len(detector.winning_templates) == 0:
        return {"error": "No templates loaded"}
    
    results = []
    best_scores_all = []
    
    for i in range(num_frames):
        frame = frame_detector.capture_screen()
        if frame is None:
            break
        
        # Get ROI
        screen_region = config.get('detection', {}).get('screen_region')
        if screen_region and len(screen_region) == 4:
            x, y, w, h = screen_region
            roi = frame[y:y+h, x:x+w]
        else:
            roi = frame
        
        if roi.size == 0:
            continue
        
        # Test template matching
        processed = detector._preprocess_badge_image(roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))
        
        best_score = -1.0
        best_number = None
        all_scores = {}
        
        for number, template in detector.winning_templates:
            h_t, w_t = template.shape
            if processed.shape[0] < h_t or processed.shape[1] < w_t:
                continue
            
            resized = cv2.resize(processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
            try:
                result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
                score = float(result[0][0])
                all_scores[number] = score
                
                if score > best_score:
                    best_score = score
                    best_number = number
            except cv2.error:
                continue
        
        best_scores_all.append(best_score)
        results.append({
            "frame": i,
            "best_score": best_score,
            "best_number": best_number,
            "top_5_scores": dict(sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:5])
        })
    
    frame_detector.release()
    
    threshold = config.get('detection', {}).get('winning_template_threshold', 0.65)
    avg_best_score = sum(best_scores_all) / len(best_scores_all) if best_scores_all else -1.0
    
    return {
        "frames_tested": len(results),
        "average_best_score": avg_best_score,
        "max_best_score": max(best_scores_all) if best_scores_all else -1.0,
        "min_best_score": min(best_scores_all) if best_scores_all else -1.0,
        "threshold": threshold,
        "scores_above_threshold": sum(1 for s in best_scores_all if s >= threshold),
        "results": results
    }


def test_full_detection(video_path: str, config: Dict, num_frames: int = 20) -> Dict:
    """Test full detection pipeline."""
    detector = ScreenDetector(config)
    frame_detector = FrameDetector(config, video_path)
    
    detections = []
    no_detections = 0
    
    for i in range(num_frames):
        frame = frame_detector.capture_screen()
        if frame is None:
            break
        
        result = detector.detect_result(frame)
        
        if result.get('number') is not None:
            detections.append({
                "frame": i,
                "number": result.get('number'),
                "method": result.get('method'),
                "confidence": result.get('confidence')
            })
        else:
            no_detections += 1
    
    frame_detector.release()
    
    return {
        "frames_tested": num_frames,
        "detections": len(detections),
        "no_detections": no_detections,
        "detection_rate": (len(detections) / num_frames * 100) if num_frames > 0 else 0,
        "results": detections
    }


def main():
    """Main diagnostic function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnose video detection issues')
    parser.add_argument('video', type=str, help='Path to video file')
    parser.add_argument('--config', type=str, default='config/default_config.json', help='Config file path')
    parser.add_argument('--frame', type=int, default=0, help='Frame number to check')
    parser.add_argument('--test-frames', type=int, default=20, help='Number of frames to test')
    
    args = parser.parse_args()
    
    video_path = Path(args.video)
    if not video_path.exists():
        print(f" Error: Video file not found: {video_path}")
        sys.exit(1)
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f" Error: Config file not found: {config_path}")
        sys.exit(1)
    
    print("=" * 80)
    print("VIDEO DETECTION DIAGNOSTIC")
    print("=" * 80)
    print(f"Video: {video_path}")
    print(f"Config: {config_path}")
    print()
    
    # Load config
    config = ConfigLoader.load_config(str(config_path))
    
    # 1. Check templates
    print("1. Checking Templates...")
    print("-" * 80)
    template_check = check_templates(config)
    print(f"   Templates directory: {template_check['templates_dir']}")
    print(f"   Directory exists: {template_check['templates_dir_exists']}")
    print(f"   Templates loaded: {template_check['templates_loaded']}")
    
    if template_check['templates_loaded'] == 0:
        print("    PROBLEM: No templates loaded!")
        print(f"   Check if templates exist in: {template_check['templates_dir']}")
        if template_check['template_files']:
            print(f"   Found files: {template_check['template_files']}")
        else:
            print("   No PNG files found in templates directory")
    else:
        print(f"    Templates loaded: {template_check['template_numbers']}")
    print()
    
    # 2. Check screen region
    print("2. Checking Screen Region...")
    print("-" * 80)
    region_check = check_screen_region(str(video_path), config, args.frame)
    print(f"   Video resolution: {region_check.get('video_resolution')}")
    print(f"   Screen region: {region_check.get('screen_region')}")
    print(f"   Region valid: {region_check.get('region_valid')}")
    
    if not region_check.get('region_valid'):
        print(f"    PROBLEM: {region_check.get('error', 'Screen region invalid')}")
    else:
        print(f"    Region is valid")
        print(f"   ROI size: {region_check.get('roi_size')}")
        if region_check.get('roi_preview_saved'):
            print(f"    ROI preview saved: {region_check.get('roi_path')}")
            print(f"   👀 CHECK THIS FILE - Does it show a winning number?")
            if region_check.get('roi_looks_blank'):
                print(f"     WARNING: ROI looks blank (low variance)")
            else:
                print(f"    ROI has content (variance: {region_check.get('roi_variance', 0):.1f})")
    print()
    
    # 3. Test template matching
    if template_check['templates_loaded'] > 0 and region_check.get('region_valid'):
        print("3. Testing Template Matching...")
        print("-" * 80)
        matching_test = test_template_matching(str(video_path), config, args.test_frames)
        
        if 'error' in matching_test:
            print(f"    Error: {matching_test['error']}")
        else:
            print(f"   Frames tested: {matching_test['frames_tested']}")
            print(f"   Average best score: {matching_test['average_best_score']:.3f}")
            print(f"   Max score: {matching_test['max_best_score']:.3f}")
            print(f"   Min score: {matching_test['min_best_score']:.3f}")
            print(f"   Threshold: {matching_test['threshold']}")
            print(f"   Scores above threshold: {matching_test['scores_above_threshold']}/{matching_test['frames_tested']}")
            
            if matching_test['average_best_score'] < matching_test['threshold']:
                print(f"    PROBLEM: Average score ({matching_test['average_best_score']:.3f}) < threshold ({matching_test['threshold']})")
                print(f"   Templates don't match the video!")
            elif matching_test['scores_above_threshold'] == 0:
                print(f"    PROBLEM: No scores above threshold")
            else:
                print(f"    Some matches found")
    print()
    
    # 4. Test full detection
    print("4. Testing Full Detection Pipeline...")
    print("-" * 80)
    detection_test = test_full_detection(str(video_path), config, args.test_frames)
    print(f"   Frames tested: {detection_test['frames_tested']}")
    print(f"   Detections: {detection_test['detections']}")
    print(f"   No detections: {detection_test['no_detections']}")
    print(f"   Detection rate: {detection_test['detection_rate']:.1f}%")
    
    if detection_test['detection_rate'] < 50:
        print(f"    PROBLEM: Very low detection rate!")
    elif detection_test['detection_rate'] < 80:
        print(f"     WARNING: Low detection rate")
    else:
        print(f"    Good detection rate")
    
    if detection_test['detections'] > 0:
        methods = {}
        for r in detection_test['results']:
            method = r.get('method', 'unknown')
            methods[method] = methods.get(method, 0) + 1
        print(f"   Methods used: {methods}")
    print()
    
    # Summary and recommendations
    print("=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    issues = []
    if template_check['templates_loaded'] == 0:
        issues.append("No templates loaded")
    if not region_check.get('region_valid'):
        issues.append("Screen region invalid")
    if region_check.get('roi_looks_blank'):
        issues.append("ROI appears blank")
    if 'matching_test' in locals() and matching_test.get('average_best_score', -1) < matching_test.get('threshold', 1.0):
        issues.append("Templates don't match video")
    if detection_test['detection_rate'] < 50:
        issues.append("Very low detection rate")
    
    if issues:
        print(" ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
        print()
        print("RECOMMENDATIONS:")
        if template_check['templates_loaded'] == 0:
            print("   1. Create templates from your video:")
            print("      python capture_winning-numbers.py --video your_video.mp4")
        if not region_check.get('region_valid') or region_check.get('roi_looks_blank'):
            print("   2. Find correct screen_region coordinates:")
            print("      python verify_screen_region.py")
            print("      Or check diagnostic_roi.png - does it show a number?")
        if 'matching_test' in locals() and matching_test.get('average_best_score', -1) < matching_test.get('threshold', 1.0):
            print("   3. Templates don't match video - recreate them:")
            print("      python capture_winning-numbers.py --video your_video.mp4")
            print("   4. Or lower threshold in config:")
            print("      Set winning_template_threshold to 0.5 or 0.55")
    else:
        print(" No major issues found!")
        print("   Detection should be working. If not, check:")
        print("   - Video quality")
        print("   - Number visibility in video")
        print("   - Try different frames")
    
    print("=" * 80)


if __name__ == '__main__':
    main()

