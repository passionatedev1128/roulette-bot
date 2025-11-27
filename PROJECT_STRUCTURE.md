# Project Structure

This document describes the organization of the Roulette Bot project.

## Directory Structure

```
roulette-bot/
├── README.md                    # Main project documentation
├── PROJECT_STRUCTURE.md         # This file
├── requirements.txt              # Python dependencies
├── main.py                      # Standalone bot entry point
├── start_web_interface.py       # Start web interface server
│
├── backend/                     # Backend application
│   ├── app/                     # Core bot logic
│   │   ├── bot.py              # Main bot orchestrator
│   │   ├── config_loader.py    # Configuration loader
│   │   ├── detection/          # Screen detection module
│   │   ├── strategy/           # Betting strategies
│   │   ├── betting/            # Bet automation
│   │   └── logging/            # Logging module
│   ├── server/                 # FastAPI server
│   │   ├── app.py             # FastAPI application
│   │   ├── websocket.py       # WebSocket handler
│   │   ├── bot_manager.py     # Bot state manager
│   │   ├── routes/             # API endpoints
│   │   └── events.py          # Event dispatcher
│   └── tests/                  # Unit tests
│
├── web/                        # Frontend React application
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── api/               # API client
│   │   ├── hooks/             # React hooks
│   │   └── utils/             # Utilities
│   ├── package.json
│   └── vite.config.js
│
├── config/                     # Configuration files
│   ├── default_config.json     # Default configuration
│   └── presets/                # Configuration presets
│
├── scripts/                    # Utility and diagnostic scripts
│   ├── README.md              # Scripts documentation
│   ├── diagnose_*.py          # Diagnostic tools
│   ├── capture_*.py           # Template capture tools
│   ├── test_*.py              # Test utilities
│   └── ...
│
├── tests/                      # Test scripts
│   ├── README.md              # Tests documentation
│   ├── test_*.py              # Test files
│   └── ...
│
├── docs/                       # Documentation
│   ├── README.md              # Full documentation
│   ├── archive/               # Archived documentation
│   └── *.md                   # Various guides
│
├── logs/                       # Log files (generated)
├── winning-number_templates/  # Number detection templates
└── betting-number_templates/  # Betting area templates
```

## Key Files

### Entry Points
- `main.py` - Standalone bot (no web interface)
- `start_web_interface.py` - Start full application with web interface

### Configuration
- `config/default_config.json` - Main configuration file

### Documentation
- `README.md` - Quick start and overview
- `docs/README.md` - Comprehensive documentation
- `PROJECT_STRUCTURE.md` - This file

## File Organization

### Scripts (`scripts/`)
Utility scripts for development, testing, and troubleshooting:
- Diagnostic tools
- Template creation
- Coordinate capture
- Analysis tools

### Tests (`tests/`)
Test scripts for various components:
- Integration tests
- Component tests
- Test utilities

### Documentation (`docs/`)
- Main documentation in root of `docs/`
- Archived/old documentation in `docs/archive/`

## Ignored Files

The following are excluded from version control (see `.gitignore`):
- Log files (`logs/`, `*.log`)
- Test outputs (`test_results/`, debug directories)
- Media files (`*.mp4`, `*.png`, except templates)
- Configuration backups
- Python cache files
- Node modules

## Development Workflow

1. **Configuration**: Edit `config/default_config.json`
2. **Development**: Use scripts in `scripts/` for testing
3. **Testing**: Run tests from `tests/` directory
4. **Documentation**: Update `docs/` as needed

