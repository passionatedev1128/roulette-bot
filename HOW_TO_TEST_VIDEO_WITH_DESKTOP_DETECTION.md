# How to Test Bot Using Video with Desktop Detection

This guide explains how to test your roulette bot by playing a video on your desktop and having the bot detect from the desktop screen (instead of reading the video file directly).

---

## 🎯 Two Testing Methods

### Method 1: Play Video on Desktop + Desktop Detection (Recommended)

This method tests the actual desktop detection that will be used in production.

#### Step 1: Prepare Your Video
1. Have your roulette video file ready (e.g., `roleta_brazileria.mp4`)
2. Make sure the video shows the roulette table clearly

#### Step 2: Configure Screen Region
Edit `config/default_config.json` and set the `screen_region` to match where the video will be displayed:

```json
{
  "detection": {
    "screen_region": [x, y, width, height],
    ...
  }
}
```

**How to find the screen region:**
- Open the video in a video player
- Position it where you want (fullscreen or windowed)
- Use a tool to get the coordinates, or:
  - For fullscreen: set `screen_region` to `null` (detects full screen)
  - For windowed: measure the window position and size

#### Step 3: Play Video and Run Detection
1. **Open your video in a video player** (VLC, Windows Media Player, etc.)
2. **Position the video window** where you want detection to happen
3. **Run the desktop detection test:**

```powershell
# Option A: Use test_video.py with screen mode (reads video info but detects from desktop)
python test_video.py your_video.mp4 --mode screen --config config/default_config.json

# Option B: Use the bot in test mode (detects from desktop continuously)
python backend/app/bot.py --test --config config/default_config.json
```

**Note:** The `--mode screen` option in `test_video.py` will:
- Use `ScreenDetector` (desktop capture)
- Still read video file for frame counting/timing
- Actually detect from your desktop screen

#### Step 4: Monitor Results
- Watch the console for detection results
- Check that numbers are being detected correctly
- Results will be saved to `test_results/` directory

---

### Method 2: Use Video File with Desktop Detection Mode

This uses the video file but tests with desktop detection logic.

```powershell
python test_video.py your_video.mp4 --mode screen --config config/default_config.json --max-frames 100
```

**What this does:**
- Uses `ScreenDetector` (desktop capture method)
- Reads video file for timing/frame info
- Detects from your desktop (make sure video is playing!)

---

## 🔧 Step-by-Step: Full Desktop Detection Test

### Complete Workflow

1. **Prepare Configuration**
   ```powershell
   # Check your config
   type config\default_config.json
   ```
   
   Verify:
   - ✅ `screen_region` is set correctly (or `null` for fullscreen)
   - ✅ `winning_templates_dir` points to your templates
   - ✅ Detection thresholds are appropriate

2. **Start Video Player**
   - Open your video file in a video player
   - Make it fullscreen or position the window
   - **Important:** Keep the video playing and visible

3. **Run Desktop Detection Test**
   ```powershell
   # Quick test (100 frames)
   python test_video.py your_video.mp4 --mode screen --max-frames 100 --display
   
   # Full test with display window
   python test_video.py your_video.mp4 --mode screen --display
   
   # Test specific time range
   python test_video.py your_video.mp4 --mode screen --start 30 --end 60
   ```

4. **Monitor Detection**
   - Console will show detection results in real-time
   - If `--display` is used, you'll see the detection window
   - Press 'q' to quit, 's' to save frame, 'p' to pause

5. **Review Results**
   - Check `test_results/` directory for JSON results
   - Review detection rate (should be > 90%)
   - Verify numbers are detected correctly

---

## 📋 Command Reference

### Basic Commands

```powershell
# Test with desktop detection (screen mode)
python test_video.py video.mp4 --mode screen

# Test with video file reading (frame mode - default)
python test_video.py video.mp4 --mode frame

# Test with display window
python test_video.py video.mp4 --mode screen --display

# Test limited frames
python test_video.py video.mp4 --mode screen --max-frames 50

# Test specific time range
python test_video.py video.mp4 --mode screen --start 0 --end 30

# Test every 5th frame (faster)
python test_video.py video.mp4 --mode screen --skip 5
```

### Advanced Options

```powershell
# Custom config file
python test_video.py video.mp4 --mode screen --config config/my_config.json

# Custom output directory
python test_video.py video.mp4 --mode screen --output my_results

# Full test with all options
python test_video.py video.mp4 --mode screen --config config/default_config.json --output test_results --start 0 --end 60 --max-frames 200 --display
```

---

## 🎬 Alternative: Manual Desktop Testing

If you want to test desktop detection without using `test_video.py`:

### Option 1: Use Bot in Test Mode
```powershell
# Bot will detect from desktop continuously
python backend/app/bot.py --test --config config/default_config.json
```

Then:
1. Play your video on desktop
2. Bot will detect from desktop screen
3. Watch console for detection results

### Option 2: Create Custom Test Script

You can create a simple script that:
1. Captures desktop screen
2. Detects numbers
3. Displays results

---

## ⚙️ Configuration Tips

### Screen Region Setup

**For Fullscreen Video:**
```json
{
  "detection": {
    "screen_region": null  // Detects full screen
  }
}
```

**For Windowed Video:**
```json
{
  "detection": {
    "screen_region": [x, y, width, height]  // Window coordinates
  }
}
```

**To find window coordinates:**
- Use Windows Snipping Tool to see coordinates
- Or use a tool like `pyautogui.position()` to get mouse coordinates
- Or set to `null` and crop in post-processing

### Detection Settings

```json
{
  "detection": {
    "winning_template_threshold": 0.65,  // Lower = more sensitive
    "ocr_confidence_threshold": 0.9,     // Higher = more strict
    "screen_region": [953, 511, 57, 55]  // Your region
  }
}
```

---

## ✅ What to Check

### Good Signs ✅
- Detection rate > 90%
- Numbers detected correctly
- Colors detected correctly
- No major errors in console
- Results saved successfully

### Warning Signs ⚠️
- Detection rate < 80% → Check templates and thresholds
- Wrong numbers detected → Adjust `screen_region` or thresholds
- No detections → Check if video is visible and `screen_region` is correct
- Errors in console → Check configuration and dependencies

---

## 🐛 Troubleshooting

### Problem: No detections

**Solutions:**
1. Check `screen_region` matches video position
2. Verify video is playing and visible
3. Check templates exist in `winning-number_templates/`
4. Lower `winning_template_threshold` (try 0.6)
5. Make sure video shows roulette table clearly

### Problem: Wrong detections

**Solutions:**
1. Adjust `screen_region` to focus on winning number area
2. Increase `winning_template_threshold` (try 0.7-0.8)
3. Check video quality and lighting
4. Verify templates match video style

### Problem: Detection too slow

**Solutions:**
1. Use `--skip` to process every Nth frame
2. Use `--max-frames` to limit test size
3. Reduce video resolution
4. Disable `--display` if not needed

---

## 📊 Understanding Results

After running the test, check `test_results/test_results_*.json`:

```json
{
  "total_frames": 1000,
  "processed_frames": 1000,
  "successful_detections": 950,
  "detection_rate": 95.0,
  "results": [
    {
      "frame_number": 1,
      "timestamp": 0.033,
      "result": {
        "number": 15,
        "color": "black",
        "confidence": 0.85,
        "method": "template_badge"
      }
    }
  ]
}
```

**Key Metrics:**
- `detection_rate`: Should be > 90%
- `successful_detections`: Number of valid detections
- `results`: Array of all detection results

---

## 🚀 Quick Start Example

```powershell
# 1. Make sure video is ready
# 2. Open video in player (fullscreen or windowed)

# 3. Run quick test
python test_video.py roleta_brazileria.mp4 --mode screen --max-frames 50 --display

# 4. Watch console output
# 5. Press 'q' to quit when done
# 6. Check test_results/ for JSON file
```

---

## 📝 Notes

- **Desktop detection** (`--mode screen`) captures from your actual screen
- **Frame detection** (`--mode frame`) reads directly from video file
- For production testing, use `--mode screen` to test real desktop capture
- Make sure video is playing and visible when using `--mode screen`
- Use `--display` to see what the bot is detecting in real-time

---

## 🎯 Recommended Testing Flow

1. **Quick Test** (50 frames)
   ```powershell
   python test_video.py video.mp4 --mode screen --max-frames 50
   ```

2. **If detection rate > 90%**: Proceed to full test
   ```powershell
   python test_video.py video.mp4 --mode screen
   ```

3. **If detection rate < 90%**: Adjust configuration
   - Check `screen_region`
   - Adjust thresholds
   - Verify templates

4. **Full Integration Test**
   ```powershell
   python backend/app/bot.py --test --config config/default_config.json
   ```

---

**Remember:** Desktop detection (`--mode screen`) requires the video to be playing and visible on your screen. The bot will capture from your desktop, not read the video file directly.

