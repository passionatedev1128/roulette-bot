# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Important**: Install Tesseract OCR separately:
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`

## Step 2: Configure Betting Areas

1. Open `config/default_config.json`
2. Set coordinates for betting areas:
   ```json
   "betting_areas": {
     "red": [500, 400],    // Your red bet button coordinates
     "black": [600, 400]   // Your black bet button coordinates
   }
   ```
3. Set confirm button coordinates if needed

**How to find coordinates:**
- Use a tool like `pyautogui.position()` or screenshot tools
- Take screenshot of roulette table
- Identify pixel coordinates of betting buttons

## Step 3: Configure Strategy

Edit `config/default_config.json`:

```json
{
  "strategy": {
    "type": "martingale",  // or "fibonacci", "custom"
    "base_bet": 10.0,
    "max_gales": 5,
    "multiplier": 2.0
  }
}
```

## Step 4: Set Screen Region (Optional)

If you want to detect only part of screen:

```json
{
  "detection": {
    "screen_region": [0, 0, 1920, 1080]  // [x, y, width, height]
  }
}
```

Leave as `null` to capture full screen.

## Step 5: Create Number Templates (Recommended)

For better detection accuracy:

1. Capture screenshots of numbers 0-36 from roulette table
2. Save as `templates/number_0.png`, `templates/number_1.png`, etc.
3. Bot will use template matching instead of OCR

## Step 6: Test Detection

Run in test mode first:

```bash
python main.py --test
```

Or manually test detection:

```python
from backend.app.detection import ScreenDetector
from backend.app.config_loader import ConfigLoader

config = ConfigLoader.load_config('config/default_config.json')
detector = ScreenDetector(config)
result = detector.detect_result()
print(result)
```

## Step 7: Run the Bot

```bash
python main.py
```

## Important Notes

1. **Calibration Required**: You MUST set betting area coordinates before running
2. **Test First**: Always test with small bets first
3. **Monitor Closely**: Watch the bot during first few rounds
4. **Stop Loss**: Set appropriate stop loss in config
5. **Failsafe**: Move mouse to screen corner to emergency stop

## Troubleshooting

### "Betting area not found"
- Check coordinates in config
- Verify coordinates are correct for your screen resolution

### "Detection failed"
- Check screen region settings
- Try creating number templates
- Adjust color ranges in config

### "Insufficient funds"
- Check initial balance in config
- Verify stop loss settings

## Next Steps

1. Review logs in `logs/` directory
2. Analyze performance statistics
3. Adjust strategy parameters
4. Fine-tune detection settings

