"""
Template Matching Diagnostic Script
Tests all winning number templates against video frames to identify detection issues.
"""

import cv2
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

from backend.app.config_loader import ConfigLoader
from backend.app.detection.frame_detector import FrameDetector


def test_template_matching(
    video_path: str,
    config_path: str = 'config/default_config.json',
    num_frames: int = 100,
    threshold: float = 0.75
):
    """
    Test template matching for all templates in the video.
    
    Args:
        video_path: Path to video file
        config_path: Path to configuration file
        num_frames: Number of frames to test
        threshold: Template matching threshold
    """
    # Load configuration
    print(f"Loading configuration from {config_path}...")
    config = ConfigLoader.load_config(config_path)
    
    # Initialize frame detector
    print(f"Loading video: {video_path}")
    frame_detector = FrameDetector(config, video_path)
    
    # Get detector's template matching method
    detector = frame_detector
    
    # Track detection results
    detection_stats: Dict[int, List[float]] = {}  # number -> list of scores
    all_detections: List[Tuple[int, int, float, str]] = []  # (frame_num, number, score, method)
    
    print(f"\nTesting {num_frames} frames with threshold={threshold}...")
    print("=" * 80)
    
    frame_count = 0
    tested_frames = 0
    
    while tested_frames < num_frames:
        frame = frame_detector.capture_screen()
        if frame is None:
            print("\nEnd of video reached.")
            break
        
        frame_count += 1
        
        # Skip frames (test every 10th frame to get variety)
        if frame_count % 10 != 0:
            continue
        
        tested_frames += 1
        
        # Get ROI
        detection_config = config.get('detection', {})
        screen_region = detection_config.get('screen_region', None)
        
        if screen_region:
            x, y, w, h = screen_region
            roi = frame[y:y+h, x:x+w]
        else:
            roi = frame
        
        # Test template matching
        result = detector.detect_result(frame)
        
        if result and result.get('number') is not None:
            number = result['number']
            confidence = result.get('confidence', 0.0)
            method = result.get('method', 'unknown')
            
            if number not in detection_stats:
                detection_stats[number] = []
            detection_stats[number].append(confidence)
            all_detections.append((frame_count, number, confidence, method))
            
            if tested_frames % 10 == 0:
                print(f"Frame {frame_count}: Detected {number} (confidence={confidence:.3f}, method={method})")
    
    frame_detector.release()
    
    # Print summary
    print("\n" + "=" * 80)
    print("DETECTION SUMMARY")
    print("=" * 80)
    
    if not detection_stats:
        print(" No numbers detected in any frame!")
        print("\nPossible issues:")
        print("  1. Template threshold too high (current: {})".format(threshold))
        print("  2. Templates not matching video frames")
        print("  3. ROI region incorrect")
        print("  4. Video quality/resolution mismatch")
        return
    
    # Expected numbers from templates
    template_dir = Path(config.get('detection', {}).get('winning_templates_dir', 'winning-numbers'))
    expected_numbers = set()
    if template_dir.exists():
        import re
        for path in template_dir.glob("*.png"):
            match = re.search(r'(\d+)', path.stem)
            if match:
                expected_numbers.add(int(match.group(1)))
    
    print(f"\nExpected numbers (from templates): {sorted(expected_numbers)}")
    print(f"Detected numbers: {sorted(detection_stats.keys())}")
    
    missing = expected_numbers - set(detection_stats.keys())
    if missing:
        print(f"\n  Missing detections: {sorted(missing)}")
    
    print("\nDetection Statistics:")
    print("-" * 80)
    print(f"{'Number':<8} {'Count':<8} {'Avg Score':<12} {'Min Score':<12} {'Max Score':<12}")
    print("-" * 80)
    
    for number in sorted(detection_stats.keys()):
        scores = detection_stats[number]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        print(f"{number:<8} {len(scores):<8} {avg_score:<12.3f} {min_score:<12.3f} {max_score:<12.3f}")
    
    # Analyze threshold issues
    print("\n" + "=" * 80)
    print("THRESHOLD ANALYSIS")
    print("=" * 80)
    
    below_threshold = []
    for number in sorted(expected_numbers):
        if number in detection_stats:
            scores = detection_stats[number]
            below_count = sum(1 for s in scores if s < threshold)
            if below_count > 0:
                below_threshold.append((number, below_count, len(scores)))
        else:
            below_threshold.append((number, 0, 0))
    
    if below_threshold:
        print(f"\nNumbers with scores below threshold ({threshold}):")
        print("-" * 80)
        print(f"{'Number':<8} {'Below Threshold':<18} {'Total Attempts':<18}")
        print("-" * 80)
        for number, below, total in below_threshold:
            if total > 0:
                pct = (below / total) * 100
                print(f"{number:<8} {below}/{total} ({pct:.1f}%)")
            else:
                print(f"{number:<8} Not detected")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if missing:
        print(f"\n1.   {len(missing)} template(s) never detected:")
        for num in sorted(missing):
            print(f"   - Number {num}")
        print("\n   Suggestions:")
        print("   - Lower the threshold (try 0.65 or 0.70)")
        print("   - Verify template images match video quality")
        print("   - Check if ROI region is correct")
        print("   - Re-capture templates from video frames")
    
    # Check if threshold is too high
    all_scores = []
    for scores in detection_stats.values():
        all_scores.extend(scores)
    
    if all_scores:
        avg_all = sum(all_scores) / len(all_scores)
        min_all = min(all_scores)
        print(f"\n2. Overall score statistics:")
        print(f"   - Average: {avg_all:.3f}")
        print(f"   - Minimum: {min_all:.3f}")
        print(f"   - Current threshold: {threshold}")
        
        if min_all < threshold:
            suggested_threshold = max(0.6, min_all - 0.05)
            print(f"\n    Suggested threshold: {suggested_threshold:.2f}")
            print(f"      (Current threshold may be too high)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test template matching for all winning number templates'
    )
    parser.add_argument(
        'video',
        type=str,
        help='Path to video file'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to configuration file (default: config/default_config.json)'
    )
    parser.add_argument(
        '--frames',
        type=int,
        default=100,
        help='Number of frames to test (default: 100)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.75,
        help='Template matching threshold (default: 0.75)'
    )
    
    args = parser.parse_args()
    
    # Check if video exists
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Check if config exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Run test
    test_template_matching(
        str(video_path),
        str(config_path),
        args.frames,
        args.threshold
    )


if __name__ == '__main__':
    main()

