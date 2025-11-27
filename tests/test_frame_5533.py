"""
Test specific frame 5533 from video to diagnose false positive detection.
"""

import cv2
import sys
from pathlib import Path
import numpy as np

from backend.app.detection import ScreenDetector
from backend.app.config_loader import ConfigLoader

def test_frame_5533(video_path: str, frame_number: int = 5533, config_path: str = 'config/default_config.json'):
    """Test detection on a specific frame and show detailed template matching results."""
    
    print(f"Testing frame {frame_number} from {video_path}")
    print("=" * 80)
    
    # Load configuration
    print(f"Loading configuration from {config_path}...")
    config = ConfigLoader.load_config(config_path)
    
    # Initialize detector
    print("Initializing detector...")
    detector = ScreenDetector(config)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_path}")
        sys.exit(1)
    
    # Get video info
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Video info: {total_frames} frames, {fps:.2f} FPS")
    
    if frame_number >= total_frames:
        print(f"Error: Frame {frame_number} is beyond video length ({total_frames} frames)")
        sys.exit(1)
    
    # Seek to frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    
    if not ret or frame is None:
        print(f"Error: Could not read frame {frame_number}")
        sys.exit(1)
    
    print(f"\nSuccessfully loaded frame {frame_number}")
    print(f"Frame shape: {frame.shape}")
    
    # Save frame for inspection
    frame_file = f"test_results/frame_{frame_number}_original.png"
    Path("test_results").mkdir(exist_ok=True)
    cv2.imwrite(frame_file, frame)
    print(f"Saved original frame to: {frame_file}")
    
    # Get ROI
    screen_region = config.get('detection', {}).get('screen_region')
    if screen_region:
        x, y, w, h = screen_region
        roi = frame[y:y+h, x:x+w]
        print(f"\nROI region: x={x}, y={y}, w={w}, h={h}")
        print(f"ROI shape: {roi.shape}")
        
        # Save ROI
        roi_file = f"test_results/frame_{frame_number}_roi.png"
        cv2.imwrite(roi_file, roi)
        print(f"Saved ROI to: {roi_file}")
    else:
        roi = frame
        print("\nNo screen_region configured, using full frame")
    
    # Test detection
    print("\n" + "=" * 80)
    print("TESTING DETECTION")
    print("=" * 80)
    
    result = detector.detect_result(frame)
    
    print(f"\nDetection Result:")
    print(f"  Number: {result.get('number')}")
    print(f"  Color: {result.get('color')}")
    print(f"  Confidence: {result.get('confidence', 0):.4f}")
    print(f"  Method: {result.get('method')}")
    
    # Test template matching in detail
    print("\n" + "=" * 80)
    print("DETAILED TEMPLATE MATCHING ANALYSIS")
    print("=" * 80)
    
    if detector.winning_templates:
        print(f"\nTesting {len(detector.winning_templates)} templates...")
        
        # Preprocess ROI
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        processed = detector._preprocess_badge_image(roi_gray)
        
        # Test all templates
        all_scores = {}
        best_number = None
        best_score = -1.0
        
        threshold = detector.winning_template_threshold
        print(f"Template threshold: {threshold}")
        print(f"\n{'Number':<8} {'Score':<10} {'Status':<10} {'Match Quality'}")
        print("-" * 80)
        
        for number, template in detector.winning_templates:
            h, w = template.shape
            if processed.shape[0] < h or processed.shape[1] < w:
                all_scores[number] = -1.0
                continue
            
            resized = cv2.resize(processed, (w, h), interpolation=cv2.INTER_AREA)
            try:
                match_result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
                score = float(match_result[0][0])
                all_scores[number] = score
                
                if score > best_score:
                    best_score = score
                    best_number = number
                
                status = "PASS" if score >= threshold else "FAIL"
                quality = "Excellent" if score >= 0.9 else "Good" if score >= 0.8 else "Fair" if score >= 0.7 else "Poor"
                
                print(f"{number:<8} {score:<10.4f} {status:<10} {quality}")
            except cv2.error as e:
                all_scores[number] = -1.0
                print(f"{number:<8} {'ERROR':<10} {'FAIL':<10} {str(e)}")
        
        print("-" * 80)
        print(f"\nBest match: Number {best_number} with score {best_score:.4f}")
        
        # Show top 5 matches
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        print(f"\nTop 5 matches:")
        for i, (num, score) in enumerate(sorted_scores[:5], 1):
            marker = "[PASS]" if score >= threshold else "[FAIL]"
            print(f"  {marker} {i}. Number {num}: {score:.4f}")
        
        # Check if number 8 is in top matches
        number_8_score = all_scores.get(8, -1.0)
        if number_8_score >= threshold:
            print(f"\nWARNING: Number 8 matched with score {number_8_score:.4f} (above threshold {threshold})")
            print(f"   This is the FALSE POSITIVE we need to fix!")
            
            # Check what number 2 scored
            number_2_score = all_scores.get(2, -1.0)
            print(f"\n   Number 2 score: {number_2_score:.4f}")
            if number_2_score > number_8_score:
                print(f"   WARNING: Number 2 scored HIGHER than 8, but 8 was selected!")
                print(f"   This suggests the template matching logic may have an issue.")
            elif number_2_score < threshold:
                print(f"   Number 2 is below threshold, so it wasn't selected.")
        else:
            print(f"\nNumber 8 score ({number_8_score:.4f}) is below threshold ({threshold})")
            print(f"   However, it was still detected - checking validation logic...")
    else:
        print("No templates loaded!")
    
    # Test validation
    print("\n" + "=" * 80)
    print("VALIDATION TEST")
    print("=" * 80)
    
    is_valid = detector.validate_result(result)
    print(f"Validation result: {'PASSED' if is_valid else 'FAILED'}")
    
    if not is_valid:
        print("This detection should have been rejected by validation!")
    else:
        print("WARNING: Validation passed, but this is a false positive!")
        print("   We need to improve validation to catch this case.")
    
    # Save processed ROI for inspection
    if detector.winning_templates:
        processed_file = f"test_results/frame_{frame_number}_processed.png"
        cv2.imwrite(processed_file, processed)
        print(f"\nSaved processed ROI to: {processed_file}")
    
    cap.release()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nFiles saved in test_results/ directory:")
    print(f"  - frame_{frame_number}_original.png (full frame)")
    print(f"  - frame_{frame_number}_roi.png (ROI region)")
    if detector.winning_templates:
        print(f"  - frame_{frame_number}_processed.png (processed ROI for template matching)")

if __name__ == '__main__':
    video_path = 'roleta_brazileria.mp4'
    frame_number = 5533
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    if len(sys.argv) > 2:
        frame_number = int(sys.argv[2])
    
    test_frame_5533(video_path, frame_number)

