"""
Colab Test Script - Copy and paste into Google Colab cells
This tests roulette bot detection on video files.
"""

# ============================================================================
# CELL 1: Install Dependencies
# ============================================================================
# Run this first:
# !pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils -q

# ============================================================================
# CELL 2: Import Libraries and Setup
# ============================================================================
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import cv2
import numpy as np
from IPython.display import display
import matplotlib.pyplot as plt

# Create directories
os.makedirs('backend/app/detection', exist_ok=True)
os.makedirs('config', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('test_results', exist_ok=True)

print("Setup complete!")

# ============================================================================
# CELL 3: Upload Video File
# ============================================================================
from google.colab import files

print("Upload your video file (roleta_brazileria.mp4 or similar):")
uploaded = files.upload()

video_file = list(uploaded.keys())[0] if uploaded else None
print(f"\nVideo file: {video_file}")

# ============================================================================
# CELL 4: Create Config
# ============================================================================
config = {
  "detection": {
    "screen_region": None,
    "color_ranges": {
      "red": [
        [[0, 100, 100], [10, 255, 255]],
        [[170, 100, 100], [180, 255, 255]]
      ],
      "black": [
        [[0, 0, 0], [180, 255, 30]]
      ],
      "green": [
        [[50, 100, 100], [70, 255, 255]]
      ]
    },
    "templates_dir": "templates"
  },
  "strategy": {
    "type": "martingale",
    "base_bet": 10.0,
    "max_gales": 5
  },
  "logging": {
    "logs_dir": "logs"
  }
}

with open('config/default_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Config created!")

# ============================================================================
# CELL 5: Create Detector Code
# ============================================================================
detector_code = '''
import cv2
import numpy as np
import pytesseract
from typing import Dict, Optional

class ScreenDetector:
    def __init__(self, config):
        self.config = config
        self.color_ranges = config.get("detection", {}).get("color_ranges", {})
        if not self.color_ranges:
            self._initialize_default_color_ranges()
    
    def _initialize_default_color_ranges(self):
        self.color_ranges = {
            "red": [
                ([0, 100, 100], [10, 255, 255]),
                ([170, 100, 100], [180, 255, 255])
            ],
            "black": [([0, 0, 0], [180, 255, 30])],
            "green": [([50, 100, 100], [70, 255, 255])]
        }
    
    def get_color_from_number(self, number):
        if number == 0:
            return "green"
        red_numbers = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
        black_numbers = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
        if number in red_numbers:
            return "red"
        elif number in black_numbers:
            return "black"
        return "green"
    
    def detect_number_ocr(self, frame, region=None):
        try:
            if region:
                x, y, w, h = region
                roi = frame[y:y+h, x:x+w]
            else:
                roi = frame
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            custom_config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"
            text = pytesseract.image_to_string(thresh, config=custom_config)
            for char in text.strip():
                if char.isdigit():
                    number = int(char)
                    if 0 <= number <= 36:
                        return number
            return None
        except:
            return None
    
    def detect_result(self, frame=None):
        result = {"number": None, "color": None, "zero": False, "confidence": 0.0, "method": None}
        number = self.detect_number_ocr(frame)
        if number is not None:
            result["number"] = number
            result["color"] = self.get_color_from_number(number)
            result["zero"] = (number == 0)
            result["confidence"] = 0.7
            result["method"] = "ocr"
        return result
'''

with open('backend/app/detection/screen_detector.py', 'w') as f:
    f.write(detector_code)

with open('backend/app/__init__.py', 'w') as f:
    f.write('')
with open('backend/app/detection/__init__.py', 'w') as f:
    f.write('from .screen_detector import ScreenDetector')

print("Detector code created!")

# ============================================================================
# CELL 6: Test Video Function
# ============================================================================
def test_video_colab(video_path, config, frame_skip=1, max_frames=None):
    """Test detection on video file in Colab."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video: {video_path}")
    print(f"Frames: {total_frames}, FPS: {fps:.2f}")
    print(f"Processing every {frame_skip} frame(s)...")
    if max_frames:
        print(f"Limiting to {max_frames} frames")
    print("-" * 60)
    
    sys.path.append('.')
    from backend.app.detection import ScreenDetector
    detector = ScreenDetector(config)
    
    results = []
    frame_count = 0
    processed_count = 0
    successful_detections = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % frame_skip != 0:
            continue
        
        if max_frames and processed_count >= max_frames:
            break
        
        processed_count += 1
        
        try:
            # Detect result (pass frame directly to detector)
            result = detector.detect_result(frame)
            
            # Only process if we got a valid number
            if result.get('number') is not None:
                detected_number = result.get('number')
                
                # Skip if same number as last detection (number still on screen - normal in video)
                # Note: This test doesn't track last_detected_number, so it will show all detections
                # For production use, add: if detected_number == last_detected_number: continue
                
                # Validate result
                if not detector.validate_result(result):
                    # Validation failed - skip this detection
                    status = "[VALIDATION FAILED]"
                else:
                    successful_detections += 1
                    status = "[OK]"
            else:
                status = "[FAIL]"
            
            if processed_count % 10 == 0 or result.get('number') is not None:
                print(f"Frame {frame_count}/{total_frames} ({processed_count} processed) {status}")
                if result.get('number') is not None:
                    print(f"  Number: {result.get('number')}, Color: {result.get('color')}, "
                          f"Confidence: {result.get('confidence', 0):.2f}")
            
            results.append({
                "frame_number": frame_count,
                "timestamp": frame_count / fps if fps > 0 else frame_count,
                "result": result
            })
        except Exception as e:
            print(f"Frame {frame_count} - Error: {e}")
    
    cap.release()
    
    output_file = f"test_results/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "video_path": video_path,
            "total_frames": total_frames,
            "processed_frames": processed_count,
            "successful_detections": successful_detections,
            "detection_rate": (successful_detections / processed_count * 100) if processed_count > 0 else 0,
            "results": results
        }, f, indent=2)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total frames: {total_frames}")
    print(f"Processed: {processed_count}")
    print(f"Successful detections: {successful_detections}")
    print(f"Detection rate: {(successful_detections / processed_count * 100) if processed_count > 0 else 0:.2f}%")
    print(f"Results saved to: {output_file}")
    print("=" * 60)
    
    return results

print("Test function ready!")

# ============================================================================
# CELL 7: Run Test
# ============================================================================
if video_file:
    results = test_video_colab(
        video_file,
        config,
        frame_skip=5,      # Process every 5th frame (1 = all frames)
        max_frames=100     # Limit to 100 frames (None = all frames)
    )
else:
    print("Please upload a video file first!")

# ============================================================================
# CELL 8: Download Results
# ============================================================================
from google.colab import files
import glob

result_files = glob.glob('test_results/results_*.json')
if result_files:
    latest = max(result_files, key=os.path.getctime)
    files.download(latest)
    print(f"Downloaded: {latest}")
else:
    print("No results file found")

