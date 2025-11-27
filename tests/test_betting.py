"""
Test betting automation.
This script tests if the bot can place bets correctly.
"""

from backend.app.betting.bet_controller import BetController
from backend.app.config_loader import load_config
import time
import sys


def test_betting():
    """Test betting automation with real clicks."""
    print("=" * 70)
    print("TESTING BETTING AUTOMATION")
    print("=" * 70)
    print("\nThis will test if the bot can place bets correctly.")
    print("  WARNING: This will place REAL bets on your game!")
    print("Make sure you're using a test account or small amounts!")
    print("\nThe bot will:")
    print("  1. Move mouse to Red button and click")
    print("  2. Move mouse to Black button and click")
    print("\nPress Enter to continue, Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    # Load config
    try:
        config = load_config()
        print("\n Config loaded successfully")
    except Exception as e:
        print(f"\n Error loading config: {e}")
        return
    
    # Create bet controller
    try:
        bet_controller = BetController(config)
        print(" Bet controller created")
    except Exception as e:
        print(f"\n Error creating bet controller: {e}")
        return
    
    # Get betting areas
    betting_areas = config.get('betting', {}).get('betting_areas', {})
    if not betting_areas.get('red') or not betting_areas.get('black'):
        print("\n Error: Red or Black coordinates not found in config!")
        print("   Make sure you've captured coordinates first.")
        return
    
    print(f"\nRed button coordinates: {betting_areas['red']}")
    print(f"Black button coordinates: {betting_areas['black']}")
    
    # Test Red bet
    print("\n" + "=" * 70)
    print("TEST 1: RED BET")
    print("=" * 70)
    print("\nIn 5 seconds, the bot will:")
    print("  - Move mouse to Red button")
    print("  - Click to place bet")
    print("  - Use minimum bet amount (R$ 1.00)")
    print("\nMake sure your game window is visible!")
    print("\nStarting in...")
    for i in range(5, 0, -1):
        print(f"  {i}...", end='\r')
        time.sleep(1)
    print("\n")
    
    try:
        result = bet_controller.place_bet('red', 1.0)
        if result:
            print(" Red bet placed successfully!")
            print("  Check your game to verify the bet was placed.")
        else:
            print(" Red bet failed (returned False)")
    except Exception as e:
        print(f" Error placing Red bet: {e}")
        import traceback
        traceback.print_exc()
    
    # Wait before next test
    print("\nWaiting 3 seconds before next test...")
    time.sleep(3)
    
    # Test Black bet
    print("\n" + "=" * 70)
    print("TEST 2: BLACK BET")
    print("=" * 70)
    print("\nIn 5 seconds, the bot will:")
    print("  - Move mouse to Black button")
    print("  - Click to place bet")
    print("  - Use minimum bet amount (R$ 1.00)")
    print("\nStarting in...")
    for i in range(5, 0, -1):
        print(f"  {i}...", end='\r')
        time.sleep(1)
    print("\n")
    
    try:
        result = bet_controller.place_bet('black', 1.0)
        if result:
            print(" Black bet placed successfully!")
            print("  Check your game to verify the bet was placed.")
        else:
            print(" Black bet failed (returned False)")
    except Exception as e:
        print(f" Error placing Black bet: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Verify bets were placed correctly in your game")
    print("  2. If bets worked: Proceed to test number detection")
    print("  3. If bets failed: Check coordinates and try again")
    print("\nTo test number detection, run:")
    print("  python test_video.py")
    print("\nTo run the full bot, run:")
    print("  python main.py")


if __name__ == '__main__':
    test_betting()

