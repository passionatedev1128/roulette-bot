# What the Screen Detection Model Detects

## Overview

The `ScreenDetector` class detects roulette game results from screen captures or video frames. Here's exactly what it detects:

---

## 1. Winning Number (0-36)

**What it detects:**
- The winning number from the roulette wheel
- Range: 0 to 36 (37 possible numbers)

**How it detects:**
- **Primary method**: Template matching (most reliable)
  - Compares captured frame with saved number templates (0-36)
  - Finds best match using OpenCV template matching
- **Fallback method**: OCR (Optical Character Recognition)
  - Uses pytesseract to read numbers from the screen
  - Extracts digits from the captured image

**Output:**
```python
result["number"] = 17  # Example: number 17 detected
```

---

## 2. Color (Red, Black, or Green)

**What it detects:**
- The color of the winning number
- Three possible values: `"red"`, `"black"`, or `"green"`

**How it detects:**
- **Method 1**: Determined from number (most reliable)
  - If number = 0  color = "green"
  - If number in red list  color = "red"
  - If number in black list  color = "black"
  
- **Method 2**: Direct color detection (fallback)
  - Uses HSV color space to detect colors on screen
  - Compares against configured color ranges

**Roulette Color Mapping:**
- **Red numbers**: 1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36
- **Black numbers**: 2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35
- **Green number**: 0

**Output:**
```python
result["color"] = "black"  # Example: black detected
```

---

## 3. Zero Detection

**What it detects:**
- Whether the winning number is zero (0)
- Boolean value: `True` or `False`

**How it detects:**
- Checks if detected number equals 0
- Or checks if detected color is "green" (since only 0 is green)

**Output:**
```python
result["zero"] = False  # Example: not zero
result["zero"] = True   # Example: zero detected
```

---

## 4. Detection Confidence

**What it detects:**
- How confident the detection is
- Range: 0.0 to 1.0 (0% to 100% confidence)

**Confidence Levels:**
- **0.9-1.0**: Very confident (high reliability)
- **0.7-0.9**: Confident (reliable)
- **0.5-0.7**: Fair confidence (may have errors)
- **<0.5**: Low confidence (likely incorrect)

**How it's calculated:**
- Template matching: 0.9 (high confidence)
- OCR: 0.7 (medium confidence)
- Color fallback: 0.5 (low confidence)

**Output:**
```python
result["confidence"] = 0.95  # Example: 95% confident
```

---

## 5. Detection Method

**What it detects:**
- Which detection method was used
- Three possible values: `"template"`, `"ocr"`, or `"color_fallback"`

**Methods:**
- **"template"**: Template matching (best, most accurate)
  - Uses saved number images (0-36) to match against screen
  - Highest accuracy and confidence
  
- **"ocr"**: Optical Character Recognition
  - Uses pytesseract to read numbers
  - Less reliable than templates
  
- **"color_fallback"**: Color-only detection
  - Only color detected, no number
  - Lowest confidence, last resort

**Output:**
```python
result["method"] = "template"  # Example: used template matching
```

---

## Complete Detection Result

The detector returns a dictionary with all detected information:

```python
{
    "number": 17,           # Detected number (0-36)
    "color": "black",       # Detected color (red/black/green)
    "zero": False,          # Is it zero? (True/False)
    "confidence": 0.95,      # Confidence score (0.0-1.0)
    "method": "template"    # Detection method used
}
```

### Example Results:

**Example 1: Successful Detection**
```python
{
    "number": 17,
    "color": "black",
    "zero": False,
    "confidence": 0.95,
    "method": "template"
}
```

**Example 2: Zero Detected**
```python
{
    "number": 0,
    "color": "green",
    "zero": True,
    "confidence": 0.92,
    "method": "template"
}
```

**Example 3: OCR Fallback**
```python
{
    "number": 3,
    "color": "red",
    "zero": False,
    "confidence": 0.70,
    "method": "ocr"
}
```

**Example 4: Failed Detection**
```python
{
    "number": None,         # No number detected
    "color": None,          # No color detected
    "zero": False,
    "confidence": 0.0,
    "method": None
}
```

---

## Detection Process Flow

```
1. Capture Screen/Video Frame
   ↓
2. Try Template Matching (if templates exist)
   ├─ Success  number detected, confidence = 0.9
   └─ Fail  continue
   ↓
3. Try OCR Detection
   ├─ Success  number detected, confidence = 0.7
   └─ Fail  continue
   ↓
4. Try Color Detection Only
   ├─ Success  color detected, confidence = 0.5
   └─ Fail  return None
   ↓
5. Determine Color from Number (if number detected)
   ↓
6. Check if Zero
   ↓
7. Return Complete Result
```

---

## What It Does NOT Detect

The detector does NOT detect:
-  Bet amounts
-  Balance/account information
-  Previous results history
-  Betting buttons/interface
-  Game state (paused, active, etc.)
-  Round number or spin count
-  Multiple numbers at once

**It ONLY detects the current winning number and its color.**

---

## Validation

The detector also validates results:
-  Checks if number is in valid range (0-36)
-  Verifies color matches number
-  Compares with recent history to catch errors
-  Filters low-confidence detections

---

## Usage Example

```python
from backend.app.detection import ScreenDetector

# Initialize detector
detector = ScreenDetector(config)

# Detect result from frame
result = detector.detect_result(frame)

# Access detected values
number = result["number"]        # 17
color = result["color"]          # "black"
is_zero = result["zero"]          # False
confidence = result["confidence"] # 0.95
method = result["method"]         # "template"

# Use for betting decisions
if result["number"] is not None:
    print(f"Number {result['number']} ({result['color']}) detected!")
    # Place bet based on result
else:
    print("Detection failed!")
```

---

## Summary

**What the detector detects:**
1.  **Winning number** (0-36)
2.  **Color** (red/black/green)
3.  **Zero status** (True/False)
4.  **Confidence score** (0.0-1.0)
5.  **Detection method** (template/ocr/color)

**Output format:**
```python
{
    "number": int or None,
    "color": str or None,
    "zero": bool,
    "confidence": float,
    "method": str or None
}
```

**Key point:** The detector focuses on extracting the winning number and color from the roulette table display. This is the core information needed for betting decisions.

