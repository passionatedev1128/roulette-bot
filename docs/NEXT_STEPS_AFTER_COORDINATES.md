# Next Steps After Capturing Coordinates

##  What You've Completed

-  Captured Red (Vermelho) betting button coordinates
-  Captured Black (Preto) betting button coordinates
-  Verified coordinates are correct

---

## 📋 Next Steps (In Order)

### Step 1: Verify Coordinates in Config File 

**Check:** `config/default_config.json`

Your coordinates should be in the `betting_areas` section:

```json
"betting": {
  "betting_areas": {
    "red": [968, 904],      // Your Red coordinates
    "black": [1039, 907]    // Your Black coordinates
  }
}
```

**Action:** If coordinates are already there, you're good! If not, add them.

---

### Step 2: Test Betting Automation (Critical!)

**Purpose:** Make sure the bot can actually click the buttons correctly.

**Run this test:**
```bash
python -c "from backend.app.betting.bet_controller import BetController; from backend.app.config_loader import load_config; config = load_config(); bc = BetController(config); bc.place_bet('red', 1.0)"
```

**OR create a simple test script:**

**File:** `test_betting.py`
```python
"""Test betting automation."""
from backend.app.betting.bet_controller import BetController
from backend.app.config_loader import load_config
import time

def test_betting():
    print("=" * 70)
    print("TESTING BETTING AUTOMATION")
    print("=" * 70)
    
    # Load config
    config = load_config()
    
    # Create bet controller
    bet_controller = BetController(config)
    
    print("\n  WARNING: This will place REAL bets!")
    print("Make sure you're using a test account or small amounts!")
    print("\nPress Enter to continue, Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    # Test Red bet
    print("\n1. Testing RED bet...")
    print("   Moving mouse to Red button in 3 seconds...")
    time.sleep(3)
    try:
        bet_controller.place_bet('red', 1.0)  # Minimum bet
        print("    Red bet placed successfully!")
    except Exception as e:
        print(f"    Error: {e}")
    
    time.sleep(2)
    
    # Test Black bet
    print("\n2. Testing BLACK bet...")
    print("   Moving mouse to Black button in 3 seconds...")
    time.sleep(3)
    try:
        bet_controller.place_bet('black', 1.0)  # Minimum bet
        print("    Black bet placed successfully!")
    except Exception as e:
        print(f"    Error: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nCheck your game to verify bets were placed correctly!")

if __name__ == '__main__':
    test_betting()
```

**What to check:**
-  Mouse moves to correct location
-  Click happens on the button
-  Bet is placed in the game
-  No errors occur

---

### Step 3: Test Number Detection (If Not Done)

**Purpose:** Make sure the bot can detect winning numbers correctly.

**Run:**
```bash
python test_video.py
```

**OR test on live game:**
```bash
python -c "from backend.app.detection.screen_detector import ScreenDetector; from backend.app.config_loader import load_config; import pyautogui; config = load_config(); detector = ScreenDetector(config); frame = pyautogui.screenshot(); import numpy as np; from PIL import Image; frame = np.array(frame); result = detector.detect_result(frame); print(f'Detected: {result}')"
```

**What to check:**
-  Can detect numbers (0-36)
-  Can determine color (red/black/green)
-  Accuracy is acceptable (>90%)

---

### Step 4: Configure Your Strategy

**File:** `config/default_config.json`

**Update strategy section:**

```json
"strategy": {
  "type": "martingale",           // or "fibonacci", "custom"
  "base_bet": 1.0,                // Your starting bet amount
  "max_gales": 5,                  // Maximum gale steps
  "multiplier": 2.0,               // Bet multiplier after loss
  "bet_color_pattern": "opposite", // Strategy: "opposite", "same", "custom"
  "zero_handling": {
    "rule": "continue_sequence",    // How to handle zero
    "reset_on_zero": false
  }
}
```

**Key settings:**
- `base_bet`: Minimum bet amount (e.g., 1.0 = R$ 1.00)
- `max_gales`: How many times to double after loss (1-10)
- `multiplier`: How much to multiply bet (usually 2.0 for Martingale)

---

### Step 5: Configure Risk Management

**File:** `config/default_config.json`

**Update risk section:**

```json
"risk": {
  "initial_balance": 100.0,        // Your starting balance
  "stop_loss": 50.0,               // Stop when balance reaches this
  "guarantee_fund_percentage": 20  // Reserve % for gale bets
}
```

**Important:**
- `initial_balance`: Your actual game balance
- `stop_loss`: Bot stops if balance drops to this amount
- `guarantee_fund_percentage`: Reserves this % for gale progression

---

### Step 6: Configure Session Management

**File:** `config/default_config.json`

**Update session section:**

```json
"session": {
  "maintenance_bet_interval": 1800,  // 30 minutes = 1800 seconds
  "min_bet_amount": 1.0              // Minimum bet for maintenance
}
```

**This ensures:**
- Bot places small bet every 30 minutes
- Prevents game from pausing/disconnecting
- Keeps session active 24/7

---

### Step 7: Test Full Bot (Dry Run)

**Before running live, test everything:**

**File:** `test_full_bot.py`
```python
"""Test full bot functionality."""
from backend.app.bot import RouletteBot
from backend.app.config_loader import load_config
import time

def test_bot():
    print("=" * 70)
    print("TESTING FULL BOT")
    print("=" * 70)
    
    # Load config
    config = load_config()
    
    # Create bot
    bot = RouletteBot(config)
    
    print("\n  WARNING: This will run the bot!")
    print("Make sure you're ready!")
    print("\nPress Enter to start, Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    print("\nStarting bot...")
    print("Bot will run for 60 seconds as a test...")
    print("Press Ctrl+C to stop early\n")
    
    try:
        # Run for 60 seconds
        start_time = time.time()
        while time.time() - start_time < 60:
            bot.run_cycle()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nBot stopped by user.")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    test_bot()
```

**What to check:**
-  Bot detects numbers correctly
-  Bot places bets when strategy says so
-  Bot places maintenance bets every 30 min
-  Bot handles errors gracefully
-  Logs are created correctly

---

### Step 8: Run Bot Live

**Once everything is tested:**

**Run the bot:**
```bash
python main.py
```

**OR run in background:**
```bash
python main.py > bot_output.log 2>&1 &
```

**Monitor logs:**
```bash
tail -f logs/bot.log
```

---

## 📊 Quick Checklist

Before running live, verify:

- [ ] Coordinates are correct in config
- [ ] Betting automation works (tested)
- [ ] Number detection works (tested)
- [ ] Strategy is configured correctly
- [ ] Risk limits are set appropriately
- [ ] Session management is configured
- [ ] You've tested with small amounts first
- [ ] You understand how the bot works
- [ ] You know how to stop the bot (Ctrl+C)

---

## 🚨 Important Reminders

1. **Start Small:** Test with minimum bets first (R$ 1.00)
2. **Monitor Closely:** Watch the bot for first few hours
3. **Check Logs:** Review logs regularly
4. **Stop Loss:** Make sure stop_loss is set correctly
5. **Balance:** Ensure you have enough balance for gale progression

---

## 🆘 Troubleshooting

### Bot doesn't place bets?
- Check coordinates are correct
- Verify game window is visible
- Check if confirm button is needed

### Bot doesn't detect numbers?
- Check screen_region in config
- Verify detection settings
- Test detection separately

### Bot places wrong bets?
- Verify betting_areas coordinates
- Check color mapping logic
- Review strategy configuration

---

## 📝 Next Actions

**Right now, do this:**

1.  **Verify config has coordinates** (should already be there)
2.  **Test betting automation** (create `test_betting.py` and run it)
3.  **Test number detection** (if not done yet)
4.  **Configure strategy** (update base_bet, max_gales, etc.)
5.  **Test full bot** (run `test_full_bot.py`)
6.  **Run bot live** (when ready)

---

**You're making great progress! The hardest part (coordinates) is done. Now it's just testing and configuration!** 🎉

