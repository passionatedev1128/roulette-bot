# Step-by-Step Guide: Testing Bot on luck.bet.br

This guide will walk you through setting up and testing the roulette bot on luck.bet.br.

## Prerequisites

1.  Bot code is ready (already done)
2.  Backend is running (via ngrok)
3.  Frontend is deployed on Vercel
4. 🌐 **Open luck.bet.br in your browser**
5. 🎰 **Have a roulette game ready to test**

---

## Step 1: Open the Roulette Game

1. **Open your browser**
2. **Go to:** `https://luck.bet.br`
3. **Log in** to your account (if needed)
4. **Navigate to the Roulette game**
   - Look for "Roleta" or "Roulette" in the games menu
   - Open the Brazilian roulette table
5. **Make sure the game window is visible and not minimized**
   - The betting table should be fully visible
   - You should see the roulette wheel and betting grid

---

## Step 2: Capture Betting Coordinates

The bot needs to know WHERE to click to place bets. You need to capture the coordinates for the betting areas.

### Option A: Use Coordinate Capture Tool (Recommended)

1. **Keep the game window open and visible**

2. **Open a new terminal** (keep game visible)

3. **Run the coordinate capture tool:**
   ```bash
   python coordinate_capture_tool.py
   ```

4. **Follow the on-screen prompts:**

   **For Even/Odd betting (most common):**
   
   - **Prompt 1: "Move mouse to EVEN betting area"**
     - Look at the betting grid on the roulette table
     - Find the "Even" or "Par" betting button/area
     - Move your mouse to the CENTER of that button/area
     - Press Enter
     - Wait 5 seconds (don't move mouse!)
     - Coordinates will be captured automatically
   
   - **Prompt 2: "Move mouse to ODD betting area"**
     - Find the "Odd" or "Ímpar" betting button/area
     - Move your mouse to the CENTER of that button/area
     - Press Enter
     - Wait 5 seconds (don't move mouse!)
     - Coordinates will be captured automatically

5. **The coordinates will be saved** to `even_odd_coordinates.json` or updated in your config

### Option B: Capture All Betting Areas

If you want to capture Red/Black areas too:

1. **Run the capture tool:**
   ```bash
   python capture_even_odd_coordinates.py
   ```

2. **Follow prompts for each area:**
   - Red (Vermelho) betting area
   - Black (Preto) betting area
   - Even (Par) betting area
   - Odd (Ímpar) betting area
   - Confirm button (if visible)

---

## Step 3: Update Configuration

After capturing coordinates, update your config file.

### Option A: If coordinates were saved automatically

1. **Check if coordinates were added to config:**
   ```bash
   # Check the config file
   cat config/default_config.json
   ```

2. **Verify the coordinates are correct:**
   - Look for `"betting_areas"` section
   - Should have entries like:
     ```json
     "betting": {
       "betting_areas": {
         "even": [x, y],
         "odd": [x, y],
         "red": [x, y],
         "black": [x, y]
       },
       "confirm_button": [x, y]
     }
     ```

### Option B: Manual Configuration

If coordinates weren't saved automatically:

1. **Open the config file:**
   ```bash
   # Open in your editor
   config/default_config.json
   ```

2. **Find the `betting` section** (around line 23)

3. **Update `betting_areas`** with your captured coordinates:
   ```json
   "betting": {
     "betting_areas": {
       "even": [907, 905],    // Replace with your captured coordinates
       "odd": [1111, 906],    // Replace with your captured coordinates
       "red": [970, 904],     // If captured
       "black": [1040, 906]   // If captured
     },
     "confirm_button": [1044, 949],  // If captured
     "requires_amount_entry": false,  // Set to true if game requires typing amount
     "human_delays": {
       "min": 0.1,
       "max": 0.5
     }
   }
   ```

4. **Save the config file**

---

## Step 4: Test Betting Coordinates

Before running the full bot, test that the coordinates work:

1. **Run the betting test script:**
   ```bash
   python test_betting.py
   ```

2. **This will:**
   - Move mouse to each betting area
   - Click (without placing real bet)
   - Verify coordinates are correct

3. **Watch the mouse movement:**
   - Mouse should move to the betting areas
   - Click should happen on the correct areas

4. **If coordinates are wrong:**
   - Re-run coordinate capture tool
   - Update config again
   - Test again

---

## Step 5: Configure Screen Detection

The bot needs to detect where the winning number is displayed.

1. **Check current detection settings** in `config/default_config.json`:
   ```json
   "detection": {
     "screen_region": [953, 511, 57, 55],  // Region where winning number appears
     "winning_templates_dir": "winning-number_templates/",
     "winning_template_threshold": 0.65
   }
   ```

2. **If winning number detection doesn't work:**
   - The screen region might need adjustment
   - Check if winning number appears in a different location
   - You may need to capture templates for the numbers

3. **Test screen detection:**
   ```bash
   python test_detection_pipeline.py
   ```

---

## Step 6: Set Up Strategy Configuration

Configure your betting strategy:

1. **Open config file:** `config/default_config.json`

2. **Check strategy settings** (around line 14):
   ```json
   "strategy": {
     "type": "even_odd",      // Strategy type
     "base_bet": 10.0,        // Starting bet amount
     "max_gales": 6,          // Maximum gales (doubling steps)
     "multiplier": 1.75,      // Bet multiplier for gales
     "streak_length": 2,      // Streak length to trigger bet
     "zero_policy": "neutral" // How to handle zero
   }
   ```

3. **Adjust as needed:**
   - `base_bet`: Minimum bet amount for the game
   - `max_gales`: How many times to double the bet
   - `multiplier`: How much to multiply bet (1.75 means 75% increase)

---

## Step 7: Configure Risk Settings

Set your risk management:

1. **Check risk settings** in config (around line 83):
   ```json
   "risk": {
     "initial_balance": 1000.0,        // Starting balance
     "stop_loss": 500.0,               // Stop if balance drops to this
     "guarantee_fund_percentage": 20   // Percentage to keep as safety
   }
   ```

2. **Adjust based on your account:**
   - Set `initial_balance` to your actual balance
   - Set `stop_loss` to your risk tolerance

---

## Step 8: Start the Backend Server

1. **Open a terminal**

2. **Start the backend:**
   ```bash
   # Option 1: Using helper script (with ngrok)
   python start_with_ngrok.py
   
   # Option 2: Manual start
   uvicorn backend.server.app:app --host 0.0.0.0 --port 8000
   ```

3. **Keep it running** (don't close this terminal)

4. **Copy the ngrok URL** (if using ngrok)
   - Example: `https://abc123.ngrok.io`

---

## Step 9: Verify Frontend is Configured

1. **Go to your Vercel site:** `https://roulette-bot-zeta.vercel.app`

2. **Check browser console** (F12):
   - Should see: "API Configuration: { API_BASE_URL: 'https://...' }"
   - Should show your ngrok URL, not localhost

3. **If not configured:**
   - Go to Vercel  Settings  Environment Variables
   - Set `VITE_API_URL` = your ngrok URL
   - Redeploy

---

## Step 10: Start Testing the Bot

### 10.1: Open the Web Interface

1. **Open your Vercel site:** `https://roulette-bot-zeta.vercel.app`

2. **You should see:**
   - Dashboard with status
   - Configuration panel
   - Control buttons (Start/Stop)

### 10.2: Configure the Bot

1. **In the web interface:**
   - Check strategy settings
   - Adjust base bet if needed
   - Set risk limits

2. **Make sure coordinates are correct:**
   - Can't verify from UI, but coordinates should be in config

### 10.3: Start the Bot (TEST MODE FIRST!)

**IMPORTANT:** Always start in TEST MODE first!

1. **In the web interface:**
   - Click **"Start Bot"** button
   - Select **"Test Mode"** (if option available)
   - Or make sure `test_mode: true` is set

2. **What Test Mode does:**
   - Detects numbers from screen/video
   - Makes betting decisions
   - BUT **does NOT click** (doesn't place real bets)
   - Logs everything for review

### 10.4: Monitor the Bot

1. **Watch the web interface:**
   - Status should show "Running"
   - Should see detected results
   - Should see betting decisions (in logs)

2. **Watch the browser window:**
   - Bot should be detecting winning numbers
   - Should show betting decisions

3. **Check logs:**
   - Look for successful detections
   - Check for any errors

### 10.5: Test for 5-10 Rounds

1. **Let bot run for several rounds**
2. **Verify:**
   - Number detection is working
   - Betting decisions make sense
   - No errors in logs

---

## Step 11: Test Real Betting (Small Amounts First!)

** WARNING:** Only do this after TEST MODE works correctly!

### 11.1: Start with Small Bets

1. **Set very small base bet:**
   - In config: `"base_bet": 1.0` (minimum bet)
   - Update via web interface or config file

2. **Set low max gales:**
   - `"max_gales": 2` (only 2 doubling steps)
   - Limits maximum bet amount

### 11.2: Start Bot in Production Mode

1. **Make sure TEST MODE is OFF**
2. **Click "Start Bot"**
3. **Monitor closely:**
   - Watch mouse movement
   - Verify clicks are on correct areas
   - Check that bets are actually placed

### 11.3: Watch First Few Bets

1. **Keep your hand near the mouse**
   - Be ready to move mouse to corner to stop (failsafe)
   - Or press Ctrl+C in terminal

2. **Verify:**
   - Mouse moves to betting area 
   - Click happens on correct area 
   - Bet appears in game 

---

## Step 12: Troubleshooting

### Issue: Bot doesn't detect numbers

**Solution:**
- Check `screen_region` in config matches winning number location
- Test detection: `python test_detection_pipeline.py`
- May need to capture number templates

### Issue: Bot clicks wrong place

**Solution:**
- Re-capture coordinates: `python coordinate_capture_tool.py`
- Update config with new coordinates
- Test coordinates: `python test_betting.py`

### Issue: Bot doesn't place bets

**Solution:**
- Check if `test_mode` is disabled
- Verify coordinates are correct
- Check if confirm button coordinate is needed
- Look for errors in logs

### Issue: CORS errors in browser

**Solution:**
- Check backend CORS includes Vercel domain
- Restart backend after setting CORS
- Verify ngrok is running

---

## Step 13: Full Production Setup

Once everything works in testing:

1. **Adjust strategy settings:**
   - Set your desired base bet
   - Set max gales
   - Configure stop loss

2. **Set risk limits:**
   - Initial balance
   - Stop loss threshold
   - Guarantee fund

3. **Monitor closely for first few hours:**
   - Watch bot behavior
   - Check balance changes
   - Verify all bets are placed correctly

---

## Quick Reference Commands

```bash
# Capture betting coordinates
python coordinate_capture_tool.py

# Test betting coordinates
python test_betting.py

# Test number detection
python test_detection_pipeline.py

# Start backend with ngrok
python start_with_ngrok.py

# Start backend manually
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000

# View config
cat config/default_config.json
```

---

## Important Notes

1.  **Always test in TEST MODE first**
2.  **Start with minimum bets**
3.  **Monitor closely for first few bets**
4.  **Keep failsafe enabled** (mouse to corner stops bot)
5.  **Don't leave bot unattended initially**
6.  **Keep game window visible and not minimized**
7.  **Don't move mouse manually while bot is running**

---

## Next Steps

After successful testing:
- Adjust strategy parameters
- Monitor performance
- Fine-tune detection settings
- Gradually increase bet amounts (if desired)

Good luck! 🎰🎲

