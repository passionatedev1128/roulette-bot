"""
Brazilian Roulette Bot - Main Entry Point
"""

import argparse
import sys
from pathlib import Path

from backend.app.bot import RouletteBot


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Brazilian Roulette Bot')
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (simulation only)'
    )
    
    args = parser.parse_args()
    
    # Check if config exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        print("Please create a configuration file or use --config to specify one.")
        sys.exit(1)
    
    try:
        # Initialize bot
        bot = RouletteBot(str(config_path), test_mode=args.test)
        
        # Run bot
        if args.test:
            print("Running in test mode (no real bets will be placed)...")
        bot.run()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

