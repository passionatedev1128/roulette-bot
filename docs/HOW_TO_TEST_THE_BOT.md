# How to Test the Roulette Bot - Complete Guide

## Quick Start Testing

### Option 1: Video Simulation (Recommended First Step)

Test the strategy logic using a recorded video file:

```powershell
python simulate_strategy.py roleta_brazileria.mp4 --config config/default_config.json --max-spins 50
```

**What this does:**
- Detects winning numbers from video frames
- Applies Even/Odd strategy logic
- Shows bet decisions and outcomes
- Generates statistics and logs

---

## Complete Testing Workflow

### Phase 1: Pre-Testing Setup

#### 1.1 Verify Configuration

Check your `config/default_config.json`:

```powershell
type config\default_config.json
```

**Verify:**
-  Strategy type is `"even_odd"`
-  Even/Odd coordinates are set: `"even": [907, 905]`, `"odd": [1111, 906]`
-  Base bet and risk settings are appropriate
-  Stop loss/win conditions are set

**Example valid config:**
```json
{
  "strategy": {
    "type": "even_odd",
    "base_bet": 10.0,
    "max_gales": 5,
    "streak_length": 5,
    "zero_policy": "count_as_loss"
  },
  "betting": {
    "betting_areas": {
      "even": [907, 905],
      "odd": [1111, 906]
    }
  }
}
```

#### 1.2 Check Dependencies

```powershell
# Install dependencies if needed
pip install -r requirements.txt
```

#### 1.3 Prepare Test Video (Optional but Recommended)

- Place video file in project root (e.g., `roleta_brazileria.mp4`)
- Video should show roulette results clearly
- At least 50-100 spins for meaningful testing

---

### Phase 2: Detection Testing

Before testing strategy, verify detection works:

#### 2.1 Test Video Detection

```powershell
python test_video.py roleta_brazileria.mp4 --config config/default_config.json --max-frames 100
```

**What to check:**
-  Detection rate > 90%
-  Numbers detected correctly
-  No major errors in console

**If detection fails:**
- Check `screen_region` in config matches video
- Verify winning number templates exist
- Adjust detection threshold if needed

#### 2.2 Test Detection on Specific Frames

```powershell
# Test first 60 seconds
python test_video.py roleta_brazileria.mp4 --start 0 --end 60
```

---

### Phase 3: Strategy Logic Testing

#### 3.1 Basic Strategy Simulation

```powershell
python simulate_strategy.py roleta_brazileria.mp4 --config config/default_config.json
```

**Watch for:**
- Entry conditions triggering (streak ≥ 5)
- Bet decisions (Even/Odd)
- Gale progression on losses
- Cycle start/end
- Win/loss outcomes

#### 3.2 Limited Spins Test

```powershell
# Test first 30 spins
python simulate_strategy.py roleta_brazileria.mp4 --max-spins 30 --config config/default_config.json
```

**What to verify:**
-  Streaks are tracked correctly
-  Entry triggers when streak = 5
-  Bets are placed against streak
-  Gale progression works (doubles on loss)
-  Cycles end on win or max gale

#### 3.3 Verbose Mode (See Details)

```powershell
# See detailed output
python simulate_strategy.py roleta_brazileria.mp4 --max-spins 20 --verbose
```

**Look for:**
```
[Spin 1] Detected: 2 (even)  Even streak: 1
[Spin 2] Detected: 4 (even)  Even streak: 2
...
[Spin 5] Detected: 10 (even)  Even streak: 5  ENTRY!
   Betting ODD with 10.0
[Spin 6] Detected: 12 (even)  LOSS  Gale step 1
   Betting ODD with 20.0
```

---

### Phase 4: Live Testing (Test Mode)

#### 4.1 Test Mode (No Real Bets)

```powershell
python backend/app/bot.py --test --config config/default_config.json
```

**What this does:**
- Connects to live game
- Detects results in real-time
- Calculates bets but doesn't place them
- Logs all decisions

**Watch for:**
-  Detection works on live game
-  Strategy logic executes correctly
-  Bet decisions are calculated
-  No errors or crashes

#### 4.2 Monitor Console Output

Look for:
```
INFO - Even/Odd strategy initialized
INFO - Detected: 2 (even)  Even streak: 1
INFO - Entry condition met: 5 consecutive Even  Betting Odd
INFO - Bet decision: ODD 10.0
```

---

### Phase 5: Coordinate Testing

#### 5.1 Test Even Coordinate

Create a simple test script or manually verify:

```python
import pyautogui
import time

# Test Even coordinate
even_coord = [907, 905]
pyautogui.moveTo(even_coord[0], even_coord[1])
time.sleep(2)
# Check if mouse is over Even betting area
```

#### 5.2 Test Odd Coordinate

```python
# Test Odd coordinate
odd_coord = [1111, 906]
pyautogui.moveTo(odd_coord[0], odd_coord[1])
time.sleep(2)
# Check if mouse is over Odd betting area
```

#### 5.3 Test Bet Placement (Manual)

```powershell
# Run bot in test mode and watch if it clicks correct areas
python backend/app/bot.py --test --config config/default_config.json
```

**Verify:**
- Mouse moves to Even area when betting Even
- Mouse moves to Odd area when betting Odd
- Coordinates are accurate

---

### Phase 6: Full Integration Testing

#### 6.1 Small Stakes Test (If Going Live)

**Before real betting:**
1. Set very small base_bet (e.g., 1.0 or 2.0)
2. Test for 1-2 hours
3. Monitor closely
4. Check logs

**Config for testing:**
```json
{
  "strategy": {
    "base_bet": 1.0,  // Very small for testing
    "max_gales": 3,   // Fewer gale steps
    "streak_length": 5
  },
  "risk": {
    "stop_loss": 50.0,  // Low stop loss
    "stop_win": 20.0    // Low stop win
  }
}
```

#### 6.2 Monitor Logs

```powershell
# Watch logs in real-time
Get-Content logs\roulette_log_*.log -Wait -Tail 50
```

**Check for:**
- Bet decisions
- Win/loss outcomes
- Cycle progression
- Errors or warnings

---

## Testing Checklist

### Pre-Testing
- [ ] Configuration file is correct
- [ ] Even/Odd coordinates are set
- [ ] Dependencies installed
- [ ] Test video available (optional)

### Detection Testing
- [ ] Video detection works (>90% accuracy)
- [ ] Numbers detected correctly
- [ ] No major errors

### Strategy Testing
- [ ] Streak tracking works
- [ ] Entry conditions trigger correctly
- [ ] Bets are calculated correctly
- [ ] Gale progression works
- [ ] Cycles start/end properly
- [ ] Win/loss determination works

### Coordinate Testing
- [ ] Even coordinate is correct
- [ ] Odd coordinate is correct
- [ ] Bet placement clicks right areas

### Integration Testing
- [ ] Live detection works
- [ ] Strategy executes correctly
- [ ] Logs are generated
- [ ] No crashes or errors

---

## Common Testing Scenarios

### Scenario 1: Test Streak Detection

**Expected behavior:**
```
Spin 1: 2 (even)  Even streak: 1
Spin 2: 4 (even)  Even streak: 2
Spin 3: 6 (even)  Even streak: 3
Spin 4: 8 (even)  Even streak: 4
Spin 5: 10 (even)  Even streak: 5  ENTRY!
```

**Test command:**
```powershell
python simulate_strategy.py video.mp4 --max-spins 10 --verbose
```

### Scenario 2: Test Gale Progression

**Expected behavior:**
```
Entry: Bet ODD 10.0
Loss 1: Bet ODD 20.0 (gale step 1)
Loss 2: Bet ODD 40.0 (gale step 2)
Loss 3: Bet ODD 80.0 (gale step 3)
Win: Cycle ends
```

**Test command:**
```powershell
python simulate_strategy.py video.mp4 --max-spins 20
```

### Scenario 3: Test Zero Handling

**Expected behavior (with `zero_policy: "count_as_loss"`):**
```
Cycle active, bet ODD 10.0
Result: 0 (zero)
 Counted as loss
 Next bet: ODD 20.0 (gale step 1)
```

**Test:** Look for zero outcomes in video and verify handling

### Scenario 4: Test Keepalive

**Expected behavior:**
```
29 minutes pass with no active cycle
 Keepalive bet: Random Even or Odd with 1.0 stake
```

**Test:** Run bot for 30+ minutes and watch for keepalive bets

---

## Testing Commands Reference

### Video Simulation

```powershell
# Basic test
python simulate_strategy.py video.mp4 --config config/default_config.json

# Limited spins
python simulate_strategy.py video.mp4 --max-spins 50

# Verbose output
python simulate_strategy.py video.mp4 --verbose

# With delay (for debugging)
python simulate_strategy.py video.mp4 --delay 1.0

# Quiet mode
python simulate_strategy.py video.mp4 --quiet
```

### Detection Testing

```powershell
# Test video detection
python test_video.py video.mp4 --config config/default_config.json

# Test specific time range
python test_video.py video.mp4 --start 0 --end 60

# Test with frame limit
python test_video.py video.mp4 --max-frames 100
```

### Live Testing

```powershell
# Test mode (no real bets)
python backend/app/bot.py --test --config config/default_config.json

# Production mode (real bets - use with caution!)
python backend/app/bot.py --config config/default_config.json
```

---

## What to Look For

###  Good Signs

- **Detection rate > 90%**: Most numbers detected correctly
- **Entry triggers correctly**: Bets when streak = 5
- **Gale progression works**: Doubles after losses
- **Cycles complete**: Start and end properly
- **Win/loss accurate**: Correctly determines outcomes
- **No errors**: Clean console output
- **Logs generated**: Files created in `logs/` directory

###  Warning Signs

- **Low detection rate**: < 80% - need more templates
- **Entry not triggering**: Check streak_length setting
- **Gale not working**: Check max_gales and multiplier
- **Wrong coordinates**: Bet clicks wrong areas
- **Errors in logs**: Review error messages
- **Crashes**: Check dependencies and configuration

---

## Troubleshooting

### Problem: Detection fails

**Solution:**
1. Check `screen_region` in config matches video
2. Verify winning number templates exist
3. Adjust `winning_template_threshold` (try 0.6-0.7)
4. Check video quality and resolution

### Problem: Strategy not entering

**Solution:**
1. Check `streak_length` - might be too high
2. Verify streak tracking is working
3. Check logs for streak counts
4. Try lowering `streak_length` to 3-4 for testing

### Problem: Wrong coordinates

**Solution:**
1. Re-run coordinate capture script
2. Verify coordinates manually
3. Test with mouse movement
4. Update config with correct coordinates

### Problem: Bot crashes

**Solution:**
1. Check Python version (3.7+)
2. Verify all dependencies installed
3. Check config file syntax (valid JSON)
4. Review error messages in console

---

## Testing Results Analysis

### After Testing, Review:

1. **Win Rate**: Should be ~48-50% (close to theoretical)
2. **Cycle Completion**: Most cycles should complete (win or max gale)
3. **Average Profit/Loss**: Track per cycle
4. **Max Drawdown**: Largest losing streak
5. **Detection Accuracy**: Should be > 90%

### Log Files to Check

- `logs/roulette_log_*.csv` - Detailed spin records
- `logs/roulette_log_*.json` - Summary statistics
- `bot.log` - General bot logs

---

## Next Steps After Testing

1. **If tests pass**: Gradually increase stakes
2. **If issues found**: Fix and retest
3. **Monitor closely**: Watch first few live sessions
4. **Adjust parameters**: Based on performance
5. **Set strict limits**: Stop loss/win before going live

---

## Quick Test Commands

```powershell
# 1. Quick detection test (30 seconds)
python test_video.py video.mp4 --start 0 --end 30

# 2. Quick strategy test (20 spins)
python simulate_strategy.py video.mp4 --max-spins 20

# 3. Quick live test (test mode, 5 minutes)
python backend/app/bot.py --test --config config/default_config.json
# (Stop after 5 minutes with Ctrl+C)
```

---

## Safety Reminders

 **Before Live Testing:**
- Always test in `--test` mode first
- Start with minimum stakes
- Set strict stop loss/win
- Monitor closely
- Have exit plan ready

 **Best Practice:**
1. Video simulation first
2. Test mode second
3. Small stakes third
4. Scale gradually

---

**Remember**: Testing is crucial! Don't skip it. Test thoroughly before risking real money.

