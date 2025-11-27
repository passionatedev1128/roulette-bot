# Next Steps After Detection Testing

##  You've Completed: Detection Testing

You've run `test_video.py` and tested the detection system. Now let's analyze results and proceed.

---

## Step 1: Analyze Your Test Results

### 1.1 Check the Test Summary

Look at the console output for:
```
TEST SUMMARY
============
Total frames in video: X
Frames processed: Y
Successful detections: Z
Detection rate: XX.XX%
```

**What to look for:**
-  **Detection rate > 90%**: Good - proceed to strategy testing
-  **Detection rate 70-90%**: Acceptable - may need more templates
-  **Detection rate < 70%**: Needs improvement - capture more templates

### 1.2 Check Detection Methods

Look at the output for each frame:
```
Method: template_badge   Best (using templates)
Method: template         Good (generic templates)
Method: ocr              Fallback (less reliable)
Method: color_fallback   Last resort (no number detected)
```

**Ideal distribution:**
- Most detections should use `template_badge` or `template`
- Few or no `ocr` detections (means templates are working)
- No `color_fallback` (means numbers are being detected)

### 1.3 Review the JSON Results File

Check `test_results/test_results_YYYYMMDD_HHMMSS.json`:

```python
# Quick analysis script
import json

with open('test_results/test_results_*.json', 'r') as f:
    data = json.load(f)

# Check detection rate
print(f"Detection rate: {data['detection_rate']:.2f}%")

# Check methods used
methods = {}
for r in data['results']:
    if 'result' in r:
        method = r['result'].get('method', 'unknown')
        methods[method] = methods.get(method, 0) + 1

print("\nDetection methods:")
for method, count in methods.items():
    print(f"  {method}: {count}")
```

---

## Step 2: Decision Point - Is Detection Good Enough?

###  If Detection Rate > 90% and Mostly Templates

**Proceed to Strategy Testing:**

```powershell
# Test strategy with video simulation
python simulate_strategy.py roleta_brazileria.mp4 --config config/default_config.json --max-spins 50
```

This will:
- Use your detected numbers
- Apply Even/Odd strategy logic
- Show bet decisions
- Track streaks and cycles
- Generate statistics

###  If Detection Rate 70-90% or Too Many OCR Detections

**Improve Detection First:**

1. **Capture More Templates**
   ```powershell
   # Use snapshot capture to get more templates
   python capture_even_odd_from_snapshot.py
   # Or use the template capture tools
   ```

2. **Check Which Numbers Are Missing**
   - Review JSON results
   - Find frames where detection failed
   - Capture templates for those numbers

3. **Adjust Template Threshold** (if needed)
   ```json
   {
     "detection": {
       "winning_template_threshold": 0.60  // Lower = more matches (but more false positives)
     }
   }
   ```

###  If Detection Rate < 70%

**Fix Detection Issues:**

1. **Verify screen_region is correct**
   - Check if coordinates match your video
   - Region should cover the winning number display

2. **Capture templates for all numbers (0-36)**
   - Use snapshot capture tools
   - Ensure templates are clear and match video quality

3. **Disable OCR if causing false positives**
   ```json
   {
     "detection": {
       "enable_ocr_fallback": false  // Rely only on templates
     }
   }
   ```

4. **Re-test detection**
   ```powershell
   python test_video.py roleta_brazileria.mp4 --config config/default_config.json --max-frames 100
   ```

---

## Step 3: Strategy Testing (If Detection is Good)

### 3.1 Test Strategy Logic

```powershell
# Basic strategy test
python simulate_strategy.py roleta_brazileria.mp4 --config config/default_config.json --max-spins 50
```

**What to verify:**
-  Streaks are tracked correctly (Even/Odd counts)
-  Entry triggers when streak = 5
-  Bets are placed against the streak
-  Gale progression works (doubles on loss)
-  Cycles start and end properly
-  Win/loss determination is correct

### 3.2 Check Strategy Output

Look for:
```
[Spin 1] Detected: 2 (even)  Even streak: 1
[Spin 2] Detected: 4 (even)  Even streak: 2
...
[Spin 5] Detected: 10 (even)  Even streak: 5  ENTRY!
   Betting ODD with 10.0
[Spin 6] Detected: 12 (even)  LOSS  Gale step 1
   Betting ODD with 20.0
```

### 3.3 Review Strategy Statistics

After simulation, check:
- Win rate (should be ~48-50% for Even/Odd)
- Number of cycles started
- Average profit/loss per cycle
- Max drawdown

---

## Step 4: Coordinate Testing (If Strategy Works)

### 4.1 Verify Even/Odd Coordinates

Make sure coordinates are correct:
```json
{
  "betting": {
    "betting_areas": {
      "even": [907, 905],
      "odd": [1111, 906]
    }
  }
}
```

### 4.2 Test Coordinates Manually (Optional)

You can test if coordinates are correct by checking the video frames:
- Frame 7642: Check if [907, 905] is over Even area
- Frame 7645: Check if [1111, 906] is over Odd area

---

## Step 5: Full Integration Test

### 5.1 Test Mode (No Real Bets)

```powershell
# Test with live game (no actual betting)
python backend/app/bot.py --test --config config/default_config.json
```

**What to verify:**
-  Detection works on live game
-  Strategy logic executes
-  Bet decisions are calculated
-  Coordinates are correct (watch mouse movement)
-  No errors or crashes

### 5.2 Monitor for 5-10 Minutes

Watch the console output:
- Detection results
- Strategy decisions
- Bet calculations
- Any errors

---

## Step 6: Small Stakes Testing (If Everything Works)

### 6.1 Prepare for Live Testing

**Update config for safe testing:**
```json
{
  "strategy": {
    "base_bet": 1.0,  // Very small
    "max_gales": 3,   // Fewer steps
    "streak_length": 5
  },
  "risk": {
    "stop_loss": 50.0,  // Low stop loss
    "stop_win": 20.0,    // Low stop win
    "stop_loss_count": 3,
    "stop_win_count": 5
  }
}
```

### 6.2 Run Small Stakes Test

```powershell
# Production mode with small stakes
python backend/app/bot.py --config config/default_config.json
```

**Monitor closely:**
- First 10-20 spins
- Check logs regularly
- Verify bets are placed correctly
- Watch balance changes

---

## Quick Decision Tree

```
Detection Test Results
│
├─ Detection Rate > 90%?
│  │
│  ├─ YES  Strategy Testing
│  │        │
│  │        ├─ Strategy works?
│  │        │  │
│  │        │  ├─ YES  Coordinate Testing  Full Integration  Small Stakes
│  │        │  │
│  │        │  └─ NO  Check strategy logic, review logs
│  │        │
│  │        └─ Mostly templates?
│  │           │
│  │           ├─ YES  Good, proceed
│  │           │
│  │           └─ NO  Capture more templates
│  │
│  └─ NO  Improve Detection
│         │
│         ├─ Capture more templates
│         ├─ Adjust threshold
│         ├─ Disable OCR if needed
│         └─ Re-test
```

---

## Recommended Next Steps (Based on Your Test)

### If Detection is Good (>90%):

1. **Test Strategy** (5 minutes)
   ```powershell
   python simulate_strategy.py roleta_brazileria.mp4 --max-spins 50
   ```

2. **Review Strategy Output** (5 minutes)
   - Check if streaks tracked correctly
   - Verify entry conditions
   - Confirm bet decisions

3. **Test Coordinates** (5 minutes)
   - Verify Even/Odd coordinates are correct
   - Test manually if needed

4. **Full Integration Test** (10-15 minutes)
   - Test mode with live game
   - Monitor for errors

### If Detection Needs Improvement:

1. **Analyze Failed Detections** (10 minutes)
   - Check which frames failed
   - Identify missing numbers

2. **Capture Missing Templates** (20-30 minutes)
   - Use snapshot capture
   - Get templates for missing numbers

3. **Re-test Detection** (5 minutes)
   - Run test_video.py again
   - Verify improvement

4. **Then proceed to Strategy Testing**

---

## What to Check in Your Test Results

### Key Metrics:

1. **Detection Rate**
   - Target: >90%
   - Your result: _____%

2. **Method Distribution**
   - template_badge: _____ (should be most)
   - template: _____
   - ocr: _____ (should be few/none)
   - color_fallback: _____ (should be none)

3. **False Positives**
   - Frames with wrong numbers: _____
   - Frames with no number but detected: _____ (should be 0)

4. **Missing Detections**
   - Frames with numbers but not detected: _____
   - Which numbers are missing: _____

---

## Action Items Checklist

Based on your test results, check off what applies:

### Detection Analysis
- [ ] Checked detection rate
- [ ] Reviewed method distribution
- [ ] Identified false positives
- [ ] Found missing detections
- [ ] Analyzed JSON results file

### If Detection is Good
- [ ] Test strategy simulation
- [ ] Verify streak tracking
- [ ] Check entry conditions
- [ ] Test coordinate accuracy
- [ ] Run full integration test

### If Detection Needs Work
- [ ] Capture missing templates
- [ ] Adjust template threshold
- [ ] Disable OCR if needed
- [ ] Re-test detection
- [ ] Verify improvement

---

## Expected Timeline

- **Detection Analysis**: 5-10 minutes
- **Strategy Testing**: 10-15 minutes
- **Coordinate Verification**: 5 minutes
- **Full Integration Test**: 15-20 minutes
- **Total**: ~30-50 minutes

---

## Questions to Answer

After reviewing your test results, answer:

1. **What's your detection rate?** _____%
2. **Which method is used most?** _____
3. **Are there false positives?** Yes/No
4. **Are there missing detections?** Yes/No
5. **Is detection good enough to proceed?** Yes/No

Based on your answers, follow the appropriate path above.

---

## Need Help?

If you're unsure about your results:
1. Share the detection rate and method distribution
2. Check if there are many OCR detections
3. Review the JSON results file
4. Then we can decide next steps together

---

**Remember**: It's better to fix detection issues now than to have problems later with strategy execution!

