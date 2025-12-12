# How to Check Coordinates - Complete Guide

## Overview

This guide shows you all the ways to check and verify coordinates in your config file, including:
- Screen region (detection region)
- Betting area coordinates
- Chip selection coordinates
- Confirm button coordinates

---

## Method 1: Check All Coordinates at Once (Easiest)

### Quick Check Command

```bash
python scripts/check_all_coordinates.py
```

This will:
- ✅ Check screen region coordinates
- ✅ Check all betting area coordinates
- ✅ Check chip selection coordinates
- ✅ Check confirm button coordinate
- ✅ Validate all coordinates are within screen bounds
- ✅ Save images showing each region/coordinate
- ✅ Generate a summary report

### What You'll See

```
===============================================================================
COORDINATE CHECKER
===============================================================================
Config file: config/default_config.json
Screen size: 1920x1080

================================================================================
1. CHECKING SCREEN REGION (Detection Region)
================================================================================

📊 Screen Region Info:
   Coordinates: x=953, y=511, width=57, height=55
   Screen size: 1920x1080
 ✓ Region is within screen bounds
 📸 Saved exact region to: coordinate_check_output/1_screen_region_exact.png
 📸 Saved full screen with region marked to: coordinate_check_output/2_screen_region_marked.png
   👀 CHECK THIS IMAGE - Does the green rectangle show the winning number area?

 ✓ Screen region is valid!
```

### Output Images

The script saves images to `coordinate_check_output/`:
- `1_screen_region_exact.png` - Exact region captured
- `2_screen_region_marked.png` - Full screen with region marked in green

**Check these images** to visually verify the coordinates are correct!

---

## Method 2: Visualize Screen Region Only

### Show Detection Region

```bash
python scripts/show_detection_region.py
```

This will:
- Display the detection region on your screen
- Save multiple images showing:
  - Close-up of exact region
  - Context view with surrounding area
  - Full screen overlay
- Show coordinates and size

### What It Does

1. Takes a screenshot of the detection region
2. Draws a green rectangle around the region
3. Saves images for inspection
4. Shows coordinates and dimensions

**Output location**: `detection_region_output/`

---

## Method 3: Test Coordinates in Browser

### Interactive Coordinate Testing

```bash
python scripts/test_browser_coordinates.py
```

This will:
- Move mouse to each coordinate
- Ask you to verify if each coordinate is correct
- Test all betting areas, chips, and confirm button
- Save results to `coordinate_test_results.json`

### Steps

1. **Open your browser game** before running
2. **Run the script**
3. **Watch the mouse** move to each coordinate
4. **Answer y/n** when asked if coordinates are correct

### Test with Clicking

```bash
python scripts/test_browser_coordinates.py --click
```

⚠️ **Warning**: This will actually click on coordinates. Use only with a test account!

---

## Method 4: Verify Screen Region from Video

If you have a video file of gameplay:

```bash
python scripts/verify_screen_region.py
```

This will:
- Check if screen region is within video frame bounds
- Test ROI extraction on multiple frames
- Verify region shows winning numbers

---

## Method 5: Manual Visual Inspection

### Step 1: Take a Screenshot

1. Open your roulette game in browser
2. Take a screenshot (Print Screen or Snipping Tool)

### Step 2: Open in Image Editor

1. Open screenshot in Paint, GIMP, or any image editor
2. Note the pixel coordinates shown at bottom/status bar

### Step 3: Check Coordinates

Compare the coordinates in your config with the screenshot:
- Does the region/point match where it should be?
- Are coordinates within screen bounds?

---

## Detailed Checks

### Check Screen Region Specifically

**What to verify:**
- ✅ Region shows the winning number display area
- ✅ Coordinates are within screen bounds
- ✅ Size is appropriate (not too small/large)
- ✅ Region doesn't overlap with other UI elements

**Command:**
```bash
python scripts/check_all_coordinates.py
```

**Visual check:**
```bash
python scripts/show_detection_region.py
```

Open the saved images and verify the green rectangle shows the winning number area.

### Check Betting Area Coordinates

**What to verify:**
- ✅ Coordinates point to center of betting buttons
- ✅ All required areas are configured (red, black, etc.)
- ✅ Coordinates are within screen bounds

**Command:**
```bash
python scripts/test_browser_coordinates.py
```

Move mouse will move to each betting area - verify it's correct.

### Check Chip Selection Coordinates

**What to verify:**
- ✅ All chip values have coordinates (0.5, 1, 2.5, 5, 20, 50)
- ✅ Each coordinate points to the correct chip button
- ✅ Coordinates are within screen bounds

**Command:**
```bash
python scripts/test_browser_coordinates.py
```

The script will test all chip coordinates.

### Check Confirm Button

**What to verify:**
- ✅ Coordinate points to confirm/place bet button
- ✅ Coordinate is within screen bounds

**Command:**
```bash
python scripts/test_browser_coordinates.py
```

---

## Common Issues and Solutions

### Issue: "Region out of bounds"

**Problem**: Coordinates are outside screen size

**Solution:**
1. Check your screen resolution matches when coordinates were captured
2. Re-capture coordinates with current screen resolution
3. Verify coordinates are positive numbers

### Issue: "Region doesn't show winning number"

**Problem**: Screen region coordinates are wrong

**Solution:**
1. Run `python scripts/show_detection_region.py`
2. Check saved images - does green rectangle show winning number?
3. If not, adjust `screen_region` in config
4. Re-capture coordinates

### Issue: "Coordinates seem wrong"

**Problem**: Coordinates point to wrong location

**Solution:**
1. Check browser zoom is 100% (Ctrl+0)
2. Verify browser window position hasn't changed
3. Re-capture coordinates
4. Test with `python scripts/test_browser_coordinates.py`

---

## Quick Reference Commands

| What to Check | Command |
|--------------|---------|
| **All coordinates** | `python scripts/check_all_coordinates.py` |
| **Screen region only** | `python scripts/show_detection_region.py` |
| **Test in browser** | `python scripts/test_browser_coordinates.py` |
| **Test with clicking** | `python scripts/test_browser_coordinates.py --click` |
| **Verify from video** | `python scripts/verify_screen_region.py` |
| **Custom config** | `python scripts/check_all_coordinates.py --config config/my_config.json` |

---

## Step-by-Step Verification Process

### Recommended Workflow

1. **Initial Check**
   ```bash
   python scripts/check_all_coordinates.py
   ```
   - Verify all coordinates are valid
   - Check output images
   - Note any issues

2. **Visual Verification (Screen Region)**
   ```bash
   python scripts/show_detection_region.py
   ```
   - Open saved images
   - Verify green rectangle shows winning number area
   - Adjust if needed

3. **Interactive Testing**
   ```bash
   python scripts/test_browser_coordinates.py
   ```
   - Open browser game
   - Watch mouse move to each coordinate
   - Verify each is correct
   - Fix incorrect coordinates

4. **Final Verification**
   ```bash
   python scripts/check_all_coordinates.py
   ```
   - Run again after fixes
   - Confirm all coordinates are valid

---

## Output Files

### coordinate_check_output/

Contains images from `check_all_coordinates.py`:
- `1_screen_region_exact.png` - Exact detection region
- `2_screen_region_marked.png` - Full screen with region marked

### detection_region_output/

Contains images from `show_detection_region.py`:
- `1_closeup_exact_region.png`
- `2_context_with_surrounding.png`
- `3_fullscreen_overlay.png`
- `4_original_region.png`
- `5_full_screen_with_region.png`

### coordinate_test_results.json

Contains test results from `test_browser_coordinates.py`:
- Which coordinates were tested
- Which are correct/incorrect
- Summary statistics

---

## Tips

1. **Always check images**: The saved images show exactly what the bot sees
2. **Test in browser**: Use the interactive test to verify coordinates work
3. **Check after changes**: Verify coordinates after changing screen resolution or browser position
4. **Keep backups**: Save working coordinate configurations
5. **Start with screen region**: Screen region is most critical - verify it first

---

## Summary

✅ **Best method**: Use `python scripts/check_all_coordinates.py` for comprehensive check

✅ **Visual verification**: Use `python scripts/show_detection_region.py` to see detection region

✅ **Interactive testing**: Use `python scripts/test_browser_coordinates.py` to test in browser

✅ **Always check images**: Saved images show exactly what bot sees

✅ **Fix issues before running bot**: Ensure all coordinates are correct before live use

---

**Need help?** Check the saved images - they show exactly what coordinates point to!

