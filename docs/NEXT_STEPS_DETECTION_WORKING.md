# Next Steps - Detection Working 

##  What You've Completed

-  Captured Red (Vermelho) betting button coordinates
-  Captured Black (Preto) betting button coordinates
-  Created number templates (0-36)
-  Verified templates work correctly
-  **Fixed detection issues** 
-  **Test video detection working** 

---

## 📋 Next Steps (In Order)

### Step 1: Analyze Detection Results (Optional but Recommended)

**Check your detection accuracy:**

**Run:**
```bash
python analyze_results.py
```

**OR manually check:**
- Open the JSON result file in `test_results/`
- Check accuracy percentage
- Review which frames were detected correctly

**What to check:**
-  Detection rate > 80% (good)
-  Detection rate > 90% (excellent)
-  No false positives
-  Correct numbers detected

---

### Step 2: Test Full Detection Pipeline  (Do This Now!)

**Test detection + strategy together:**

**Run:**
```bash
python test_detection_pipeline.py roleta_brazileria.mp4
```

**What this tests:**
-  Detection works with templates
-  Strategy logic works
-  Full pipeline integration
-  Shows when bot would place bets (simulation)

**This simulates the full bot without placing actual bets!**

**What to check:**
-  Strategy receives detection results
-  Strategy makes decisions (when to bet)
-  Bet signals are generated correctly
-  No errors in pipeline

---

### Step 3: Configure Your Strategy

**File:** `config/default_config.json`

**Update strategy section:**

```json
"strategy": {
  "type": "martingale",
  "base_bet": 1.0,                // Start small for testing
  "max_gales": 5,                 // Maximum gale steps
  "multiplier": 2.0,              // Bet multiplier after loss
  "bet_color_pattern": "opposite", // Strategy pattern
  "zero_handling": {
    "rule": "continue_sequence",
    "reset_on_zero": false
  }
}
```

**Key settings:**
- `base_bet`: Your starting bet (e.g., 1.0 = R$ 1.00)
- `max_gales`: How many times to double after loss (1-10)
- `multiplier`: How much to multiply bet (usually 2.0 for Martingale)
- `bet_color_pattern`: "opposite", "same", or "custom"

**For testing:**
- Start with `base_bet: 1.0` (minimum bet)
- `max_gales: 3-5` (reasonable limit)
- `multiplier: 2.0` (standard Martingale)

---

### Step 4: Configure Risk Management

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
- Set `stop_loss` to a safe limit (e.g., 50% of balance)
- `guarantee_fund_percentage`: 20% is good

---

### Step 5: Test Betting Automation (When You Have Live Game)

** Important:** This requires a LIVE game, not video!

**When ready:**
```bash
python test_betting.py
```

**What this tests:**
-  Mouse moves to correct coordinates
-  Clicks work on betting buttons
-  Bets are placed in game
-  No errors occur

**For now:** Skip this until you have a live game.

---

### Step 6: Run Full Bot (When Ready)

**After all tests pass:**

```bash
python main.py
```

**This runs the complete bot:**
- Detects numbers from screen/video
- Executes strategy
- Places bets automatically
- Maintains session (30-min bets)

---

##  Quick Start (Right Now)

**Do these 2 things:**

### 1. Test Full Pipeline
```bash
python test_detection_pipeline.py roleta_brazileria.mp4
```

**This will show:**
-  Detection + strategy working together
-  When bot would place bets
-  Full simulation

### 2. Configure Strategy
- Update `config/default_config.json`
- Set `base_bet`, `max_gales`, etc.
- Set risk management limits

---

## 📊 Testing Checklist

**What you CAN test now (with video):**
-  Number detection with templates 
-  Detection accuracy 
- [ ] Full detection pipeline
- [ ] Strategy logic (simulation)
- [ ] Configuration settings

**What you CANNOT test yet (needs live game):**
- [ ] Actual betting clicks
- [ ] Bet confirmation
- [ ] Real-time interaction
- [ ] Session management

---

## 🚀 Recommended Order

**Right now (with video):**

1.  **Test detection pipeline** - `python test_detection_pipeline.py roleta_brazileria.mp4`
2.  **Configure strategy** - Update `config/default_config.json`
3.  **Configure risk** - Update risk settings in config

**Later (with live game):**

4. ⏳ **Test betting** - `python test_betting.py`
5. ⏳ **Run full bot** - `python main.py`

---

## 📝 Summary

**You've completed:**
-  Coordinates captured
-  Templates created and verified
-  Detection working correctly

**Next:**
1. **Test full pipeline** (detection + strategy)
2. **Configure strategy** (bet amounts, gales, etc.)
3. **Test betting** (when you have live game)
4. **Run bot live** (when ready)

---

##  Most Important Next Step

**Test the full pipeline:**

```bash
python test_detection_pipeline.py roleta_brazileria.mp4
```

**This will show you:**
-  If detection + strategy work together
-  When the bot would place bets
-  Full bot simulation

**After this, configure your strategy and you're almost ready!**

---

**Great progress! Detection is working - now test the full pipeline!** 

