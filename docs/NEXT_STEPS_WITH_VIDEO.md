# Next Steps - Testing with Video File

##  What You've Completed

-  Captured Red (Vermelho) betting button coordinates
-  Captured Black (Preto) betting button coordinates
-  Verified coordinates are correct
-  Using video file for testing (not live game)

---

## 📋 Next Steps (For Video Testing)

### Step 1: Test Number Detection with Video  (Do This First!)

**Since you're using a video file, you can test detection right now!**

**Run:**
```bash
python test_video.py
```

**OR if you have the video in Colab:**
- Use the Colab notebook: `roulette_bot_test.ipynb`

**What this tests:**
-  Can detect numbers from video frames
-  Can determine colors (red/black/green)
-  Detection accuracy
-  Works with your video file

**Expected output:**
- JSON file with detection results
- Accuracy percentage
- Frame-by-frame results

---

### Step 2: Analyze Detection Results

**After running `test_video.py`, analyze results:**

**Run:**
```bash
python analyze_results.py
```

**OR manually check:**
- Look at the JSON result file
- Check accuracy percentage
- Review which frames were detected correctly
- Identify any issues

**What to look for:**
-  Accuracy > 80% (good)
-  Accuracy > 90% (excellent)
-  Accuracy < 80% (needs improvement)

---

### Step 3: Improve Detection (If Needed)

**If accuracy is low, try:**

1. **Adjust screen_region in config:**
   ```json
   "detection": {
     "screen_region": [x, y, width, height]
   }
   ```
   - Make sure region covers where numbers appear
   - Use coordinate tool to find number display area

2. **Create number templates:**
   ```bash
   python template_creation_helper.py
   ```
   - Extract number images from video
   - Create templates for better matching

3. **Calibrate color detection:**
   - Adjust HSV color ranges in config
   - Test different color thresholds

**See:** `IMPROVE_DETECTION_RATE.md` for detailed guide

---

### Step 4: Test Betting Automation (Requires Live Game)

** Important:** Betting automation CANNOT be tested with video file!

**Why:**
- Video file is just images - no interactive elements
- Need live game to click buttons
- Need actual game interface to interact with

**When to test betting:**
- When you have access to live game
- Or use a test/demo account
- Or wait until you're ready to go live

**How to test betting (when ready):**
```bash
python test_betting.py
```

**For now:** Skip this step until you have a live game.

---

### Step 5: Configure Strategy (Can Do Now)

**File:** `config/default_config.json`

**Update strategy section:**

```json
"strategy": {
  "type": "martingale",
  "base_bet": 1.0,                // Start small for testing
  "max_gales": 5,
  "multiplier": 2.0,
  "bet_color_pattern": "opposite",
  "zero_handling": {
    "rule": "continue_sequence",
    "reset_on_zero": false
  }
}
```

**Recommendations for testing:**
- `base_bet`: 1.0 (minimum bet)
- `max_gales`: 3-5 (reasonable limit)
- `multiplier`: 2.0 (standard Martingale)

---

### Step 6: Configure Risk Management (Can Do Now)

**File:** `config/default_config.json`

```json
"risk": {
  "initial_balance": 100.0,        // Your test balance
  "stop_loss": 50.0,               // Stop at 50% loss
  "guarantee_fund_percentage": 20   // Reserve 20% for gales
}
```

**For testing:**
- Set `initial_balance` to your test account balance
- Set `stop_loss` to a safe limit
- `guarantee_fund_percentage`: 20% is good

---

### Step 7: Test Full Detection Pipeline (With Video)

**Create a test that simulates the full bot cycle:**

**File:** `test_detection_pipeline.py`
```python
"""Test detection pipeline with video file."""
from backend.app.detection.screen_detector import ScreenDetector
from backend.app.strategy.martingale_strategy import MartingaleStrategy
from backend.app.config_loader import load_config
import cv2
import json

def test_pipeline():
    """Test detection + strategy logic with video."""
    print("=" * 70)
    print("TESTING DETECTION PIPELINE")
    print("=" * 70)
    
    # Load config
    config = load_config()
    
    # Create detector
    detector = ScreenDetector(config)
    
    # Create strategy
    strategy = MartingaleStrategy(config)
    
    # Open video
    video_path = "roleta_brazileria.mp4"  # Your video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f" Error: Could not open video: {video_path}")
        return
    
    print(f"\n Video opened: {video_path}")
    print("\nProcessing frames...")
    print("This simulates what the bot will do:\n")
    
    results = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Skip frames (process every 30th frame)
        if frame_count % 30 != 0:
            continue
        
        # Detect result
        result = detector.detect_result(frame)
        
        if result['number'] is not None:
            print(f"Frame {frame_count}: Detected {result['number']} ({result['color']})")
            
            # Update strategy with result
            strategy.update_history(result)
            
            # Check if strategy wants to bet
            bet_signal = strategy.should_bet()
            if bet_signal:
                print(f"   Strategy says: BET {bet_signal['color']} with {bet_signal['amount']}")
            
            results.append({
                'frame': frame_count,
                'detected': result,
                'bet_signal': bet_signal
            })
    
    cap.release()
    
    # Save results
    with open('pipeline_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("PIPELINE TEST COMPLETE")
    print("=" * 70)
    print(f"\nProcessed {len(results)} frames with detections")
    print("Results saved to: pipeline_test_results.json")
    print("\nThis shows:")
    print("  - Detection accuracy")
    print("  - Strategy logic (when it wants to bet)")
    print("  - Full pipeline working together")

if __name__ == '__main__':
    test_pipeline()
```

**This tests:**
-  Detection works with video
-  Strategy logic works
-  Full pipeline integration
-  No betting needed (just simulation)

---

## 📊 Testing Checklist (Video-Based)

**What you CAN test with video:**
-  Number detection accuracy
-  Color detection
-  Strategy logic (simulation)
-  Full detection pipeline
-  Configuration settings

**What you CANNOT test with video:**
- [ ] Actual betting clicks (needs live game)
- [ ] Bet confirmation
- [ ] Real-time interaction
- [ ] Session management

---

##  Recommended Order

**Right now (with video):**

1.  **Test number detection** - `python test_video.py`
2.  **Analyze results** - `python analyze_results.py`
3.  **Improve detection** (if needed)
4.  **Configure strategy** - Update config file
5.  **Test pipeline** - `python test_detection_pipeline.py` (if you create it)

**Later (with live game):**

6. ⏳ **Test betting automation** - `python test_betting.py`
7. ⏳ **Test full bot** - `python main.py`
8. ⏳ **Run bot live**

---

## 🚀 Quick Start (Right Now)

**Step 1: Test Detection**
```bash
python test_video.py
```

**Step 2: Check Results**
- Look at JSON output
- Check accuracy percentage
- Review detected numbers

**Step 3: If Accuracy is Good (>80%)**
- Configure strategy in config file
- You're ready for live testing when you have access

**Step 4: If Accuracy is Low (<80%)**
- See `IMPROVE_DETECTION_RATE.md`
- Adjust screen_region
- Create templates
- Calibrate colors

---

## 📝 Summary

**Since you're using video:**
-  Focus on detection testing first
-  Can test strategy logic (simulation)
- ⏳ Betting testing waits until live game
-  Can configure everything now

**Next action:**
```bash
python test_video.py
```

This will test if your detection works correctly with your video file!

