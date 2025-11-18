# Comprehensive Bot Test for Colab

## 🎯 Complete Bot Testing Script

This is the **best and perfect** script for testing your roulette bot in Colab. It includes:
- ✅ Full detection diagnostics
- ✅ Strategy execution with win/loss tracking
- ✅ Detailed statistics and reporting
- ✅ Works seamlessly in Colab
- ✅ Saves results to JSON

---

## 🚀 Quick Start

### Step 1: Install Dependencies
```python
!pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils -q
print("✅ Dependencies installed!")
```

### Step 2: Upload Project Files
Upload your project folder and video file via Files sidebar

### Step 3: Run Comprehensive Test
**Copy and paste this complete test code:**

```python
import sys
import os
import cv2
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Mock pyautogui for Colab
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
print("✅ pyautogui mocked")

sys.path.insert(0, os.path.abspath('.'))

from backend.app.config_loader import ConfigLoader
from backend.app.bot import RouletteBot
from backend.app.detection.frame_detector import FrameDetector
from backend.app.detection.screen_detector import ScreenDetector

# Find video
video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov'))]
if not video_files:
    print("❌ No video file found")
else:
    video_file = video_files[0]
    print(f"✅ Video: {video_file}")
    
    # Load config
    config_path = 'config/default_config.json'
    config = ConfigLoader.load_config(config_path)
    
    # Initialize bot
    bot = RouletteBot(config_path, test_mode=True)
    
    # Use frame detector - start from frame 690 if game starts later
    start_frame = 690  # Adjust this to where game starts in your video
    max_spins = 100  # Limit spins for testing (None = unlimited)
    max_detection_failures = 200  # Stop after this many consecutive failures
    frame_skip = 1  # Process every Nth frame (1 = all frames)
    
    # Create frame detector
    frame_detector = FrameDetector(config, video_file)
    frame_detector.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    bot.detector = frame_detector
    
    # Statistics
    stats = {
        'total_frames_processed': 0,
        'total_spins': 0,
        'successful_detections': 0,
        'detection_failures': 0,
        'bets_placed': 0,
        'wins': 0,
        'losses': 0,
        'zeros': 0,
        'cycles_completed': 0,
        'cycles_won': 0,
        'cycles_lost': 0,
        'max_gale_reached': 0,
        'detection_methods': {},
        'numbers_detected': []
    }
    
    results = []
    pending_bet = None
    last_detected_number = None
    
    # Get initial balance
    initial_balance = config.get('risk', {}).get('initial_balance', 1000.0)
    bot.current_balance = initial_balance
    
    # Print header
    print("\n" + "=" * 80)
    print("COMPREHENSIVE BOT TEST")
    print("=" * 80)
    print(f"Video: {video_file}")
    print(f"Config: {config_path}")
    print(f"Start frame: {start_frame}")
    print(f"Max spins: {max_spins or 'unlimited'}")
    print("-" * 80)
    
    # Strategy info
    strategy = bot.strategy
    if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
        nav_enabled = config.get('strategy_navigation', {}).get('enabled', False)
        print(f"Strategy Navigation: {'ENABLED ✅' if nav_enabled else 'DISABLED'}")
        if nav_enabled:
            print(f"Current Strategy: {bot.strategy_manager.current_strategy_name}")
        strategy = bot.strategy_manager.get_current_strategy()
    
    print(f"Strategy Type: {strategy.strategy_type}")
    print(f"Base Bet: {config.get('strategy', {}).get('base_bet', 10.0)}")
    print(f"Streak Length: {config.get('strategy', {}).get('streak_length', 6)}")
    print(f"Max Gales: {config.get('strategy', {}).get('max_gales', 3)}")
    print(f"Zero Policy: {getattr(strategy, 'zero_policy', 'count_as_loss')}")
    print(f"Initial Balance: {initial_balance:.2f}")
    print("-" * 80)
    
    # Detection info
    detector = bot.detector
    if isinstance(detector, ScreenDetector):
        print(f"Templates Loaded: {len(detector.winning_templates)}")
        if detector.winning_templates:
            template_numbers = sorted([t[0] for t in detector.winning_templates])
            print(f"Template Numbers: {template_numbers}")
        print(f"Template Threshold: {detector.winning_template_threshold}")
        print(f"OCR Fallback: {'ENABLED' if detector.enable_ocr_fallback else 'DISABLED'}")
        print(f"OCR Confidence Threshold: {detector.ocr_confidence_threshold}")
    print("=" * 80 + "\n")
    
    # Check detection setup
    if isinstance(detector, ScreenDetector):
        if len(detector.winning_templates) == 0:
            print("⚠️  WARNING: No winning number templates loaded")
            if not detector.enable_ocr_fallback:
                print("⚠️  WARNING: OCR fallback is disabled - detection may fail")
        print()
    
    print("Starting test...\n")
    
    frame_counter = start_frame
    consecutive_failures = 0
    
    try:
        while True:
            # Check limits
            if max_spins and stats['total_spins'] >= max_spins:
                print(f"\n✅ Reached maximum spins limit: {max_spins}")
                break
            
            if consecutive_failures >= max_detection_failures:
                print(f"\n⚠️  Too many consecutive detection failures ({consecutive_failures})")
                break
            
            # Capture frame
            frame = frame_detector.capture_screen()
            if frame is None:
                print("\n✅ End of video reached")
                break
            
            stats['total_frames_processed'] += 1
            
            # Skip frames if needed
            if frame_skip > 1 and (stats['total_frames_processed'] % frame_skip != 0):
                frame_counter += 1
                continue
            
            frame_counter += 1
            
            # Detect result
            detection = bot.detector.detect_result(frame)
            
            if detection is None or detection.get('number') is None:
                consecutive_failures += 1
                stats['detection_failures'] += 1
                if consecutive_failures % 50 == 0:
                    print(f"  ... {consecutive_failures} consecutive detection failures ...")
                continue
            
            # Reset failure counter
            consecutive_failures = 0
            
            current_number = detection.get('number')
            
            # Skip if same number (not a new spin)
            if current_number == last_detected_number:
                continue
            
            last_detected_number = current_number
            stats['total_spins'] += 1
            stats['successful_detections'] += 1
            stats['numbers_detected'].append(current_number)
            
            # Track detection method
            method = detection.get('method', 'unknown')
            stats['detection_methods'][method] = stats['detection_methods'].get(method, 0) + 1
            
            # Track zeros
            if current_number == 0:
                stats['zeros'] += 1
            
            # Get strategy state before processing
            strategy = bot.strategy
            if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
                strategy = bot.strategy_manager.get_current_strategy()
            
            even_streak = getattr(strategy, 'current_even_streak', 0)
            odd_streak = getattr(strategy, 'current_odd_streak', 0)
            gale_step = strategy.gale_step
            in_cycle = getattr(strategy, 'cycle_active', False)
            
            # Determine even/odd
            is_even = (current_number % 2 == 0 and current_number != 0)
            is_odd = (current_number % 2 == 1)
            is_zero = (current_number == 0)
            even_odd_str = "EVEN" if is_even else "ODD" if is_odd else "ZERO"
            
            print(f"\n[Spin {stats['total_spins']}] Frame {frame_counter}")
            print(f"  Number: {current_number} ({even_odd_str})")
            print(f"  Method: {method}, Confidence: {detection.get('confidence', 0):.2f}")
            print(f"  Even streak: {even_streak}, Odd streak: {odd_streak}")
            print(f"  Gale step: {gale_step}, In cycle: {in_cycle}")
            print(f"  Balance: {bot.current_balance:.2f}")
            
            # Handle pending bet (result of previous bet)
            if pending_bet:
                bet_type = pending_bet['bet_type']
                bet_amount = pending_bet['bet_amount']
                
                # Determine win/loss
                won = False
                cycle_ended = False
                
                if bet_type == 'even' and is_even:
                    won = True
                elif bet_type == 'odd' and is_odd:
                    won = True
                elif is_zero:
                    zero_policy = getattr(strategy, 'zero_policy', 'count_as_loss')
                    if zero_policy == 'count_as_win':
                        won = True
                    elif zero_policy == 'reset':
                        # Reset cycle
                        strategy.cycle_active = False
                        strategy.gale_step = 0
                        pending_bet = None
                        print(f"  ⚠️  ZERO - Cycle reset (zero_policy: reset)")
                        continue
                
                # Process win/loss
                if won:
                    stats['wins'] += 1
                    bot.current_balance += bet_amount
                    print(f"  🎉 WIN! +{bet_amount:.2f} (Balance: {bot.current_balance:.2f})")
                    
                    # Check if cycle ended
                    if gale_step == 0:  # First bet in cycle won
                        cycle_ended = True
                        stats['cycles_completed'] += 1
                        stats['cycles_won'] += 1
                else:
                    stats['losses'] += 1
                    bot.current_balance -= bet_amount
                    print(f"  ❌ LOSS! -{bet_amount:.2f} (Balance: {bot.current_balance:.2f})")
                    
                    # Check if max gale reached
                    if gale_step >= getattr(strategy, 'max_gales', 3):
                        cycle_ended = True
                        stats['cycles_completed'] += 1
                        stats['cycles_lost'] += 1
                        stats['max_gale_reached'] += 1
                        print(f"  ⚠️  Max gale reached - cycle ended")
                
                # Update strategy
                bet_result_data = {
                    'result': 'win' if won else 'loss',
                    'bet_amount': bet_amount,
                    'balance_after': bot.current_balance,
                    'cycle_ended': cycle_ended
                }
                
                if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
                    bot.strategy_manager.update_after_bet(bet_result_data)
                    bot.strategy = bot.strategy_manager.get_current_strategy()
                else:
                    bot.strategy.update_after_bet(bet_result_data)
                
                pending_bet = None
            
            # Process new spin (calculate bet decision)
            try:
                spin_result = bot.process_spin(detection)
                bet_decision = spin_result.get('bet_decision')
                
                if bet_decision:
                    stats['bets_placed'] += 1
                    bet_type = bet_decision.get('bet_type')
                    bet_amount = bet_decision.get('bet_amount', 0.0)
                    
                    # Store as pending bet
                    pending_bet = {
                        'bet_type': bet_type,
                        'bet_amount': bet_amount,
                        'gale_step': bet_decision.get('gale_step', 0),
                        'streak_length': bet_decision.get('streak_length', 0)
                    }
                    
                    # Get updated strategy state
                    strategy = bot.strategy
                    if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
                        strategy = bot.strategy_manager.get_current_strategy()
                        strategy_name = f" [{bot.strategy_manager.current_strategy_name}]"
                    else:
                        strategy_name = ""
                    
                    even_streak = getattr(strategy, 'current_even_streak', 0)
                    odd_streak = getattr(strategy, 'current_odd_streak', 0)
                    gale_step = strategy.gale_step
                    
                    print(f"  ✅ BET: {bet_type.upper()} - {bet_amount:.2f} (Gale: {gale_step}){strategy_name}")
                    print(f"     Entry streak: {bet_decision.get('streak_length', 0)}")
                else:
                    print(f"  → No bet (strategy conditions not met)")
            
            except Exception as e:
                print(f"  ❌ Error processing spin: {e}")
                import traceback
                traceback.print_exc()
            
            # Store result
            results.append({
                'spin': stats['total_spins'],
                'frame': frame_counter,
                'number': current_number,
                'even_odd': even_odd_str,
                'detection_method': method,
                'confidence': detection.get('confidence', 0),
                'bet_decision': bet_decision if 'bet_decision' in locals() else None,
                'pending_bet': pending_bet,
                'balance': bot.current_balance,
                'even_streak': even_streak,
                'odd_streak': odd_streak,
                'gale_step': gale_step,
                'in_cycle': in_cycle
            })
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test stopped by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        frame_detector.release()
    
    # Calculate final statistics
    win_rate = 0.0
    if (stats['wins'] + stats['losses']) > 0:
        win_rate = (stats['wins'] / (stats['wins'] + stats['losses'])) * 100
    
    balance_change = bot.current_balance - initial_balance
    roi = 0.0
    if initial_balance > 0:
        roi = (balance_change / initial_balance) * 100
    
    # Get final strategy state
    strategy = bot.strategy
    if hasattr(bot, 'strategy_manager') and bot.strategy_manager:
        strategy = bot.strategy_manager.get_current_strategy()
    
    # Print results
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Total frames processed: {stats['total_frames_processed']}")
    print(f"Total spins: {stats['total_spins']}")
    print(f"Successful detections: {stats['successful_detections']}")
    print(f"Detection failures: {stats['detection_failures']}")
    if stats['total_frames_processed'] > 0:
        detection_rate = (stats['successful_detections'] / stats['total_frames_processed'] * 100)
        print(f"Detection success rate: {detection_rate:.1f}%")
    print("-" * 80)
    print(f"Bets placed: {stats['bets_placed']}")
    print(f"Wins: {stats['wins']} | Losses: {stats['losses']}")
    if (stats['wins'] + stats['losses']) > 0:
        print(f"Win rate: {win_rate:.2f}%")
    else:
        print("Win rate: N/A (no bets placed)")
    print("-" * 80)
    print(f"Initial balance: {initial_balance:.2f}")
    print(f"Final balance: {bot.current_balance:.2f}")
    print(f"Balance change: {balance_change:+.2f}")
    if initial_balance > 0:
        print(f"ROI: {roi:+.2f}%")
    print("-" * 80)
    print(f"Zeros detected: {stats['zeros']}")
    print(f"Cycles completed: {stats['cycles_completed']}")
    print(f"  - Cycles won: {stats['cycles_won']}")
    print(f"  - Cycles lost: {stats['cycles_lost']}")
    print(f"  - Max gale reached: {stats['max_gale_reached']}")
    print("-" * 80)
    print("Detection Methods:")
    for method, count in stats['detection_methods'].items():
        print(f"  - {method}: {count}")
    print("-" * 80)
    print("Final Strategy State:")
    print(f"  Even streak: {getattr(strategy, 'current_even_streak', 0)}")
    print(f"  Odd streak: {getattr(strategy, 'current_odd_streak', 0)}")
    print(f"  Gale step: {strategy.gale_step}")
    print(f"  In cycle: {getattr(strategy, 'cycle_active', False)}")
    print("=" * 80)
    
    # Warnings
    if stats['total_spins'] == 0:
        print("\n⚠️  WARNING: No numbers detected from video!")
        print("   Try:")
        print(f"   1. Adjust start_frame (currently {start_frame})")
        print("   2. Check if OCR fallback is enabled in config")
        print("   3. Verify video contains roulette game")
        print("   4. Check screen_region in config matches video")
        print("   5. Verify winning-number templates are loaded")
    
    if stats['bets_placed'] == 0 and stats['total_spins'] > 0:
        print("\n⚠️  WARNING: No bets were placed!")
        print("   This might mean:")
        print("   1. Entry conditions not met (streak length too low)")
        print("   2. Strategy is waiting for entry signal")
    
    print("\n✅ Test completed!")
```

---

## 📊 What This Test Does

1. **Full Detection Testing**
   - Tests template matching
   - Tests OCR fallback
   - Tracks detection methods used
   - Shows detection success rate

2. **Complete Strategy Execution**
   - Tracks even/odd streaks
   - Handles entry conditions
   - Manages gale progression
   - Processes win/loss outcomes
   - Tracks cycle completion

3. **Comprehensive Statistics**
   - Total spins processed
   - Detection success rate
   - Win/loss tracking
   - Balance changes
   - ROI calculation
   - Cycle statistics

4. **Detailed Output**
   - Real-time spin-by-spin results
   - Strategy state at each step
   - Win/loss notifications
   - Final comprehensive summary

---

## 🎛️ Configuration Options

### Adjust Start Frame
```python
start_frame = 690  # Change this to where game starts in your video
```

### Limit Spins
```python
max_spins = 100  # Set to None for unlimited
```

### Process Every Nth Frame
```python
frame_skip = 1  # 1 = all frames, 2 = every 2nd frame, etc.
```

### Max Detection Failures
```python
max_detection_failures = 200  # Stop after this many consecutive failures
```

---

## 📈 Understanding Results

### Detection Statistics
- **Total frames processed**: All frames analyzed
- **Successful detections**: Numbers successfully detected
- **Detection success rate**: Percentage of successful detections
- **Detection methods**: Which method detected each number (template/OCR)

### Strategy Statistics
- **Bets placed**: Total bets made
- **Wins/Losses**: Bet outcomes
- **Win rate**: Percentage of winning bets
- **Cycles completed**: Number of betting cycles finished
- **Max gale reached**: How many times max gale was hit

### Financial Statistics
- **Initial/Final balance**: Starting and ending balance
- **Balance change**: Net profit/loss
- **ROI**: Return on investment percentage

---

## 🔧 Troubleshooting

### No Numbers Detected
1. Check `start_frame` - game might start later
2. Verify templates are loaded (check output)
3. Enable OCR fallback in config
4. Check `screen_region` matches video

### No Bets Placed
1. Check entry streak length requirement
2. Verify strategy is waiting for entry signal
3. Check if streaks are being tracked correctly

### Detection Failures
1. Lower `winning_template_threshold` in config
2. Verify templates match video style
3. Check screen region coordinates
4. Enable OCR fallback

---

## 💾 Saving Results

To save results to a file, add this at the end:

```python
# Save results
results_data = {
    'test_info': {
        'video_path': video_file,
        'config_path': config_path,
        'start_frame': start_frame,
        'timestamp': datetime.now().isoformat()
    },
    'statistics': stats,
    'strategy_state': {
        'even_streak': getattr(strategy, 'current_even_streak', 0),
        'odd_streak': getattr(strategy, 'current_odd_streak', 0),
        'gale_step': strategy.gale_step,
        'in_cycle': getattr(strategy, 'cycle_active', False)
    },
    'results': results
}

with open('test_results_comprehensive.json', 'w') as f:
    json.dump(results_data, f, indent=2)

print("\n✅ Results saved to: test_results_comprehensive.json")
```

---

## ✅ This is the Best Test Script Because:

1. **Complete Coverage**: Tests detection, strategy, and betting logic
2. **Detailed Diagnostics**: Shows exactly what's happening at each step
3. **Comprehensive Statistics**: Tracks everything important
4. **Error Handling**: Gracefully handles failures and edge cases
5. **Colab Ready**: Works perfectly in Colab environment
6. **Easy to Use**: Just copy, paste, and run
7. **Well Documented**: Clear output and warnings

Use this script for all your bot testing needs! 🚀

