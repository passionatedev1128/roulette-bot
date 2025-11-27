# How to Improve Detection Rate

## Quick Summary

**Most Important:**
1.  **Create number templates** (0-36) - Can increase accuracy by 20-30%
2.  **Use template matching** instead of OCR
3.  **Calibrate color ranges** for your specific game
4.  **Set screen region** to focus on table area
5.  **Improve video quality** (resolution, lighting)

---

## Method 1: Create Number Templates (BEST - +20-30% Accuracy)

### Why Templates?
- **Template matching is 90%+ accurate**
- **OCR is only 60-70% accurate**
- Templates are game-specific and very reliable

### How to Create Templates

#### Step 1: Capture Screenshots
1. Record or capture frames when numbers appear clearly
2. Save frames with visible numbers (0-36)

#### Step 2: Extract Numbers
1. Open frame in image editor (GIMP, Photoshop, etc.)
2. Crop individual numbers
3. Each number should be:
   - Clear and not blurry
   - Match the game's font exactly
   - Size: 20-50 pixels height (recommended)
   - Format: PNG (transparent background preferred)

#### Step 3: Save Templates
Save as:
```
templates/
  number_0.png
  number_1.png
  number_2.png
  ...
  number_36.png
```

#### Step 4: Test
```python
# The detector will automatically use templates if available
# No code changes needed - just place files in templates/ folder
```

**Expected Improvement:** 60-70%  90-95% detection rate

---

## Method 2: Optimize OCR Settings

### Improve OCR Accuracy

If you can't create templates, optimize OCR:

```python
# In screen_detector.py, improve OCR preprocessing:

def detect_number_ocr(self, frame, region=None):
    try:
        if region:
            x, y, w, h = region
            roi = frame[y:y+h, x:x+w]
        else:
            roi = frame
        
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Resize if too small (OCR works better on larger text)
        height, width = gray.shape
        if height < 50:
            scale = 50 / height
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Apply denoising
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Apply adaptive thresholding (better than simple threshold)
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        # Try different OCR configurations
        configs = [
            r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',  # Single line
            r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',  # Single word
            r'--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789', # Single character
        ]
        
        for config in configs:
            text = pytesseract.image_to_string(thresh, config=config)
            for char in text.strip():
                if char.isdigit():
                    number = int(char)
                    if 0 <= number <= 36:
                        return number
        
        return None
    except:
        return None
```

**Expected Improvement:** +5-10% detection rate

---

## Method 3: Calibrate Color Ranges

### Adjust HSV Color Ranges

Colors vary by game/screen. Calibrate for your specific game:

#### Step 1: Find Color Values
```python
import cv2
import numpy as np

# Load a frame with a red number
frame = cv2.imread('red_example.png')
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Get average HSV values for red area
red_region = frame[100:200, 100:200]  # Adjust coordinates
red_hsv = cv2.cvtColor(red_region, cv2.COLOR_BGR2HSV)
avg_hsv = np.mean(red_hsv.reshape(-1, 3), axis=0)

print(f"Average HSV: {avg_hsv}")
# Use this to adjust color ranges in config
```

#### Step 2: Update Config
```json
{
  "detection": {
    "color_ranges": {
      "red": [
        [[0, 100, 100], [10, 255, 255]],      // Adjust these values
        [[170, 100, 100], [180, 255, 255]]
      ],
      "black": [
        [[0, 0, 0], [180, 255, 30]]           // Adjust for your game
      ],
      "green": [
        [[50, 100, 100], [70, 255, 255]]     // Adjust for your game
      ]
    }
  }
}
```

**Expected Improvement:** +5-10% for color-based detections

---

## Method 4: Set Screen Region

### Focus Detection on Table Area

Instead of processing entire screen, focus on table:

#### Step 1: Find Table Coordinates
```python
# Take screenshot
import pyautogui
screenshot = pyautogui.screenshot()
screenshot.save('full_screen.png')

# Open in image editor and find table coordinates
# Example: table is at x=100, y=200, width=800, height=600
```

#### Step 2: Update Config
```json
{
  "detection": {
    "screen_region": [100, 200, 800, 600]  // [x, y, width, height]
  }
}
```

**Benefits:**
- Faster processing
- Less noise
- Higher accuracy
- Better focus on numbers

**Expected Improvement:** +5-15% detection rate

---

## Method 5: Improve Image Preprocessing

### Enhance Image Quality Before Detection

```python
def preprocess_frame(self, frame):
    """Preprocess frame for better detection."""
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Increase contrast
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
    
    # Apply sharpening
    kernel = np.array([[-1,-1,-1],
                       [-1, 9,-1],
                       [-1,-1,-1]])
    gray = cv2.filter2D(gray, -1, kernel)
    
    # Remove noise
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    return gray
```

**Expected Improvement:** +3-7% detection rate

---

## Method 6: Use Multiple Detection Attempts

### Try Multiple Regions/Methods

```python
def detect_result(self, frame=None):
    """Try multiple detection strategies."""
    if frame is None:
        frame = self.capture_screen()
    
    # Try different regions
    regions = [
        None,  # Full frame
        (100, 100, 200, 100),  # Region 1
        (300, 100, 200, 100),  # Region 2
    ]
    
    best_result = None
    best_confidence = 0
    
    for region in regions:
        # Try template matching
        number = self.detect_number_template(frame, region)
        if number is not None:
            confidence = 0.9
            if confidence > best_confidence:
                best_result = {
                    "number": number,
                    "color": self.get_color_from_number(number),
                    "zero": (number == 0),
                    "confidence": confidence,
                    "method": "template"
                }
                best_confidence = confidence
        
        # Try OCR
        if best_result is None:
            number = self.detect_number_ocr(frame, region)
            if number is not None:
                confidence = 0.7
                if confidence > best_confidence:
                    best_result = {
                        "number": number,
                        "color": self.get_color_from_number(number),
                        "zero": (number == 0),
                        "confidence": confidence,
                        "method": "ocr"
                    }
                    best_confidence = confidence
    
    return best_result or {
        "number": None,
        "color": None,
        "zero": False,
        "confidence": 0.0,
        "method": None
    }
```

**Expected Improvement:** +5-10% detection rate

---

## Method 7: Improve Video Quality

### Record Better Test Videos

1. **Resolution**: Use higher resolution (1080p or higher)
2. **Lighting**: Ensure good lighting on screen
3. **Stability**: Use stable video (not shaky)
4. **Focus**: Ensure numbers are in focus
5. **Frame Rate**: Higher FPS for smoother detection

**Expected Improvement:** +5-15% detection rate

---

## Method 8: Validate and Filter Results

### Add Better Validation

```python
def validate_result(self, result):
    """Enhanced validation."""
    if result["number"] is None:
        return False
    
    # Check confidence threshold
    if result["confidence"] < 0.6:  # Increase threshold
        return False
    
    # Check against recent history
    if len(self.detection_history) > 0:
        last_number = self.detection_history[-1].get("number")
        # Reject if same number twice in a row (unless very confident)
        if result["number"] == last_number and result["confidence"] < 0.95:
            return False
    
    # Check if number is in valid range
    if not (0 <= result["number"] <= 36):
        return False
    
    # Cross-validate color with number
    expected_color = self.get_color_from_number(result["number"])
    if result["color"] != expected_color:
        # Allow small mismatch but lower confidence
        if result["confidence"] < 0.9:
            return False
    
    return True
```

**Expected Improvement:** Reduces false positives, improves reliability

---

## Method 9: Use Machine Learning (Advanced)

### Train Custom OCR Model

For very specific games, consider training a custom model:

```python
# Example using EasyOCR (alternative to pytesseract)
import easyocr

reader = easyocr.Reader(['en'])

def detect_with_easyocr(self, frame):
    """Use EasyOCR for better accuracy."""
    results = reader.readtext(frame)
    for (bbox, text, confidence) in results:
        if text.isdigit():
            number = int(text)
            if 0 <= number <= 36:
                return number, confidence
    return None, 0
```

**Expected Improvement:** +10-15% over standard OCR

---

## Priority Action Plan

### Quick Wins (Do First)
1.  **Create number templates** - Biggest impact (+20-30%)
2.  **Set screen region** - Easy fix (+5-15%)
3.  **Calibrate color ranges** - Quick adjustment (+5-10%)

### Medium Effort
4.  **Improve OCR preprocessing** - Code changes (+5-10%)
5.  **Add validation** - Code changes (reduces errors)
6.  **Try multiple regions** - Code changes (+5-10%)

### Advanced
7.  **Use EasyOCR or custom model** - Requires setup (+10-15%)
8.  **Machine learning approach** - Complex but very accurate

---

## Testing Your Improvements

### Before/After Comparison

```python
# Test with same video
results_before = test_video_colab(video_file, config_old)
results_after = test_video_colab(video_file, config_new)

print(f"Before: {results_before['detection_rate']}%")
print(f"After: {results_after['detection_rate']}%")
print(f"Improvement: {results_after['detection_rate'] - results_before['detection_rate']}%")
```

---

## Expected Results

| Method | Difficulty | Expected Improvement |
|--------|-----------|---------------------|
| Create Templates | Easy | +20-30% |
| Set Screen Region | Easy | +5-15% |
| Calibrate Colors | Easy | +5-10% |
| Improve OCR | Medium | +5-10% |
| Better Validation | Medium | Reduces errors |
| Multiple Regions | Medium | +5-10% |
| EasyOCR | Medium | +10-15% |
| ML Model | Hard | +15-25% |

**Combined:** Can improve from 60-70% to 90-95%+ detection rate

---

## Troubleshooting Low Detection

### If Detection Rate < 50%
- Check video quality (too blurry?)
- Verify templates exist and match game
- Check screen region is correct
- Test OCR separately

### If Detection Rate 50-70%
- Create templates (biggest impact)
- Set screen region
- Calibrate color ranges
- Improve preprocessing

### If Detection Rate 70-90%
- Fine-tune templates
- Add validation
- Try multiple detection methods
- Optimize preprocessing

---

## Summary

**Best Practices:**
1.  Always create number templates first
2.  Set screen region to focus detection
3.  Calibrate for your specific game
4.  Test with multiple videos
5.  Validate results before using

**Quick Start:**
1. Create templates for numbers 0-36
2. Set screen_region in config
3. Test and compare results
4. Iterate and improve

**Goal:** Achieve >90% detection rate with >0.8 confidence

