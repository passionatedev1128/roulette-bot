# Fix for "config is not defined" Error

## Problem
You're getting `NameError: name 'config' is not defined` because the config variable hasn't been created yet.

## Solution
Create the config variable before calling the test function.

---

## Quick Fix

**Run this cell BEFORE calling `test_video_colab`:**

```python
# Create config
import json

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
    "max_gales": 5,
    "multiplier": 2.0
  },
  "logging": {
    "logs_dir": "logs"
  }
}

# Save config file (optional but recommended)
os.makedirs('config', exist_ok=True)
with open('config/default_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Config created!")
print(f"Config keys: {list(config.keys())}")
```

**Then run your test:**
```python
results = test_video_colab(
    video_file,
    config,  # Now this will be defined!
    frame_skip=5,
    max_frames=100
)
```

---

## Complete Working Sequence

Make sure you run these cells IN ORDER:

### Cell 1: Setup
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

### Cell 2: Upload Video
```python
from google.colab import files

print("Upload your video file:")
uploaded = files.upload()

video_file = list(uploaded.keys())[0] if uploaded else None
print(f"Video file: {video_file}")
```

### Cell 3: Create Config
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

### Cell 4: Create Detector Code
```python
# (Copy detector code from roulette_bot_test.ipynb or COLAB_INSTRUCTIONS.md)
```

### Cell 5: Define Test Function
```python
# (Copy test_video_colab function from roulette_bot_test.ipynb)
```

### Cell 6: Run Test
```python
# Make sure video_file and config are defined
if 'video_file' not in locals():
    print("Error: video_file not defined. Run upload cell first!")
elif 'config' not in locals():
    print("Error: config not defined. Run config cell first!")
else:
    results = test_video_colab(
        video_file,
        config,
        frame_skip=5,
        max_frames=100
    )
```

---

## Check Variables

Before running the test, verify both variables exist:

```python
# Check if variables are defined
print(f"video_file: {video_file if 'video_file' in locals() else 'NOT DEFINED'}")
print(f"config: {config if 'config' in locals() else 'NOT DEFINED'}")

# If config is not defined, create it:
if 'config' not in locals():
    print("Creating config...")
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
    print("Config created!")
```

---

## Common Issues

### Issue 1: Config not created
**Solution**: Run the config creation cell (Cell 3 above)

### Issue 2: Config created in different cell/session
**Solution**: Re-run the config cell in the same session

### Issue 3: Typo in variable name
**Solution**: Make sure it's `config` (lowercase), not `Config` or `CONFIG`

---

## Quick Test

Run this to verify everything is set up:

```python
# Quick check
try:
    print(f" video_file: {video_file}")
    print(f" config: {type(config)}")
    print(f" test_video_colab function: {callable(test_video_colab) if 'test_video_colab' in locals() else 'NOT DEFINED'}")
    print("\n Ready to run test!")
except NameError as e:
    print(f" Missing: {e}")
    print("\nPlease run the setup cells first.")
```

---

## Summary

**The fix is simple:**
1. Create the `config` dictionary before calling the test function
2. Make sure you run cells in order
3. Verify variables exist before using them

**Copy the "Cell 3: Create Config" code above and run it, then your test will work!**

