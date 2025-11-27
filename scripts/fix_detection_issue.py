"""
Fix Detection Issues - Based on Diagnostic Results
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path

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


def analyze_roi_content(video_path: str, config: Dict, start_frame: int = 690, num_frames: int = 50):
    """Analyze ROI content across multiple frames to find where numbers appear."""
    print("=" * 80)
    print("ANALYZING ROI CONTENT ACROSS FRAMES")
    print("=" * 80)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(" Cannot open video")
        return
    
    screen_region = config.get('detection', {}).get('screen_region', [])
    if not screen_region or len(screen_region) != 4:
        print(" Screen region not configured")
        cap.release()
        return
    
    x, y, w, h = screen_region
    
    # Collect ROI samples
    roi_samples = []
    frame_numbers = []
    
    print(f"Analyzing {num_frames} frames starting from {start_frame}...")
    
    for i in range(num_frames):
        frame_num = start_frame + i
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        
        if not ret:
            break
        
        roi = frame[y:y+h, x:x+w]
        if roi.size > 0:
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
            variance = np.var(roi_gray)
            
            roi_samples.append({
                'frame': frame_num,
                'roi': roi,
                'variance': variance,
                'mean': np.mean(roi_gray)
            })
            frame_numbers.append(frame_num)
    
    cap.release()
    
    if not roi_samples:
        print(" No ROI samples collected")
        return
    
    # Analyze variance
    variances = [s['variance'] for s in roi_samples]
    mean_var = np.mean(variances)
    max_var = max(variances)
    min_var = min(variances)
    
    print(f"\nROI Variance Analysis:")
    print(f"   Mean: {mean_var:.1f}")
    print(f"   Min: {min_var:.1f}")
    print(f"   Max: {max_var:.1f}")
    
    # Find frames with highest variance (likely contain numbers)
    high_var_frames = [s for s in roi_samples if s['variance'] > mean_var * 1.5]
    
    if high_var_frames:
        print(f"\n Found {len(high_var_frames)} frames with high variance (likely contain numbers):")
        for s in high_var_frames[:5]:
            print(f"   Frame {s['frame']}: variance={s['variance']:.1f}")
        
        # Save sample ROIs
        print(f"\nSaving sample ROIs...")
        for i, s in enumerate(high_var_frames[:5]):
            path = f'roi_sample_frame_{s["frame"]}.png'
            cv2.imwrite(path, s['roi'])
            print(f"    {path}")
    else:
        print(f"\n  No frames with high variance found")
        print(f"   ROI might be consistently empty or showing same content")
    
    # Save ROI with lowest variance (likely empty)
    if roi_samples:
        low_var_sample = min(roi_samples, key=lambda x: x['variance'])
        cv2.imwrite('roi_low_variance_sample.png', low_var_sample['roi'])
        print(f"\n    Saved low variance sample: roi_low_variance_sample.png")
        print(f"      Frame {low_var_sample['frame']}, variance: {low_var_sample['variance']:.1f}")
    
    return roi_samples


def try_different_regions(video_path: str, config: Dict, start_frame: int = 690):
    """Try detecting numbers in different regions to find correct coordinates."""
    print("\n" + "=" * 80)
    print("TRYING DIFFERENT REGIONS")
    print("=" * 80)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(" Cannot open video")
        return
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    ret, frame = cap.read()
    if not ret:
        print(" Cannot read frame")
        cap.release()
        return
    
    height, width = frame.shape[:2]
    print(f"Frame size: {width}x{height}")
    
    # Current region
    current_region = config.get('detection', {}).get('screen_region', [])
    if current_region and len(current_region) == 4:
        x, y, w, h = current_region
        print(f"\nCurrent region: x={x}, y={y}, w={w}, h={h}")
    
    # Try some common regions (center area where numbers often appear)
    test_regions = [
        # Center regions
        [width//2 - 30, height//2 - 30, 60, 60],
        [width//2 - 50, height//2 - 50, 100, 100],
        # Top center
        [width//2 - 30, 100, 60, 60],
        [width//2 - 50, 50, 100, 100],
        # Right side (common for winning numbers)
        [width - 200, height//2 - 30, 60, 60],
        [width - 150, height//2 - 50, 100, 100],
    ]
    
    # Add variations around current region
    if current_region and len(current_region) == 4:
        x, y, w, h = current_region
        test_regions.extend([
            [x - 50, y - 50, w + 100, h + 100],  # Larger
            [x - 20, y - 20, w + 40, h + 40],    # Slightly larger
            [x + 20, y + 20, w, h],              # Shifted
            [x - 20, y + 20, w, h],              # Shifted
        ])
    
    detector = ScreenDetector(config)
    
    print(f"\nTesting {len(test_regions)} different regions...")
    print("(This will test template matching on each region)")
    
    best_region = None
    best_score = -1.0
    
    for i, region in enumerate(test_regions):
        x, y, w, h = region
        
        # Check bounds
        if x < 0 or y < 0 or x + w > width or y + h > height:
            continue
        
        roi = frame[y:y+h, x:x+w]
        if roi.size == 0:
            continue
        
        # Test template matching
        if len(detector.winning_templates) > 0:
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
            roi_processed = detector._preprocess_badge_image(roi_gray)
            
            best_match_score = -1.0
            for number, template in detector.winning_templates[:3]:  # Test first 3 templates
                h_t, w_t = template.shape
                roi_resized = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
                result = cv2.matchTemplate(roi_resized, template, cv2.TM_CCOEFF_NORMED)
                score = float(result[0][0])
                if score > best_match_score:
                    best_match_score = score
            
            if best_match_score > best_score:
                best_score = best_match_score
                best_region = region
            
            if i < 10:  # Show first 10
                marker = "" if best_match_score > 0.3 else "  "
                print(f"{marker} Region {i+1}: [{x}, {y}, {w}, {h}] - Best score: {best_match_score:.3f}")
    
    cap.release()
    
    if best_region and best_score > 0.3:
        print(f"\n Found better region!")
        print(f"   Region: {best_region}")
        print(f"   Best score: {best_score:.3f}")
        print(f"\n Update your config with:")
        print(f'   "screen_region": {best_region}')
    else:
        print(f"\n  No region found with good template match")
        print(f"   Best score: {best_score:.3f}")
        print(f"   This suggests templates don't match the video style")


def suggest_fixes(diagnostic_results: Dict):
    """Suggest specific fixes based on diagnostic results."""
    print("\n" + "=" * 80)
    print("SPECIFIC FIX RECOMMENDATIONS")
    print("=" * 80)
    
    template_score = diagnostic_results.get('best_template_score', -1.0)
    threshold = diagnostic_results.get('threshold', 0.65)
    
    if template_score < 0:
        print("\n🔴 CRITICAL ISSUE: Template scores are NEGATIVE")
        print("   This means templates don't match the video at all!")
        print("\n   Possible causes:")
        print("   1. Templates were created from a different video/game")
        print("   2. Screen region doesn't contain the winning number")
        print("   3. Video resolution/format changed")
        print("   4. Game UI changed")
        print("\n   Solutions:")
        print("    Check diagnostic_roi.png - does it show a number?")
        print("    If ROI is wrong, adjust screen_region coordinates")
        print("    If ROI is correct but templates don't match, recreate templates")
        print("    Try different start_frame values")
    
    if template_score < 0.3:
        print("\n  Template matching is very poor")
        print("   Even if you lower the threshold, detection will be unreliable")
        print("   Recommendation: Recreate templates from this video")
    
    print("\n📋 Action Plan:")
    print("   1. Check diagnostic_roi.png - verify it shows the winning number")
    print("   2. If ROI is wrong:")
    print("      - Use coordinate capture tool to find correct region")
    print("      - Or try different regions using the analysis script")
    print("   3. If ROI is correct but templates don't match:")
    print("      - Recreate templates from this video")
    print("      - Use create_templates_from_video.py")
    print("   4. Try different start_frame values")
    print("   5. Lower thresholds only as last resort (won't help if scores are negative)")


def main():
    """Main function."""
    config_path = 'config/default_config.json'
    video_path = 'roleta_brazileria.mp4'
    start_frame = 690
    
    # Find video
    if not Path(video_path).exists():
        video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov'))]
        if video_files:
            video_path = video_files[0]
    
    if not Path(config_path).exists():
        print(f" Config not found: {config_path}")
        return
    
    config = ConfigLoader.load_config(config_path)
    
    print("=" * 80)
    print("DETECTION FIX ANALYSIS")
    print("=" * 80)
    
    # Analyze ROI content
    roi_samples = analyze_roi_content(video_path, config, start_frame, num_frames=50)
    
    # Try different regions
    try_different_regions(video_path, config, start_frame)
    
    # Suggest fixes
    diagnostic_results = {
        'best_template_score': -0.128,  # From your diagnostic
        'threshold': 0.65
    }
    suggest_fixes(diagnostic_results)
    
    print("\n" + "=" * 80)
    print(" Analysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

