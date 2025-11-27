# Step-by-Step Strategy Testing Guide

This is a detailed, step-by-step guide to test your roulette bot's strategy using video files.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Video file (`roleta_brazileria.mp4` or similar) in the project root
- [ ] Configuration file (`config/default_config.json`) properly configured
- [ ] Winning number templates in `winning-numbers/` directory (at least a few)
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Project structure intact (all backend modules present)

---

## Step 1: Verify Your Setup

### 1.1 Check Video File

```powershell
# Verify video exists
dir roleta_brazileria.mp4
```

**Expected:** File should exist and be readable.

**If missing:** Place your video file in the project root directory.

### 1.2 Check Configuration

```powershell
# View config file
type config\default_config.json
```

**Check these settings:**
- `detection.screen_region`: Should match video frame coordinates
- `strategy.type`: Should be "martingale" (or your preferred strategy)
- `strategy.base_bet`: Your starting bet amount
- `strategy.max_gales`: Maximum gale steps
- `risk.initial_balance`: Starting balance
- `risk.stop_loss`: Stop loss threshold

**Example valid config:**
```json
{
  "detection": {
    "screen_region": [953, 511, 57, 55],
    "winning_templates_dir": "winning-numbers/"
  },
  "strategy": {
    "type": "martingale",
    "base_bet": 10.0,
    "max_gales": 5,
    "multiplier": 2.0
  },
  "risk": {
    "initial_balance": 1000.0,
    "stop_loss": 500.0
  }
}
```

### 1.3 Check Winning Templates

```powershell
# List templates
dir winning-numbers\*.png
```

**Expected:** At least a few template files like `winning-number_22.png`, etc.

**If empty:** You can still test, but detection will rely on OCR (slower, less accurate).

---

## Step 2: Test Detection First (Recommended)

Before testing strategy, verify detection works correctly.

### 2.1 Run Detection Test

```powershell
python test_video.py roleta_brazileria.mp4 --config config/default_config.json --mode frame --start 0 --end 60 --skip 1
```

**What this does:**
- Tests detection on first 60 seconds of video
- Uses frame mode (reads from video file)
- Processes every frame
- Generates a report

### 2.2 Check Results

After the test completes, look for:

```
TEST SUMMARY
============================================================
Total frames in video: 1800
Frames processed: 1800
Successful detections: 150
Detection rate: 8.33%
============================================================

Detection Methods:
  template_badge: 120
  ocr: 30
  None: 1650
```

**What to look for:**
-  **Good:** `template_badge` method used (fast, accurate)
-  **Acceptable:** `ocr` method used (slower but works)
-  **Problem:** Mostly `None` or very low detection rate

**If detection rate is low (<5%):**
1. Check `screen_region` coordinates match video
2. Add more winning number templates
3. Verify video quality is good

### 2.3 Review JSON Report

```powershell
# Find the latest test result
dir test_results\*.json | sort LastWriteTime -Descending | select -First 1
```

Open the JSON file and check:
- Detection methods used
- Confidence scores
- Which numbers were detected

**Good signs:**
- High confidence scores (>0.8) for template_badge
- Multiple different numbers detected
- Consistent detection across frames

---

## Step 3: Run Strategy Simulation

### 3.1 Basic Strategy Test

Start with a small test to verify everything works:

```powershell
python simulate_strategy.py roleta_brazileria.mp4 --config config/default_config.json --max-spins 10
```

**What to expect:**
```
Loading configuration from config/default_config.json...
Initializing bot in test mode...
Loading video: roleta_brazileria.mp4

============================================================
STRATEGY SIMULATION STARTED
============================================================
Video: roleta_brazileria.mp4
Strategy: martingale
Base bet: 10.0
Max spins: 10
------------------------------------------------------------

[Spin 1] Detected: 22 (red)
  Method: template_badge, Confidence: 0.95
   Bet decision: black - 10.0 (Gale step: 0)
   Bet placed (simulated - no actual bet in test mode)

[Spin 2] Detected: 15 (black)
  Method: template_badge, Confidence: 0.92
   Bet decision: red - 20.0 (Gale step: 1)
   Bet placed (simulated - no actual bet in test mode)
...
```

### 3.2 Monitor Output

Watch for:

** Good signs:**
- Numbers detected successfully
- Bet decisions being made
- Gale steps incrementing after losses
- No errors or exceptions

** Warning signs:**
- Many "Failed to detect result" messages
- No bet decisions (strategy conditions not met)
- Errors or crashes

### 3.3 Check Console Output

Look for these patterns:

**Pattern 1: Normal operation**
```
[Spin 1] Detected: 22 (red)
   Bet decision: black - 10.0 (Gale step: 0)
[Spin 2] Detected: 15 (black)  ← Previous bet won
   Bet decision: red - 10.0 (Gale step: 0)  ← Reset to base
```

**Pattern 2: Gale progression**
```
[Spin 1] Detected: 22 (red)
   Bet decision: black - 10.0 (Gale step: 0)
[Spin 2] Detected: 15 (red)  ← Previous bet lost
   Bet decision: black - 20.0 (Gale step: 1)  ← Doubled
[Spin 3] Detected: 7 (red)  ← Still lost
   Bet decision: black - 40.0 (Gale step: 2)  ← Doubled again
```

**Pattern 3: No bet (strategy condition not met)**
```
[Spin 1] Detected: 22 (red)
   No bet decision (strategy conditions not met)
```

---

## Step 4: Analyze Results

### 4.1 Check Log Files

After simulation completes, check the logs:

```powershell
# List log files
dir logs\*.csv | sort LastWriteTime -Descending | select -First 1
```

**Open the CSV file** (Excel, Google Sheets, or text editor) and review:

| Column | What to Check |
|--------|---------------|
| `spin_number` | Should increment sequentially |
| `outcome_number` | Detected numbers (0-36) |
| `outcome_color` | red/black/green |
| `bet_type` | red/black (or None if no bet) |
| `bet_amount` | Bet size (should follow strategy) |
| `gale_step` | Should increment after losses |
| `balance_before` | Starting balance for each spin |
| `detection_method` | template_badge/ocr/None |
| `detection_confidence` | Should be >0.7 for good detections |

### 4.2 Calculate Statistics

**Win Rate:**
- Count wins vs losses
- Calculate percentage

**Gale Progression:**
- Verify bets double after losses
- Check max gale is respected

**Balance Tracking:**
- Starting balance: 1000.0
- After each spin, balance should change
- Check stop loss triggers if applicable

### 4.3 Review Summary

At the end of simulation, you'll see:

```
============================================================
SIMULATION SUMMARY
============================================================
Total spins processed: 50
Successful detections: 50
Bets placed: 35
Current balance: 850.0
Gale step: 2
Result history length: 50
============================================================
```

**What to check:**
- **Total spins:** Matches your `--max-spins` (if set)
- **Successful detections:** Should match total spins (or close)
- **Bets placed:** May be less than spins (strategy conditions)
- **Current balance:** Should reflect wins/losses
- **Gale step:** Current gale progression level

---

## Step 5: Extended Testing

### 5.1 Longer Test Run

Once basic test works, run a longer simulation:

```powershell
python simulate_strategy.py roleta_brazileria.mp4 --config config/default_config.json --max-spins 100
```

**Purpose:**
- Test strategy over more spins
- Identify patterns or issues
- Validate stop conditions

### 5.2 Test Different Scenarios

**Test 1: Stop Loss**
```powershell
# Set low stop loss in config, then test
python simulate_strategy.py roleta_brazileria.mp4 --max-spins 200
```

**Expected:** Bot should stop when balance reaches stop loss.

**Test 2: Max Gale**
```powershell
# Set max_gales to 3, then test
python simulate_strategy.py roleta_brazileria.mp4 --max-spins 100
```

**Expected:** Bot should stop or reset when max gale reached.

**Test 3: Zero Handling**
```powershell
# Test with video containing zero results
python simulate_strategy.py roleta_brazileria.mp4 --max-spins 50
```

**Expected:** Zero should be handled according to config (continue/reset).

---

## Step 6: Troubleshooting

### Problem: "No detections found"

**Symptoms:**
- Console shows: "Failed to detect result, retrying..."
- No numbers detected
- Detection rate is 0%

**Solutions:**

1. **Check screen_region:**
   ```powershell
   # Verify coordinates in config
   type config\default_config.json | findstr screen_region
   ```
   - Coordinates should match video frame
   - Use `test_video.py --display` to visualize region

2. **Add more templates:**
   ```powershell
   # Capture more winning numbers
   python capture_winning-numbers.py --region 953 511 57 55 --count 5
   ```

3. **Test detection separately:**
   ```powershell
   python test_video.py roleta_brazileria.mp4 --mode frame --start 0 --end 30
   ```

### Problem: "Strategy not placing bets"

**Symptoms:**
- Numbers detected successfully
- But no bet decisions made
- Console shows: "No bet decision (strategy conditions not met)"

**Solutions:**

1. **Check strategy config:**
   ```json
   {
     "strategy": {
       "type": "martingale",
       "base_bet": 10.0,
       "bet_color_pattern": "opposite"  // or "same"
     }
   }
   ```

2. **Verify entry conditions:**
   - Strategy may require specific patterns
   - Check if you need consecutive colors, etc.

3. **Check balance:**
   - Ensure `initial_balance` is sufficient
   - Verify `stop_loss` isn't too high

### Problem: "Errors or crashes"

**Symptoms:**
- Python exceptions
- Script stops unexpectedly
- Error messages in console

**Solutions:**

1. **Check dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Verify file paths:**
   - Video file exists and is readable
   - Config file is valid JSON
   - Templates directory exists

3. **Check Python version:**
   ```powershell
   python --version
   ```
   - Should be Python 3.7+

4. **Review error messages:**
   - Read full traceback
   - Check which line failed
   - Verify that module/file exists

---

## Step 7: Validation Checklist

After testing, verify:

- [ ] Detection works reliably (>80% detection rate)
- [ ] Strategy places bets when conditions are met
- [ ] Gale progression works (doubles after losses)
- [ ] Stop conditions trigger (stop loss, max gale)
- [ ] Balance tracking is accurate
- [ ] Logs are generated correctly
- [ ] No errors or crashes during test
- [ ] Console output is clear and informative

---

## Step 8: Interpret Results

### Good Results Indicators:

 **High detection rate** (>80%)
- Means detection is working well
- Strategy can make decisions reliably

 **Consistent bet placement**
- Strategy is triggering as expected
- Entry conditions are being met

 **Proper gale progression**
- Bets double after losses
- Resets after wins

 **Stop conditions work**
- Bot stops at stop loss
- Bot respects max gale limit

### Areas for Improvement:

 **Low detection rate** (<50%)
- Add more winning number templates
- Adjust screen_region coordinates
- Improve video quality

 **Too few bets placed**
- Review strategy entry conditions
- May need to adjust pattern requirements
- Check if strategy is too conservative

 **Balance issues**
- Verify win/loss calculations
- Check if payout ratio is correct
- Ensure balance updates correctly

---

## Step 9: Next Steps

After successful testing:

1. **Refine Strategy:**
   - Adjust parameters based on results
   - Test different configurations
   - Optimize entry conditions

2. **Improve Detection:**
   - Capture more winning number templates
   - Fine-tune screen_region
   - Test with different video qualities

3. **Prepare for Live:**
   - Test with `--test` flag on live casino
   - Start with minimal stakes
   - Monitor closely for first sessions

---

## Quick Reference Commands

```powershell
# Test detection only
python test_video.py roleta_brazileria.mp4 --mode frame --start 0 --end 60

# Test strategy (10 spins)
python simulate_strategy.py roleta_brazileria.mp4 --max-spins 10

# Test strategy (100 spins, quiet mode)
python simulate_strategy.py roleta_brazileria.mp4 --max-spins 100 --quiet

# Test with custom delay
python simulate_strategy.py roleta_brazileria.mp4 --delay 1.0

# View latest log
dir logs\*.csv | sort LastWriteTime -Descending | select -First 1
```

---

## Support

If you encounter issues not covered here:

1. Check `logs/` directory for detailed error logs
2. Review console output for specific error messages
3. Verify all prerequisites are met
4. Test detection separately before strategy testing
5. Start with small tests (`--max-spins 5`) to isolate issues

