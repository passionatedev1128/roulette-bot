# Bot Standalone Operation Guide

##  Overview

The bot can run **completely independently** without the backend or web interface. This guide shows you how to run the bot standalone.

---

##  Bot Already Works Standalone!

The bot is designed to work independently. The backend/web interface is **optional** - it only provides:
- Web dashboard for monitoring
- WebSocket events for real-time updates
- API endpoints for control

**The bot core (`RouletteBot`) does NOT require backend to function.**

---

## 🚀 Running Bot Standalone

### Method 1: Using main.py (Recommended)

**Simple standalone execution:**

```bash
# Basic run (uses config/default_config.json)
python main.py

# With custom config
python main.py --config config/my_config.json

# Test mode (no real bets)
python main.py --test
```

**What happens:**
- Bot loads configuration
- Bot starts detection loop
- Bot processes results and places bets (if Full Auto Mode)
- All logs saved to `logs/` directory
- Bot runs until stopped (Ctrl+C) or stop conditions met

---

### Method 2: Using Python Directly

**Import and run:**

```python
from backend.app.bot import RouletteBot

# Initialize bot
bot = RouletteBot(
    config_path="config/default_config.json",
    test_mode=True  # Set to False for real bets
)

# Run bot
bot.run()
```

**Save as `run_bot_standalone.py`:**

```python
#!/usr/bin/env python3
"""
Standalone bot runner - no backend required.
"""

import sys
from pathlib import Path
from backend.app.bot import RouletteBot

def main():
    config_path = "config/default_config.json"
    
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    if not Path(config_path).exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("Roulette Bot - Standalone Mode")
    print("=" * 60)
    print(f"Config: {config_path}")
    print("Mode: Test (no real bets)")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    try:
        bot = RouletteBot(config_path, test_mode=True)
        bot.run()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Run:**
```bash
python run_bot_standalone.py
```

---

## 📋 Standalone Features

###  What Works Without Backend:

1. **Detection** - Full detection capabilities
2. **Strategy** - All betting strategies work
3. **Betting** - Can place bets (if not in test mode)
4. **Logging** - All logs saved to CSV and text files
5. **Stop Conditions** - StopLoss/StopWin work
6. **Statistics** - Stats calculated from logs

###  What Requires Backend:

1. **Web Dashboard** - Requires backend + frontend
2. **WebSocket Events** - Requires backend
3. **API Control** - Requires backend
4. **Real-time Monitoring** - Requires backend + frontend

---

## 🔧 Configuration for Standalone

**No special configuration needed!** The bot uses the same `config/default_config.json`.

**Optional: Disable features you don't need:**

```json
{
  "detection": {
    "enable_game_state": false  // Disable if not needed
  },
  "logging": {
    "logs_dir": "logs",
    "log_level": "INFO"  // Or "DEBUG" for more details
  }
}
```

---

## 📊 Monitoring Standalone Bot

### Method 1: Console Output

**Bot prints to console:**
- Detection results
- Bet decisions
- Win/loss results
- Balance updates
- Errors

**Example output:**
```
INFO: Detection succeeded: number=17 color=black method=template_badge confidence=0.92
INFO: Bet decision: even for 10.0 (reason: Entry triggered: 5 consecutive odd  betting even)
INFO: Bet placed successfully: even - 10.0
INFO: Round completed: win, Balance: 1010.0, Bet: even, Result: 18
```

---

### Method 2: Log Files

**All activity logged to:**

1. **CSV Log**: `logs/roulette_log_YYYYMMDD_HHMMSS.csv`
   - All spins, bets, results
   - Can be opened in Excel

2. **Text Log**: `logs/bot_log_YYYYMMDD_HHMMSS.txt`
   - Detailed debug information
   - All detection attempts
   - Errors and warnings

**Check logs:**
```bash
# View latest CSV log
cat logs/roulette_log_*.csv | tail -20

# View latest text log
tail -f logs/bot_log_*.txt
```

---

### Method 3: Statistics Export

**When bot stops, it exports summary:**

- Location: `logs/summary_YYYYMMDD_HHMMSS.json`
- Contains:
  - Total spins
  - Wins/losses
  - Profit/loss
  - Strategy stats
  - Stop trigger info

**View summary:**
```bash
cat logs/summary_*.json | python -m json.tool
```

---

## 🎮 Running Modes

### Test Mode (Recommended for Testing)

**No real bets placed:**
```bash
python main.py --test
```

**What happens:**
- Detection works normally
- Strategy calculates bets
- Bet placement is simulated (logged but not executed)
- Safe for testing

---

### Production Mode (Real Bets)

**Real bets placed:**
```bash
python main.py
# Or set test_mode=False in code
```

** WARNING**: This will place real bets! Make sure:
- Configuration is correct
- Balance is set appropriately
- Stop conditions are configured
- You understand the strategy

---

## 🔄 Stopping the Bot

### Graceful Stop

**Press `Ctrl+C`** - Bot will:
- Stop detection loop
- Resolve any pending bets
- Export final statistics
- Save logs
- Exit cleanly

---

### Stop Conditions

**Bot stops automatically if:**
- StopLoss reached (balance ≤ threshold)
- StopWin reached (profit ≥ threshold)
- Max gales reached
- Video ended (if using video file)

---

## 🐛 Troubleshooting

### Issue: Bot doesn't detect numbers

**Check:**
1. Screen region is correct: `python show_detection_region.py`
2. Templates exist: Check `winning-number_templates/` directory
3. Game window is visible and not minimized
4. Check logs for errors

---

### Issue: Bot places wrong bets

**Check:**
1. Betting coordinates in config
2. Strategy configuration
3. Test mode first: `python main.py --test`

---

### Issue: Bot stops immediately

**Check:**
1. Stop conditions in config
2. Logs for error messages
3. Video file (if using video mode)

---

## 📝 Example: Complete Standalone Session

```bash
# 1. Start bot in test mode
python main.py --test

# Output:
# INFO: RouletteBot initialized
# INFO: Starting roulette bot...
# INFO: Detection succeeded: number=17 color=black
# INFO: Bet decision: even for 10.0
# INFO: Bet placed successfully: even - 10.0
# ...

# 2. In another terminal, monitor logs
tail -f logs/bot_log_*.txt

# 3. Stop bot with Ctrl+C
# Bot exports summary and exits
```

---

## 🔗 Related Files

- `main.py` - Standalone entry point
- `backend/app/bot.py` - Bot core (works independently)
- `config/default_config.json` - Configuration
- `logs/` - All logs and statistics

---

##  Summary

**The bot is fully standalone:**
-  No backend required
-  No web interface required
-  Works with just `python main.py`
-  All features work independently
-  Logs everything for later analysis

**Backend/web interface is optional** - it only adds:
- Real-time monitoring dashboard
- Web-based control
- WebSocket events

**For standalone operation, just use `main.py`!**

