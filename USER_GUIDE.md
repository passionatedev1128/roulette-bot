# Roulette Bot - User Guide

A simple step-by-step guide to get your Roulette Bot up and running.

---

## Prerequisites

Before starting, make sure you have:

- **Python 3.12 or higher** installed
- **Node.js 18 or higher** (only for web interface)
- **Tesseract OCR** installed on your system

**Install Tesseract OCR:**
- **Windows**: Download from [here](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

---

## Quick Setup (3 Steps)

### Step 1: Install Dependencies

**Backend (Python):**
```bash
pip install -r requirements.txt
```

**Frontend (for web interface only):**
```bash
cd web
npm install
cd ..
```

### Step 2: Configure Settings

Open `config/default_config.json` and adjust these key settings:

```json
{
  "strategy": {
    "base_bet": 10.0,
    "max_gales": 6,
    "multiplier": 2.0
  },
  "risk": {
    "initial_balance": 1000.0,
    "stop_loss": 500.0
  }
}
```

**What each setting means:**
- `base_bet`: Your starting bet amount
- `max_gales`: Maximum gale progression steps
- `multiplier`: Bet multiplier for gale system (doubles bet after loss)
- `initial_balance`: Your starting balance
- `stop_loss`: Bot stops when balance reaches this amount

> **Note:** Betting coordinates are already configured. Only adjust if your screen resolution is different.

### Step 3: Start the Bot

**Option A: Web Interface (Recommended)**
```bash
python start_web_interface.py
```
1. Choose option **1** to start the backend
2. Open a **new terminal** and run the command again
3. Choose option **2** to start the frontend
4. Open your browser and go to: `http://localhost:3000`

**Option B: Standalone Bot (No Web Interface)**
```bash
python main.py
```

---

## Using the Web Interface

### Dashboard Features

Once you open `http://localhost:3000`, you'll see:

- **Live Status**: Bot status and current balance
- **Active Bet**: Information about the current bet
- **Bet History**: All previous bets
- **Statistics**: Performance charts and win rates

### Bot Modes

**Full Auto Mode** (Recommended)
- Bot automatically detects results and places bets
- Click "Start Bot" to begin

**Detection Only Mode**
- Bot only detects results (no betting)
- Useful for testing detection accuracy

### Control Buttons

- **Start Bot**: Begin automated betting
- **Stop Bot**: Pause the bot (can restart anytime)
- **View Config**: See and edit settings

---

## Important Settings

### Strategy Configuration

Edit `config/default_config.json`:

- **base_bet**: Starting bet amount (e.g., 10.0)
- **max_gales**: Maximum progression steps (recommended: 5-6)
- **multiplier**: How much to multiply bet after loss (typically 2.0)

### Risk Management

- **stop_loss**: Bot stops when balance reaches this amount
- **guarantee_fund_percentage**: Reserve this % of balance for gale bets (recommended: 20%)

---

## Test Before Live Betting

Always test first in **Detection Only Mode**:

1. Start the web interface
2. Set mode to "Detection Only"
3. Click "Start Bot"
4. Watch the dashboard to verify detection accuracy
5. Once satisfied, switch to "Full Auto Mode"

---

## How to Stop the Bot

**Normal Stop:**
- Click "Stop Bot" button in web interface
- Or press `Ctrl+C` in the terminal

**Emergency Stop:**
- Move your mouse to the top-left corner of the screen
- This triggers an immediate stop (safety feature)

---

## Monitoring Performance

The web dashboard shows:
- Current balance and profit/loss
- Win rate percentage
- Number of bets placed
- Gale statistics (how often gale system activates)

Check `logs/` folder for detailed CSV and JSON logs.

---

## Troubleshooting

**Bot not detecting results?**
- Make sure the roulette game window is visible
- Check that detection region coordinates in config are correct
- Verify Tesseract OCR is installed

**Bets not placing?**
- Ensure betting coordinates in config match your screen
- Check that the game window is not minimized
- Verify you have sufficient balance

**Web interface won't load?**
- Make sure both backend and frontend are running
- Check that ports 8000 (backend) and 3000 (frontend) are not in use
- Try refreshing the browser page

---

## Tips for Best Results

1. **Start Small**: Begin with small bet amounts to test
2. **Monitor Closely**: Watch the first few rounds closely
3. **Set Stop Loss**: Always configure a stop loss to protect your balance
4. **Check Logs**: Review logs regularly to understand bot performance
5. **Adjust Settings**: Fine-tune strategy based on your preferences

---

## Need Help?

- Check the `docs/` folder for detailed documentation
- Review logs in `logs/` folder for error messages
- Verify all dependencies are installed correctly

---

## Important Reminders

- **This bot is for educational purposes only**
- **Gambling involves risk - use responsibly**
- **Always test in Detection Only mode first**
- **Never leave the bot unattended without monitoring**
- **Set appropriate stop loss limits**

---

**That's it! You're ready to use the Roulette Bot. Good luck!**

