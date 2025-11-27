# Verifying Browser Detection - Critical Testing Guide

##  Important: Will It Work in Real Life?

**Short Answer:** Yes, BUT it requires careful setup and testing. The bot uses screen capture (`pyautogui.screenshot()`) to detect numbers from your browser, which means:

 **Will Work If:**
- Screen region coordinates are accurate
- Templates match the browser's number display
- Browser window position is stable
- Screen resolution matches calibration

 **Will Fail If:**
- Browser window moves or resizes
- Zoom level changes
- Screen resolution changes
- Templates don't match browser rendering
- Winning number area is covered/obscured

---

## 🔍 How Browser Detection Works

### Current Setup

1. **Screen Capture**: Uses `pyautogui.screenshot(region=[x, y, w, h])` to capture a small region
2. **Current Region**: `[953, 511, 57, 55]` - Only 57x55 pixels!
3. **Detection Methods**:
   - **Primary**: Template matching (compares captured region with saved templates)
   - **Fallback**: OCR (reads numbers using pytesseract/EasyOCR)

### Critical Requirements

```json
{
  "detection": {
    "screen_region": [953, 511, 57, 55],  // MUST be accurate!
    "winning_templates_dir": "winning-number_templates/",  // Templates MUST exist
    "winning_template_threshold": 0.65  // Match confidence threshold
  }
}
```

---

##  Step-by-Step: Verify Browser Detection

### Step 1: Prepare Your Browser Setup

1. **Open the roulette game in your browser**
2. **Position the browser window** where you want it
3. **Set browser zoom to 100%** (Ctrl+0 or Cmd+0)
4. **Make sure the winning number area is visible**
5. **DO NOT move or resize the window** during testing

### Step 2: Find the Correct Screen Region

The `screen_region` must point to where the winning number appears in your browser.

**Option A: Use the Verification Script**

```powershell
# This will help you find the correct region
python verify_screen_region.py
```

**Option B: Manual Method**

1. Take a screenshot of your browser with the game visible
2. Use an image editor to find the exact pixel coordinates of the winning number
3. Update `config/default_config.json`:
   ```json
   {
     "detection": {
       "screen_region": [x, y, width, height]
     }
   }
   ```

### Step 3: Test Detection with Real Browser

Create and run this test script:

```powershell
python test_browser_detection.py
```

This script will:
- Capture from your desktop (where browser is showing)
- Try to detect numbers
- Show you what it's seeing
- Save sample captures for inspection

### Step 4: Verify Templates Match

The templates in `winning-number_templates/` must match what appears in your browser.

**Check if templates exist:**
```powershell
dir winning-number_templates
```

**If templates don't match:**
1. Capture screenshots of each number (0-36) from your browser
2. Save them as `0.png`, `1.png`, `2.png`, etc. in `winning-number_templates/`
3. Make sure they match the exact appearance in your browser

---

## 🧪 Test Script: Verify Browser Detection

I'll create a test script for you to verify browser detection works.

### What the Test Does

1. Captures screen from desktop (where browser is)
2. Extracts the region specified in config
3. Tries to detect numbers
4. Shows you what it sees
5. Saves sample images for inspection

### How to Use

1. **Open your roulette game in browser**
2. **Position it where you want**
3. **Run the test:**
   ```powershell
   python test_browser_detection.py
   ```
4. **Watch the console** - it will show detection attempts
5. **Check saved images** - see what the bot is "seeing"

---

##  Common Issues & Solutions

### Issue 1: No Detections

**Symptoms:**
- Console shows "No detection" repeatedly
- Detection rate is 0%

**Possible Causes:**
1. **Screen region is wrong**
   - Solution: Recalibrate `screen_region` coordinates
   - Use `verify_screen_region.py` to find correct region

2. **Templates don't match**
   - Solution: Recreate templates from your browser
   - Capture screenshots of numbers directly from browser

3. **Browser window moved**
   - Solution: Keep browser window in fixed position
   - Or use fullscreen mode

4. **Zoom level changed**
   - Solution: Set browser zoom to 100% (Ctrl+0)
   - Don't change zoom after calibration

### Issue 2: Wrong Numbers Detected

**Symptoms:**
- Bot detects numbers, but they're wrong
- Detection rate > 0% but accuracy is low

**Possible Causes:**
1. **Template threshold too low**
   - Solution: Increase `winning_template_threshold` to 0.7-0.8
   ```json
   {
     "detection": {
       "winning_template_threshold": 0.75
     }
   }
   ```

2. **Region includes multiple numbers**
   - Solution: Make `screen_region` smaller, focus only on winning number
   - Check saved ROI images to verify

3. **Templates are from different source**
   - Solution: Recreate templates from your actual browser

### Issue 3: Detection Works Sometimes

**Symptoms:**
- Detection works initially, then stops
- Works after restart, then fails

**Possible Causes:**
1. **Browser window moved**
   - Solution: Use fullscreen or lock window position
   - Consider using window management tools

2. **Screen resolution changed**
   - Solution: Keep same resolution
   - Or recalibrate if resolution changes

3. **Game UI changed**
   - Solution: Check if game updated
   - Recalibrate if UI changed

---

##  Best Practices for Reliable Detection

### 1. Use Fullscreen Mode

**Why:** Eliminates window position issues

**How:**
- Press F11 in browser (fullscreen)
- Or maximize browser window
- Set `screen_region` for fullscreen position

### 2. Lock Browser Position

**Why:** Prevents accidental movement

**How:**
- Use window management tools
- Or physically mark screen position
- Or use a second monitor dedicated to the game

### 3. Standardize Setup

**Why:** Consistency improves reliability

**Setup:**
- Same browser (Chrome, Firefox, etc.)
- Same zoom level (100%)
- Same screen resolution
- Same window position

### 4. Create Templates from Your Browser

**Why:** Templates must match your browser's rendering

**How:**
1. Open game in browser
2. Wait for each number (0-36) to appear
3. Capture screenshot of winning number area
4. Crop to just the number
5. Save as `0.png`, `1.png`, etc. in `winning-number_templates/`

### 5. Test Before Going Live

**Why:** Catch issues early

**Test Checklist:**
- [ ] Detection rate > 90%
- [ ] Correct numbers detected
- [ ] Works for 10+ consecutive spins
- [ ] Works after browser restart
- [ ] Works with different numbers (0-36)

---

## 📊 Expected Performance

### Good Performance 
- **Detection Rate**: > 90%
- **Accuracy**: > 95% (correct numbers)
- **Speed**: < 1 second per detection
- **Reliability**: Works consistently

### Poor Performance 
- **Detection Rate**: < 80%
- **Accuracy**: < 90%
- **Speed**: > 2 seconds
- **Reliability**: Fails randomly

### If Performance is Poor

1. **Check screen region** - Use verification script
2. **Check templates** - Verify they match browser
3. **Check threshold** - Adjust `winning_template_threshold`
4. **Check browser setup** - Zoom, position, resolution
5. **Test with video first** - Verify detection logic works

---

## 🔧 Calibration Process

### Step 1: Initial Setup
```powershell
# 1. Open game in browser
# 2. Position window
# 3. Set zoom to 100%
# 4. Note screen resolution
```

### Step 2: Find Region
```powershell
# Run verification script
python verify_screen_region.py

# Or manually:
# - Take screenshot
# - Find winning number coordinates
# - Update config
```

### Step 3: Create Templates
```powershell
# Capture numbers from browser
# Save to winning-number_templates/
# Name: 0.png, 1.png, 2.png, ..., 36.png
```

### Step 4: Test Detection
```powershell
# Test with browser open
python test_browser_detection.py

# Should see:
# - Detection rate > 90%
# - Correct numbers
# - Fast detection (< 1 second)
```

### Step 5: Verify Consistency
```powershell
# Test multiple times
# Test after browser restart
# Test with different numbers
# All should work consistently
```

---

## 🚨 Critical Warnings

###  Window Position
- **If browser window moves, detection will fail**
- Use fullscreen or lock window position
- Test after any window movement

###  Zoom Level
- **If zoom changes, detection will fail**
- Always use 100% zoom
- Recalibrate if zoom changes

###  Screen Resolution
- **If resolution changes, coordinates change**
- Keep same resolution
- Recalibrate if resolution changes

###  Game Updates
- **If game UI changes, detection may fail**
- Check detection after game updates
- Recalibrate if needed

###  Multiple Monitors
- **Coordinates depend on primary monitor**
- Test with your monitor setup
- Recalibrate if monitor setup changes

---

##  Verification Checklist

Before using the bot in production:

- [ ] **Screen region is accurate** - Verified with test script
- [ ] **Templates exist and match** - All 37 numbers (0-36) present
- [ ] **Detection rate > 90%** - Tested with 50+ spins
- [ ] **Accuracy > 95%** - Correct numbers detected
- [ ] **Works consistently** - Tested multiple times
- [ ] **Works after restart** - Tested after browser restart
- [ ] **Fast detection** - < 1 second per detection
- [ ] **Browser setup stable** - Zoom, position, resolution fixed
- [ ] **Tested with different numbers** - Verified 0-36 all work
- [ ] **Backup plan ready** - Know how to recalibrate if needed

---

##  Next Steps

1. **Run verification script** to check current setup
2. **Test with browser** to verify detection works
3. **Fix any issues** found during testing
4. **Re-test** until detection rate > 90%
5. **Then proceed** with strategy testing

**Remember:** Detection must be reliable before strategy matters!

