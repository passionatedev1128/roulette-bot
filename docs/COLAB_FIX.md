# Fix for Colab Import Error

## Problem
You're trying to import `test_video_colab` but it's not installed as a module.

## Solution
**Don't import it** - just copy the function definition directly into a Colab cell.

---

## Quick Fix

### Option 1: Copy Function Directly (Recommended)

**Copy this entire code block into a Colab cell and run it:**

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

**Then run your test:**
```python
# Make sure video_file has the .mp4 extension
video_file = "roleta_brazileria.mp4"  # Add .mp4 if needed

results = test_video_colab(
    video_file,
    config,
    frame_skip=5,
    max_frames=100
)
```

---

### Option 2: Check Video Filename

Also, make sure your video filename includes the extension:

```python
# If you uploaded as "roleta_brazileria.mp4", use:
video_file = "roleta_brazileria.mp4"  # Not just "roleta_brazileria"

results = test_video_colab(
    video_file,  # Use the full filename
    config,
    frame_skip=5,
    max_frames=100
)
```

---

## Complete Working Example

Here's the complete sequence in Colab:

**Cell 1: Setup (run first)**
```python
# Install dependencies
!pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils -q

# Import and setup
import sys
import os
import json
from datetime import datetime
import cv2
import numpy as np

# Create directories
os.makedirs('backend/app/detection', exist_ok=True)
os.makedirs('config', exist_ok=True)
os.makedirs('test_results', exist_ok=True)
```

**Cell 2: Upload video**
```python
from google.colab import files
uploaded = files.upload()
video_file = list(uploaded.keys())[0]
print(f"Video: {video_file}")
```

**Cell 3: Create config**
```python
config = {
  "detection": {
    "screen_region": None,
    "color_ranges": {
      "red": [
        [[0, 100, 100], [10, 255, 255]],
        [[170, 100, 100], [180, 255, 255]]
      ],
      "black": [[[0, 0, 0], [180, 255, 30]]],
      "green": [[[50, 100, 100], [70, 255, 255]]]
    },
    "templates_dir": "templates"
  }
}

with open('config/default_config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

**Cell 4: Create detector**
```python
# (Copy the detector code from earlier cells or roulette_bot_test.ipynb)
# ... detector code ...
```

**Cell 5: Define test function**
```python
# Copy the test_video_colab function from above
```

**Cell 6: Run test**
```python
results = test_video_colab(
    video_file,  # Use the actual filename from upload
    config,
    frame_skip=5,
    max_frames=100
)
```

---

## Why This Happens

- `roulette_bot_test.py` is a reference file, not meant to be imported
- Colab cells define functions in the current session
- You need to define the function in a Colab cell first, then call it

---

## Quick Check

Before running, verify:
1.  Video uploaded (check `video_file` variable)
2.  Config created (check `config` variable)
3.  Detector code created (check `backend/app/detection/screen_detector.py` exists)
4.  Function defined (run the function definition cell)
5.  Then call the function

