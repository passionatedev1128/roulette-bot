# Deep Detection Analysis for Colab

## 🔍 Comprehensive Deep Analysis

This script analyzes EVERY aspect of the detection pipeline to find the root cause.

---

## 🚀 Run Deep Analysis

```python
import sys
import os
import cv2
import numpy as np
from pathlib import Path

# Mock pyautogui
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

if not screen_region or len(screen_region) != 4:
    print("❌ Screen region not configured")
else:
    x, y, w, h = screen_region
    
    # Initialize detector
    detector = ScreenDetector(config)
    
    if len(detector.winning_templates) == 0:
        print("❌ No templates loaded")
    else:
        print("=" * 80)
        print("DEEP DETECTION ANALYSIS")
        print("=" * 80)
        print(f"Loaded {len(detector.winning_templates)} templates")
        template_numbers = [t[0] for t in detector.winning_templates]
        print(f"Template numbers: {template_numbers}")
        
        # Get a frame
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            ret, frame = cap.read()
            
            if ret:
                # Extract ROI
                roi = frame[y:y+h, x:x+w]
                
                if roi.size > 0:
                    print(f"\n✅ Extracted ROI: {roi.shape}")
                    
                    # Get first template
                    first_template_num, first_template = detector.winning_templates[0]
                    print(f"\nUsing template number {first_template_num} for analysis")
                    
                    # ========================================================================
                    # ANALYZE PREPROCESSING
                    # ========================================================================
                    print("\n" + "=" * 80)
                    print("ANALYZING PREPROCESSING PIPELINE")
                    print("=" * 80)
                    
                    # Original ROI
                    print(f"\n1. Original ROI:")
                    print(f"   Shape: {roi.shape}")
                    if len(roi.shape) == 3:
                        print(f"   Channels: {roi.shape[2]} (BGR)")
                    else:
                        print(f"   Grayscale")
                    
                    # Convert to grayscale
                    if len(roi.shape) == 3:
                        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    else:
                        roi_gray = roi.copy()
                    
                    print(f"\n2. After BGR to Grayscale:")
                    print(f"   Shape: {roi_gray.shape}")
                    print(f"   Mean: {roi_gray.mean():.1f}, Std: {roi_gray.std():.1f}")
                    
                    # Apply preprocessing
                    roi_processed = detector._preprocess_badge_image(roi_gray)
                    print(f"\n3. After preprocessing (equalizeHist + GaussianBlur):")
                    print(f"   Shape: {roi_processed.shape}")
                    print(f"   Mean: {roi_processed.mean():.1f}, Std: {roi_processed.std():.1f}")
                    
                    # Template info
                    print(f"\n4. Template:")
                    print(f"   Shape: {first_template.shape}")
                    print(f"   Mean: {first_template.mean():.1f}, Std: {first_template.std():.1f}")
                    
                    # Size analysis
                    h_roi, w_roi = roi_processed.shape
                    h_t, w_t = first_template.shape
                    
                    print(f"\n5. Size Analysis:")
                    print(f"   ROI size: {w_roi}x{h_roi}")
                    print(f"   Template size: {w_t}x{h_t}")
                    
                    if w_roi == w_t and h_roi == h_t:
                        print(f"   ✅ Same size - no resize needed")
                        needs_resize = False
                    else:
                        print(f"   ⚠️  Different sizes - resize needed")
                        print(f"   Aspect ratio ROI: {w_roi/h_roi:.2f}")
                        print(f"   Aspect ratio Template: {w_t/h_t:.2f}")
                        if abs((w_roi/h_roi) - (w_t/h_t)) > 0.1:
                            print(f"   ⚠️  WARNING: Aspect ratios differ significantly!")
                            print(f"      Resize will distort the image!")
                        needs_resize = True
                    
                    # Save images
                    cv2.imwrite('deep_analysis_roi_original.png', roi)
                    cv2.imwrite('deep_analysis_roi_gray.png', roi_gray)
                    cv2.imwrite('deep_analysis_roi_processed.png', roi_processed)
                    cv2.imwrite('deep_analysis_template.png', first_template)
                    
                    if needs_resize:
                        roi_resized = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
                        cv2.imwrite('deep_analysis_roi_resized.png', roi_resized)
                        comparison = np.hstack([roi_processed, cv2.resize(roi_processed, (w_t, h_t)), first_template])
                        cv2.imwrite('deep_analysis_comparison.png', comparison)
                        print(f"\n✅ Saved comparison: deep_analysis_comparison.png")
                        print(f"   Left: ROI processed, Middle: ROI resized, Right: Template")
                    
                    # ========================================================================
                    # TEST TEMPLATE MATCHING VARIATIONS
                    # ========================================================================
                    print("\n" + "=" * 80)
                    print("TESTING TEMPLATE MATCHING VARIATIONS")
                    print("=" * 80)
                    
                    # Standard approach
                    roi_resized_std = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
                    result_std = cv2.matchTemplate(roi_resized_std, first_template, cv2.TM_CCOEFF_NORMED)
                    score_std = float(result_std[0][0])
                    print(f"\n1. Standard approach (current):")
                    marker = "✅" if score_std > 0.3 else "⚠️" if score_std > 0 else "❌"
                    print(f"   {marker} Score: {score_std:.3f}")
                    
                    # Test different resize methods
                    print(f"\n2. Different resize interpolation methods:")
                    resize_scores = {}
                    for name, method in [('INTER_AREA', cv2.INTER_AREA), 
                                        ('INTER_LINEAR', cv2.INTER_LINEAR),
                                        ('INTER_CUBIC', cv2.INTER_CUBIC),
                                        ('INTER_NEAREST', cv2.INTER_NEAREST)]:
                        roi_resized_var = cv2.resize(roi_processed, (w_t, h_t), interpolation=method)
                        result = cv2.matchTemplate(roi_resized_var, first_template, cv2.TM_CCOEFF_NORMED)
                        score = float(result[0][0])
                        resize_scores[name] = score
                        marker = "✅" if score > 0.3 else "⚠️" if score > 0 else "❌"
                        print(f"   {marker} {name}: {score:.3f}")
                    
                    # Test without preprocessing
                    print(f"\n3. Testing without preprocessing:")
                    roi_no_preprocess = cv2.resize(roi_gray, (w_t, h_t), interpolation=cv2.INTER_AREA)
                    result = cv2.matchTemplate(roi_no_preprocess, first_template, cv2.TM_CCOEFF_NORMED)
                    score_no_preprocess = float(result[0][0])
                    marker = "✅" if score_no_preprocess > 0.3 else "⚠️" if score_no_preprocess > 0 else "❌"
                    print(f"   {marker} Without preprocessing: {score_no_preprocess:.3f}")
                    
                    # Test without equalization
                    roi_no_eq = cv2.GaussianBlur(roi_gray, (3, 3), 0)
                    roi_no_eq_resized = cv2.resize(roi_no_eq, (w_t, h_t), interpolation=cv2.INTER_AREA)
                    result = cv2.matchTemplate(roi_no_eq_resized, first_template, cv2.TM_CCOEFF_NORMED)
                    score_no_eq = float(result[0][0])
                    marker = "✅" if score_no_eq > 0.3 else "⚠️" if score_no_eq > 0 else "❌"
                    print(f"   {marker} Without equalizeHist: {score_no_eq:.3f}")
                    
                    # Test without blur
                    roi_no_blur = cv2.equalizeHist(roi_gray)
                    roi_no_blur_resized = cv2.resize(roi_no_blur, (w_t, h_t), interpolation=cv2.INTER_AREA)
                    result = cv2.matchTemplate(roi_no_blur_resized, first_template, cv2.TM_CCOEFF_NORMED)
                    score_no_blur = float(result[0][0])
                    marker = "✅" if score_no_blur > 0.3 else "⚠️" if score_no_blur > 0 else "❌"
                    print(f"   {marker} Without GaussianBlur: {score_no_blur:.3f}")
                    
                    # Test raw (no preprocessing)
                    roi_raw_resized = cv2.resize(roi_gray, (w_t, h_t), interpolation=cv2.INTER_AREA)
                    result = cv2.matchTemplate(roi_raw_resized, first_template, cv2.TM_CCOEFF_NORMED)
                    score_raw = float(result[0][0])
                    marker = "✅" if score_raw > 0.3 else "⚠️" if score_raw > 0 else "❌"
                    print(f"   {marker} Raw (no preprocessing): {score_raw:.3f}")
                    
                    # Test all templates
                    print(f"\n4. Testing all templates:")
                    all_template_scores = {}
                    for num, template in detector.winning_templates:
                        roi_resized = cv2.resize(roi_processed, (template.shape[1], template.shape[0]), interpolation=cv2.INTER_AREA)
                        result = cv2.matchTemplate(roi_resized, template, cv2.TM_CCOEFF_NORMED)
                        score = float(result[0][0])
                        all_template_scores[num] = score
                    
                    sorted_scores = sorted(all_template_scores.items(), key=lambda x: x[1], reverse=True)
                    print(f"   Top 3 matches:")
                    for i, (num, score) in enumerate(sorted_scores[:3], 1):
                        marker = "✅" if score > 0.3 else "⚠️" if score > 0 else "❌"
                        print(f"   {marker} {i}. Number {num}: {score:.3f}")
                    
                    # ========================================================================
                    # SUMMARY
                    # ========================================================================
                    print("\n" + "=" * 80)
                    print("DEEP ANALYSIS SUMMARY")
                    print("=" * 80)
                    
                    best_score = max([
                        score_std,
                        max(resize_scores.values()),
                        score_no_preprocess,
                        score_no_eq,
                        score_no_blur,
                        score_raw,
                        max(all_template_scores.values())
                    ])
                    
                    print(f"\nBest score achieved: {best_score:.3f}")
                    
                    if best_score > 0.5:
                        print(f"✅ Found good match!")
                        print(f"   Detection should work with proper configuration")
                    elif best_score > 0.3:
                        print(f"⚠️  Moderate match")
                        print(f"   Consider lowering threshold or using best method")
                    elif best_score > 0:
                        print(f"⚠️  Weak match")
                        print(f"   Templates might not match video style perfectly")
                    else:
                        print(f"❌ All scores negative or very low")
                        print(f"   Critical issue - check ROI image")
                        print(f"   ROI might not contain winning number")
                    
                    print("\n" + "=" * 80)
                    print("Check saved images:")
                    print("  - deep_analysis_comparison.png (ROI vs Template)")
                    print("  - deep_analysis_roi_processed.png (Processed ROI)")
                    print("  - deep_analysis_template.png (Template)")
                    print("=" * 80)
                    
                else:
                    print("❌ ROI is empty")
            else:
                print("❌ Cannot read frame")
            cap.release()
        else:
            print("❌ Cannot open video")
```

---

## What This Analysis Does

1. **Preprocessing Analysis**
   - Shows each step of preprocessing
   - Compares ROI and template sizes
   - Checks for aspect ratio mismatches
   - Saves intermediate images

2. **Template Matching Variations**
   - Tests different resize methods
   - Tests with/without preprocessing steps
   - Tests all templates
   - Finds the best matching approach

3. **Visual Comparison**
   - Saves side-by-side comparison images
   - Shows ROI vs Template visually

4. **Root Cause Identification**
   - Identifies if preprocessing is the issue
   - Identifies if resize is the issue
   - Identifies if templates don't match

---

## What to Look For

### Good Results:
- Best score > 0.5 → Detection should work
- Comparison image shows similar patterns

### Issues Found:
- Best score < 0 → ROI doesn't contain number
- Aspect ratio mismatch → Resize distorts image
- Preprocessing lowers score → Preprocessing is incompatible

Run this and share the results!

