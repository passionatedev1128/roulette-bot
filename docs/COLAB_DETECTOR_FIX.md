# Fix for "No module named 'backend'" Error

## Problem
You're getting `ModuleNotFoundError: No module named 'backend'` because the detector code hasn't been created yet.

## Solution
Create the detector code before calling the test function.

---

## Quick Fix

**Run this cell BEFORE calling `test_video_colab`:**

```python
# Create detector code
import os

# Create directories
os.makedirs('backend/app/detection', exist_ok=True)

# Create detector code
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
        self.detection_history = []
    
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

# Write detector code to file
with open('backend/app/detection/screen_detector.py', 'w') as f:
    f.write(detector_code)

# Create __init__ files
with open('backend/app/__init__.py', 'w') as f:
    f.write('')

with open('backend/app/detection/__init__.py', 'w') as f:
    f.write('from .screen_detector import ScreenDetector')

print("Detector code created!")
print(" backend/app/detection/screen_detector.py")
print(" backend/app/__init__.py")
print(" backend/app/detection/__init__.py")
```

**Then your test will work:**

```python
results = test_video_colab(
    video_file,
    config,
    frame_skip=5,
    max_frames=100
)
```

---

## Complete Working Sequence

Make sure you run these cells IN ORDER:

### 1. Setup
```python
!pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils -q

import sys
import os
import json
from datetime import datetime
import cv2
import numpy as np

os.makedirs('backend/app/detection', exist_ok=True)
os.makedirs('config', exist_ok=True)
os.makedirs('test_results', exist_ok=True)

print("Setup complete!")
```

### 2. Upload Video
```python
from google.colab import files

print("Upload your video file:")
uploaded = files.upload()

video_file = list(uploaded.keys())[0] if uploaded else None
print(f"Video file: {video_file}")
```

### 3. Create Config
```python
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

os.makedirs('config', exist_ok=True)
with open('config/default_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Config created!")
```

### 4. Create Detector Code (THIS IS WHAT YOU'RE MISSING!)
```python
# Copy the detector code from above (the "Quick Fix" section)
```

### 5. Define Test Function
```python
def test_video_colab(video_path, config, frame_skip=1, max_frames=None):
    """Test detection on video file in Colab."""
    import cv2
    import sys
    from datetime import datetime
    import json
    import os
    
    # Import detector
    sys.path.append('.')
    from backend.app.detection import ScreenDetector
    
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
            result = detector.detect_result(frame)
            if result.get('number') is not None:
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
    os.makedirs('test_results', exist_ok=True)
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
```

### 6. Run Test
```python
results = test_video_colab(
    video_file,
    config,
    frame_skip=5,
    max_frames=100
)
```

---

## Verify Setup

Before running the test, check if everything is set up:

```python
# Check if files exist
import os

files_to_check = [
    'backend/app/detection/screen_detector.py',
    'backend/app/__init__.py',
    'backend/app/detection/__init__.py',
    'config/default_config.json'
]

print("Checking files...")
for file_path in files_to_check:
    exists = os.path.exists(file_path)
    status = "" if exists else ""
    print(f"{status} {file_path}")

# Check if variables are defined
print("\nChecking variables...")
print(f"video_file: {'' if 'video_file' in locals() else ''}")
print(f"config: {'' if 'config' in locals() else ''}")
print(f"test_video_colab: {'' if 'test_video_colab' in locals() else ''}")

# Try importing
try:
    sys.path.append('.')
    from backend.app.detection import ScreenDetector
    print(f"\n ScreenDetector imported successfully!")
except Exception as e:
    print(f"\n Import failed: {e}")
```

---

## Summary

**The issue:** You're missing the detector code files.

**The fix:** Run the "Create Detector Code" cell (Step 4 above) before calling the test function.

**Key point:** The `backend` module needs to be created by writing the Python files. It's not a package you install - it's code you create in Colab.

---

## Quick Copy-Paste Solution

Just copy the entire "Quick Fix" code block at the top of this file into a Colab cell and run it. Then your test will work!

