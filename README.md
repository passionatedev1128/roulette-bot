# Brazilian Roulette Bot

Automated roulette betting bot using screen detection and mouse automation.

## Features

- **Screen Detection**: Automatically detects roulette results using OpenCV and OCR
- **Multiple Strategies**: Supports Martingale, Fibonacci, and custom betting sequences
- **Automated Betting**: Places bets using mouse automation (pyautogui)
- **Gale System**: Implements Martingale progression with configurable limits
- **Zero Handling**: Configurable rules for handling zero (0) results
- **Comprehensive Logging**: Logs all spins, bets, and outcomes in CSV and JSON formats
- **Risk Management**: Stop-loss and guarantee fund protection

## Requirements

- Python 3.12+
- Tesseract OCR (for number detection)
- Windows/Linux/macOS

## Installation

1. **Clone or download the project**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Tesseract OCR:**
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

4. **Configure the bot:**
   - Edit `config/default_config.json` with your settings
   - Set betting area coordinates
   - Configure strategy parameters

## Configuration

Edit `config/default_config.json` to configure:

- **Detection**: Screen region, color ranges, template paths
- **Strategy**: Betting strategy type, base bet, max gales
- **Betting**: Betting area coordinates, delays, confirm button
- **Risk**: Initial balance, stop loss, guarantee fund
- **Session**: Maintenance bet intervals

### Key Configuration Options

```json
{
  "strategy": {
    "type": "martingale",  // "martingale", "fibonacci", "custom"
    "base_bet": 10.0,
    "max_gales": 5,
    "multiplier": 2.0
  },
  "betting": {
    "betting_areas": {
      "red": [500, 400],    // X, Y coordinates
      "black": [600, 400]
    }
  },
  "risk": {
    "initial_balance": 1000.0,
    "stop_loss": 500.0
  }
}
```

## Usage

### Basic Usage

```bash
python main.py
```

### With Custom Config

```bash
python main.py --config config/my_config.json
```

### Test Mode

```bash
python main.py --test
```

## Project Structure

```
roulette-bot/
├── backend/
│   ├── app/
│   │   ├── detection/      # Screen detection module
│   │   ├── strategy/        # Betting strategies
│   │   ├── betting/         # Bet automation
│   │   ├── logging/         # Logging module
│   │   ├── bot.py           # Main bot orchestrator
│   │   └── config_loader.py # Configuration loader
│   └── tests/               # Unit tests
├── config/                  # Configuration files
├── logs/                    # Log files (generated)
├── templates/               # Number templates for detection
├── main.py                  # Entry point
└── requirements.txt         # Python dependencies
```

## Modules

### Screen Detection (`detection/screen_detector.py`)
- Captures screen/video frames
- Detects winning number using OCR and template matching
- Detects color (red/black/green)
- Validates detection results

### Strategy (`strategy/`)
- **MartingaleStrategy**: Doubles bet after each loss
- **FibonacciStrategy**: Uses Fibonacci sequence progression
- **CustomStrategy**: User-defined betting sequence

### Betting (`betting/bet_controller.py`)
- Places bets using mouse automation
- Human-like delays and interactions
- Verifies bet placement

### Logging (`logging/logger.py`)
- Logs all spins to CSV and JSON
- Tracks statistics (win rate, profit/loss)
- Error logging

## Calibration

Before first use, you need to:

1. **Set betting area coordinates:**
   - Take screenshot of roulette table
   - Identify coordinates for red, black, green betting areas
   - Update `config/default_config.json`

2. **Create number templates (optional but recommended):**
   - Capture screenshots of numbers 0-36
   - Save as `templates/number_0.png`, `templates/number_1.png`, etc.
   - Improves detection accuracy

3. **Test detection:**
   - Run bot in test mode
   - Verify detection accuracy
   - Adjust color ranges if needed

## Logs

Logs are saved in `logs/` directory:

- `roulette_log_YYYYMMDD_HHMMSS.csv` - CSV log with all spins
- `roulette_log_YYYYMMDD_HHMMSS.json` - JSON log
- `errors_YYYYMMDD_HHMMSS.log` - Error log
- `summary_YYYYMMDD_HHMMSS.json` - Statistics summary

## Safety Features

- **Failsafe**: Move mouse to corner to stop bot (pyautogui failsafe)
- **Stop Loss**: Automatically stops when balance reaches stop loss
- **Max Gales**: Limits maximum gale progression steps
- **Error Handling**: Logs errors and continues operation

## Troubleshooting

### Detection Issues
- **Low accuracy**: Create number templates or adjust color ranges
- **Missing results**: Check screen region configuration
- **Wrong colors**: Calibrate HSV color ranges

### Betting Issues
- **Bets not placing**: Check betting area coordinates
- **Double betting**: Verify bet detection logic
- **Wrong amounts**: Check bet amount calculation

### Performance Issues
- **Slow detection**: Reduce screen region size
- **High CPU**: Optimize image processing
- **Memory leaks**: Restart bot periodically

## Development

### Running Tests

```bash
pytest backend/tests/
```

### Code Structure

- Modular design for easy extension
- Strategy pattern for betting strategies
- Configuration-driven behavior
- Comprehensive error handling

## License

This project is for educational purposes only. Use at your own risk.

## Disclaimer

Gambling involves risk. This bot is provided as-is without warranty. Use responsibly and within legal boundaries.

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review configuration settings
3. Test detection accuracy
4. Verify betting area coordinates

