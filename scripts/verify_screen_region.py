"""
Quick script to verify the new screen_region coordinates
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

# Configuration
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

print("=" * 80)
print("VERIFYING NEW SCREEN REGION")
print("=" * 80)
print(f"Screen region: {screen_region}")
print(f"Format: [x, y, width, height]")

if not screen_region or len(screen_region) != 4:
    print(" Screen region not configured properly")
    sys.exit(1)

x, y, w, h = screen_region
print(f"Coordinates: x={x}, y={y}, width={w}, height={h}")

# Open video and extract ROI
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f" Cannot open video: {video_path}")
    sys.exit(1)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"\nVideo info:")
print(f"  Resolution: {width}x{height}")
print(f"  Total frames: {total_frames}")

# Check bounds
if x < 0 or y < 0 or x + w > width or y + h > height:
    print(f"\n  WARNING: Screen region extends beyond frame bounds!")
    print(f"   Frame bounds: 0-{width} (width), 0-{height} (height)")
    print(f"   Region bounds: {x}-{x+w} (width), {y}-{y+h} (height)")
else:
    print(f"\n Screen region is within frame bounds")

# Test multiple frames
print(f"\nTesting ROI on multiple frames starting from {start_frame}...")
print("-" * 80)

detector = ScreenDetector(config)
frame_detector = FrameDetector(config, video_path)
frame_detector.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

roi_samples = []
detections = []

for i in range(10):
    frame = frame_detector.capture_screen()
    if frame is None:
        break
    
    frame_num = start_frame + i
    
    # Extract ROI
    roi = frame[y:y+h, x:x+w]
    
    if roi.size == 0:
        print(f"Frame {frame_num}:  ROI is empty")
        continue
    
    # Check ROI quality
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    variance = np.var(roi_gray)
    mean_val = np.mean(roi_gray)
    
    # Try detection
    detection = detector.detect_result(frame)
    
    if detection and detection.get('number') is not None:
        number = detection.get('number')
        method = detection.get('method', 'unknown')
        confidence = detection.get('confidence', 0)
        detections.append(detection)
        print(f"Frame {frame_num}:  Detected {number} (method: {method}, conf: {confidence:.2f}, var: {variance:.1f})")
    else:
        # Test template matching manually
        if len(detector.winning_templates) > 0:
            roi_processed = detector._preprocess_badge_image(roi_gray)
            best_score = -1.0
            best_match = None
            
            for num, template in detector.winning_templates[:3]:
                h_t, w_t = template.shape
                roi_resized = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
                result = cv2.matchTemplate(roi_resized, template, cv2.TM_CCOEFF_NORMED)
                score = float(result[0][0])
                if score > best_score:
                    best_score = score
                    best_match = num
            
            if best_match is not None:
                marker = "" if best_score > 0.3 else "" if best_score > 0 else ""
                print(f"Frame {frame_num}: {marker} No detection (best template: {best_match}, score: {best_score:.3f}, var: {variance:.1f})")
            else:
                print(f"Frame {frame_num}:  No detection (var: {variance:.1f})")
        else:
            print(f"Frame {frame_num}:  No detection (var: {variance:.1f})")
    
    # Save first ROI for inspection
    if i == 0:
        cv2.imwrite('verify_roi_new_region.png', roi)
        print(f"\n Saved first ROI to: verify_roi_new_region.png")
        print(f"   👀 CHECK THIS IMAGE - Does it show the winning number?")

frame_detector.release()

# Summary
print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print(f"Successful detections: {len(detections)}/10")
print(f"Success rate: {len(detections)/10*100:.1f}%")

if len(detections) > 0:
    print(f"\n GOOD! Detection is working with new screen_region")
    methods = {}
    for d in detections:
        method = d.get('method', 'unknown')
        methods[method] = methods.get(method, 0) + 1
    print(f"   Methods used: {methods}")
else:
    print(f"\n  Still no detections")
    print(f"   Check verify_roi_new_region.png - does it show a number?")
    print(f"   If ROI is correct, you may need to recreate templates")

print("\n" + "=" * 80)
print("Next steps:")
print("  1. Check verify_roi_new_region.png - verify it shows winning number")
print("  2. If ROI is correct but no detection, recreate templates")
print("  3. If ROI is wrong, adjust screen_region again")
print("=" * 80)

