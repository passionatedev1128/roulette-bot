# 🔴 CRITICAL: Negative Template Scores Detected

## Problem Identified

Your diagnostic shows:
- **Template scores are NEGATIVE** (-0.128 best match)
- **Threshold is 0.65** (positive)
- **0% detection rate**

**This means templates don't match your video at all!**

---

## Why Negative Scores Are Bad

In OpenCV template matching (TM_CCOEFF_NORMED):
- **1.0** = Perfect match
- **0.0** = No correlation  
- **-1.0** = Inverse match (completely different)

**Negative scores mean the templates are incompatible with your video.**

---

## Root Causes

### 1. ROI Doesn't Contain Winning Number ⚠️
**Most likely issue!** The `screen_region` coordinates might be wrong.

**Check:** Look at `diagnostic_roi.png` - does it show a number?

**If ROI is blank/wrong:**
- Screen region coordinates are incorrect
- Need to find correct coordinates

### 2. Templates From Different Video ⚠️
Templates were created from a different video/game.

**Solution:** Recreate templates from THIS video

### 3. Video Resolution/Format Changed ⚠️
Video resolution or game UI changed since templates were created.

**Solution:** Recreate templates

---

## Immediate Action Plan

### Step 1: Check the ROI Image ✅

**Look at `diagnostic_roi.png`:**

1. **Does it show a number?**
   - ✅ YES → Templates are wrong, recreate them
   - ❌ NO → Screen region is wrong, find correct coordinates

2. **Is it blank/empty?**
   - ✅ YES → Screen region is definitely wrong
   - ❌ NO → Check if it shows something else (not a number)

### Step 2A: If ROI is Wrong (No Number Visible)

**You need to find the correct screen region coordinates.**

#### Option 1: Use Coordinate Capture Tool
```python
# Run this to capture coordinates interactively
python coordinate_capture_tool.py
```

#### Option 2: Manual Analysis
1. Open `diagnostic_frame_with_roi.png`
2. Find where the winning number appears
3. Note the coordinates
4. Update config with new coordinates

#### Option 3: Try Different Regions
```python
# Run the fix script to try different regions
python fix_detection_issue.py
```

### Step 2B: If ROI is Correct (Shows Number)

**Templates don't match - recreate them from this video.**

#### Create Templates from Video
```python
# Run template creation from video
python create_templates_from_video.py roleta_brazileria.mp4
```

Or use the Colab template creation script.

---

## Quick Fixes to Try

### Fix 1: Try Different Start Frame

The game might start at a different frame:

```python
# In your test script, try different start frames:
start_frames = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900]

for start_frame in start_frames:
    # Run diagnostic with this start_frame
    # Check if ROI shows number at this frame
```

### Fix 2: Adjust Screen Region

If ROI is close but not exact, try adjusting:

```python
# Current: [953, 511, 57, 55]
# Try variations:
test_regions = [
    [953, 511, 57, 55],    # Original
    [950, 510, 60, 60],    # Slightly larger, shifted
    [955, 515, 50, 50],    # Smaller
    [948, 508, 65, 65],    # Larger
    [960, 520, 55, 55],    # Shifted right/down
]
```

### Fix 3: Lower Threshold (Won't Help if Negative!)

**⚠️ WARNING:** Lowering threshold won't help if scores are negative!

If best score is -0.128 and threshold is 0.65:
- Even if you set threshold to -1.0, it will match incorrectly
- You'll get false positives

**Only lower threshold if scores are positive but below threshold!**

---

## Step-by-Step Fix Process

### Scenario A: ROI Shows Wrong Area

1. **Find correct coordinates:**
   ```python
   # Use coordinate capture or manual inspection
   ```

2. **Update config:**
   ```json
   {
     "detection": {
       "screen_region": [NEW_X, NEW_Y, NEW_WIDTH, NEW_HEIGHT]
     }
   }
   ```

3. **Re-run diagnostic:**
   ```python
   python diagnose_detection_issue.py
   ```

4. **Check if scores are now positive**

### Scenario B: ROI Shows Number But Templates Don't Match

1. **Recreate templates from video:**
   ```python
   python create_templates_from_video.py roleta_brazileria.mp4
   ```

2. **Or manually create from ROI:**
   - Extract ROI when number is visible
   - Save as template
   - Name correctly (e.g., `winning-number_8.png`)

3. **Re-run diagnostic**

### Scenario C: Can't Find Correct Region

1. **Try different start frames:**
   - Game might start later
   - UI might appear at different time

2. **Check video resolution:**
   - Templates might be for different resolution
   - Video might be scaled

3. **Verify video contains roulette game:**
   - Check if game is actually in video
   - Check if it's the right game

---

## Verification Checklist

After applying fixes, verify:

- [ ] ROI shows the winning number clearly
- [ ] Template scores are POSITIVE (not negative)
- [ ] Best template score is above 0.3 (ideally above 0.5)
- [ ] Detection works on multiple frames
- [ ] Success rate is above 50%

---

## Expected Results After Fix

### Good Results:
```
Template Matching Results:
   Best match: 8 (score: 0.72)  ← POSITIVE and above threshold
   Threshold: 0.65
   ✅ Match above threshold!
```

### Still Bad (Need More Fixes):
```
Template Matching Results:
   Best match: 8 (score: 0.45)  ← Positive but below threshold
   Threshold: 0.65
   ❌ Match below threshold!
   💡 Lower threshold to 0.45
```

### Critical (Still Broken):
```
Template Matching Results:
   Best match: 8 (score: -0.128)  ← Still negative!
   Threshold: 0.65
   ❌ Match below threshold!
   → ROI or templates still wrong
```

---

## Quick Test Script

Run this to quickly test if ROI is correct:

```python
import cv2
from pathlib import Path

# Load the saved ROI
roi = cv2.imread('diagnostic_roi.png')

if roi is None:
    print("❌ Cannot load ROI image")
else:
    print("✅ ROI loaded")
    print(f"   Size: {roi.shape}")
    
    # Check if it looks like it has content
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    variance = gray.var()
    print(f"   Variance: {variance:.1f}")
    
    if variance < 100:
        print("   ⚠️  Very low variance - likely empty/blank")
    else:
        print("   ✅ Has content - check if it shows a number")
    
    # Display (in Colab, use cv2_imshow)
    # cv2.imshow('ROI', roi)
    # cv2.waitKey(0)
```

---

## Summary

**Your Issue:** Negative template scores = Templates don't match video

**Most Likely Cause:** 
1. Screen region wrong (ROI doesn't show number) - **70% chance**
2. Templates from different video - **25% chance**  
3. Other issues - **5% chance**

**Next Steps:**
1. ✅ Check `diagnostic_roi.png` - does it show a number?
2. ✅ If NO → Fix screen_region coordinates
3. ✅ If YES → Recreate templates from this video
4. ✅ Re-run diagnostic to verify fix

**Don't lower threshold if scores are negative - fix the root cause!**

