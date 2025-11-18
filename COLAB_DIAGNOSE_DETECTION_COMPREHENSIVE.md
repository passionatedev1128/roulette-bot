# Comprehensive Detection Diagnostic for Colab

## 🔍 Complete Detection Troubleshooting

This script will systematically check every aspect of detection to identify why numbers aren't being detected.

---

## 🚀 Quick Start

### Step 1: Install Dependencies
```python
!pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils -q
print("✅ Dependencies installed!")
```

### Step 2: Upload Project Files
Upload your project folder and video file via Files sidebar

### Step 3: Run Comprehensive Diagnostic
**Copy and paste this complete diagnostic code:**

```python
import sys
import os
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Mock pyautogui for Colab
from unittest.mock import MagicMock
sys.modules['pyautogui'] = MagicMock()
mock_pyautogui = sys.modules['pyautogui']
mock_pyautogui.screenshot = MagicMock(return_value=None)
mock_pyautogui.moveTo = MagicMock()
mock_pyautogui.click = MagicMock()
mock_pyautogui.write = MagicMock()
mock_pyautogui.press = MagicMock()
mock_pyautogui.PAUSE = 0.1
mock_pyautogui.FAILSAFE = False
print("✅ pyautogui mocked")

sys.path.insert(0, os.path.abspath('.'))

from backend.app.config_loader import ConfigLoader
from backend.app.detection.frame_detector import FrameDetector
from backend.app.detection.screen_detector import ScreenDetector

# Configuration
config_path = 'config/default_config.json'
video_path = 'roleta_brazileria.mp4'
start_frame = 690  # Adjust this

# Find video file
if not Path(video_path).exists():
    video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov'))]
    if video_files:
        video_path = video_files[0]
        print(f"✅ Using video: {video_path}")
    else:
        print(f"❌ No video file found!")
        raise FileNotFoundError("No video file found")

# Load config
if not Path(config_path).exists():
    print(f"❌ Config file not found: {config_path}")
    raise FileNotFoundError(f"Config file not found: {config_path}")

config = ConfigLoader.load_config(config_path)
detection_config = config.get('detection', {})
threshold = detection_config.get('winning_template_threshold', 0.65)

print("=" * 80)
print("COMPREHENSIVE DETECTION DIAGNOSTIC")
print("=" * 80)
print(f"Config: {config_path}")
print(f"Video: {video_path}")
print(f"Start frame: {start_frame}")
print(f"Template threshold: {threshold}")
print(f"OCR fallback: {detection_config.get('enable_ocr_fallback', True)}")
print(f"OCR threshold: {detection_config.get('ocr_confidence_threshold', 70.0)}")

# ============================================================================
# STEP 1: CHECK TEMPLATES
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: CHECKING TEMPLATES")
print("=" * 80)

detector = ScreenDetector(config)
templates_dir = detection_config.get('winning_templates_dir', 'winning-number_templates/')
print(f"Templates directory: {templates_dir}")
print(f"Current working directory: {Path.cwd()}")

template_path = Path(templates_dir)
if not template_path.is_absolute():
    # Try multiple locations
    possible_paths = [
        template_path,
        Path.cwd() / template_path,
    ]
    current = Path.cwd()
    for parent in [current] + list(current.parents)[:3]:
        possible_paths.append(parent / template_path)
    
    found = False
    for path in possible_paths:
        if path.exists() and path.is_dir():
            template_path = path
            found = True
            print(f"✅ Found templates directory at: {template_path.absolute()}")
            break
    
    if not found:
        print(f"❌ Templates directory NOT FOUND!")
        print(f"   Tried locations:")
        for p in possible_paths[:5]:
            print(f"      - {p.absolute()}")
        raise FileNotFoundError("Templates directory not found")
else:
    if not template_path.exists():
        print(f"❌ Templates directory NOT FOUND at: {template_path}")
        raise FileNotFoundError("Templates directory not found")
    print(f"✅ Templates directory exists: {template_path}")

# Check templates loaded
print(f"\nTemplates loaded by detector: {len(detector.winning_templates)}")
if len(detector.winning_templates) == 0:
    print("❌ No templates loaded!")
    template_files = list(template_path.glob("*.png"))
    print(f"   Template files found in directory: {len(template_files)}")
    if template_files:
        print(f"   Examples: {[f.name for f in template_files[:5]]}")
        print("   ⚠️  Templates exist but not loaded - check file naming or format")
    else:
        print("   ⚠️  No template files found in directory")
else:
    template_numbers = sorted([t[0] for t in detector.winning_templates])
    print(f"✅ Templates loaded: {len(detector.winning_templates)}")
    print(f"   Template numbers: {template_numbers}")

# ============================================================================
# STEP 2: CHECK VIDEO AND ROI
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: CHECKING VIDEO AND ROI")
print("=" * 80)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"❌ Cannot open video file")
    raise RuntimeError("Cannot open video file")

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"✅ Video opened successfully")
print(f"   Total frames: {total_frames}")
print(f"   FPS: {fps:.2f}")
print(f"   Resolution: {width}x{height}")
print(f"   Start frame: {start_frame}")

if start_frame >= total_frames:
    print(f"⚠️  Start frame ({start_frame}) >= total frames ({total_frames})")
    start_frame = 0
    print(f"   Using frame 0 instead")

cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
ret, frame = cap.read()
if not ret:
    print(f"❌ Cannot read frame {start_frame}")
    cap.release()
    raise RuntimeError("Cannot read frame from video")

print(f"✅ Frame {start_frame} read successfully: {frame.shape}")

# Check screen region
screen_region = detection_config.get('screen_region', [])
print(f"\nScreen region: {screen_region}")
print(f"   Format: [x, y, width, height]")

if not screen_region or len(screen_region) != 4:
    print(f"❌ Screen region not configured or invalid")
    cap.release()
    raise ValueError("Screen region not configured")

x, y, w, h = screen_region
print(f"   Coordinates: x={x}, y={y}, width={w}, height={h}")

# Check if region is within frame bounds
if x < 0 or y < 0 or x + w > width or y + h > height:
    print(f"⚠️  WARNING: Screen region extends beyond frame bounds!")
    print(f"   Frame bounds: 0-{width} (width), 0-{height} (height)")
    print(f"   Region bounds: {x}-{x+w} (width), {y}-{y+h} (height)")

# Extract ROI
roi = frame[y:y+h, x:x+w]
print(f"✅ ROI extracted: {roi.shape}")

if roi.size == 0:
    print(f"❌ ROI is empty!")
    cap.release()
    raise ValueError("ROI is empty")

# Check ROI quality
roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
variance = np.var(roi_gray)
print(f"   ROI variance: {variance:.1f}")

if variance < 100:
    print(f"⚠️  WARNING: ROI variance is very low - region might be empty/blank")

# Save ROI for inspection
roi_path = 'diagnostic_roi.png'
cv2.imwrite(roi_path, roi)
print(f"✅ ROI saved to: {roi_path}")
print(f"   👀 CHECK THIS IMAGE - Does it show the winning number?")

# Save full frame with ROI marked
frame_marked = frame.copy()
cv2.rectangle(frame_marked, (x, y), (x+w, y+h), (0, 255, 0), 2)
frame_path = 'diagnostic_frame_with_roi.png'
cv2.imwrite(frame_path, frame_marked)
print(f"✅ Full frame with ROI marked saved to: {frame_path}")

cap.release()

# ============================================================================
# STEP 3: TEST TEMPLATE MATCHING
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: TESTING TEMPLATE MATCHING")
print("=" * 80)

if len(detector.winning_templates) == 0:
    print("❌ No templates available for matching")
else:
    print(f"Testing {len(detector.winning_templates)} templates...")
    
    # Preprocess ROI
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    roi_processed = detector._preprocess_badge_image(roi_gray)
    
    # Try matching all templates
    all_scores = {}
    best_match = None
    best_score = -1.0
    
    for number, template in detector.winning_templates:
        h_t, w_t = template.shape
        roi_resized = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
        
        try:
            result = cv2.matchTemplate(roi_resized, template, cv2.TM_CCOEFF_NORMED)
            score = float(result[0][0])
            all_scores[number] = score
            
            if score > best_score:
                best_score = score
                best_match = number
        except Exception as e:
            print(f"   ⚠️  Error matching template {number}: {e}")
            all_scores[number] = -1.0
    
    # Show results
    print(f"\nTemplate Matching Results:")
    print(f"   Best match: {best_match} (score: {best_score:.3f})")
    print(f"   Threshold: {threshold}")
    
    if best_match is not None:
        if best_score >= threshold:
            print(f"   ✅ Match above threshold!")
        else:
            print(f"   ❌ Match below threshold!")
            print(f"   💡 Try lowering threshold to {best_score:.2f}")
        
        # Show top 5 matches
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        print(f"\n   Top 5 matches:")
        for i, (num, score) in enumerate(sorted_scores[:5], 1):
            marker = "✅" if score >= threshold else "  "
            print(f"   {marker} {i}. Number {num}: {score:.3f}")

# ============================================================================
# STEP 4: TEST OCR
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: TESTING OCR FALLBACK")
print("=" * 80)

if not detector.enable_ocr_fallback:
    print("⚠️  OCR fallback is DISABLED")
else:
    print(f"OCR fallback: ENABLED")
    print(f"OCR confidence threshold: {detector.ocr_confidence_threshold}")
    
    # Try OCR
    number = detector.detect_number_ocr(roi)
    
    if number is not None:
        print(f"✅ OCR detected number: {number}")
    else:
        print(f"❌ OCR did not detect a number")
        print(f"   This could mean:")
        print(f"   - ROI is empty/blank")
        print(f"   - OCR cannot read the number")
        print(f"   - Confidence below threshold ({detector.ocr_confidence_threshold})")

# ============================================================================
# STEP 5: TEST MULTIPLE FRAMES
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: TESTING MULTIPLE FRAMES")
print("=" * 80)

frame_detector = FrameDetector(config, video_path)
frame_detector.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

detections = []
frame_numbers = []
num_frames = 20

print(f"Testing {num_frames} frames starting from frame {start_frame}...")

for i in range(num_frames):
    frame = frame_detector.capture_screen()
    if frame is None:
        break
    
    frame_num = start_frame + i
    detection = detector.detect_result(frame)
    
    if detection and detection.get('number') is not None:
        detections.append(detection)
        frame_numbers.append(frame_num)
        print(f"   Frame {frame_num}: ✅ Detected {detection.get('number')} "
              f"(method: {detection.get('method')}, confidence: {detection.get('confidence', 0):.2f})")
    else:
        if i < 5:  # Show first 5 failures
            print(f"   Frame {frame_num}: ❌ No detection")

frame_detector.release()

success_rate = len(detections) / num_frames * 100 if num_frames > 0 else 0
print(f"\nDetection Results:")
print(f"   Successful: {len(detections)}/{num_frames}")
print(f"   Success rate: {success_rate:.1f}%")

if detections:
    methods = {}
    for d in detections:
        method = d.get('method', 'unknown')
        methods[method] = methods.get(method, 0) + 1
    print(f"   Methods used: {methods}")

# ============================================================================
# SUMMARY AND RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

print(f"\n✅ Templates: {'OK' if len(detector.winning_templates) > 0 else 'ISSUES FOUND'}")
print(f"✅ Video/ROI: OK")
print(f"✅ Template Matching: {'OK' if best_match is not None and best_score >= threshold else 'BELOW THRESHOLD'}")
if best_match is not None:
    print(f"   Best match: {best_match} (score: {best_score:.3f}, threshold: {threshold})")
print(f"✅ OCR: {'OK' if number is not None else 'FAILED'}")
if number is not None:
    print(f"   Detected: {number}")
print(f"✅ Multiple Frames Test: {success_rate:.1f}% success rate")
print(f"   Successful: {len(detections)}/{num_frames}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

recommendations = []

if len(detector.winning_templates) == 0:
    recommendations.append("1. Fix template loading - check directory path and file names")

if variance < 100:
    recommendations.append("2. Check screen_region - ROI appears empty/blank")

if best_match is not None and best_score < threshold:
    recommendations.append(f"3. Lower winning_template_threshold from {threshold} to {best_score:.2f}")

if number is None and detector.enable_ocr_fallback:
    recommendations.append("4. OCR is failing - check if ROI shows readable number")
    recommendations.append("5. Try lowering ocr_confidence_threshold or improving ROI quality")

if success_rate < 10:
    recommendations.append("6. Very low detection rate - try different start_frame")
    recommendations.append("7. Verify video contains roulette game at specified frame")

if not recommendations:
    recommendations.append("✅ All checks passed! If detection still fails, try:")
    recommendations.append("   - Different start_frame values")
    recommendations.append("   - Lowering thresholds")
    recommendations.append("   - Recreating templates from this video")

for rec in recommendations:
    print(f"   {rec}")

print("\n" + "=" * 80)
print("Check the saved images:")
print(f"   - {roi_path} (ROI extracted)")
print(f"   - {frame_path} (Full frame with ROI marked)")
print("=" * 80)
print("\n✅ Diagnostic complete!")
```

---

## 📊 What This Diagnostic Does

1. **Checks Templates**
   - Verifies templates directory exists
   - Checks if templates are loading
   - Shows which templates are available

2. **Checks Video and ROI**
   - Verifies video can be opened
   - Checks frame dimensions
   - Validates screen_region coordinates
   - Extracts and saves ROI for inspection
   - Checks ROI quality (variance)

3. **Tests Template Matching**
   - Tries all templates on the ROI
   - Shows best match and score
   - Compares against threshold
   - Shows top 5 matches

4. **Tests OCR Fallback**
   - Checks if OCR is enabled
   - Tests OCR on ROI
   - Shows OCR results

5. **Tests Multiple Frames**
   - Tests detection on 20 frames
   - Shows success rate
   - Identifies which methods work

6. **Provides Recommendations**
   - Specific fixes based on findings
   - Actionable steps to resolve issues

---

## 🔧 Common Issues and Fixes

### Issue: Templates Not Loading
**Fix:** Check that:
- Templates directory path is correct
- Template files are named correctly (e.g., `winning-number_2.png`)
- Files are valid PNG images

### Issue: ROI is Empty/Blank
**Fix:** 
- Check `screen_region` coordinates in config
- Verify coordinates match your video resolution
- Use the saved `diagnostic_frame_with_roi.png` to see if region is correct

### Issue: Template Match Below Threshold
**Fix:**
- Lower `winning_template_threshold` in config
- Use the suggested threshold from diagnostic output
- Recreate templates from your video if they don't match

### Issue: OCR Failing
**Fix:**
- Lower `ocr_confidence_threshold` in config
- Check if ROI shows a readable number
- Verify ROI has enough contrast

### Issue: Low Detection Rate
**Fix:**
- Try different `start_frame` values
- Verify video contains roulette game
- Check if game UI changed

---

## 📸 Saved Images

The diagnostic saves two images:

1. **`diagnostic_roi.png`** - The extracted ROI
   - Check if this shows the winning number
   - If blank/empty, screen_region is wrong

2. **`diagnostic_frame_with_roi.png`** - Full frame with ROI marked
   - Green rectangle shows the detection region
   - Verify it's over the winning number area

---

## ✅ Next Steps

After running the diagnostic:

1. **Check the saved images** - Do they show the winning number?
2. **Follow the recommendations** - Apply the suggested fixes
3. **Re-run the test** - Use `test_bot_comprehensive.py` after fixing issues
4. **Adjust config** - Update thresholds or coordinates as needed

This diagnostic will identify exactly what's wrong with detection! 🔍

