# Video Testing Guide

## Overview

This guide explains how to test the roulette bot's detection capabilities using a video file. This is useful for:
- Testing detection accuracy before running live
- Calibrating detection settings
- Debugging detection issues
- Validating configuration

---

## Quick Start

### Basic Test

```bash
python test_video.py your_video.mp4
```

This will:
- Process every frame of the video
- Display detection results in real-time
- Save results to `test_results/` directory
- Show detection statistics

### Advanced Options

```bash
# Use custom config file
python test_video.py video.mp4 --config config/my_config.json

# Process every 5th frame (faster processing)
python test_video.py video.mp4 --skip 5

# Save results to custom directory
python test_video.py video.mp4 --output my_test_results
```

---

## Video Requirements

### Supported Formats
- MP4, AVI, MOV, MKV, and other formats supported by OpenCV
- Any resolution (will work with your screen detection settings)

### Recommended Video
- Clear view of roulette table
- Good lighting
- Numbers and colors clearly visible
- Stable video (not too shaky)

---

## Step-by-Step Testing

### Step 1: Prepare Your Video

1. Record or obtain a video of the roulette game
2. Ensure the video shows:
   - Roulette table clearly
   - Winning numbers displayed
   - Colors visible (red/black/green)
3. Save in a supported format (MP4 recommended)

### Step 2: Configure Detection Settings

Edit `config/default_config.json`:

```json
{
  "detection": {
    "screen_region": null,  // null = full frame, or [x, y, width, height]
    "color_ranges": {
      // Adjust if colors not detected correctly
    },
    "templates_dir": "templates"
  }
}
```

**Tip**: If video is cropped, you can set `screen_region` to focus on the table area.

### Step 3: Run the Test

```bash
python test_video.py your_video.mp4
```

### Step 4: Monitor Results

While testing, you'll see:
- Frame-by-frame detection results
- Success/failure indicators (/)
- Detected numbers and colors
- Confidence scores
- Detection method used

**Interactive Controls:**
- `q` - Quit and save results
- `s` - Save current frame as image
- `p` - Pause/resume processing

### Step 5: Analyze Results

After testing, check:
1. **Detection Rate**: Should be >90% for good results
2. **Confidence Scores**: Higher is better (>0.7 is good)
3. **Method Used**: Template matching is most reliable
4. **Saved Results**: JSON file with all detections

---

## Understanding Results

### Detection Rate

```
Detection rate: 85.5%
```

- **>90%**: Excellent - Ready for live use
- **70-90%**: Good - May need minor calibration
- **<70%**: Needs improvement - Check configuration

### Confidence Scores

```
Confidence: 0.95
```

- **0.9-1.0**: Excellent - Very confident detection
- **0.7-0.9**: Good - Reliable detection
- **0.5-0.7**: Fair - May have errors
- **<0.5**: Poor - Likely incorrect

### Detection Methods

- **template**: Best method - uses number templates
- **ocr**: Fallback - uses OCR (less reliable)
- **color_fallback**: Last resort - only color detected

**Goal**: Most detections should use "template" method.

---

## Troubleshooting

### Low Detection Rate

**Problem**: Detection rate <70%

**Solutions**:
1. **Create Number Templates**
   - Capture screenshots of numbers 0-36 from video
   - Save as `templates/number_0.png`, `number_1.png`, etc.
   - Template matching is much more accurate than OCR

2. **Adjust Color Ranges**
   - If colors not detected, adjust HSV ranges in config
   - Use HSV color picker tool to find correct ranges

3. **Set Screen Region**
   - If video has other content, set `screen_region` to focus on table
   - Example: `[100, 200, 800, 600]` = x, y, width, height

4. **Check Video Quality**
   - Ensure video is clear and not blurry
   - Good lighting helps detection

### Wrong Numbers Detected

**Problem**: Numbers detected but incorrect

**Solutions**:
1. **Improve Templates**
   - Use exact font/style from your roulette table
   - Ensure templates match video resolution

2. **Adjust OCR Settings**
   - May need to preprocess frames
   - Try different thresholding methods

3. **Verify Color Mapping**
   - Check if numbers match colors correctly
   - Red: 1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
   - Black: 2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35
   - Green: 0

### Colors Not Detected

**Problem**: Colors detected as "None" or incorrect

**Solutions**:
1. **Calibrate Color Ranges**
   - Use HSV color picker on video frames
   - Adjust ranges in config

2. **Use Number-Based Color**
   - If number detected, color is determined from number
   - This is more reliable than color detection

3. **Check Lighting**
   - Different lighting affects color detection
   - May need different ranges for different conditions

---

## Creating Number Templates

### Method 1: From Video

1. Run video test and pause on frames with numbers
2. Press `s` to save frame
3. Open frame in image editor
4. Crop individual numbers (0-36)
5. Save as `templates/number_X.png` (X = 0-36)

### Method 2: From Screenshots

1. Take screenshots of roulette table
2. Extract numbers from screenshots
3. Save to templates directory

### Template Requirements

- **Size**: 20-50 pixels height (recommended)
- **Format**: PNG (transparent background preferred)
- **Naming**: `number_0.png`, `number_1.png`, ..., `number_36.png`
- **Quality**: Clear, not blurry, matches game font

---

## Example Output

```
Loading configuration from config/default_config.json...
Initializing screen detector...
Opening video: test_video.mp4
Video info: 1200 frames, 30.00 FPS, 40.00 seconds
Processing every 1 frame(s)...
------------------------------------------------------------

Processing frames...
Press 'q' to quit, 's' to save current frame, 'p' to pause/resume

Frame 1/1200 (1 processed) 
  Number: 17
  Color: black
  Zero: False
  Confidence: 0.95
  Method: template

Frame 2/1200 (2 processed) 
  Number: 3
  Color: red
  Zero: False
  Confidence: 0.92
  Method: template

...

------------------------------------------------------------
Saving results...
Results saved to: test_results/test_results_20231103_143022.json

============================================================
TEST SUMMARY
============================================================
Total frames in video: 1200
Frames processed: 1200
Successful detections: 1080
Detection rate: 90.00%
Results saved to: test_results/test_results_20231103_143022.json
============================================================

Detection Analysis:

Detection Methods:
  template: 1080
  ocr: 120

Colors Detected:
  red: 540
  black: 540

Numbers Detected: 1080
  Range: 0 - 36
  Unique numbers: 37

Confidence Statistics:
  Average: 0.89
  Min: 0.65
  Max: 0.98
```

---

## Next Steps After Testing

### If Detection Rate >90%

1.  Ready for live testing
2. Configure betting areas
3. Test with small bets
4. Monitor closely

### If Detection Rate 70-90%

1. Create number templates
2. Fine-tune color ranges
3. Adjust screen region
4. Re-test

### If Detection Rate <70%

1. Check video quality
2. Verify configuration
3. Create templates
4. Consider manual calibration

---

## Tips for Best Results

1. **Use Templates**: Most reliable detection method
2. **Good Video Quality**: Clear, well-lit videos work best
3. **Consistent Settings**: Use same config for video and live
4. **Test Multiple Videos**: Test with different conditions
5. **Save Frames**: Save problematic frames for analysis
6. **Monitor Confidence**: Low confidence = potential issues

---

## Files Generated

After testing, you'll find:

- `test_results/test_results_TIMESTAMP.json` - Complete test results
- `test_results/frame_X.png` - Saved frames (if you pressed 's')

Open the JSON file to see detailed results for each frame.

---

## Command Reference

```bash
# Basic test
python test_video.py video.mp4

# Custom config
python test_video.py video.mp4 --config my_config.json

# Process every 10th frame (faster)
python test_video.py video.mp4 --skip 10

# Custom output directory
python test_video.py video.mp4 --output my_results
```

---

## Questions?

If you encounter issues:
1. Check detection rate - should be >70%
2. Review confidence scores - should be >0.7
3. Check saved frames for visual inspection
4. Adjust configuration as needed
5. Create number templates for better accuracy

