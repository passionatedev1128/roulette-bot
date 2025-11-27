# Perfect Bot Implementation Guide - Step-by-Step

## Philosophy

This guide ensures you build a **perfect, production-ready bot** by:
-  Validating each step before proceeding
-  Testing components individually
-  Verifying accuracy at every stage
-  Following best practices
-  Handling edge cases
-  Ensuring reliability

**Follow this guide exactly, and you'll have a perfect bot.**

---

## Phase 0: Pre-Implementation Analysis

### 0.1 Understand Your Game Platform

**Before starting, you MUST know:**

1. **Game Platform Details:**
   - [ ] What is the exact URL/name of the roulette game?
   - [ ] Does it run in browser or desktop app?
   - [ ] What resolution does it run at?
   - [ ] Are there any specific requirements?

2. **Game Interface Analysis:**
   - [ ] Where exactly does the winning number appear?
   - [ ] What does the number font/style look like?
   - [ ] Where are the betting buttons located?
   - [ ] How does the betting interface work?
   - [ ] What happens when you place a bet?

3. **Game Timing:**
   - [ ] How long between spins?
   - [ ] When does the number appear?
   - [ ] How long is it visible?
   - [ ] When can you place bets?

**Action:** Document all findings in a text file for reference.

---

## Phase 1: Environment Setup (Validation Required)

### 1.1 Python Environment

**Step 1.1.1: Verify Python Version**
```bash
python --version
```
**Expected:** Python 3.12 or higher
**If not:** Install/upgrade Python first

**Step 1.1.2: Create Virtual Environment (Recommended)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```
**Verify:** Prompt should show `(venv)`

**Step 1.1.3: Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
**Verify Installation:**
```bash
python check_setup.py
```
**Expected Output:**
```
[OK] OpenCV installed
[OK] NumPy installed
[OK] pytesseract installed
[OK] pyautogui installed
```

**If any  appears:** Fix that dependency before proceeding.

### 1.2 Tesseract OCR (Optional but Recommended)

**Step 1.2.1: Install Tesseract**

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH:
   - Search "Environment Variables"
   - Edit Path  Add: `C:\Program Files\Tesseract-OCR`
   - Restart terminal

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Step 1.2.2: Verify Tesseract**
```bash
tesseract --version
```
**Expected:** Version number (e.g., "tesseract 5.3.0")

**Step 1.2.3: Test Tesseract in Python**
```python
import pytesseract
try:
    version = pytesseract.get_tesseract_version()
    print(f" Tesseract {version} accessible")
except:
    print(" Tesseract not found - bot will work but templates recommended")
```

** Validation Checkpoint:** All dependencies installed and verified.

---

## Phase 2: Project Structure Validation

### 2.1 Verify Project Structure

**Check that these directories exist:**
```
Roulette Bot/
├── backend/
│   └── app/
│       ├── detection/
│       ├── strategy/
│       ├── betting/
│       └── logging/
├── config/
├── templates/
├── logs/
└── test_results/
```

**If missing, create:**
```bash
# Windows
mkdir backend\app\detection backend\app\strategy backend\app\betting backend\app\logging config templates logs test_results

# Mac/Linux
mkdir -p backend/app/{detection,strategy,betting,logging} config templates logs test_results
```

### 2.2 Verify Core Files Exist

```bash
# Check critical files
python -c "
import os
files = [
    'main.py',
    'requirements.txt',
    'backend/app/bot.py',
    'backend/app/detection/screen_detector.py',
    'backend/app/strategy/martingale_strategy.py',
    'backend/app/betting/bet_controller.py',
    'config/default_config.json'
]
for f in files:
    print('' if os.path.exists(f) else '', f)
"
```

** Validation Checkpoint:** All files present.

---

## Phase 3: Game Interface Analysis (Critical)

### 3.1 Capture Game Screenshots

**Step 3.1.1: Take Reference Screenshots**
1. Open your roulette game
2. Take screenshots at different moments:
   - When number is displayed
   - When betting interface is visible
   - When bet is placed
   - When round is waiting

**Step 3.1.2: Analyze Screenshots**
Create a document with:
- Screenshot 1: Number display location
- Screenshot 2: Betting buttons location
- Screenshot 3: Confirm button location
- Screenshot 4: Game interface overview

**Step 3.1.3: Measure Coordinates**
Use this script to find exact coordinates:

```python
import pyautogui
import time
import json

def capture_coordinates():
    """Interactive coordinate capture."""
    coordinates = {}
    
    print("=" * 60)
    print("COORDINATE CAPTURE TOOL")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Move mouse to target location")
    print("2. Wait 5 seconds")
    print("3. Coordinates will be captured")
    print("4. Press Ctrl+C to finish\n")
    
    targets = {
        "number_display_center": "Center of winning number display",
        "red_bet_button": "Red betting button",
        "black_bet_button": "Black betting button",
        "green_bet_button": "Green/Zero betting button (if exists)",
        "confirm_button": "Confirm/Place bet button",
        "amount_input": "Bet amount input field (if needed)",
    }
    
    for key, description in targets.items():
        try:
            print(f"\n{description}")
            print("Move mouse now... (5 seconds)")
            time.sleep(5)
            x, y = pyautogui.position()
            coordinates[key] = [x, y]
            print(f" Captured: [{x}, {y}]")
        except KeyboardInterrupt:
            break
    
    # Save coordinates
    with open('game_coordinates.json', 'w') as f:
        json.dump(coordinates, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Coordinates saved to game_coordinates.json")
    print("=" * 60)
    
    return coordinates

if __name__ == '__main__':
    capture_coordinates()
```

**Run this script and capture ALL coordinates.**

### 3.2 Analyze Number Display

**Step 3.2.1: Number Display Characteristics**
Document:
- [ ] Font style (bold, italic, serif, sans-serif)
- [ ] Font size (estimate pixels)
- [ ] Color (exact color values if possible)
- [ ] Background (color, gradient, transparent)
- [ ] Position on screen (describe location)
- [ ] Size of display area (width x height)

**Step 3.2.2: Number Visibility**
- [ ] How long is number visible? (seconds)
- [ ] Does it animate/fade?
- [ ] Is it always in same location?
- [ ] Does it change size?

**Step 3.2.3: Capture Sample Numbers**
Take screenshots showing:
- Each digit (0-9) clearly
- Different numbers (0, 1, 17, 36, etc.)
- Various conditions (bright, dim, etc.)

** Validation Checkpoint:** Complete understanding of game interface documented.

---

## Phase 4: Configuration - Perfect Setup

### 4.1 Create Custom Configuration

**Step 4.1.1: Copy Default Config**
```bash
cp config/default_config.json config/my_game_config.json
```

**Step 4.1.2: Configure Detection Settings**

```json
{
  "detection": {
    "screen_region": [100, 200, 800, 600],
    // Calculate from your game analysis:
    // [x, y, width, height] where number appears
    // Use screenshot tool to find exact values
    
    "color_ranges": {
      // These are defaults - may need adjustment
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
    "templates_dir": "templates",
    "number_display_region": [x, y, width, height],
    // Exact region where number appears (from Phase 3)
    "confidence_threshold": 0.7
    // Minimum confidence to accept detection
  }
}
```

**Step 4.1.3: Configure Betting Areas**

**CRITICAL - Use coordinates from Phase 3:**

```json
{
  "betting": {
    "betting_areas": {
      "red": [500, 400],      // From coordinate capture
      "black": [600, 400],    // From coordinate capture
      "green": [550, 350]     // From coordinate capture (if exists)
    },
    "confirm_button": [550, 500],  // From coordinate capture
    "amount_input": [400, 450],    // From coordinate capture (if needed)
    "requires_amount_entry": false,
    // true if you need to type amount before betting
    
    "human_delays": {
      "min": 0.2,  // Minimum delay (seconds)
      "max": 0.8   // Maximum delay (seconds)
      // Higher delays = more human-like, slower
    },
    "bet_verification": {
      "enabled": true,
      "timeout": 5,
      // Verify bet was placed within 5 seconds
      "check_method": "balance_change"
      // "balance_change" or "visual_confirmation"
    }
  }
}
```

**Step 4.1.4: Configure Strategy**

```json
{
  "strategy": {
    "type": "martingale",
    // Choose: "martingale", "fibonacci", "custom"
    
    "base_bet": 10.0,
    // Starting bet amount - USE MINIMUM FOR TESTING
    
    "max_gales": 5,
    // Maximum progression steps
    // Calculate: Can you afford 5 steps?
    // Example: 10, 20, 40, 80, 160 = 310 total
    
    "multiplier": 2.0,
    // Martingale multiplier (2.0 = double)
    
    "entry_conditions": {
      "enabled": true,
      "conditions": [
        {
          "type": "color_pattern",
          // Bet after N consecutive same color
          "pattern_length": 3,
          "action": "bet_opposite"
        }
      ]
    },
    
    "zero_handling": {
      "rule": "continue_sequence",
      // "continue_sequence", "reset", or "skip"
      "reset_on_zero": false
    }
  }
}
```

**Step 4.1.5: Configure Risk Management**

```json
{
  "risk": {
    "initial_balance": 1000.0,
    // Your starting balance
    
    "stop_loss": 500.0,
    // Bot stops if balance reaches this
    // Calculate: initial - stop_loss = max loss
    
    "stop_win": null,
    // Optional: Stop if profit reaches this
    
    "guarantee_fund_percentage": 20,
    // Reserve 20% for gale bets
    
    "max_bet_amount": 1000.0,
    // Never bet more than this (safety)
    
    "max_consecutive_losses": 10,
    // Stop after N consecutive losses
  }
}
```

**Step 4.1.6: Configure Session Management**

```json
{
  "session": {
    "maintenance_bet_interval": 1800,
    // 1800 seconds = 30 minutes
    // Place minimum bet every 30 min to keep session active
    
    "min_bet_amount": 1.0,
    // Minimum bet for maintenance
    
    "reconnection": {
      "enabled": true,
      "max_retries": 3,
      "retry_delay": 5
    }
  }
}
```

**Step 4.1.7: Validate Configuration**

```python
import json

def validate_config(config_path):
    """Validate configuration file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    errors = []
    
    # Check betting areas
    betting = config.get('betting', {})
    areas = betting.get('betting_areas', {})
    if not areas.get('red') or not areas.get('black'):
        errors.append("Missing betting area coordinates")
    
    # Check strategy
    strategy = config.get('strategy', {})
    if not strategy.get('base_bet') or strategy['base_bet'] <= 0:
        errors.append("Invalid base_bet")
    
    # Check risk management
    risk = config.get('risk', {})
    if not risk.get('stop_loss') or risk['stop_loss'] >= risk.get('initial_balance', 1000):
        errors.append("Invalid stop_loss - must be less than initial_balance")
    
    if errors:
        print(" Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(" Configuration valid")
        return True

validate_config('config/my_game_config.json')
```

** Validation Checkpoint:** Configuration valid and tested.

---

## Phase 5: Create Perfect Templates (Critical for Accuracy)

### 5.1 Template Creation Strategy

**Step 5.1.1: Capture High-Quality Screenshots**

**Method 1: From Video**
```python
import cv2

def extract_frames_for_templates(video_path, output_dir="template_frames"):
    """Extract frames showing numbers clearly."""
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    extracted = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Extract every Nth frame (adjust based on video)
        if frame_count % 10 == 0:
            cv2.imwrite(f"{output_dir}/frame_{frame_count}.png", frame)
            extracted += 1
            print(f"Extracted frame {frame_count}")
    
    cap.release()
    print(f"Extracted {extracted} frames to {output_dir}/")

extract_frames_for_templates("roleta_brazileria.mp4")
```

**Method 2: From Live Game**
- Take screenshots when numbers appear
- Ensure good quality, clear focus

**Step 5.1.2: Extract Individual Numbers**

**For each number (0-36):**

1. **Open frame in image editor** (GIMP, Photoshop, Paint.NET, etc.)

2. **Identify number location:**
   - Use coordinates from Phase 3
   - Zoom in for precision

3. **Crop the number:**
   - Crop tightly around the number
   - Include small margin (2-3 pixels)
   - Keep consistent size

4. **Save with exact naming:**
   ```
   templates/number_0.png
   templates/number_1.png
   ...
   templates/number_36.png
   ```

**Step 5.1.3: Template Quality Standards**

**Each template should:**
-  Be clear and not blurry
-  Match game font exactly
-  Be consistent size (recommended: 30-50 pixels height)
-  Have transparent or solid background
-  Be in PNG format
-  Show number clearly centered

**Step 5.1.4: Create Multiple Templates (Advanced)**

For even better accuracy, create multiple templates per number:
```
templates/
  number_0_v1.png
  number_0_v2.png
  number_1_v1.png
  ...
```

Then modify detector to try all variations.

**Step 5.1.5: Verify Templates**

```python
import cv2
import os

def verify_templates(template_dir="templates"):
    """Verify all templates exist and are valid."""
    missing = []
    invalid = []
    valid = []
    
    for i in range(37):
        file_path = f"{template_dir}/number_{i}.png"
        
        if not os.path.exists(file_path):
            missing.append(i)
        else:
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                invalid.append(i)
            else:
                valid.append(i)
                h, w = img.shape[:2]
                print(f" number_{i}.png: {w}x{h} pixels")
    
    print("\n" + "=" * 60)
    print("TEMPLATE VERIFICATION")
    print("=" * 60)
    print(f"Valid templates: {len(valid)}/37")
    
    if missing:
        print(f"\n Missing: {missing}")
    if invalid:
        print(f"\n Invalid: {invalid}")
    
    if len(valid) == 37:
        print("\n All templates valid!")
        return True
    else:
        print(f"\n Need {37 - len(valid)} more templates")
        return False

verify_templates()
```

** Validation Checkpoint:** All 37 templates (0-36) created and verified.

---

## Phase 6: Detection Testing & Calibration

### 6.1 Test Detection with Video

**Step 6.1.1: Run Video Test**
```bash
python test_video.py roleta_brazileria.mp4 --skip 5 --max-frames 100
```

**Step 6.1.2: Analyze Results**
```bash
python analyze_results.py test_results/results_*.json
```

**Step 6.1.3: Target Metrics**

**Minimum Acceptable:**
- Detection rate: >85%
- Average confidence: >0.75
- Template method usage: >80%

**Perfect Target:**
- Detection rate: >95%
- Average confidence: >0.90
- Template method usage: >95%

**If below minimum:**
- Re-check templates quality
- Adjust screen_region
- Calibrate color ranges
- See `IMPROVE_DETECTION_RATE.md`

### 6.2 Calibrate Color Ranges

**Step 6.2.1: Extract Color Samples**

```python
import cv2
import numpy as np

def extract_color_samples(frame, regions):
    """Extract HSV color samples from regions."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    for name, (x, y, w, h) in regions.items():
        roi = hsv[y:y+h, x:x+w]
        avg_hsv = np.mean(roi.reshape(-1, 3), axis=0)
        min_hsv = np.min(roi.reshape(-1, 3), axis=0)
        max_hsv = np.max(roi.reshape(-1, 3), axis=0)
        
        print(f"{name}:")
        print(f"  Average HSV: {avg_hsv}")
        print(f"  Range: {min_hsv} - {max_hsv}")
        print()

# Use this to find color ranges for your game
# Mark red, black, green areas on screenshot first
```

**Step 6.2.2: Update Color Ranges**

Based on samples, update config:
```json
{
  "detection": {
    "color_ranges": {
      "red": [
        [[your_min_h, your_min_s, your_min_v], 
         [your_max_h, your_max_s, your_max_v]]
      ],
      // Repeat for black and green
    }
  }
}
```

### 6.3 Optimize Screen Region

**Step 6.3.1: Find Optimal Region**

```python
import cv2
import pyautogui

def find_optimal_region():
    """Find best region for number detection."""
    screenshot = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Display and let user select region
    # Or use coordinates from Phase 3
    
    # Test different regions
    test_regions = [
        None,  # Full screen
        [100, 200, 800, 600],  # Region 1
        [200, 300, 600, 400],  # Region 2
        # Add more test regions
    ]
    
    # Test each and compare detection accuracy
    # Choose region with best results
```

**Step 6.3.2: Set Optimal Region**

Update config with best region:
```json
{
  "detection": {
    "screen_region": [x, y, width, height]  // Best performing region
  }
}
```

** Validation Checkpoint:** Detection rate >90% with confidence >0.85.

---

## Phase 7: Betting System Testing (Critical)

### 7.1 Test Betting Coordinates

**Step 7.1.1: Visual Verification**

```python
import pyautogui
import time

def test_betting_coordinates(config_path):
    """Test if betting coordinates are correct."""
    import json
    from backend.app.config_loader import ConfigLoader
    
    config = ConfigLoader.load_config(config_path)
    betting = config.get('betting', {})
    areas = betting.get('betting_areas', {})
    
    print("=" * 60)
    print("TESTING BETTING COORDINATES")
    print("=" * 60)
    print("\nMake sure game window is visible and ready!")
    print("Mouse will move to each coordinate - verify they're correct")
    print("\nPress Enter to start, Ctrl+C to cancel...")
    input()
    
    # Test red button
    if 'red' in areas:
        x, y = areas['red']
        print(f"\n1. Moving to RED button: [{x}, {y}]")
        pyautogui.moveTo(x, y, duration=1)
        time.sleep(2)
        print("   Is this the RED betting button? (y/n)")
        if input().lower() != 'y':
            print("    RED coordinates incorrect!")
            return False
    
    # Test black button
    if 'black' in areas:
        x, y = areas['black']
        print(f"\n2. Moving to BLACK button: [{x}, {y}]")
        pyautogui.moveTo(x, y, duration=1)
        time.sleep(2)
        print("   Is this the BLACK betting button? (y/n)")
        if input().lower() != 'y':
            print("    BLACK coordinates incorrect!")
            return False
    
    # Test confirm button
    confirm = betting.get('confirm_button')
    if confirm:
        x, y = confirm
        print(f"\n3. Moving to CONFIRM button: [{x}, {y}]")
        pyautogui.moveTo(x, y, duration=1)
        time.sleep(2)
        print("   Is this the CONFIRM button? (y/n)")
        if input().lower() != 'y':
            print("    CONFIRM coordinates incorrect!")
            return False
    
    print("\n All coordinates verified!")
    return True

test_betting_coordinates('config/my_game_config.json')
```

**Step 7.1.2: Test Actual Bet Placement**

** WARNING: Use minimum bet amount for testing!**

```python
from backend.app.betting import BetController
from backend.app.config_loader import ConfigLoader

# Load config
config = ConfigLoader.load_config('config/my_game_config.json')

# Set minimum bet for testing
config['strategy']['base_bet'] = 1.0  # Minimum bet

# Initialize bet controller
bet_controller = BetController(config)

# Test placing minimum bet
print("Testing bet placement with MINIMUM bet...")
print("Make sure game is ready and visible")
print("Press Enter to continue...")
input()

result = bet_controller.place_bet('red', 1.0)

if result['success']:
    print(" Bet placed successfully!")
    print(f"  Type: {result['bet_type']}")
    print(f"  Amount: {result['bet_amount']}")
else:
    print(f" Bet placement failed: {result.get('error')}")
```

**Step 7.1.3: Verify Bet Verification**

Ensure bot can verify bets were placed:
```python
# Test bet verification
can_verify = bet_controller.verify_bet_placed()
print(f"Bet verification: {' Working' if can_verify else ' Not working'}")
```

** Validation Checkpoint:** All betting coordinates verified and tested with minimum bet.

---

## Phase 8: Strategy Testing

### 8.1 Test Strategy Logic

**Step 8.1.1: Simulate Strategy**

```python
from backend.app.strategy import MartingaleStrategy
from backend.app.config_loader import ConfigLoader

config = ConfigLoader.load_config('config/my_game_config.json')
strategy = MartingaleStrategy(config.get('strategy', {}))

# Simulate sequence
history = [
    {"number": 17, "color": "black"},
    {"number": 3, "color": "red"},
    {"number": 25, "color": "red"},
]

for result in history:
    bet = strategy.calculate_bet(history, 1000.0, result)
    print(f"Result: {result['number']} ({result['color']})")
    print(f"  Bet: {bet}")
    if bet:
        # Simulate loss
        strategy.update_after_bet({"result": "loss", "balance_after": 990.0})
    print()
```

**Step 8.1.2: Verify Gale Progression**

```python
# Test gale progression
strategy = MartingaleStrategy(config.get('strategy', {}))

for i in range(5):
    bet = strategy.get_bet_amount()
    print(f"Gale step {i}: Bet amount = {bet}")
    strategy.update_after_bet({"result": "loss", "balance_after": 1000.0})

# Verify amounts are correct
# Step 0: base_bet
# Step 1: base_bet * multiplier
# Step 2: base_bet * multiplier^2
# etc.
```

**Step 8.1.3: Test Zero Handling**

```python
# Test zero handling
zero_result = {"number": 0, "color": "green", "zero": True}
handling = strategy.handle_zero([], 1000.0)
print(f"Zero handling: {handling}")
```

** Validation Checkpoint:** Strategy logic verified and working correctly.

---

## Phase 9: Integration Testing

### 9.1 End-to-End Test (Simulation)

**Step 9.1.1: Test Complete Flow**

```python
from backend.app.bot import RouletteBot
from backend.app.config_loader import ConfigLoader

# Load config
config = ConfigLoader.load_config('config/my_game_config.json')

# Initialize bot
bot = RouletteBot('config/my_game_config.json')

# Test detection
result = bot.detect_result()
print(f"Detection test: {result}")

# Test strategy
if result.get('number') is not None:
    spin_result = bot.process_spin(result)
    print(f"Spin processing: {spin_result}")
```

### 9.2 Test Maintenance Bets

```python
# Test maintenance bet system
import time

# Simulate 30 minutes
bot.last_maintenance_bet_time = time.time() - 1800  # 30 min ago

needs_maintenance = bot.check_maintenance_bet()
print(f"Needs maintenance bet: {needs_maintenance}")

if needs_maintenance:
    bot.place_maintenance_bet()
```

### 9.3 Test Stop Conditions

```python
# Test stop loss
bot.current_balance = 450.0  # Below stop loss
should_stop = bot.check_stop_conditions()
print(f"Should stop: {should_stop}")

# Test max gale
bot.strategy.gale_step = 6  # Exceeds max
should_stop = bot.check_stop_conditions()
print(f"Should stop (max gale): {should_stop}")
```

** Validation Checkpoint:** All components working together correctly.

---

## Phase 10: Pre-Production Validation

### 10.1 Final Configuration Review

**Checklist:**
- [ ] Betting coordinates verified and tested
- [ ] Detection rate >90% with confidence >0.85
- [ ] Templates created for all numbers (0-36)
- [ ] Strategy configured correctly
- [ ] Stop loss set appropriately
- [ ] Maintenance bet interval set (1800 seconds)
- [ ] Risk parameters configured
- [ ] All tests passed

### 10.2 Safety Verification

**Safety Checklist:**
- [ ] Stop loss is less than initial balance
- [ ] Base bet is minimum amount for testing
- [ ] Max gale progression is affordable
- [ ] Guarantee fund covers gale progression
- [ ] Failsafe is understood (mouse to corner)
- [ ] Logs directory exists and writable
- [ ] Error handling is working

### 10.3 Performance Verification

**Run Complete Test:**
```bash
# Test with video
python test_video.py video.mp4 --skip 1

# Analyze results
python analyze_results.py test_results/results_*.json

# Verify metrics
# - Detection rate >90%
# - Confidence >0.85
# - Template usage >90%
```

** Validation Checkpoint:** All safety and performance checks passed.

---

## Phase 11: Production Deployment

### 11.1 Final Preparation

**Step 11.1.1: Backup Configuration**
```bash
cp config/my_game_config.json config/my_game_config_backup.json
```

**Step 11.1.2: Set Production Values**
- Set appropriate base bet
- Verify stop loss
- Check all settings

**Step 11.1.3: Test Account Setup**
- Use test/sandbox account if available
- Or use minimum bets on real account
- Never start with large amounts

### 11.2 Start Bot

**Step 11.2.1: Initial Run**
```bash
python main.py --config config/my_game_config.json
```

**Step 11.2.2: Monitor First 10 Rounds**
- Watch console output
- Verify detections are correct
- Check bets are placing correctly
- Monitor balance changes

**Step 11.2.3: Check Logs**
```bash
# View latest log
ls -lt logs/ | head -1

# Check for errors
grep -i error logs/roulette_log_*.log
```

### 11.3 Long-Term Operation

**For 24/7 Operation:**

**Option A: Process Manager (Recommended)**
```bash
# Windows: Use NSSM or Task Scheduler
# Linux/Mac: Use Supervisor or PM2

# Example with Supervisor (Linux)
supervisorctl start roulette-bot
supervisorctl status roulette-bot
```

**Option B: Screen/Tmux Session**
```bash
# Linux
screen -S roulette-bot
python main.py
# Ctrl+A, D to detach

# Reattach
screen -r roulette-bot
```

**Monitoring:**
- Check logs daily
- Monitor detection rate
- Review balance changes
- Verify maintenance bets working

---

## Implementation Tools

### Validation Tool

**Before running the bot, validate your implementation:**

```bash
python validate_implementation.py config/my_game_config.json
```

This tool checks:
-  Project structure
-  Dependencies installed
-  Configuration valid
-  Betting coordinates set
-  Templates present
-  Risk management configured
-  All safety checks

**Run this before every bot run to ensure perfection.**

### Coordinate Capture Tool

**Find exact coordinates for your game:**

```bash
python coordinate_capture_tool.py
```

This interactive tool:
- Guides you to capture coordinates
- Tests coordinates automatically
- Generates config snippets
- Saves coordinates to file

**Use this in Phase 3 and Phase 7.**

### Template Helper Tool

**Extract frames for template creation:**

```bash
# Extract frames from video
python template_creation_helper.py extract video.mp4

# Verify templates
python template_creation_helper.py verify
```

**Use this in Phase 5.**

---

## Phase 12: Continuous Improvement

### 12.1 Performance Monitoring

**Daily Checks:**
- Detection rate trends
- Average confidence scores
- Win/loss ratio
- Balance changes

**Weekly Analysis:**
```bash
python analyze_results.py logs/roulette_log_*.json
```

### 12.2 Optimization

**Based on results:**
- Adjust strategy parameters
- Fine-tune detection settings
- Update templates if game changes
- Optimize betting timing

### 12.3 Maintenance

**Regular Tasks:**
- Update templates if game UI changes
- Re-calibrate coordinates if needed
- Review and update configuration
- Backup logs and configurations

---

## Perfect Bot Checklist

### Pre-Implementation
- [ ] Game platform analyzed
- [ ] Interface documented
- [ ] Coordinates captured

### Setup
- [ ] Python environment ready
- [ ] Dependencies installed
- [ ] Tesseract installed (optional)
- [ ] Project structure verified

### Configuration
- [ ] Detection settings configured
- [ ] Betting coordinates set and verified
- [ ] Strategy configured
- [ ] Risk management set
- [ ] Configuration validated

### Templates
- [ ] All 37 templates created (0-36)
- [ ] Templates verified
- [ ] Quality standards met

### Testing
- [ ] Detection tested (>90% rate)
- [ ] Betting coordinates tested
- [ ] Strategy logic verified
- [ ] Integration tested
- [ ] Safety checks passed

### Production
- [ ] Final validation complete
- [ ] Test account ready
- [ ] Monitoring set up
- [ ] Backup created

---

## Success Criteria

**Perfect Bot Has:**
-  Detection rate >95%
-  Confidence >0.90
-  Template usage >95%
-  All coordinates verified
-  Safety mechanisms working
-  Logging functional
-  Error handling robust

**Follow this guide exactly, validate each step, and you'll have a perfect bot.**

---

## Troubleshooting Quick Reference

**Low Detection:**
- Check templates quality
- Verify screen region
- Calibrate color ranges
- Improve video quality

**Bets Not Placing:**
- Verify coordinates
- Check game visibility
- Test coordinates manually
- Verify confirm button

**Bot Crashes:**
- Check error logs
- Verify dependencies
- Validate configuration
- Test components individually

**See detailed guides:**
- `IMPROVE_DETECTION_RATE.md`
- `HOW_TO_ANALYZE_RESULTS.md`
- `COMPLETE_IMPLEMENTATION_GUIDE.md`

---

**This guide ensures perfection. Follow it step-by-step, validate everything, and you'll have a production-ready bot.**

