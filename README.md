# Brazilian Roulette Bot

Automated roulette betting bot with web interface, screen detection, and mouse automation.

## Features

- **Web Interface**: Real-time dashboard with statistics, bet history, and live results
- **Screen Detection**: Automatically detects roulette results using OpenCV and OCR
- **Multiple Strategies**: Supports Even/Odd, Martingale, Fibonacci, and custom betting sequences
- **Automated Betting**: Places bets using mouse automation (pyautogui)
- **Gale System**: Implements Martingale progression with configurable limits
- **Comprehensive Logging**: Logs all spins, bets, and outcomes in CSV and JSON formats
- **Risk Management**: Stop-loss and guarantee fund protection
- **Real-time Stats**: Daily performance, gale statistics, and strategy analysis

## Project Structure

```
roulette-bot/
├── backend/              # Backend API and bot logic
│   ├── app/             # Core application modules
│   │   ├── detection/   # Screen detection module
│   │   ├── strategy/    # Betting strategies
│   │   ├── betting/     # Bet automation
│   │   ├── logging/     # Logging module
│   │   └── bot.py       # Main bot orchestrator
│   ├── server/          # FastAPI server and WebSocket
│   │   ├── routes/      # API endpoints
│   │   └── websocket.py # WebSocket event handling
│   └── tests/           # Unit tests
├── web/                 # Frontend React application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── api/         # API client
│   │   └── hooks/       # React hooks
│   └── package.json
├── config/              # Configuration files
├── scripts/              # Utility and diagnostic scripts
├── tests/               # Test scripts
├── docs/                # Documentation
├── main.py              # Standalone bot entry point
├── start_web_interface.py  # Start web interface
└── requirements.txt     # Python dependencies
```

## Quick Start

### 1. Install Dependencies

**Backend (Python):**
```bash
pip install -r requirements.txt
```

**Frontend (Node.js):**
```bash
cd web
npm install
```

### 2. Configure the Bot

Edit `config/default_config.json` with your settings:
- Detection region coordinates
- Betting area coordinates
- Strategy parameters
- Risk management settings

### 3. Start the Application

**Option 1: Web Interface (Recommended)**
```bash
python start_web_interface.py
```
Then open `http://localhost:3000` in your browser.

**Option 2: Standalone Bot**
```bash
python main.py
```

## Web Interface

The web interface provides:
- **Real-time Dashboard**: Live bot status, balance, and statistics
- **Active Bet Panel**: Current bet information
- **Bet History**: Complete history of all bets
- **Performance Charts**: Daily performance and gale statistics
- **Configuration**: Easy configuration management
- **Mode Controls**: Start/stop bot and switch between modes

### Web Interface Features

- **Full Auto Mode**: Bot places bets automatically
- **Detection Only Mode**: Bot detects numbers but doesn't place bets
- **Demo Mode**: Test the interface with mock data (`?demo=true`)

## Configuration

Key configuration options in `config/default_config.json`:

```json
{
  "strategy": {
    "type": "even_odd",
    "base_bet": 10.0,
    "max_gales": 6,
    "multiplier": 1.75,
    "streak_length": 2
  },
  "betting": {
    "betting_areas": {
      "even": [x, y],
      "odd": [x, y]
    }
  },
  "risk": {
    "initial_balance": 1000.0,
    "stop_loss": 500.0
  }
}
```

## Requirements

- **Python**: 3.12+
- **Node.js**: 18+ (for web interface)
- **Tesseract OCR**: For number detection
- **Operating System**: Windows/Linux/macOS

## Documentation

- [Full Documentation](docs/README.md)
- [Web Interface Guide](docs/WEB_INTERFACE_ARCHITECTURE.md)
- [Strategy Guide](docs/EVEN_ODD_STRATEGY_GUIDE.md)
- [Testing Guide](docs/HOW_TO_TEST_THE_BOT.md)

## API Endpoints

- `GET /api/status` - Bot status
- `GET /api/balance` - Balance and statistics
- `GET /api/bets/active` - Active bet information
- `GET /api/bets/history` - Bet history
- `GET /api/stats/daily` - Daily performance statistics
- `GET /api/stats/gale` - Gale step statistics
- `GET /api/config/` - Get configuration
- `POST /api/config/` - Update configuration
- `POST /api/bot/start` - Start bot
- `POST /api/bot/stop` - Stop bot
- `WebSocket /ws/events` - Real-time events

## Safety Features

- **Failsafe**: Move mouse to corner to stop bot
- **Stop Loss**: Automatically stops when balance reaches stop loss
- **Max Gales**: Limits maximum gale progression steps
- **Error Handling**: Comprehensive error logging and recovery

## License

This project is for educational purposes only. Use at your own risk.

## Disclaimer

Gambling involves risk. This bot is provided as-is without warranty. Use responsibly and within legal boundaries.

