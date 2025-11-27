"""
Simple script to run the bot for testing.
This runs the bot directly without frontend/backend.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.app.bot import RouletteBot

def main():
    """Run bot in test mode."""
    config_path = "config/default_config.json"
    
    print("=" * 60)
    print("Starting Roulette Bot - Real-World Test")
    print("=" * 60)
    print(f"Config: {config_path}")
    print()
    print("IMPORTANT: Bot will move mouse and click!")
    print("   The bot will:")
    print("   1. Detect numbers from your screen (screen_region)")
    print("   2. Make betting decisions based on strategy")
    print("   3. Move mouse to betting positions (betting_areas)")
    print("   4. Click to place bets")
    print()
    print("Make sure:")
    print("   1. Video/game is playing and visible on screen")
    print("   2. screen_region in config matches winning number area")
    print("   3. betting_areas in config matches betting positions")
    print("   4. You're using a test account")
    print("   5. Press Ctrl+C to stop")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print()
    print("Starting bot...")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    print()
    print("Watch console for:")
    print("  - 'Detection: number=X' - Bot detected a number")
    print("  - 'Bet decision: ...' - Strategy made a betting decision")
    print("  - 'Moving mouse to betting area: (x, y)' - Mouse will move")
    print("  - 'Mouse moved and clicked at (x, y)' - Bet placed")
    print()
    print("If mouse doesn't move, check:")
    print("  - Are numbers being detected?")
    print("  - Is strategy making betting decisions?")
    print("  - Are betting coordinates correct?")
    print("-" * 60)
    print()
    
    try:
        # Create bot instance
        # Note: test_mode=True doesn't disable mouse - it's just a flag for logging
        # The mouse WILL move and click if betting decisions are made
        bot = RouletteBot(
            config_path=config_path,
            event_dispatcher=None,
            state_callback=None,
            test_mode=True
        )
        
        # Run bot
        bot.run()
        
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
        if 'bot' in locals():
            bot.stop()
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

