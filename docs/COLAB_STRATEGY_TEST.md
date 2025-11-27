# How to Test Strategy in Google Colab

##  Overview

This guide shows you how to test the **Even/Odd strategy** logic in Google Colab using a video file. You'll be able to:
- Test streak detection (waiting for 5 consecutive Even/Odd)
- See bet decisions (when to bet Even or Odd)
- Track gale progression (betting after losses)
- Analyze win/loss outcomes
- Get statistics and performance metrics

---

## 🚀 Quick Start (Using Your Uploaded Project)

### Step 1: Open Google Colab
1. Go to: https://colab.research.google.com/
2. Click **"New notebook"**
3. Name it: "Roulette Strategy Test"

---

### Step 2: Install Dependencies
**Copy and run this in a cell:**

```python
!pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils -q
print(" Dependencies installed!")
```

---

### Step 3: Upload Project Files
**If you haven't uploaded the project yet, use this:**

```python
from google.colab import files
import zipfile
import os

# Upload project zip file (or use Files sidebar to upload)
print("📤 Upload your project zip file (or use Files sidebar):")
print("   Option 1: Upload zip file here")
print("   Option 2: Use Files sidebar (📁 icon) to upload individual files/folders")

# If you uploaded a zip file:
# uploaded = files.upload()
# zip_file = list(uploaded.keys())[0]
# with zipfile.ZipFile(zip_file, 'r') as zip_ref:
#     zip_ref.extractall('.')
# print(" Project extracted!")
```

**OR use the Files sidebar:**
1. Click the 📁 icon in the left sidebar
2. Click "Upload to session storage"
3. Upload your project files/folders

---

### Step 4: Upload Video File
**Copy and run this:**

```python
from google.colab import files

print("📤 Upload your video file (roleta_brazileria.mp4 or similar):")
uploaded = files.upload()
video_file = list(uploaded.keys())[0] if uploaded else None
print(f" Video file: {video_file}")
```

**Then upload your video file when prompted.**

---

### Step 5: Setup Path & Import Project
**Copy and run this (uses your existing project files):**

```python
import sys
import os
from pathlib import Path

#  IMPORTANT: Mock pyautogui for Colab (headless environment)
# Since we're only testing strategy logic, we don't need actual mouse automation
from unittest.mock import MagicMock

# Mock pyautogui before any imports that use it
sys.modules['pyautogui'] = MagicMock()
mock_pyautogui = sys.modules['pyautogui']
mock_pyautogui.screenshot = MagicMock(return_value=None)
mock_pyautogui.moveTo = MagicMock()
mock_pyautogui.click = MagicMock()
mock_pyautogui.write = MagicMock()
mock_pyautogui.press = MagicMock()
mock_pyautogui.PAUSE = 0.1
mock_pyautogui.FAILSAFE = False

print(" pyautogui mocked for Colab (no actual mouse automation needed)")

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

# Verify project structure
print("📁 Checking project structure...")
required_files = [
    'backend/app/detection/screen_detector.py',
    'backend/app/strategy/even_odd_strategy.py',
    'backend/app/detection/frame_detector.py',
    'config/default_config.json',
    'simulate_strategy.py'
]

missing = []
for file in required_files:
    if os.path.exists(file):
        print(f"   {file}")
    else:
        print(f"   {file} - MISSING")
        missing.append(file)

if missing:
    print(f"\n  Missing files: {missing}")
    print("   Make sure you uploaded the complete project!")
else:
    print("\n All required files found!")

# Load config
import json
with open('config/default_config.json', 'r') as f:
    config = json.load(f)
print(f"\n Config loaded: Strategy = {config.get('strategy', {}).get('type', 'N/A')}")
```

---

### Step 6: Run Strategy Test (Using Your Project Code)
**Copy and run this (uses your existing `simulate_strategy.py` logic):**

```python
import cv2
import sys
import os
from datetime import datetime
from pathlib import Path

#  IMPORTANT: Make sure pyautogui is mocked (should be done in Step 5)
# If you skipped Step 5, uncomment this:
# from unittest.mock import MagicMock
# sys.modules['pyautogui'] = MagicMock()

# Import from your project
from backend.app.config_loader import ConfigLoader
from backend.app.bot import RouletteBot
from backend.app.detection.frame_detector import FrameDetector

def test_strategy_colab(video_path, config_path='config/default_config.json', 
                        frame_skip=5, max_spins=None, verbose=True):
    """Test Even/Odd strategy using your project's code."""
    
    # Load configuration
    config = ConfigLoader.load_config(config_path)
    
    # Initialize bot in test mode
    bot = RouletteBot(config_path, test_mode=True)
    
    # Replace detector with frame detector for video
    frame_detector = FrameDetector(config, video_path)
    bot.detector = frame_detector
    
    # Open video to get info
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f" Error: Could not open video {video_path}")
        return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    if verbose:
        print("=" * 70)
        print("STRATEGY TEST STARTED")
        print("=" * 70)
        print(f"Video: {video_path}")
        
        # Check if strategy navigation is enabled
        if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
            print(f"Strategy Navigation: ENABLED")
            print(f"Current Strategy: {bot.strategy_manager.current_strategy_name}")
            print(f"Available Strategies: {', '.join(bot.strategy_manager.strategies.keys())}")
        else:
            print(f"Strategy Navigation: DISABLED")
            print(f"Strategy: {bot.strategy.strategy_type}")
        
        print(f"Base bet: {config.get('strategy', {}).get('base_bet', 10.0)}")
        print(f"Streak length: {config.get('strategy', {}).get('streak_length', 5)}")
        print(f"Max gales: {config.get('strategy', {}).get('max_gales', 5)}")
        print(f"Processing every {frame_skip} frame(s)...")
        if max_spins:
            print(f"Limiting to {max_spins} spins")
        print("-" * 70)
    
    # Statistics
    total_spins = 0
    successful_detections = 0
    bets_placed = 0
    last_detected_number = None
    consecutive_no_detection = 0
    results = []
    
    # Track pending bets (bet placed but outcome not yet known)
    pending_bet = None  # {bet_type, bet_amount, gale_step, spin_number}
    wins = 0
    losses = 0
    total_profit = 0.0
    total_loss = 0.0
    
    try:
        while True:
            # Check max spins limit
            if max_spins and total_spins >= max_spins:
                if verbose:
                    print(f"\n Reached maximum spins limit: {max_spins}")
                break
            
            # Capture frame
            frame = frame_detector.capture_screen()
            if frame is None:
                if verbose:
                    print("\n End of video reached.")
                break
            
            # Detect result
            detection = bot.detector.detect_result(frame)
            
            if detection is None or detection.get('number') is None:
                consecutive_no_detection += 1
                if consecutive_no_detection > 10 and verbose:
                    print(".", end="", flush=True)
                continue
            
            # Reset consecutive no-detection counter
            consecutive_no_detection = 0
            
            # Check if this is a new result
            current_number = detection.get('number')
            if current_number == last_detected_number:
                continue
            
            last_detected_number = current_number
            total_spins += 1
            successful_detections += 1
            
            # Get strategy state before processing
            strategy = bot.strategy
            # Update strategy reference if navigation is enabled
            if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
                strategy = bot.strategy_manager.get_current_strategy()
                bot.strategy = strategy  # Keep reference updated
            
            # Get strategy-specific state (for even_odd strategy)
            even_streak = getattr(strategy, 'current_even_streak', 0)
            odd_streak = getattr(strategy, 'current_odd_streak', 0)
            in_cycle = getattr(strategy, 'cycle_active', False)
            gale_step = strategy.gale_step
            
            if verbose:
                even_odd_str = "EVEN" if current_number % 2 == 0 and current_number != 0 else "ODD" if current_number % 2 == 1 else "ZERO"
                print(f"\n[Spin {total_spins}] Number: {current_number} ({even_odd_str})")
                print(f"   Even streak: {even_streak}, Odd streak: {odd_streak}")
            
            #  CRITICAL FIX: Check if pending bet won/lost BEFORE processing new result
            bet_outcome = None
            if pending_bet:
                # Determine if pending bet won or lost
                bet_type = pending_bet['bet_type']
                bet_amount = pending_bet['bet_amount']
                is_even = (current_number % 2 == 0 and current_number != 0)
                is_odd = (current_number % 2 == 1)
                is_zero = (current_number == 0)
                
                won = False
                if bet_type == 'even' and is_even:
                    won = True
                elif bet_type == 'odd' and is_odd:
                    won = True
                elif is_zero:
                    # Handle zero according to policy
                    if strategy.zero_policy == 'count_as_loss':
                        won = False
                    elif strategy.zero_policy == 'count_as_win':
                        won = True
                    elif strategy.zero_policy == 'reset':
                        # Reset cycle, don't count as win/loss
                        strategy.cycle_active = False
                        strategy.gale_step = 0
                        pending_bet = None
                        if verbose:
                            print(f"    ZERO detected - Cycle reset (zero_policy: reset)")
                        # Continue to process this result normally
                        bet_outcome = None
                
                if bet_outcome is None and pending_bet:  # Not reset by zero
                    # Process win/loss
                    if won:
                        bet_outcome = 'win'
                        profit = bet_amount
                        bot.current_balance += profit
                        total_profit += profit
                        wins += 1
                        if verbose:
                            print(f"  🎉 WIN! Bet {bet_type.upper()} won. Profit: +{profit:.2f}")
                    else:
                        bet_outcome = 'loss'
                        loss = bet_amount
                        bot.current_balance -= loss
                        total_loss += loss
                        losses += 1
                        if verbose:
                            print(f"   LOSS! Bet {bet_type.upper()} lost. Loss: -{loss:.2f}")
                    
                    # Update strategy after bet outcome (use strategy manager if enabled)
                    bet_result_data = {
                        'result': bet_outcome,
                        'bet_type': bet_type,
                        'bet_amount': bet_amount,
                        'gale_step': pending_bet['gale_step'],
                        'balance_after': bot.current_balance,
                        'cycle_ended': False
                    }
                    
                    if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
                        bot.strategy_manager.update_after_bet(bet_result_data)
                        strategy = bot.strategy_manager.get_current_strategy()
                        bot.strategy = strategy  # Update reference
                    else:
                        strategy.update_after_bet(bet_result_data)
                    
                    # Check if cycle ended
                    if not getattr(strategy, 'cycle_active', False):
                        if verbose:
                            if bet_outcome == 'win':
                                print(f"   Cycle {pending_bet.get('cycle_number', '?')} ended: WIN")
                            else:
                                print(f"    Cycle {pending_bet.get('cycle_number', '?')} ended: MAX GALE")
                    
                    # Clear pending bet
                    pending_bet = None
            
            # Now process the new result for strategy decisions
            try:
                spin_result = bot.process_spin(detection)
                
                   # Check if bet was placed
                   bet_decision = spin_result.get('bet_decision')
                   if bet_decision:
                       bets_placed += 1
                       bet_type = bet_decision.get('bet_type')
                       bet_amount = bet_decision.get('bet_amount', 0.0)
                       
                       # Check for strategy switch (if navigation enabled)
                       if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
                           current_strategy_name = bot.strategy_manager.current_strategy_name
                           if verbose and bet_decision.get('strategy') != current_strategy_name:
                               print(f"  🔄 Strategy: {current_strategy_name}")
                       
                       # Store as pending bet (will be resolved on next result)
                       pending_bet = {
                           'bet_type': bet_type,
                           'bet_amount': bet_amount,
                           'gale_step': bet_decision.get('gale_step', 0),
                           'cycle_number': bet_decision.get('cycle_number', 0),
                           'spin_number': total_spins
                       }
                       
                       if verbose:
                           if bet_decision.get('reason', '').startswith('Entry'):
                               print(f"   ENTRY! Betting {bet_type.upper()} - {bet_amount} (Gale step: {gale_step})")
                           else:
                               print(f"  📊 BET: {bet_type.upper()} - {bet_amount} (Gale step: {gale_step})")
                
                # Store result
                results.append({
                    "spin": total_spins,
                    "number": current_number,
                    "even_streak": even_streak,
                    "odd_streak": odd_streak,
                    "bet_decision": bet_decision,
                    "bet_outcome": bet_outcome,  # 'win', 'loss', or None
                    "in_cycle": strategy.cycle_active,  # Use updated state
                    "gale_step": strategy.gale_step,  # Use updated state
                    "balance": bot.current_balance
                })
                
            except Exception as e:
                if verbose:
                    print(f"    Error processing spin: {e}")
                import traceback
                traceback.print_exc()
                continue
            
            # Check stop conditions
            if bot.check_stop_conditions():
                if verbose:
                    print("\n  Stop conditions met (stop loss or max gale reached)")
                break
        
        # Calculate final statistics
        win_rate = (wins / bets_placed * 100) if bets_placed > 0 else 0
        net_profit = total_profit - total_loss
        balance_change = bot.current_balance - bot.config.get('risk', {}).get('initial_balance', 1000.0)
        
        stats = {
            "total_spins": total_spins,
            "total_bets": bets_placed,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "total_loss": total_loss,
            "net_profit": net_profit,
            "initial_balance": bot.config.get('risk', {}).get('initial_balance', 1000.0),
            "final_balance": bot.current_balance,
            "balance_change": balance_change
        }
        
        # Save results
        import json
        os.makedirs('test_results', exist_ok=True)
        output_file = f"test_results/strategy_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "video_path": video_path,
                "config": config,
                "total_frames": total_frames,
                "processed_spins": total_spins,
                "successful_detections": successful_detections,
                "bets_placed": bets_placed,
                "statistics": stats,
                "results": results,
                "final_balance": bot.current_balance,
                "strategy_state": {
                    "even_streak": strategy.current_even_streak,
                    "odd_streak": strategy.current_odd_streak,
                    "in_cycle": strategy.cycle_active,
                    "gale_step": strategy.gale_step
                }
            }, f, indent=2)
        
               if verbose:
                   print("\n" + "=" * 70)
                   print("STRATEGY TEST SUMMARY")
                   print("=" * 70)
                   print(f"Total spins processed: {total_spins}")
                   print(f"Successful detections: {successful_detections}")
                   print(f"Bets placed: {bets_placed}")
                   print(f"Wins: {wins} | Losses: {losses}")
                   print(f"Win rate: {win_rate:.2f}%")
                   print(f"Total profit: {total_profit:.2f}")
                   print(f"Total loss: {total_loss:.2f}")
                   print(f"Net profit: {net_profit:.2f}")
                   print(f"Initial balance: {stats['initial_balance']:.2f}")
                   print(f"Final balance: {bot.current_balance:.2f}")
                   print(f"Balance change: {balance_change:.2f}")
                   
                   # Show strategy navigation info if enabled
                   if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
                       print(f"\nStrategy Navigation:")
                       print(f"  Current Strategy: {bot.strategy_manager.current_strategy_name}")
                       all_perf = bot.strategy_manager.get_all_performance()
                       for name, perf in all_perf.items():
                           print(f"  {name}: {perf['total_bets']} bets, "
                                 f"WR: {perf['win_rate']:.1f}%, "
                                 f"Score: {perf['score']:.3f}")
                   else:
                       # Show single strategy state
                       print(f"Even streak: {getattr(strategy, 'current_even_streak', 0)}")
                       print(f"Odd streak: {getattr(strategy, 'current_odd_streak', 0)}")
                       print(f"In cycle: {getattr(strategy, 'cycle_active', False)}")
                       print(f"Gale step: {strategy.gale_step}")
                   
                   print(f"Results saved to: {output_file}")
                   print("=" * 70)
        
        return {
            "results": results,
            "statistics": stats,
            "output_file": output_file,
            "bot": bot
        }
    
    except KeyboardInterrupt:
        if verbose:
            print("\n\n  Test stopped by user")
    except Exception as e:
        print(f"\n Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        frame_detector.release()
        if verbose:
            print("\n Test completed.")

# Run test
if video_file:
    test_results = test_strategy_colab(
        video_file,
        config_path='config/default_config.json',
        frame_skip=5,      # Process every 5th frame (1 = all frames)
        max_spins=50,      # Limit to 50 spins for quick test (None = all)
        verbose=True
    )
else:
    print(" Please upload a video file first!")
```

---

## Alternative: Use Your Existing `simulate_strategy.py`

**If you prefer to use your existing script directly, you can adapt it:**

```python
# Since simulate_strategy.py uses argparse, we'll call it via subprocess
# OR import and call the function directly

import sys
import subprocess

# Option 1: Run via subprocess (if video is uploaded)
if video_file:
    result = subprocess.run([
        'python', 'simulate_strategy.py', 
        video_file,
        '--config', 'config/default_config.json',
        '--max-spins', '50',
        '--delay', '0.1'
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
```

**OR import directly:**

```python
# Option 2: Import and call function directly
#  IMPORTANT: Mock pyautogui first (if not done in Step 5)
from unittest.mock import MagicMock
import sys
if 'pyautogui' not in sys.modules or not isinstance(sys.modules.get('pyautogui'), MagicMock):
    sys.modules['pyautogui'] = MagicMock()
    mock_pyautogui = sys.modules['pyautogui']
    mock_pyautogui.screenshot = MagicMock(return_value=None)
    mock_pyautogui.moveTo = MagicMock()
    mock_pyautogui.click = MagicMock()
    mock_pyautogui.write = MagicMock()
    mock_pyautogui.press = MagicMock()

from simulate_strategy import simulate_strategy

if video_file:
    simulate_strategy(
        video_file,
        'config/default_config.json',
        max_spins=50,
        delay_between_spins=0.1,
        verbose=True
    )
```

---

## 📊 Understanding the Results
    def __init__(self, config):
        self.config = config
    
    def get_color_from_number(self, number):
        if number == 0:
            return "green"
        red_numbers = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
        black_numbers = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
        if number in red_numbers:
            return "red"
        elif number in black_numbers:
            return "black"
        return "green"
    
    def is_even(self, number):
        return number != 0 and number % 2 == 0
    
    def is_odd(self, number):
        return number != 0 and number % 2 == 1
    
    def detect_number_ocr(self, frame, region=None):
        try:
            if region:
                x, y, w, h = region
                roi = frame[y:y+h, x:x+w]
            else:
                roi = frame
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            custom_config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"
            text = pytesseract.image_to_string(thresh, config=custom_config)
            for char in text.strip():
                if char.isdigit():
                    number = int(char)
                    if 0 <= number <= 36:
                        return number
            return None
        except:
            return None
    
    def detect_result(self, frame=None):
        result = {"number": None, "color": None, "zero": False, "confidence": 0.0, "method": None}
        number = self.detect_number_ocr(frame)
        if number is not None:
            result["number"] = number
            result["color"] = self.get_color_from_number(number)
            result["zero"] = (number == 0)
            result["confidence"] = 0.7
            result["method"] = "ocr"
        return result
'''

# Create Even/Odd Strategy
strategy_code = '''
class EvenOddStrategy:
    def __init__(self, config):
        self.config = config
        strategy_config = config.get("strategy", {})
        self.base_bet = strategy_config.get("base_bet", 10.0)
        self.max_gales = strategy_config.get("max_gales", 5)
        self.multiplier = strategy_config.get("multiplier", 2.0)
        self.streak_length = strategy_config.get("streak_length", 5)
        self.zero_policy = strategy_config.get("zero_policy", "count_as_loss")
        
        # State
        self.even_streak = 0
        self.odd_streak = 0
        self.gale_step = 0
        self.in_cycle = False
        self.current_bet_type = None  # "even" or "odd"
        self.result_history = []
        self.bet_history = []
        self.balance = config.get("risk", {}).get("initial_balance", 1000.0)
        self.initial_balance = self.balance
        
    def is_even(self, number):
        return number != 0 and number % 2 == 0
    
    def is_odd(self, number):
        return number != 0 and number % 2 == 1
    
    def process_result(self, number):
        """Process a new result and return bet decision if any."""
        if number is None:
            return None
        
        is_even_num = self.is_even(number)
        is_odd_num = self.is_odd(number)
        is_zero = (number == 0)
        
        # Update streaks
        if is_even_num:
            self.even_streak += 1
            self.odd_streak = 0
        elif is_odd_num:
            self.odd_streak += 1
            self.even_streak = 0
        elif is_zero:
            # Zero resets streaks
            self.even_streak = 0
            self.odd_streak = 0
        
        # Store result
        self.result_history.append({
            "number": number,
            "is_even": is_even_num,
            "is_odd": is_odd_num,
            "is_zero": is_zero,
            "even_streak": self.even_streak,
            "odd_streak": self.odd_streak
        })
        
        # If in cycle, check win/loss
        if self.in_cycle:
            won = False
            if self.current_bet_type == "even" and is_even_num:
                won = True
            elif self.current_bet_type == "odd" and is_odd_num:
                won = True
            
            # Handle zero
            if is_zero:
                if self.zero_policy == "count_as_loss":
                    won = False
                elif self.zero_policy == "count_as_win":
                    won = True
                elif self.zero_policy == "reset":
                    self.in_cycle = False
                    self.gale_step = 0
                    self.current_bet_type = None
                    return None
            
            # Calculate bet amount for this gale step
            bet_amount = self.base_bet * (self.multiplier ** self.gale_step)
            
            if won:
                # Win - cycle ends
                profit = bet_amount
                self.balance += profit
                self.bet_history.append({
                    "type": "win",
                    "bet_type": self.current_bet_type,
                    "bet_amount": bet_amount,
                    "gale_step": self.gale_step,
                    "result": number,
                    "profit": profit,
                    "balance_after": self.balance
                })
                self.in_cycle = False
                self.gale_step = 0
                self.current_bet_type = None
                return {
                    "action": "cycle_complete",
                    "result": "win",
                    "bet_type": self.current_bet_type,
                    "bet_amount": bet_amount,
                    "gale_step": self.gale_step,
                    "profit": profit
                }
            else:
                # Loss - continue gale
                loss = bet_amount
                self.balance -= loss
                self.bet_history.append({
                    "type": "loss",
                    "bet_type": self.current_bet_type,
                    "bet_amount": bet_amount,
                    "gale_step": self.gale_step,
                    "result": number,
                    "loss": loss,
                    "balance_after": self.balance
                })
                
                self.gale_step += 1
                
                # Check max gale
                if self.gale_step >= self.max_gales:
                    # Max gale reached - cycle ends with loss
                    self.in_cycle = False
                    self.gale_step = 0
                    self.current_bet_type = None
                    return {
                        "action": "cycle_complete",
                        "result": "max_gale_reached",
                        "bet_type": self.current_bet_type,
                        "bet_amount": bet_amount,
                        "gale_step": self.gale_step,
                        "loss": loss
                    }
                else:
                    # Continue gale
                    next_bet_amount = self.base_bet * (self.multiplier ** self.gale_step)
                    return {
                        "action": "gale_progression",
                        "bet_type": self.current_bet_type,
                        "bet_amount": next_bet_amount,
                        "gale_step": self.gale_step,
                        "previous_loss": loss
                    }
        
        # Check entry condition
        if not self.in_cycle:
            if self.even_streak >= self.streak_length:
                # Enter cycle - bet ODD
                self.in_cycle = True
                self.gale_step = 0
                self.current_bet_type = "odd"
                bet_amount = self.base_bet
                return {
                    "action": "entry",
                    "bet_type": "odd",
                    "bet_amount": bet_amount,
                    "gale_step": 0,
                    "reason": f"Even streak: {self.even_streak}"
                }
            elif self.odd_streak >= self.streak_length:
                # Enter cycle - bet EVEN
                self.in_cycle = True
                self.gale_step = 0
                self.current_bet_type = "even"
                bet_amount = self.base_bet
                return {
                    "action": "entry",
                    "bet_type": "even",
                    "bet_amount": bet_amount,
                    "gale_step": 0,
                    "reason": f"Odd streak: {self.odd_streak}"
                }
        
        return None
    
    def get_statistics(self):
        """Get strategy statistics."""
        total_bets = len(self.bet_history)
        wins = sum(1 for b in self.bet_history if b.get("type") == "win")
        losses = sum(1 for b in self.bet_history if b.get("type") == "loss")
        win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
        
        total_profit = sum(b.get("profit", 0) for b in self.bet_history)
        total_loss = sum(b.get("loss", 0) for b in self.bet_history)
        net_profit = total_profit - total_loss
        
        cycles = sum(1 for b in self.bet_history if b.get("type") == "win" or 
                    (b.get("type") == "loss" and b.get("gale_step", 0) == self.max_gales - 1))
        
        return {
            "total_spins": len(self.result_history),
            "total_bets": total_bets,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "total_loss": total_loss,
            "net_profit": net_profit,
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "balance_change": self.balance - self.initial_balance,
            "cycles_completed": cycles,
            "even_streak": self.even_streak,
            "odd_streak": self.odd_streak,
            "in_cycle": self.in_cycle
        }
'''

# Write files
with open('backend/app/detection/screen_detector.py', 'w') as f:
    f.write(detector_code)

with open('backend/app/strategy/even_odd_strategy.py', 'w') as f:
    f.write(strategy_code)

# Create __init__ files
with open('backend/app/__init__.py', 'w') as f:
    f.write('')
with open('backend/app/detection/__init__.py', 'w') as f:
    f.write('from .screen_detector import ScreenDetector')
with open('backend/app/strategy/__init__.py', 'w') as f:
    f.write('from .even_odd_strategy import EvenOddStrategy')

print(" Detector and Strategy code created!")
```

---

---
    """Test Even/Odd strategy on video file in Colab."""
    import sys
    sys.path.append('.')
    from backend.app.detection import ScreenDetector
    from backend.app.strategy import EvenOddStrategy
    
    # Initialize
    detector = ScreenDetector(config)
    strategy = EvenOddStrategy(config)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f" Error: Could not open video {video_path}")
        return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if verbose:
        print("=" * 70)
        print("STRATEGY TEST STARTED")
        print("=" * 70)
        print(f"Video: {video_path}")
        print(f"Strategy: Even/Odd (streak ≥ {strategy.streak_length})")
        print(f"Base bet: {strategy.base_bet}")
        print(f"Max gales: {strategy.max_gales}")
        print(f"Processing every {frame_skip} frame(s)...")
        if max_spins:
            print(f"Limiting to {max_spins} spins")
        print("-" * 70)
    
    results = []
    frame_count = 0
    processed_count = 0
    successful_detections = 0
    last_detected_number = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % frame_skip != 0:
            continue
        
        if max_spins and processed_count >= max_spins:
            break
        
        # Detect number
        detection = detector.detect_result(frame)
        number = detection.get('number')
        
        if number is None:
            continue
        
        # Avoid processing same number multiple times
        if number == last_detected_number:
            continue
        
        last_detected_number = number
        processed_count += 1
        successful_detections += 1
        
        # Process with strategy
        bet_decision = strategy.process_result(number)
        
        # Log result
        result_entry = {
            "spin": processed_count,
            "frame": frame_count,
            "number": number,
            "is_even": strategy.is_even(number),
            "is_odd": strategy.is_odd(number),
            "even_streak": strategy.even_streak,
            "odd_streak": strategy.odd_streak,
            "bet_decision": bet_decision,
            "in_cycle": strategy.in_cycle,
            "gale_step": strategy.gale_step,
            "balance": strategy.balance
        }
        results.append(result_entry)
        
        # Print output
        if verbose:
            even_odd_str = "EVEN" if strategy.is_even(number) else "ODD" if strategy.is_odd(number) else "ZERO"
            print(f"\n[Spin {processed_count}] Number: {number} ({even_odd_str})")
            print(f"   Even streak: {strategy.even_streak}, Odd streak: {strategy.odd_streak}")
            
            if bet_decision:
                action = bet_decision.get("action")
                if action == "entry":
                    print(f"   ENTRY! Betting {bet_decision.get('bet_type').upper()} with {bet_decision.get('bet_amount')}")
                    print(f"     Reason: {bet_decision.get('reason')}")
                elif action == "gale_progression":
                    print(f"    LOSS  Gale step {bet_decision.get('gale_step')}")
                    print(f"     Next bet: {bet_decision.get('bet_type').upper()} {bet_decision.get('bet_amount')}")
                elif action == "cycle_complete":
                    result_type = bet_decision.get("result")
                    if result_type == "win":
                        print(f"  🎉 WIN! Profit: +{bet_decision.get('profit')}")
                    else:
                        print(f"   MAX GALE REACHED. Loss: -{bet_decision.get('loss')}")
            
            if strategy.in_cycle:
                print(f"   Cycle active: {strategy.current_bet_type.upper()}, Gale step: {strategy.gale_step}")
    
    cap.release()
    
    # Get statistics
    stats = strategy.get_statistics()
    
    # Save results
    output_file = f"test_results/strategy_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "video_path": video_path,
            "config": config,
            "total_frames": total_frames,
            "processed_spins": processed_count,
            "successful_detections": successful_detections,
            "statistics": stats,
            "results": results
        }, f, indent=2)
    
    # Print summary
    if verbose:
        print("\n" + "=" * 70)
        print("STRATEGY TEST SUMMARY")
        print("=" * 70)
        print(f"Total spins processed: {stats['total_spins']}")
        print(f"Total bets placed: {stats['total_bets']}")
        print(f"Wins: {stats['wins']} | Losses: {stats['losses']}")
        print(f"Win rate: {stats['win_rate']:.2f}%")
        print(f"Total profit: {stats['total_profit']:.2f}")
        print(f"Total loss: {stats['total_loss']:.2f}")
        print(f"Net profit: {stats['net_profit']:.2f}")
        print(f"Initial balance: {stats['initial_balance']:.2f}")
        print(f"Current balance: {stats['current_balance']:.2f}")
        print(f"Balance change: {stats['balance_change']:.2f}")
        print(f"Cycles completed: {stats['cycles_completed']}")
        print(f"Results saved to: {output_file}")
        print("=" * 70)
    
    return {
        "results": results,
        "statistics": stats,
        "output_file": output_file
    }

# Run test
if video_file:
    test_results = test_strategy_colab(
        video_file,
        config,
        frame_skip=5,      # Process every 5th frame (1 = all frames)
        max_spins=50,      # Limit to 50 spins for quick test (None = all)
        verbose=True
    )
else:
    print(" Please upload a video file first!")
```

---

## 📊 Understanding the Results

### What You'll See:

1. **Spin-by-Spin Output:**
   ```
   [Spin 1] Number: 2 (EVEN)
      Even streak: 1, Odd streak: 0
   
   [Spin 5] Number: 10 (EVEN)
      Even streak: 5, Odd streak: 0
      ENTRY! Betting ODD with 10.0
        Reason: Even streak: 5
   
   [Spin 6] Number: 12 (EVEN)
       LOSS  Gale step 1
        Next bet: ODD 20.0
   ```

2. **Summary Statistics:**
   - Total spins processed
   - Total bets placed
   - Win/loss count and win rate
   - Profit/loss amounts
   - Balance changes
   - Cycles completed

### Key Metrics to Watch:

- **Win Rate**: Should be around 48-50% (theoretical for Even/Odd)
- **Net Profit**: Can be positive or negative (depends on variance)
- **Cycles Completed**: How many betting cycles finished
- **Balance Change**: Overall profit/loss

---

## ⚙️ Adjusting Test Parameters

### For Faster Testing:
```python
test_results = test_strategy_colab(
    video_file,
    config,
    frame_skip=10,     # Process every 10th frame
    max_spins=30,      # Only 30 spins
    verbose=True
)
```

### For Thorough Testing:
```python
test_results = test_strategy_colab(
    video_file,
    config,
    frame_skip=1,      # All frames
    max_spins=None,   # All spins
    verbose=True
)
```

### Change Strategy Settings:
```python
config["strategy"]["streak_length"] = 7  # Wait for 7 consecutive
config["strategy"]["base_bet"] = 5.0     # Lower base bet
config["strategy"]["max_gales"] = 3      # Fewer gale steps
```

---

## 📥 Download Results

**Copy and run this:**

```python
from google.colab import files
import glob

result_files = glob.glob('test_results/strategy_test_*.json')
if result_files:
    latest = max(result_files, key=os.path.getctime)
    files.download(latest)
    print(f" Downloaded: {latest}")
else:
    print(" No results file found")
```

---

## 📈 Analyze Results

**Copy and run this to see detailed analysis:**

```python
import pandas as pd

if test_results:
    results = test_results["results"]
    stats = test_results["statistics"]
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Show bet decisions
    bets = df[df['bet_decision'].notna()]
    print("\n📊 BET DECISIONS:")
    print("=" * 70)
    for idx, row in bets.iterrows():
        decision = row['bet_decision']
        action = decision.get('action')
        if action == 'entry':
            print(f"Spin {row['spin']}: ENTRY - Bet {decision.get('bet_type').upper()} {decision.get('bet_amount')}")
        elif action == 'gale_progression':
            print(f"Spin {row['spin']}: GALE Step {decision.get('gale_step')} - Bet {decision.get('bet_type').upper()} {decision.get('bet_amount')}")
        elif action == 'cycle_complete':
            result = decision.get('result')
            if result == 'win':
                print(f"Spin {row['spin']}:  WIN - Profit: +{decision.get('profit')}")
            else:
                print(f"Spin {row['spin']}:  MAX GALE - Loss: -{decision.get('loss')}")
    
    # Show streaks
    print("\n📈 STREAK ANALYSIS:")
    print("=" * 70)
    max_even_streak = df['even_streak'].max()
    max_odd_streak = df['odd_streak'].max()
    print(f"Max Even streak: {max_even_streak}")
    print(f"Max Odd streak: {max_odd_streak}")
    
    # Show balance progression
    print("\n💰 BALANCE PROGRESSION:")
    print("=" * 70)
    balance_changes = df[df['bet_decision'].notna()][['spin', 'balance']]
    for idx, row in balance_changes.iterrows():
        print(f"Spin {row['spin']}: Balance = {row['balance']:.2f}")
```

---

##  Tips

1. **Start Small**: Test with 30-50 spins first
2. **Check Detection**: Make sure numbers are detected correctly
3. **Watch Streaks**: Verify streaks are tracked correctly
4. **Monitor Entries**: Check that entries trigger at streak = 5
5. **Verify Gale**: Confirm gale progression works (doubles on loss)
6. **Analyze Results**: Review win rate and profit/loss

---

## 🔧 Troubleshooting

### "DisplayConnectionError" or "KeyError: 'DISPLAY'" Error
**Problem**: `pyautogui` tries to connect to an X display server, which doesn't exist in Colab.

**Solution**: Mock `pyautogui` **BEFORE** importing any project modules (done in Step 5):
```python
from unittest.mock import MagicMock
import sys
sys.modules['pyautogui'] = MagicMock()
mock_pyautogui = sys.modules['pyautogui']
mock_pyautogui.screenshot = MagicMock(return_value=None)
mock_pyautogui.moveTo = MagicMock()
mock_pyautogui.click = MagicMock()
mock_pyautogui.write = MagicMock()
mock_pyautogui.press = MagicMock()
```

**Why this works**: We're only testing strategy logic, not actual betting, so we don't need real mouse automation. The mock prevents the connection attempt.

**Make sure** you run Step 5 before importing `RouletteBot` or `BetController`.

### "No numbers detected"
- Try different `frame_skip` values
- Check video quality
- Verify OCR is working
- Make sure video file uploaded correctly

### "No entries triggered"
- Check if streaks reach 5
- Verify `streak_length` setting in config
- Look at streak values in output
- Verify detection is working (numbers are being detected)

### "Low win rate"
- This is normal - Even/Odd has ~48.6% theoretical win rate
- Short-term variance can vary
- Test with more spins for better accuracy

### "ModuleNotFoundError" or Import Errors
- Make sure all project files are uploaded
- Check that Step 5 verified all files exist
- Restart runtime: Runtime  Restart runtime
- Re-run Step 2 (install dependencies)

### EasyOCR Download Warnings
- **Normal**: EasyOCR downloads models on first use
- **Wait**: Let it finish downloading (may take a few minutes)
- **One-time**: Models are cached after first download

---

##  What This Tests

 **Streak Tracking**: Even/Odd streaks are counted correctly  
 **Entry Logic**: Entries trigger when streak ≥ 5  
 **Bet Decisions**: Correct bet type (Even/Odd) is chosen  
 **Gale Progression**: Bets double after losses  
 **Cycle Management**: Cycles start and end properly  
 **Win/Loss Logic**: Outcomes are determined correctly  
 **Statistics**: Performance metrics are calculated  

---

##  Next Steps

After testing in Colab:

1. **If results look good**: Test locally with `simulate_strategy.py`
2. **If issues found**: Adjust strategy parameters and retest
3. **Compare strategies**: Test different `streak_length` values
4. **Analyze performance**: Review win rates and profit/loss

---

**Remember**: This tests the **strategy logic**, not live betting. For live testing, use the bot in test mode locally.

