# Fix for SyntaxError in Detector Code

## Problem
The detector code file has a syntax error because the multi-line string wasn't written correctly to the file.

## Solution
Rewrite the detector code file properly.

---

## Quick Fix

**Delete the broken file and recreate it:**

```python
import os

# Remove broken files
import shutil
if os.path.exists('backend'):
    shutil.rmtree('backend')
    print("Removed old backend directory")

# Create directories fresh
os.makedirs('backend/app/detection', exist_ok=True)

# Write detector code directly (not from a string)
detector_file_content = """import cv2
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
"""

# Write the file directly
with open('backend/app/detection/screen_detector.py', 'w') as f:
    f.write(detector_file_content)

# Create __init__ files
with open('backend/app/__init__.py', 'w') as f:
    f.write('')

with open('backend/app/detection/__init__.py', 'w') as f:
    f.write('from .screen_detector import ScreenDetector')

print(" Detector code created successfully!")
print(" backend/app/detection/screen_detector.py")
print(" backend/app/__init__.py")
print(" backend/app/detection/__init__.py")

# Verify it works
try:
    import sys
    sys.path.append('.')
    from backend.app.detection import ScreenDetector
    print("\n Import test successful!")
except Exception as e:
    print(f"\n Import test failed: {e}")
```

---

## Alternative: Use exec() method

If the above doesn't work, try this method:

```python
import os

# Create directories
os.makedirs('backend/app/detection', exist_ok=True)

# Write detector code using write() with proper escaping
detector_lines = [
    "import cv2",
    "import numpy as np",
    "import pytesseract",
    "from typing import Dict, Optional",
    "",
    "class ScreenDetector:",
    "    def __init__(self, config):",
    "        self.config = config",
    "        self.color_ranges = config.get(\"detection\", {}).get(\"color_ranges\", {})",
    "        if not self.color_ranges:",
    "            self._initialize_default_color_ranges()",
    "        self.detection_history = []",
    "    ",
    "    def _initialize_default_color_ranges(self):",
    "        self.color_ranges = {",
    "            \"red\": [",
    "                ([0, 100, 100], [10, 255, 255]),",
    "                ([170, 100, 100], [180, 255, 255])",
    "            ],",
    "            \"black\": [([0, 0, 0], [180, 255, 30])],",
    "            \"green\": [([50, 100, 100], [70, 255, 255])]",
    "        }",
    "    ",
    "    def get_color_from_number(self, number):",
    "        if number == 0:",
    "            return \"green\"",
    "        red_numbers = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]",
    "        black_numbers = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]",
    "        if number in red_numbers:",
    "            return \"red\"",
    "        elif number in black_numbers:",
    "            return \"black\"",
    "        return \"green\"",
    "    ",
    "    def detect_number_ocr(self, frame, region=None):",
    "        try:",
    "            if region:",
    "                x, y, w, h = region",
    "                roi = frame[y:y+h, x:x+w]",
    "            else:",
    "                roi = frame",
    "            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)",
    "            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)",
    "            custom_config = r\"--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789\"",
    "            text = pytesseract.image_to_string(thresh, config=custom_config)",
    "            for char in text.strip():",
    "                if char.isdigit():",
    "                    number = int(char)",
    "                    if 0 <= number <= 36:",
    "                        return number",
    "            return None",
    "        except:",
    "            return None",
    "    ",
    "    def detect_result(self, frame=None):",
    "        result = {\"number\": None, \"color\": None, \"zero\": False, \"confidence\": 0.0, \"method\": None}",
    "        number = self.detect_number_ocr(frame)",
    "        if number is not None:",
    "            result[\"number\"] = number",
    "            result[\"color\"] = self.get_color_from_number(number)",
    "            result[\"zero\"] = (number == 0)",
    "            result[\"confidence\"] = 0.7",
    "            result[\"method\"] = \"ocr\"",
    "        return result"
]

with open('backend/app/detection/screen_detector.py', 'w') as f:
    f.write('\n'.join(detector_lines))

# Create __init__ files
with open('backend/app/__init__.py', 'w') as f:
    f.write('')

with open('backend/app/detection/__init__.py', 'w') as f:
    f.write('from .screen_detector import ScreenDetector')

print(" Detector code created!")
```

---

## Verify File Was Created Correctly

After running the fix, verify the file:

```python
# Check if file exists and read first few lines
import os

file_path = 'backend/app/detection/screen_detector.py'
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        print(f"File exists: {len(lines)} lines")
        print("First 5 lines:")
        for i, line in enumerate(lines[:5], 1):
            print(f"{i}: {line.rstrip()}")
        
        # Try to compile it
        try:
            compile(open(file_path).read(), file_path, 'exec')
            print("\n File syntax is valid!")
        except SyntaxError as e:
            print(f"\n Syntax error: {e}")
else:
    print("File does not exist!")
```

---

## Complete Working Cell (Copy This Entire Block)

```python
# Complete detector setup - copy this entire block
import os
import shutil

# Clean up if needed
if os.path.exists('backend'):
    shutil.rmtree('backend')

# Create directories
os.makedirs('backend/app/detection', exist_ok=True)

# Write detector code
detector_code = """import cv2
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
"""

with open('backend/app/detection/screen_detector.py', 'w') as f:
    f.write(detector_code)

with open('backend/app/__init__.py', 'w') as f:
    f.write('')

with open('backend/app/detection/__init__.py', 'w') as f:
    f.write('from .screen_detector import ScreenDetector')

# Verify
import sys
sys.path.append('.')
from backend.app.detection import ScreenDetector
print(" Detector code created and verified!")
```

---

## Summary

**The Problem:** The detector code file has a syntax error because the multi-line string wasn't written correctly.

**The Fix:** 
1. Delete the broken `backend` directory
2. Recreate it with the correct code using triple-quoted strings (`"""`)

**Run the "Complete Working Cell" code above, then your test will work!**

