"""
Detailed template matching test - shows all template scores for each number.
Helps identify why detection is inconsistent.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from backend.app.config_loader import ConfigLoader
    from backend.app.detection import ScreenDetector
    from backend.app.detection.frame_detector import FrameDetector
except ImportError:
    print(" Error: Cannot import bot modules. Make sure you're in the project root directory.")
    sys.exit(1)


def test_template_scores(detector, frame: np.ndarray, expected_numbers: List[int]) -> Dict:
    """Test template matching scores for all templates on a frame."""
    print("\n" + "=" * 80)
    print("TEMPLATE MATCHING SCORE ANALYSIS")
    print("=" * 80)
    
    if not detector.winning_templates:
        print(" No templates loaded!")
        return {}
    
    print(f"Templates loaded: {len(detector.winning_templates)}")
    template_numbers = sorted([t[0] for t in detector.winning_templates])
    print(f"Template numbers: {template_numbers}")
    print(f"Expected numbers in sequence: {expected_numbers}")
    print(f"Threshold: {detector.winning_template_threshold}")
    print()
    
    # Extract ROI
    screen_region = detector.config.get('detection', {}).get('screen_region')
    is_video_frame = hasattr(detector, 'cap') and hasattr(detector, 'video_path')
    
    if screen_region and is_video_frame:
        x, y, w, h = screen_region
        frame_h, frame_w = frame.shape[:2]
        if x >= 0 and y >= 0 and x + w <= frame_w and y + h <= frame_h:
            roi = frame[y:y + h, x:x + w]
        else:
            print(f"  Invalid screen_region, using full frame")
            roi = frame
    elif screen_region:
        roi = frame  # Already cropped for desktop
    else:
        roi = frame
    
    print(f"ROI shape: {roi.shape}")
    print()
    
    # Test all templates
    all_scores = {}
    for number, template in detector.winning_templates:
        h, w = template.shape
        
        if roi.shape[0] < h or roi.shape[1] < w:
            print(f"  Template {number}: ROI too small ({roi.shape} vs template {template.shape})")
            continue
        
        try:
            # Preprocess ROI same way as detector
            if len(roi.shape) == 3:
                processed = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            else:
                processed = roi.copy()
            
            processed = cv2.GaussianBlur(processed, (3, 3), 0)
            
            # Match template
            if processed.shape[0] > h * 2 or processed.shape[1] > w * 2:
                result = cv2.matchTemplate(processed, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                score = float(max_val)
            else:
                resized = cv2.resize(processed, (w, h), interpolation=cv2.INTER_AREA)
                result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
                score = float(result[0][0])
            
            all_scores[number] = score
            
        except Exception as e:
            print(f" Error matching template {number}: {e}")
            all_scores[number] = -1.0
    
    # Sort by score
    sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
    
    print("Template Match Scores:")
    print("-" * 80)
    for number, score in sorted_scores:
        status = ""
        if score >= detector.winning_template_threshold:
            if number == sorted_scores[0][0]:
                status = "  BEST MATCH"
            elif len(sorted_scores) > 1 and number == sorted_scores[1][0]:
                status = "   SECOND BEST"
        else:
            status = "  BELOW THRESHOLD"
        
        print(f"  Number {number:2d}: {score:.4f}{status}")
    
    print()
    
    # Analyze
    if sorted_scores:
        best_number, best_score = sorted_scores[0]
        second_best_number = sorted_scores[1][0] if len(sorted_scores) > 1 else None
        second_best_score = sorted_scores[1][1] if len(sorted_scores) > 1 else -1
        
        print("Analysis:")
        print("-" * 80)
        print(f"Best match: Number {best_number} with score {best_score:.4f}")
        
        if best_score < detector.winning_template_threshold:
            print(f" REJECTED: Score {best_score:.4f} < threshold {detector.winning_template_threshold}")
        else:
            if second_best_score >= detector.winning_template_threshold:
                score_gap = best_score - second_best_score
                print(f"Second best: Number {second_best_number} with score {second_best_score:.4f}")
                print(f"Score gap: {score_gap:.4f}")
                
                if score_gap < 0.04:
                    if best_score < 0.95:
                        print(f" REJECTED: Ambiguous match (gap < 0.04) requires confidence >= 0.95, got {best_score:.4f}")
                    else:
                        print(f" ACCEPTED: Ambiguous but high confidence ({best_score:.4f} >= 0.95)")
                elif score_gap < 0.05:
                    if best_score < 0.94:
                        print(f" REJECTED: Ambiguous match (gap 0.04-0.05) requires confidence >= 0.94, got {best_score:.4f}")
                    else:
                        print(f" ACCEPTED: Somewhat ambiguous but good confidence ({best_score:.4f} >= 0.94)")
                else:
                    print(f" ACCEPTED: Clear match (gap >= 0.05)")
            else:
                print(f" ACCEPTED: Clear match (second best below threshold)")
    
    return {
        "scores": all_scores,
        "best": sorted_scores[0] if sorted_scores else None,
        "second_best": sorted_scores[1] if len(sorted_scores) > 1 else None
    }


def test_sequence(detector, video_path: str, expected_numbers: List[int], start_frame: int = 1000):
    """Test template matching on a sequence of frames."""
    print("=" * 80)
    print("TESTING TEMPLATE MATCHING ON SEQUENCE")
    print("=" * 80)
    print(f"Video: {video_path}")
    print(f"Expected numbers: {expected_numbers}")
    print(f"Start frame: {start_frame}")
    print()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f" Cannot open video: {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Video info: {total_frames} frames, {fps:.2f} fps")
    print()
    
    results = []
    
    # Test each expected number
    for i, expected_number in enumerate(expected_numbers):
        # Calculate frame number (assuming each number appears for ~1 second = 30 frames at 30fps)
        frame_number = start_frame + (i * 30)
        
        if frame_number >= total_frames:
            print(f"  Frame {frame_number} beyond video length ({total_frames})")
            break
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        if not ret:
            print(f" Cannot read frame {frame_number}")
            continue
        
        print(f"\n{'=' * 80}")
        print(f"Testing Frame {frame_number} - Expected Number: {expected_number}")
        print(f"{'=' * 80}")
        
        analysis = test_template_scores(detector, frame, [expected_number])
        
        detected_number = analysis.get("best")[0] if analysis.get("best") else None
        detected_score = analysis.get("best")[1] if analysis.get("best") else 0
        
        match = "" if detected_number == expected_number else ""
        results.append({
            "frame": frame_number,
            "expected": expected_number,
            "detected": detected_number,
            "score": detected_score,
            "match": match
        })
        
        print(f"\nResult: {match} Expected {expected_number}, Detected {detected_number} (score: {detected_score:.4f})")
    
    cap.release()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    correct = sum(1 for r in results if r["match"] == "")
    total = len(results)
    
    print(f"Correct detections: {correct}/{total} ({correct/total*100:.1f}%)")
    print()
    
    print("Detailed results:")
    for r in results:
        detected_str = str(r['detected']) if r['detected'] is not None else 'None'
        print(f"  Frame {r['frame']:5d}: Expected {r['expected']:2d}, Detected {detected_str:>4}, "
              f"Score {r['score']:.4f} {r['match']}")
    
    # Identify issues
    print("\nIssues identified:")
    issues = []
    
    for r in results:
        if r["match"] == "":
            if r["detected"] is None:
                issues.append(f"Frame {r['frame']}: No detection (expected {r['expected']})")
            elif r["score"] < detector.winning_template_threshold:
                issues.append(f"Frame {r['frame']}: Score {r['score']:.4f} below threshold {detector.winning_template_threshold}")
            else:
                issues.append(f"Frame {r['frame']}: Wrong number detected ({r['detected']} instead of {r['expected']})")
    
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("   No issues found!")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python test_template_matching_detailed.py <video_path> [expected_numbers]")
        print("Example: python test_template_matching_detailed.py video.mp4 33,27,22,36,8,2,22,25")
        sys.exit(1)
    
    video_path = sys.argv[1]
    if not Path(video_path).exists():
        print(f" Video file not found: {video_path}")
        sys.exit(1)
    
    # Parse expected numbers
    expected_numbers = [33, 27, 22, 36, 8, 2, 22, 25]  # Default
    if len(sys.argv) > 2:
        try:
            expected_numbers = [int(x.strip()) for x in sys.argv[2].split(',')]
        except ValueError:
            print(f"  Invalid expected numbers format, using default: {expected_numbers}")
    
    config_path = Path("config/default_config.json")
    if not config_path.exists():
        print(f" Config file not found: {config_path}")
        sys.exit(1)
    
    config = ConfigLoader.load_config(str(config_path))
    
    # Initialize detector
    start_frame = int(os.environ.get('BOT_START_FRAME', '1000'))
    detector = FrameDetector(config, video_path, start_frame=start_frame)
    
    # Run test
    test_sequence(detector, video_path, expected_numbers, start_frame)


if __name__ == "__main__":
    import os
    main()

