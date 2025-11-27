# Quick Start: Test Bot in Colab

## 🚀 Fast Setup (5 Minutes)

### Step 1: Open Colab
Go to: https://colab.research.google.com/  
Click **"New notebook"**

---

### Step 2: Install Dependencies
**Copy and paste this in a cell, then run:**

```python
!pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils -q
print(" Dependencies installed!")
```

---

### Step 3: Upload Files
**Option A: Use Files Sidebar (Easiest)**
1. Click 📁 icon in left sidebar
2. Click "Upload to session storage"
3. Upload your entire project folder
4. Upload your video file (`roleta_brazileria.mp4`)

**Option B: Upload via Code**
```python
from google.colab import files
import zipfile

# Upload project zip
print("📤 Upload project zip file:")
uploaded = files.upload()
zip_file = list(uploaded.keys())[0]
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall('.')
print(" Project extracted!")

# Upload video
print("📤 Upload video file:")
uploaded = files.upload()
video_file = list(uploaded.keys())[0]
print(f" Video: {video_file}")
```

---

### Step 4: Run Test
**Copy and paste this complete test code:**

```python
import sys
import os
import cv2
import json
from datetime import datetime
from pathlib import Path

#  IMPORTANT: Mock pyautogui for Colab
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

print(" pyautogui mocked for Colab")

# Add project to path
sys.path.insert(0, os.path.abspath('.'))

# Import project modules
from backend.app.config_loader import ConfigLoader
from backend.app.bot import RouletteBot
from backend.app.detection.frame_detector import FrameDetector

# Find video file
video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov'))]
if not video_files:
    print(" No video file found! Please upload a video file.")
else:
    video_file = video_files[0]
    print(f" Found video: {video_file}")
    
    # Load config
    config = ConfigLoader.load_config('config/default_config.json')
    
    # Check if strategy navigation is enabled
    nav_enabled = config.get('strategy_navigation', {}).get('enabled', False)
    print(f"Strategy Navigation: {'ENABLED' if nav_enabled else 'DISABLED'}")
    
    # Initialize bot
    bot = RouletteBot('config/default_config.json', test_mode=True)
    
    # Use frame detector for video
    frame_detector = FrameDetector(config, video_file)
    bot.detector = frame_detector
    
    # Run test
    print("\n" + "=" * 70)
    print("STARTING TEST")
    print("=" * 70)
    
    total_spins = 0
    bets_placed = 0
    wins = 0
    losses = 0
    pending_bet = None
    
    try:
        while total_spins < 50:  # Test 50 spins
            frame = frame_detector.capture_screen()
            if frame is None:
                break
            
            detection = bot.detector.detect_result(frame)
            if detection is None or detection.get('number') is None:
                continue
            
            current_number = detection.get('number')
            total_spins += 1
            
            # Process spin
            spin_result = bot.process_spin(detection)
            
            # Handle pending bet
            if pending_bet:
                bet_type = pending_bet['bet_type']
                is_even = (current_number % 2 == 0 and current_number != 0)
                is_odd = (current_number % 2 == 1)
                
                won = (bet_type == 'even' and is_even) or (bet_type == 'odd' and is_odd)
                
                if won:
                    wins += 1
                    bot.current_balance += pending_bet['bet_amount']
                else:
                    losses += 1
                    bot.current_balance -= pending_bet['bet_amount']
                
                # Update strategy
                if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
                    bot.strategy_manager.update_after_bet({
                        'result': 'win' if won else 'loss',
                        'bet_amount': pending_bet['bet_amount'],
                        'balance_after': bot.current_balance
                    })
                else:
                    bot.strategy.update_after_bet({
                        'result': 'win' if won else 'loss',
                        'bet_amount': pending_bet['bet_amount'],
                        'balance_after': bot.current_balance
                    })
                
                pending_bet = None
            
            # Check for new bet
            bet_decision = spin_result.get('bet_decision')
            if bet_decision:
                bets_placed += 1
                pending_bet = {
                    'bet_type': bet_decision.get('bet_type'),
                    'bet_amount': bet_decision.get('bet_amount', 0.0)
                }
                
                # Show strategy info if navigation enabled
                if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
                    print(f"[Spin {total_spins}] Strategy: {bot.strategy_manager.current_strategy_name}, "
                          f"Bet: {bet_decision.get('bet_type')} - {bet_decision.get('bet_amount')}")
                else:
                    print(f"[Spin {total_spins}] Bet: {bet_decision.get('bet_type')} - {bet_decision.get('bet_amount')}")
    
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        frame_detector.release()
    
    # Print results
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Total spins: {total_spins}")
    print(f"Bets placed: {bets_placed}")
    print(f"Wins: {wins} | Losses: {losses}")
    print(f"Win rate: {(wins/(wins+losses)*100) if (wins+losses) > 0 else 0:.2f}%")
    print(f"Final balance: {bot.current_balance:.2f}")
    
    # Show strategy navigation performance
    if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
        print("\nStrategy Performance:")
        all_perf = bot.strategy_manager.get_all_performance()
        for name, perf in all_perf.items():
            print(f"  {name}: {perf['total_bets']} bets, "
                  f"WR: {perf['win_rate']:.1f}%, "
                  f"Net: {perf['net_profit']:.2f}, "
                  f"Score: {perf['score']:.3f}")
    
    print("=" * 70)
```

---

##  That's It!

The test will:
-  Load your bot configuration
-  Test with your video file
-  Show strategy navigation info (if enabled)
-  Display results and statistics

**For detailed testing, see:** `COLAB_STRATEGY_TEST.md`
