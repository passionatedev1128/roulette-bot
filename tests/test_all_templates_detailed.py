"""
Detailed Template Matching Diagnostic
Tests each template directly against video frames to see actual match scores.
"""

import cv2
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import re

from backend.app.config_loader import ConfigLoader
from backend.app.detection.frame_detector import FrameDetector
from backend.app.detection.screen_detector import ScreenDetector


def test_all_templates_detailed(
    video_path: str,
    config_path: str = 'config/default_config.json',
    num_frames: int = 50
):
    """
    Test each template directly against video frames to see actual match scores.
    
    Args:
        video_path: Path to video file
        config_path: Path to configuration file
        num_frames: Number of frames to test
    """
    # Load configuration
    print(f"Loading configuration from {config_path}...")
    config = ConfigLoader.load_config(config_path)
    
    # Initialize frame detector
    print(f"Loading video: {video_path}")
    frame_detector = FrameDetector(config, video_path)
    
    # Create a ScreenDetector to access template matching directly
    detector = ScreenDetector(config)
    
    # Get ROI region
    detection_config = config.get('detection', {})
    screen_region = detection_config.get('screen_region', None)
    threshold = float(detection_config.get('winning_template_threshold', 0.75))
    
    print(f"\nTemplate matching threshold: {threshold}")
    print(f"Number of templates loaded: {len(detector.winning_templates)}")
    print(f"Templates: {sorted([n for n, _ in detector.winning_templates])}")
    print("\n" + "=" * 100)
    
    # Track scores for each template across all frames
    template_scores: Dict[int, List[float]] = {}  # number -> list of scores
    frame_results: List[Dict] = []  # Store results for each frame
    
    frame_count = 0
    tested_frames = 0
    
    print(f"\nTesting {num_frames} frames...")
    print("=" * 100)
    
    while tested_frames < num_frames:
        frame = frame_detector.capture_screen()
        if frame is None:
            print("\nEnd of video reached.")
            break
        
        frame_count += 1
        
        # Test every 20th frame to get variety
        if frame_count % 20 != 0:
            continue
        
        tested_frames += 1
        
        # Get ROI
        if screen_region:
            x, y, w, h = screen_region
            roi = frame[y:y+h, x:x+w]
        else:
            roi = frame
        
        # Test each template directly
        processed = detector._preprocess_badge_image(roi)
        frame_scores = {}
        best_number = None
        best_score = -1.0
        
        for number, template in detector.winning_templates:
            h, w = template.shape
            resized = cv2.resize(processed, (w, h), interpolation=cv2.INTER_AREA)
            try:
                result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
                score = float(result[0][0])
                frame_scores[number] = score
                
                if number not in template_scores:
                    template_scores[number] = []
                template_scores[number].append(score)
                
                if score > best_score:
                    best_score = score
                    best_number = number
            except cv2.error as e:
                frame_scores[number] = -1.0
                print(f"Error matching template {number}: {e}")
        
        # Store frame result
        frame_results.append({
            'frame': frame_count,
            'scores': frame_scores.copy(),
            'best': best_number,
            'best_score': best_score,
            'above_threshold': best_score >= threshold if best_number else False
        })
        
        # Print frame result
        if tested_frames <= 10 or tested_frames % 10 == 0:
            sorted_scores = sorted(frame_scores.items(), key=lambda x: x[1], reverse=True)
            top3 = sorted_scores[:3]
            status = "" if best_score >= threshold else ""
            print(f"\nFrame {frame_count:4d}: {status} Best={best_number} ({best_score:.3f}) | Top 3: {', '.join([f'{n}({s:.3f})' for n, s in top3])}")
    
    frame_detector.release()
    
    # Print detailed analysis
    print("\n" + "=" * 100)
    print("DETAILED TEMPLATE ANALYSIS")
    print("=" * 100)
    
    if not template_scores:
        print(" No template matches found!")
        return
    
    # Statistics for each template
    print(f"\n{'Template':<10} {'Frames':<10} {'Avg Score':<12} {'Min Score':<12} {'Max Score':<12} {'Above Thresh':<15} {'Status'}")
    print("-" * 100)
    
    for number in sorted(template_scores.keys()):
        scores = template_scores[number]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        above_thresh = sum(1 for s in scores if s >= threshold)
        above_pct = (above_thresh / len(scores)) * 100
        
        if above_pct > 50:
            status = " GOOD"
        elif above_pct > 0:
            status = " PARTIAL"
        elif max_score > 0.5:
            status = " CLOSE"
        else:
            status = " POOR"
        
        print(f"{number:<10} {len(scores):<10} {avg_score:<12.3f} {min_score:<12.3f} {max_score:<12.3f} {above_thresh}/{len(scores)} ({above_pct:5.1f}%) {status}")
    
    # Find frames where each number should have been detected
    print("\n" + "=" * 100)
    print("FRAME-BY-FRAME ANALYSIS (First 10 frames with detections)")
    print("=" * 100)
    
    detection_frames = [f for f in frame_results if f['above_threshold']]
    if detection_frames:
        print(f"\n{'Frame':<8} {'Detected':<10} {'Score':<10} {'All Scores (top 5)'}")
        print("-" * 100)
        for fr in detection_frames[:10]:
            sorted_scores = sorted(fr['scores'].items(), key=lambda x: x[1], reverse=True)
            top5_str = ', '.join([f'{n}({s:.3f})' for n, s in sorted_scores[:5]])
            print(f"{fr['frame']:<8} {fr['best']:<10} {fr['best_score']:<10.3f} {top5_str}")
    
    # Analyze missing templates
    all_template_numbers = set([n for n, _ in detector.winning_templates])
    detected_numbers = set([n for n in template_scores.keys() if any(s >= threshold for s in template_scores[n])])
    missing_numbers = all_template_numbers - detected_numbers
    
    if missing_numbers:
        print("\n" + "=" * 100)
        print("MISSING TEMPLATES ANALYSIS")
        print("=" * 100)
        print(f"\n  Templates never detected above threshold: {sorted(missing_numbers)}")
        
        print("\nDetailed scores for missing templates:")
        print("-" * 100)
        print(f"{'Template':<10} {'Max Score':<12} {'Avg Score':<12} {'Frames Tested':<15} {'Recommendation'}")
        print("-" * 100)
        
        for number in sorted(missing_numbers):
            if number in template_scores:
                scores = template_scores[number]
                max_score = max(scores)
                avg_score = sum(scores) / len(scores)
                
                if max_score > 0.6:
                    rec = "Lower threshold to ~0.55-0.60"
                elif max_score > 0.4:
                    rec = "Template quality issue - re-capture from video"
                else:
                    rec = "Template mismatch - check ROI or re-capture"
                
                print(f"{number:<10} {max_score:<12.3f} {avg_score:<12.3f} {len(scores):<15} {rec}")
            else:
                print(f"{number:<10} {'N/A':<12} {'N/A':<12} {'0':<15} Template not tested")
    
    # Recommendations
    print("\n" + "=" * 100)
    print("RECOMMENDATIONS")
    print("=" * 100)
    
    if missing_numbers:
        print(f"\n1. {len(missing_numbers)} template(s) need attention:")
        for num in sorted(missing_numbers):
            if num in template_scores:
                max_s = max(template_scores[num])
                if max_s > 0.6:
                    print(f"   - Number {num}: Max score {max_s:.3f} - Lower threshold or improve template")
                elif max_s > 0.4:
                    print(f"   - Number {num}: Max score {max_s:.3f} - Re-capture template from video frame")
                else:
                    print(f"   - Number {num}: Max score {max_s:.3f} - Check template file or ROI region")
    
    # Check if threshold should be adjusted
    all_max_scores = [max(scores) for scores in template_scores.values()]
    if all_max_scores:
        min_max = min(all_max_scores)
        if min_max < threshold and min_max > 0.5:
            suggested = max(0.5, min_max - 0.05)
            print(f"\n2. Suggested threshold adjustment:")
            print(f"   Current: {threshold}")
            print(f"   Suggested: {suggested:.2f} (would catch templates with max score {min_max:.3f})")
    
    print("\n3. To fix missing templates:")
    print("   a) Find frames in video where those numbers appear")
    print("   b) Use capture_winning-numbers.py to capture new templates")
    print("   c) Ensure templates are captured from the same ROI region")
    print("   d) Verify template images are clear and match video quality")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Detailed template matching diagnostic - shows all match scores'
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
        default=50,
        help='Number of frames to test (default: 50)'
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
    test_all_templates_detailed(
        str(video_path),
        str(config_path),
        args.frames
    )


if __name__ == '__main__':
    main()

