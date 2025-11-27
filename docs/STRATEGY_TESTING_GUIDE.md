# Strategy Testing Guide

This guide explains how to test your bot's strategy using video files instead of live gameplay.

## Overview

The bot now supports:
1. **Game State Detection** - Detects whether the game is in betting phase, spinning, or showing results
2. **Strategy Simulation** - Test strategy logic using recorded video files
3. **Frame-based Detection** - Use video frames instead of live screen capture

---

## Quick Start: Testing Strategy with Video

### 1. Basic Strategy Test

Run the simulation script with your video file:

```powershell
python simulate_strategy.py roleta_brazileria.mp4 --config config/default_config.json
```

This will:
- Load your video file
- Detect winning numbers frame by frame
- Apply your strategy (Martingale, Fibonacci, etc.)
- Log all bet decisions and outcomes
- Generate statistics

### 2. Advanced Options

```powershell
# Limit to first 50 spins
python simulate_strategy.py roleta_brazileria.mp4 --max-spins 50

# Add delay between spins (useful for debugging)
python simulate_strategy.py roleta_brazileria.mp4 --delay 1.0

# Quiet mode (less output)
python simulate_strategy.py roleta_brazileria.mp4 --quiet
```

### 3. What Gets Logged

The simulation creates logs in `logs/` directory:
- **CSV files**: Detailed spin-by-spin records
- **JSON summary**: Overall statistics
- **Console output**: Real-time bet decisions and strategy progression

---

## Game State Detection

### What It Does

Game state detection helps the bot know:
- **BETTING_OPEN**: Players can place bets
- **SPINNING**: Wheel is spinning, no bets accepted
- **RESULT_SHOWN**: Result is displayed, ready to process
- **PAUSED**: Game is paused/maintenance

### How to Enable

Add to `config/default_config.json`:

```json
{
  "detection": {
    "enable_game_state": true,
    "game_state_method": "result_based",
    "betting_indicator_region": [x, y, width, height],
    "spinning_indicator_region": [x, y, width, height],
    "timer_region": [x, y, width, height]
  }
}
```

### Detection Methods

1. **result_based** (default, recommended)
   - Infers state from detection results
   - No additional configuration needed
   - Works automatically with existing detection

2. **template** (advanced)
   - Uses template matching on UI elements
   - Requires capturing templates for each state
   - More accurate but needs setup

### Configuration

**For result_based method:**
- Just set `"enable_game_state": true`
- No additional regions needed
- Works out of the box

**For template method:**
- Capture screenshots of each state:
  - `state-templates/betting_open.png`
  - `state-templates/spinning.png`
  - `state-templates/result_shown.png`
  - `state-templates/paused.png`
- Set `"game_state_method": "template"`
- Optionally configure regions for faster matching

---

## Understanding the Output

### Console Output Example

```
[Spin 1] Detected: 22 (red)
  Method: template_badge, Confidence: 0.95
   Bet decision: black - 10.0 (Gale step: 0)
   Bet placed (simulated - no actual bet in test mode)

[Spin 2] Detected: 15 (black)
  Method: template_badge, Confidence: 0.92
   Bet decision: red - 20.0 (Gale step: 1)
   Bet placed (simulated - no actual bet in test mode)
```

### Log Files

Check `logs/roulette_log_*.csv` for:
- Spin number
- Detected number and color
- Bet type and amount
- Gale step
- Balance changes
- Win/loss status

---

## Strategy Testing Workflow

### Step 1: Prepare Your Video

- Ensure video contains clear winning number displays
- Video should be from the same casino interface you'll use live
- Longer videos = more comprehensive testing

### Step 2: Run Simulation

```powershell
python simulate_strategy.py roleta_brazileria.mp4 --config config/default_config.json --max-spins 100
```

### Step 3: Analyze Results

1. **Check Detection Rate**
   - Look for `Method: template_badge` (fast, accurate)
   - `Method: ocr` means you need more templates

2. **Review Strategy Behavior**
   - Verify gale progression (doubling after losses)
   - Check stop conditions (max gale, stop loss)
   - Confirm bet amounts match strategy config

3. **Examine Logs**
   - Open `logs/roulette_log_*.csv` in Excel/Google Sheets
   - Calculate win rate, profit/loss
   - Identify patterns or issues

### Step 4: Adjust and Retest

- Modify strategy parameters in `config/default_config.json`
- Add more winning number templates if needed
- Re-run simulation to validate changes

---

## Troubleshooting

### Issue: "No detections found"

**Solution:**
- Check `screen_region` in config matches video frame coordinates
- Verify winning number templates exist in `winning-numbers/`
- Run `test_video.py` first to validate detection

### Issue: "Strategy not placing bets"

**Possible causes:**
- Strategy conditions not met (check entry logic)
- Balance too low (check stop loss settings)
- Max gale reached (check `max_gales` in config)

### Issue: "Game state always UNKNOWN"

**Solution:**
- Ensure `enable_game_state: true` in config
- For template method, verify templates exist
- Check regions are correctly configured

---

## Integration with Main Bot

### Using Frame Detector in Production

You can use `FrameDetector` with the main bot for testing:

```python
from backend.app.bot import RouletteBot
from backend.app.detection.frame_detector import FrameDetector

bot = RouletteBot("config/default_config.json", test_mode=True)
bot.detector = FrameDetector(bot.config, "roleta_brazileria.mp4")

# Run bot (will use video frames)
bot.run()
```

### Switching Back to Live

Simply don't replace the detector:

```python
bot = RouletteBot("config/default_config.json", test_mode=False)
# bot.detector is already ScreenDetector (default)
bot.run()
```

---

## Best Practices

1. **Test with Multiple Videos**
   - Different lighting conditions
   - Various number ranges
   - Different video qualities

2. **Validate Detection First**
   - Run `test_video.py` before strategy simulation
   - Ensure >90% detection rate
   - Fix detection issues before testing strategy

3. **Start Small**
   - Test with `--max-spins 10` first
   - Verify behavior matches expectations
   - Scale up to longer tests

4. **Monitor Logs**
   - Check logs after each test run
   - Look for errors or unexpected behavior
   - Keep logs for comparison

5. **Document Changes**
   - Note config changes between tests
   - Track which videos were used
   - Record results for each configuration

---

## Next Steps

After successful strategy testing:

1. **Validate on Live Test Mode**
   - Run bot with `--test` flag on live casino
   - Monitor for any differences from simulation

2. **Gradual Rollout**
   - Start with minimal stakes
   - Monitor closely for first sessions
   - Scale up as confidence grows

3. **Continuous Improvement**
   - Capture more winning number templates
   - Refine strategy parameters based on results
   - Update game state detection if needed

---

## Files Reference

- `simulate_strategy.py` - Main strategy testing script
- `test_video.py` - Video detection testing
- `backend/app/detection/game_state_detector.py` - Game state detection module
- `backend/app/detection/frame_detector.py` - Video frame detector
- `config/default_config.json` - Bot configuration

---

## Support

If you encounter issues:
1. Check logs in `logs/` directory
2. Review console output for error messages
3. Verify config file syntax
4. Ensure all dependencies are installed

