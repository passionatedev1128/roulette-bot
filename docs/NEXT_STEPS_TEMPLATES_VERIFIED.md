# Next Steps - Templates Verified 

##  What You've Completed

-  Captured Red (Vermelho) betting button coordinates
-  Captured Black (Preto) betting button coordinates
-  Created number templates (0-36)
-  **Verified templates work correctly** 

---

## 📋 Next Steps (In Order)

### Step 1: Test Detection with Video  (Do This Now!)

**This is the most important test!**

**Run:**
```bash
python test_video.py roleta_brazileria.mp4
```

**What this tests:**
-  Can detect numbers from video frames using your templates
-  Detection accuracy with templates
-  Color detection (red/black/green)
-  Works with your video file

**Expected output:**
- JSON file with detection results
- Accuracy percentage (should be >80% with good templates)
- Frame-by-frame results

**What to check:**
-  Detection rate > 80% (good)
-  Detection rate > 90% (excellent)
-  No false positives (detecting numbers when none exist)
-  Detection rate < 80% (needs improvement)

---

### Step 2: Analyze Detection Results

**After running `test_video.py`, analyze results:**

**Run:**
```bash
python analyze_results.py
```

**OR manually check:**
- Open the JSON result file in `test_results/`
- Check accuracy percentage
- Review which frames were detected correctly
- Identify any issues

**What to look for:**
- Which numbers were detected correctly
- Which numbers had errors
- Overall accuracy percentage
- Any false positives

---

### Step 3: Test Full Detection Pipeline (Recommended)

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

---

### Step 4: Configure Your Strategy

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

---

### Step 5: Configure Risk Management

**File:** `config/default_config.json`

```json
"risk": {
  "initial_balance": 100.0,        // Your test balance
  "stop_loss": 50.0,               // Stop at 50% loss
  "guarantee_fund_percentage": 20  // Reserve 20% for gales
}
```

**For testing:**
- Set `initial_balance` to your test account balance
- Set `stop_loss` to a safe limit
- `guarantee_fund_percentage`: 20% is good

---

### Step 6: Test Betting Automation (When You Have Live Game)

** Important:** This requires a LIVE game, not video!

**When ready:**
```bash
python test_betting.py
```

**What this tests:**
-  Mouse moves to correct coordinates
-  Clicks work on betting buttons
-  Bets are placed in game

**For now:** Skip this until you have a live game.

---

### Step 7: Run Full Bot (When Ready)

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

**Do these 3 things:**

### 1. Test Detection with Video
```bash
python test_video.py roleta_brazileria.mp4
```

### 2. Check Results
- Look at JSON output file
- Check accuracy percentage
- Review detected numbers

### 3. If Accuracy is Good (>80%)
- Configure strategy in config file
- You're ready for live testing when you have access

### 4. If Accuracy is Low (<80%)
- See troubleshooting below
- May need to adjust screen_region
- May need to recreate templates

---

## 📊 Testing Checklist

**What you CAN test now (with video):**
-  Number detection with templates 
- [ ] Detection accuracy on video
- [ ] Color detection
- [ ] Strategy logic (simulation)
- [ ] Full detection pipeline
- [ ] Configuration settings

**What you CANNOT test yet (needs live game):**
- [ ] Actual betting clicks
- [ ] Bet confirmation
- [ ] Real-time interaction
- [ ] Session management

---

## 🚀 Recommended Order

**Right now (with video):**

1.  **Test detection** - `python test_video.py roleta_brazileria.mp4`
2.  **Analyze results** - `python analyze_results.py`
3.  **Test pipeline** - `python test_detection_pipeline.py roleta_brazileria.mp4`
4.  **Configure strategy** - Update `config/default_config.json`

**Later (with live game):**

5. ⏳ **Test betting** - `python test_betting.py`
6. ⏳ **Run full bot** - `python main.py`

---

## 🆘 Troubleshooting

### Detection accuracy is low?
- Check templates are clear and not blurry
- Verify screen_region in config covers number display
- Try different frames for templates

### False positives still happening?
- Make sure confidence threshold is 0.75 (already fixed)
- Verify templates are from single grid snapshot
- Check screen_region is correct

### Detection not working?
- Check config has `template_dir: "templates"`
- Verify detection method is set to "template" or "hybrid"
- Review test results JSON for errors

---

## 📝 Summary

**You've completed:**
-  Coordinates captured
-  Templates created and verified

**Next:**
1. **Test detection with video** (most important!)
2. Analyze results
3. Configure strategy
4. Test with live game when ready

---

##  Most Important Next Step

**Test your detection with video:**

```bash
python test_video.py roleta_brazileria.mp4
```

**This will show you:**
-  If templates work correctly on video
-  Detection accuracy
-  What needs improvement

**After this test, you'll know if everything is working!**

---

**Start with testing detection - that's the most important step!** 

