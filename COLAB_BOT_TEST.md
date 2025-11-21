# 🎰 Roulette Bot Test Script for Google Colab

Complete test script for testing the roulette bot with all implemented features including Even/Odd strategy, Gales, StopLoss/StopWin, Keepalive, and comprehensive logging.

---

## 📋 Setup Instructions

### Step 1: Install Dependencies

```python
# Install required packages
!pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils -q
print("✅ Dependencies installed!")
```

### Step 2: Upload Project Files

**Option A: Via Colab Files Sidebar (Recommended)**
1. Click the 📁 folder icon in the left sidebar
2. Click "Upload to session storage"
3. Upload your entire project folder
4. Upload your video file (e.g., `roleta_brazileria.mp4`)

**Option B: Via Code**
```python
from google.colab import files
import zipfile
import os

# Upload project zip
print("📤 Upload project zip file:")
uploaded = files.upload()
zip_file = list(uploaded.keys())[0]
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall('.')
print("✅ Project extracted!")

# Upload video
print("📤 Upload video file:")
uploaded = files.upload()
video_file = list(uploaded.keys())[0]
print(f"✅ Video: {video_file}")
```

---

## 🚀 Complete Test Script

**⚠️ IMPORTANT: Before running, customize `START_SECONDS` to your desired start time!**

Copy and paste this complete script into a Colab cell:

```python
import sys
import os
import cv2
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# ⚠️ IMPORTANT: Mock pyautogui for Colab (no GUI available)
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
print("✅ pyautogui mocked for Colab")

# Add project to Python path
sys.path.insert(0, os.path.abspath('.'))

# Import project modules
from backend.app.config_loader import ConfigLoader
from backend.app.bot import RouletteBot, calculate_required_bankroll
from backend.app.detection.frame_detector import FrameDetector
from backend.app.strategy.even_odd_strategy import EvenOddStrategy

print("✅ Modules imported successfully")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Find video file
video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
if not video_files:
    print("❌ No video file found! Please upload a video file.")
    raise FileNotFoundError("No video file found")

video_file = video_files[0]
print(f"✅ Found video: {video_file}")

# Load configuration
config_path = 'config/default_config.json'
if not os.path.exists(config_path):
    print(f"❌ Config file not found: {config_path}")
    raise FileNotFoundError(f"Config file not found: {config_path}")

config = ConfigLoader.load_config(config_path)
print(f"✅ Config loaded: {config_path}")

# Test parameters - CUSTOMIZE THESE
START_SECONDS = 30.0  # Start from this time in seconds (e.g., 30.0 for 30 seconds, 60.5 for 1 minute 0.5 seconds)
MAX_SPINS = 100  # Limit number of spins to test (None = unlimited)
FRAME_SKIP = 1  # Process every Nth frame (1 = all frames)
MAX_DETECTION_FAILURES = 200  # Stop after this many consecutive failures

# ============================================================================
# INITIALIZE BOT
# ============================================================================

print("\n" + "="*80)
print("INITIALIZING BOT")
print("="*80)

# Initialize bot in test mode
bot = RouletteBot(config_path, test_mode=True)
print(f"✅ Bot initialized")
print(f"   Strategy: {bot.strategy.strategy_type}")
print(f"   Initial Balance: {bot.current_balance:.2f}")

# Display bankroll information if using Even/Odd strategy
if isinstance(bot.strategy, EvenOddStrategy):
    bankroll_info = calculate_required_bankroll(
        bot.strategy.base_bet,
        bot.strategy.max_gales,
        bot.strategy.multiplier
    )
    print(f"\n📊 Bankroll Estimate:")
    print(f"   Base Bet: {bankroll_info['base_bet']:.2f}")
    print(f"   Max Gales: {bankroll_info['max_gales']}")
    print(f"   Gale Sequence: {[f'{x:.2f}' for x in bankroll_info['gale_sequence']]}")
    print(f"   Total Required (worst-case): {bankroll_info['total_required']:.2f}")
    print(f"   Recommended Bankroll: {bankroll_info['recommended_bankroll']:.2f}")

# Initialize frame detector
frame_detector = FrameDetector(config, video_file)

# Get video info first
fps = frame_detector.cap.get(cv2.CAP_PROP_FPS)
total_frames = int(frame_detector.cap.get(cv2.CAP_PROP_FRAME_COUNT))
total_duration = total_frames / fps if fps > 0 else 0

# Calculate start frame from seconds
if START_SECONDS > 0 and fps > 0:
    START_FRAME = int(START_SECONDS * fps)
    START_FRAME = min(START_FRAME, max(total_frames - 1, 0))
else:
    START_FRAME = 0

frame_detector.cap.set(cv2.CAP_PROP_POS_FRAMES, START_FRAME)
bot.detector = frame_detector

print(f"\n📹 Video Info:")
print(f"   FPS: {fps:.2f}")
print(f"   Total Frames: {total_frames}")
print(f"   Total Duration: {total_duration:.2f} seconds")
print(f"   Starting from: {START_SECONDS} seconds (frame {START_FRAME})")

# ============================================================================
# TESTING STATISTICS
# ============================================================================

stats = {
    'total_frames_processed': 0,
    'total_spins': 0,
    'successful_detections': 0,
    'detection_failures': 0,
    'consecutive_failures': 0,
    'bets_placed': 0,
    'wins': 0,
    'losses': 0,
    'zeros': 0,
    'cycles_completed': 0,
    'cycles_won': 0,
    'cycles_lost': 0,
    'max_gale_reached': 0,
    'keepalive_bets': 0,
    'detection_methods': {},
    'numbers_detected': [],
    'streak_history': [],
    'cycle_history': []
}

# ============================================================================
# MAIN TEST LOOP
# ============================================================================

print("\n" + "="*80)
print("STARTING TEST")
print("="*80)
print(f"Processing up to {MAX_SPINS} spins...")
print("-"*80)

frame_count = START_FRAME
pending_bet = None
last_detected_number = None  # Track last detected number to avoid duplicates
last_detection_frame = None
detection_cooldown = 30  # Frames to wait between detections

try:
    while True:
        # Check stop conditions
        if bot.check_stop_conditions():
            print(f"\n⚠️  Stop condition reached!")
            if bot.stop_trigger_info:
                print(f"   Type: {bot.stop_trigger_info['type']}")
                print(f"   Value: {bot.stop_trigger_info['value']}")
                print(f"   Threshold: {bot.stop_trigger_info['threshold']}")
            break
        
        # Check if max spins reached
        if MAX_SPINS and stats['total_spins'] >= MAX_SPINS:
            print(f"\n✅ Reached maximum spins limit: {MAX_SPINS}")
            break
        
        # Check max detection failures
        if stats['consecutive_failures'] >= MAX_DETECTION_FAILURES:
            print(f"\n⚠️  Too many consecutive detection failures: {stats['consecutive_failures']}")
            break
        
        # Read frame
        ret, frame = frame_detector.cap.read()
        if not ret:
            print("\n✅ End of video reached")
            break
        
        frame_count += 1
        stats['total_frames_processed'] += 1
        
        # Skip frames if needed
        if frame_count % FRAME_SKIP != 0:
            continue
        
        # Detection cooldown (avoid detecting same result multiple times)
        if last_detection_frame and (frame_count - last_detection_frame) < detection_cooldown:
            continue
        
        # Process pending bet result first
        if pending_bet:
            # Detect result from current frame (pass frame directly to avoid validation issues)
            detection = bot.detector.detect_result(frame)
            
            # Only process if we got a valid number and it's different from last
            if detection and detection.get('number') is not None:
                detected_number = detection.get('number')
                
                # Skip if same number as last detection (number still on screen)
                if detected_number == last_detected_number:
                    continue
                
                # Validate only if number changed
                if not bot.detector.validate_result(detection):
                    # Validation failed - skip this detection
                    continue
                
                result_number = detected_number
                last_detected_number = result_number
                
                # Determine if bet won
                bet_type = pending_bet['bet_type']
                won = bot._determine_bet_result(bet_type, result_number)
                
                # Handle zero
                if result_number == 0:
                    stats['zeros'] += 1
                    zero_handling = bot.strategy.handle_zero(bot.result_history, bot.current_balance)
                    print(f"  ⚠️  ZERO detected - Policy: {bot.strategy.zero_policy}")
                
                # Process win/loss
                if won:
                    stats['wins'] += 1
                    bot.current_balance += pending_bet['bet_amount']
                    result = "win"
                    bot.winning_rounds += 1
                    print(f"  🎉 WIN! +{pending_bet['bet_amount']:.2f} (Balance: {bot.current_balance:.2f})")
                    
                    # Check if cycle ended
                    if isinstance(bot.strategy, EvenOddStrategy):
                        if bot.strategy.gale_step == 0:  # First bet in cycle won
                            stats['cycles_completed'] += 1
                            stats['cycles_won'] += 1
                            print(f"  ✅ Cycle {bot.strategy.cycle_number} completed with WIN")
                else:
                    stats['losses'] += 1
                    bot.current_balance -= pending_bet['bet_amount']
                    result = "loss"
                    bot.losing_rounds += 1
                    print(f"  ❌ LOSS! -{pending_bet['bet_amount']:.2f} (Balance: {bot.current_balance:.2f})")
                    
                    # Check if max gale reached
                    if isinstance(bot.strategy, EvenOddStrategy):
                        if bot.strategy.gale_step >= bot.strategy.max_gales:
                            stats['cycles_completed'] += 1
                            stats['cycles_lost'] += 1
                            stats['max_gale_reached'] += 1
                            print(f"  ⚠️  Cycle {bot.strategy.cycle_number} ended: Max gale reached")
                
                # Update strategy
                bet_result_data = {
                    'result': result,
                    'bet_amount': pending_bet['bet_amount'],
                    'balance_after': bot.current_balance
                }
                bot.strategy.update_after_bet(bet_result_data)
                
                # Update bot state
                spin_result = {
                    'spin_number': bot.spin_number,
                    'result': {'number': result_number},
                    'spin_data': {
                        'bet_amount': pending_bet['bet_amount'],
                        'bet_color': bet_type,
                        'outcome_number': result_number
                    },
                    'bet_decision': pending_bet
                }
                bot.update_after_round(spin_result, result_number)
                
                pending_bet = None
                last_detection_frame = frame_count
        
        # Detect new result (pass frame directly to detector)
        detection = bot.detector.detect_result(frame)
        
        # Only process if we got a valid number
        if detection and detection.get('number') is not None:
            detected_number = detection.get('number')
            
            # Skip if same number as last detection (number still on screen - normal in video)
            if detected_number == last_detected_number:
                continue
            
            # Validate result (only validate when number changes)
            if not bot.detector.validate_result(detection):
                # Validation failed - skip this detection
                stats['detection_failures'] += 1
                stats['consecutive_failures'] += 1
                continue
            
            # Valid new detection
            stats['successful_detections'] += 1
            stats['consecutive_failures'] = 0
            last_detection_frame = frame_count
            last_detected_number = detected_number
            
            number = detected_number
            stats['numbers_detected'].append(number)
            
            # Track detection method
            method = detection.get('method', 'unknown')
            stats['detection_methods'][method] = stats['detection_methods'].get(method, 0) + 1
            
            stats['total_spins'] += 1
            
            # Get strategy info for display
            if isinstance(bot.strategy, EvenOddStrategy):
                even_streak = bot.strategy.current_even_streak
                odd_streak = bot.strategy.current_odd_streak
                in_cycle = bot.strategy.cycle_active
                cycle_num = bot.strategy.cycle_number if in_cycle else None
                gale_step = bot.strategy.gale_step
                
                stats['streak_history'].append({
                    'spin': stats['total_spins'],
                    'number': number,
                    'even_streak': even_streak,
                    'odd_streak': odd_streak
                })
                
                print(f"\n🎲 Spin #{stats['total_spins']}: {number} | Even: {even_streak} | Odd: {odd_streak}", end="")
                if in_cycle:
                    print(f" | Cycle: {cycle_num} | Gale: {gale_step}", end="")
                print()
            else:
                print(f"\n🎲 Spin #{stats['total_spins']}: {number}")
            
            # Process spin (calculate bet decision)
            spin_result = bot.process_spin(detection)
            
            # Check if bet was placed
            bet_decision = spin_result.get('bet_decision')
            if bet_decision:
                bet_amount = bet_decision.get('bet_amount', 0)
                bet_type = bet_decision.get('bet_type')
                is_keepalive = bet_decision.get('is_keepalive', False)
                
                if is_keepalive:
                    stats['keepalive_bets'] += 1
                    print(f"  💓 Keepalive bet: {bet_amount:.2f} on {bet_type}")
                else:
                    stats['bets_placed'] += 1
                    print(f"  💰 Bet placed: {bet_amount:.2f} on {bet_type}")
                
                # Store as pending (will be resolved on next detection)
                pending_bet = {
                    'bet_type': bet_type,
                    'bet_amount': bet_amount,
                    'is_keepalive': is_keepalive
                }
        else:
            stats['detection_failures'] += 1
            stats['consecutive_failures'] += 1
            
            # Only print failures occasionally to avoid spam
            if stats['consecutive_failures'] % 50 == 0:
                print(f"  ⚠️  Detection failures: {stats['consecutive_failures']}")

except KeyboardInterrupt:
    print("\n\n⚠️  Test interrupted by user")
except Exception as e:
    print(f"\n\n❌ Error during test: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# RESULTS SUMMARY
# ============================================================================

print("\n" + "="*80)
print("TEST RESULTS SUMMARY")
print("="*80)

# Calculate statistics
win_rate = (stats['wins'] / (stats['wins'] + stats['losses']) * 100) if (stats['wins'] + stats['losses']) > 0 else 0
balance_change = bot.current_balance - bot.initial_balance
roi = (balance_change / bot.initial_balance * 100) if bot.initial_balance > 0 else 0

print(f"\n📊 Detection Statistics:")
print(f"   Total frames processed: {stats['total_frames_processed']}")
print(f"   Total spins detected: {stats['total_spins']}")
print(f"   Successful detections: {stats['successful_detections']}")
print(f"   Detection failures: {stats['detection_failures']}")
if stats['total_frames_processed'] > 0:
    detection_rate = (stats['successful_detections'] / stats['total_frames_processed'] * 100)
    print(f"   Detection success rate: {detection_rate:.1f}%")

print(f"\n💰 Betting Statistics:")
print(f"   Bets placed: {stats['bets_placed']}")
print(f"   Keepalive bets: {stats['keepalive_bets']}")
print(f"   Wins: {stats['wins']} | Losses: {stats['losses']}")
if (stats['wins'] + stats['losses']) > 0:
    print(f"   Win rate: {win_rate:.2f}%")
else:
    print("   Win rate: N/A (no bets placed)")

print(f"\n💵 Balance:")
print(f"   Initial balance: {bot.initial_balance:.2f}")
print(f"   Final balance: {bot.current_balance:.2f}")
print(f"   Balance change: {balance_change:+.2f}")
if bot.initial_balance > 0:
    print(f"   ROI: {roi:+.2f}%")

print(f"\n🔄 Cycle Statistics:")
print(f"   Total cycles: {stats['cycles_completed']}")
print(f"   Cycles won: {stats['cycles_won']}")
print(f"   Cycles lost: {stats['cycles_lost']}")
print(f"   Max gale reached: {stats['max_gale_reached']}")

print(f"\n🎲 Other:")
print(f"   Zeros detected: {stats['zeros']}")
print(f"   Unique numbers detected: {len(set(stats['numbers_detected']))}")

print(f"\n🔍 Detection Methods:")
for method, count in stats['detection_methods'].items():
    print(f"   - {method}: {count}")

# Strategy state
if isinstance(bot.strategy, EvenOddStrategy):
    print(f"\n📈 Final Strategy State:")
    print(f"   Even streak: {bot.strategy.current_even_streak}")
    print(f"   Odd streak: {bot.strategy.current_odd_streak}")
    print(f"   Cycle active: {bot.strategy.cycle_active}")
    print(f"   Cycle number: {bot.strategy.cycle_number}")
    print(f"   Gale step: {bot.strategy.gale_step}")

# Stop condition info
if bot.stop_trigger_info:
    print(f"\n🛑 Stop Condition:")
    print(f"   Type: {bot.stop_trigger_info['type']}")
    print(f"   Value: {bot.stop_trigger_info['value']}")
    print(f"   Threshold: {bot.stop_trigger_info['threshold']}")

print("\n" + "="*80)

# ============================================================================
# EXPORT RESULTS
# ============================================================================

# Save results to JSON
results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
results_data = {
    'test_info': {
        'video_file': video_file,
        'config_path': config_path,
        'start_seconds': START_SECONDS,
        'start_frame': START_FRAME,
        'max_spins': MAX_SPINS,
        'timestamp': datetime.now().isoformat()
    },
    'statistics': stats,
    'balance': {
        'initial': bot.initial_balance,
        'final': bot.current_balance,
        'change': balance_change,
        'roi_percent': roi
    },
    'strategy_state': {
        'type': bot.strategy.strategy_type,
        'even_streak': getattr(bot.strategy, 'current_even_streak', None),
        'odd_streak': getattr(bot.strategy, 'current_odd_streak', None),
        'cycle_active': getattr(bot.strategy, 'cycle_active', None),
        'cycle_number': getattr(bot.strategy, 'cycle_number', None),
        'gale_step': bot.strategy.gale_step
    },
    'stop_condition': bot.stop_trigger_info,
    'numbers_detected': stats['numbers_detected'],
    'streak_history': stats['streak_history']
}

with open(results_file, 'w') as f:
    json.dump(results_data, f, indent=2)

print(f"\n💾 Results saved to: {results_file}")

# Get session summary from logger
if hasattr(bot, 'logger'):
    summary_file = bot.logger.export_summary(stop_triggers=bot.stop_trigger_info)
    print(f"💾 Session summary saved to: {summary_file}")

print("\n✅ Test completed!")
```

---

## 📊 Understanding the Results

### Detection Statistics
- **Total frames processed**: Number of video frames analyzed
- **Successful detections**: Number of times a number was successfully detected
- **Detection success rate**: Percentage of successful detections

### Betting Statistics
- **Bets placed**: Number of strategy bets (excluding keepalive)
- **Keepalive bets**: Number of keepalive bets placed (every 29 minutes when idle)
- **Win rate**: Percentage of winning bets

### Cycle Statistics
- **Total cycles**: Number of complete betting cycles
- **Cycles won**: Cycles that ended with a win
- **Cycles lost**: Cycles that ended after max gale reached
- **Max gale reached**: Number of times maximum gale limit was hit

### Balance Information
- **Initial/Final balance**: Starting and ending balance
- **Balance change**: Net profit/loss
- **ROI**: Return on investment percentage

---

## 🔧 Configuration Options

You can modify these parameters at the top of the script:

```python
START_SECONDS = 30.0  # Start from this time in seconds (e.g., 30.0, 60.5, 120.0)
MAX_SPINS = 100  # Maximum spins to test (None = unlimited)
FRAME_SKIP = 1  # Process every Nth frame (1 = all frames)
MAX_DETECTION_FAILURES = 200  # Stop after this many failures
```

### Start Time Examples:
- `START_SECONDS = 0.0` - Start from beginning of video
- `START_SECONDS = 30.0` - Start from 30 seconds
- `START_SECONDS = 60.5` - Start from 1 minute 0.5 seconds
- `START_SECONDS = 120.0` - Start from 2 minutes

**Note:** The script automatically calculates the frame number from seconds based on video FPS.

---

## 📝 Notes

1. **pyautogui is mocked**: Since Colab has no GUI, betting actions are simulated
2. **Video file required**: Make sure to upload your video file before running
3. **Config file**: Ensure `config/default_config.json` exists and is properly configured
4. **Results saved**: Test results are automatically saved to JSON files
5. **Session summary**: Includes all logging fields (cycles, streaks, keepalive, stop triggers)

---

## 🐛 Troubleshooting

### "No video file found"
- Upload your video file using the Files sidebar or code upload

### "Config file not found"
- Make sure you uploaded the entire project folder including the `config` directory

### "Module not found"
- Ensure all project files are uploaded correctly
- Check that the project structure is intact

### Low detection rate
- Adjust `START_SECONDS` to where the game actually starts (in seconds, not frames)
- Check that `screen_region` in config matches your video
- Verify templates are loaded correctly
- Try different start times to find where the game is most active

---

## ✅ Features Tested

This script tests all implemented features:
- ✅ Even/Odd counter-sequence strategy
- ✅ Streak detection and entry conditions
- ✅ Gale progression (2x multiplier)
- ✅ Cycle management (no concurrent cycles)
- ✅ StopLoss/StopWin (by count and money)
- ✅ Keepalive system (29 minutes, random Even/Odd)
- ✅ Zero handling (configurable policy)
- ✅ Comprehensive logging (all fields)
- ✅ Session summary with stop triggers
- ✅ Bankroll pre-check calculation

---

**Ready to test!** Copy the complete script above into a Colab cell and run it. 🚀

