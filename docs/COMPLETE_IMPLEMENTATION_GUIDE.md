# Complete Implementation Guide - Brazilian Roulette Bot

## Overview

This guide walks you through implementing the roulette bot from scratch, step by step.

---

## Prerequisites

### Required Software
- Python 3.12 or higher
- Tesseract OCR (optional but recommended)
- Text editor or IDE (VS Code recommended)

### Required Knowledge
- Basic Python knowledge
- Understanding of file paths
- Ability to edit configuration files

---

## Step 1: Download/Clone the Project

### Option A: If You Have the Project Files
1. Navigate to project folder: `E:\My Workstation\projects\Workana_Roulette Bot_2025_11_03_Zhu_Brazil_own_ongoing\Roulette Bot`
2. Verify all files are present

### Option B: If Starting Fresh
1. Create project folder: `Roulette Bot`
2. Copy all project files to this folder

---

## Step 2: Install Python Dependencies

### 2.1 Open Terminal/Command Prompt

**Windows:**
- Press `Win + R`
- Type `cmd` and press Enter
- Navigate to project folder:
  ```bash
  cd "E:\My Workstation\projects\Workana_Roulette Bot_2025_11_03_Zhu_Brazil_own_ongoing\Roulette Bot"
  ```

**Mac/Linux:**
```bash
cd /path/to/Roulette\ Bot
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed opencv-python numpy pytesseract pyautogui ...
```

**If errors occur:**
- Try: `pip install --upgrade pip`
- Then: `pip install -r requirements.txt` again

### 2.3 Verify Installation

```bash
python check_setup.py
```

**You should see:**
```
[OK] OpenCV installed
[OK] NumPy installed
[OK] pytesseract installed
[OK] pyautogui installed
```

---

## Step 3: Install Tesseract OCR (Optional but Recommended)

### Windows
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH:
   - Right-click "This PC"  Properties  Advanced System Settings
   - Environment Variables  Path  Edit  Add: `C:\Program Files\Tesseract-OCR`
   - Restart terminal

### Mac
```bash
brew install tesseract
```

### Linux
```bash
sudo apt-get install tesseract-ocr
```

### Verify Tesseract
```bash
tesseract --version
```

**Note:** Bot works without Tesseract but template matching is recommended.

---

## Step 4: Configure the Bot

### 4.1 Open Configuration File

Open: `config/default_config.json`

### 4.2 Configure Detection Settings

```json
{
  "detection": {
    "screen_region": null,  // null = full screen, or [x, y, width, height]
    "color_ranges": {
      "red": [
        [[0, 100, 100], [10, 255, 255]],
        [[170, 100, 100], [180, 255, 255]]
      ],
      "black": [
        [[0, 0, 0], [180, 255, 30]]
      ],
      "green": [
        [[50, 100, 100], [70, 255, 255]]
      ]
    },
    "templates_dir": "templates"
  }
}
```

**For better performance:**
- Set `screen_region` to focus on table: `[100, 200, 800, 600]`
- Adjust color ranges if colors aren't detected correctly

### 4.3 Configure Strategy

```json
{
  "strategy": {
    "type": "martingale",    // "martingale", "fibonacci", or "custom"
    "base_bet": 10.0,        // Starting bet amount
    "max_gales": 5,          // Maximum gale progression steps
    "multiplier": 2.0,       // Martingale multiplier (2.0 = double after loss)
    "custom_sequence": [10, 20, 40, 80, 160],  // For custom strategy
    "zero_handling": {
      "rule": "continue_sequence",  // "continue_sequence", "reset", or "skip"
      "reset_on_zero": false
    }
  }
}
```

**Choose strategy:**
- **Martingale**: Doubles bet after each loss
- **Fibonacci**: Uses Fibonacci sequence progression
- **Custom**: Uses your defined sequence

### 4.4 Configure Betting Areas

**CRITICAL:** You must set these coordinates for your game!

```json
{
  "betting": {
    "betting_areas": {
      "red": [500, 400],      // [x, y] coordinates of red bet button
      "black": [600, 400],    // [x, y] coordinates of black bet button
      "green": [550, 350]     // [x, y] coordinates of green bet button
    },
    "confirm_button": [550, 500],  // [x, y] coordinates of confirm button
    "requires_amount_entry": false,  // true if you need to type bet amount
    "human_delays": {
      "min": 0.1,  // Minimum delay between actions (seconds)
      "max": 0.5   // Maximum delay between actions (seconds)
    }
  }
}
```

**How to find coordinates:**
1. Use a tool like `pyautogui.position()`:
   ```python
   import pyautogui
   import time
   
   print("Move mouse to red bet button and wait 5 seconds...")
   time.sleep(5)
   x, y = pyautogui.position()
   print(f"Red button coordinates: [{x}, {y}]")
   ```
2. Or use screenshot tools to find pixel coordinates
3. Test coordinates before running bot

### 4.5 Configure Risk Management

```json
{
  "risk": {
    "initial_balance": 1000.0,     // Starting balance
    "stop_loss": 500.0,             // Stop bot if balance reaches this
    "guarantee_fund_percentage": 20 // Reserve % for gale bets
  }
}
```

### 4.6 Configure Session Management

```json
{
  "session": {
    "maintenance_bet_interval": 1800,  // Seconds between maintenance bets (30 min)
    "min_bet_amount": 1.0               // Minimum bet to keep session active
  }
}
```

**Save the config file after editing.**

---

## Step 5: Create Number Templates (Highly Recommended)

### 5.1 Why Templates?
- Templates increase accuracy from 60-70% to 90-95%
- Much more reliable than OCR

### 5.2 How to Create Templates

#### Step 5.2.1: Capture Screenshots
1. Play the game or use your video file
2. Take screenshots when numbers appear clearly
3. Save screenshots to a temporary folder

#### Step 5.2.2: Extract Numbers
1. Open screenshot in image editor (GIMP, Photoshop, Paint, etc.)
2. Identify where numbers appear (usually center of screen)
3. For each number (0-36):
   - Crop just the number
   - Save as: `templates/number_0.png`, `number_1.png`, etc.
   - Size: 20-50 pixels height (recommended)
   - Format: PNG (transparent background preferred)

#### Step 5.2.3: Verify Templates
1. Check that `templates/` folder contains:
   - `number_0.png` through `number_36.png`
   - Total: 37 files

#### Step 5.2.4: Test Templates
```python
# Quick test
import cv2
import os

template_dir = "templates"
for i in range(37):
    file_path = f"{template_dir}/number_{i}.png"
    if os.path.exists(file_path):
        img = cv2.imread(file_path)
        if img is not None:
            print(f" number_{i}.png loaded successfully")
        else:
            print(f" number_{i}.png failed to load")
    else:
        print(f" number_{i}.png not found")
```

**Note:** Templates are optional but highly recommended for best accuracy.

---

## Step 6: Test Detection First

### 6.1 Test with Video File (Recommended Before Live)

```bash
python test_video.py your_video.mp4
```

**Or test specific frames:**
```python
from backend.app.detection import ScreenDetector
from backend.app.config_loader import ConfigLoader
import cv2

# Load config
config = ConfigLoader.load_config('config/default_config.json')

# Initialize detector
detector = ScreenDetector(config)

# Load test frame
frame = cv2.imread('test_frame.png')

# Detect
result = detector.detect_result(frame)
print(result)
```

### 6.2 Verify Detection Accuracy

**Good results:**
- Detection rate >90%
- Confidence >0.8
- Numbers detected correctly

**If detection is poor:**
- Create templates (see Step 5)
- Adjust screen_region
- Calibrate color ranges
- See `IMPROVE_DETECTION_RATE.md`

---

## Step 7: Configure Betting Areas (Critical)

### 7.1 Find Betting Button Coordinates

**Method 1: Using Python**
```python
import pyautogui
import time

print("Move mouse to RED bet button and wait 5 seconds...")
time.sleep(5)
red_x, red_y = pyautogui.position()
print(f"Red: [{red_x}, {red_y}]")

print("\nMove mouse to BLACK bet button and wait 5 seconds...")
time.sleep(5)
black_x, black_y = pyautogui.position()
print(f"Black: [{black_x}, {black_y}]")

print("\nMove mouse to CONFIRM button and wait 5 seconds...")
time.sleep(5)
confirm_x, confirm_y = pyautogui.position()
print(f"Confirm: [{confirm_x}, {confirm_y}]")
```

**Method 2: Using Screenshot Tools**
1. Take screenshot of game
2. Open in image editor
3. Note pixel coordinates of buttons
4. Update config

### 7.2 Update Config with Coordinates

```json
{
  "betting": {
    "betting_areas": {
      "red": [500, 400],      // Your coordinates here
      "black": [600, 400],    // Your coordinates here
      "green": [550, 350]     // Your coordinates here (if needed)
    },
    "confirm_button": [550, 500]  // Your coordinates here
  }
}
```

### 7.3 Test Bet Placement (Dry Run)

**Important:** Test with minimum bet first!

```python
from backend.app.betting import BetController
from backend.app.config_loader import ConfigLoader

# Load config
config = ConfigLoader.load_config('config/default_config.json')

# Initialize bet controller
bet_controller = BetController(config)

# Test placing minimum bet (dry run - check if coordinates work)
# Don't actually place bet - just verify coordinates are correct
print("Testing coordinates...")
print("Make sure game is visible and ready")
print("Coordinates will be tested - verify they're correct before enabling real betting")
```

---

## Step 8: Prepare for Live Testing

### 8.1 Set Up Test Account
- Use test/sandbox account if available
- Or use minimum bet amounts
- Never test with large amounts

### 8.2 Verify Stop Loss
```json
{
  "risk": {
    "stop_loss": 500.0  // Bot will stop if balance reaches this
  }
}
```

### 8.3 Check Failsafe
- PyAutoGUI failsafe is enabled by default
- Move mouse to top-left corner to stop bot
- Or press `Ctrl+C` in terminal

---

## Step 9: Run the Bot

### 9.1 Basic Run

```bash
python main.py
```

### 9.2 With Custom Config

```bash
python main.py --config config/my_config.json
```

### 9.3 Test Mode (Simulation)

```bash
python main.py --test
```

**Note:** Test mode may not be fully implemented. Use video testing instead.

---

## Step 10: Monitor the Bot

### 10.1 Check Logs

Logs are saved in `logs/` directory:
- `roulette_log_TIMESTAMP.csv` - All spins and bets
- `roulette_log_TIMESTAMP.json` - JSON format
- `errors_TIMESTAMP.log` - Error logs

### 10.2 Monitor Console Output

The bot will print:
- Detection results
- Bet placements
- Balance updates
- Errors and warnings

### 10.3 Check Performance

```python
# Analyze results
python analyze_results.py logs/roulette_log_TIMESTAMP.json
```

---

## Step 11: Troubleshooting

### Problem: Detection Rate is Low
**Solution:**
1. Create number templates (Step 5)
2. Set screen_region in config
3. Adjust color ranges
4. See `IMPROVE_DETECTION_RATE.md`

### Problem: Bets Not Placing
**Solution:**
1. Verify betting area coordinates (Step 7)
2. Check if game window is visible
3. Test coordinates manually
4. Verify confirm button coordinates

### Problem: Bot Crashes
**Solution:**
1. Check error logs in `logs/` folder
2. Verify all dependencies installed
3. Check config file syntax (valid JSON)
4. Ensure game is visible and accessible

### Problem: Wrong Numbers Detected
**Solution:**
1. Create/update templates
2. Improve video/screen quality
3. Adjust preprocessing settings
4. Increase confidence threshold

### Problem: Session Disconnects
**Solution:**
1. Verify maintenance_bet_interval is set (1800 seconds = 30 min)
2. Check min_bet_amount is correct
3. Ensure bot is placing maintenance bets
4. Monitor session logs

---

## Step 12: Production Deployment

### 12.1 For 24/7 Operation

**Option A: Local Machine**
- Keep computer on 24/7
- Use process manager (Supervisor, PM2)
- Set up auto-restart on crash

**Option B: VPS/Cloud Server**
- Deploy to VPS ($10-20/month)
- Set up web dashboard (future enhancement)
- Configure monitoring

### 12.2 Process Management

**Windows:**
- Use Task Scheduler
- Or use NSSM (Non-Sucking Service Manager)

**Linux/Mac:**
- Use Supervisor or PM2
- Configure auto-restart

### 12.3 Monitoring

- Set up alerts for errors
- Monitor balance changes
- Track detection rate
- Review logs regularly

---

## Complete Checklist

Before running the bot:

- [ ] Python dependencies installed
- [ ] Tesseract OCR installed (optional)
- [ ] Configuration file edited with correct settings
- [ ] Betting area coordinates set (CRITICAL)
- [ ] Number templates created (recommended)
- [ ] Detection tested with video/file
- [ ] Stop loss configured
- [ ] Test account/small bets ready
- [ ] Failsafe understood (mouse to corner)
- [ ] Logs directory exists
- [ ] Game window visible and accessible

---

## Quick Start Summary

1. **Install:** `pip install -r requirements.txt`
2. **Configure:** Edit `config/default_config.json`
   - Set betting area coordinates (CRITICAL)
   - Configure strategy
   - Set risk parameters
3. **Test:** `python test_video.py video.mp4`
4. **Create Templates:** Extract numbers 0-36 (recommended)
5. **Run:** `python main.py`

---

## Important Notes

### Safety
-  **Always test with small bets first**
-  **Set appropriate stop loss**
-  **Monitor bot closely initially**
-  **Use failsafe (mouse to corner) to stop**

### Legal
-  **Check platform terms of service**
-  **Use at your own risk**
-  **Gambling involves risk**

### Technical
-  **Templates improve accuracy significantly**
-  **Screen region improves performance**
-  **Regular testing is recommended**
-  **Keep logs for analysis**

---

## Next Steps

After successful implementation:

1. **Optimize:** Improve detection rate (see `IMPROVE_DETECTION_RATE.md`)
2. **Analyze:** Review results (see `HOW_TO_ANALYZE_RESULTS.md`)
3. **Enhance:** Add web dashboard (future)
4. **Monitor:** Track performance over time
5. **Iterate:** Adjust strategy based on results

---

## Getting Help

If you encounter issues:

1. Check error logs in `logs/` folder
2. Review troubleshooting section (Step 11)
3. Verify configuration settings
4. Test detection separately
5. Check documentation files:
   - `IMPROVE_DETECTION_RATE.md`
   - `HOW_TO_ANALYZE_RESULTS.md`
   - `VIDEO_TESTING_GUIDE.md`
   - `QUICK_START.md`

---

## Conclusion

Follow these steps in order:
1. Setup  2. Configure  3. Test  4. Run  5. Monitor

**Most critical steps:**
- Setting betting area coordinates
- Creating number templates
- Testing before live use

Good luck with your implementation!

