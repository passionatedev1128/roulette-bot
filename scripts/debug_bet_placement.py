"""
Debug Bet Placement - Check why mouse isn't moving
"""

import logging
from backend.app.config_loader import ConfigLoader
from backend.app.bot import RouletteBot
from backend.app.detection.screen_detector import ScreenDetector
import pyautogui

# Set up logging to see all details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_bet_placement():
    """Test if bet placement and mouse movement works."""
    config_path = 'config/default_config.json'
    config = ConfigLoader.load_config(config_path)
    
    print("=" * 80)
    print("BET PLACEMENT DEBUG")
    print("=" * 80)
    
    # Check betting areas
    betting_areas = config.get('betting', {}).get('betting_areas', {})
    print(f"\nBetting Areas in Config:")
    for bet_type, coords in betting_areas.items():
        print(f"  {bet_type}: {coords}")
    
    # Test finding coordinates
    from backend.app.betting.bet_controller import BetController
    bet_controller = BetController(config)
    
    print(f"\nTesting coordinate lookup:")
    test_types = ['even', 'odd', 'red', 'black']
    for bet_type in test_types:
        coords = bet_controller.find_betting_area(bet_type)
        if coords:
            print(f"   {bet_type}: {coords}")
        else:
            print(f"   {bet_type}: NOT FOUND")
    
    # Test mouse movement (simulation)
    print(f"\nTesting mouse movement (will move mouse):")
    print("  Moving to Even button...")
    even_coords = bet_controller.find_betting_area('even')
    if even_coords:
        x, y = even_coords
        print(f"  Coordinates: ({x}, {y})")
        print(f"  Moving mouse in 2 seconds...")
        import time
        time.sleep(2)
        try:
            pyautogui.moveTo(x, y, duration=1.0)
            print(f"   Mouse moved to ({x}, {y})")
            print(f"   Check if mouse is at the Even button!")
            time.sleep(2)
        except Exception as e:
            print(f"   Error moving mouse: {e}")
    else:
        print(f"   Cannot test - Even coordinates not found")
    
    # Test with bot
    print(f"\n" + "=" * 80)
    print("TESTING WITH BOT")
    print("=" * 80)
    
    print("\nInitializing bot...")
    bot = RouletteBot(config_path, test_mode=True)
    
    print(f"\nBot Strategy: {bot.strategy.strategy_type}")
    print(f"Bet Controller initialized: {bot.bet_controller is not None}")
    
    # Simulate a detection and bet decision
    print(f"\nSimulating detection and bet decision...")
    
    # Create a mock result
    mock_result = {
        'number': 33,
        'color': 'black',
        'zero': False,
        'confidence': 0.95,
        'method': 'template'
    }
    
    print(f"Mock result: {mock_result}")
    
    # Add to history
    bot.result_history.append(mock_result)
    
    # Calculate bet
    bet_decision = bot.strategy.calculate_bet(
        bot.result_history,
        bot.current_balance,
        mock_result
    )
    
    if bet_decision:
        print(f"\n Bet decision made:")
        print(f"   Type: {bet_decision.get('bet_type')}")
        print(f"   Amount: {bet_decision.get('bet_amount')}")
        print(f"   Reason: {bet_decision.get('reason', 'N/A')}")
        
        # Try to place bet
        print(f"\nAttempting to place bet...")
        bet_type = bet_decision.get('bet_type')
        bet_amount = bet_decision.get('bet_amount')
        
        coords = bot.bet_controller.find_betting_area(bet_type)
        if coords:
            print(f" Coordinates found: {coords}")
            print(f"  Mouse will move to: {coords}")
            
            # Actually place bet (will move mouse)
            print(f"\nPlacing bet (mouse will move)...")
            bet_result = bot.bet_controller.place_bet(bet_type, bet_amount)
            
            if bet_result['success']:
                print(f" Bet placed successfully!")
                print(f" Mouse should have moved to {coords}")
            else:
                print(f" Bet placement failed: {bet_result.get('error')}")
        else:
            print(f" No coordinates found for {bet_type}")
    else:
        print(f"\n No bet decision made")
        if hasattr(bot.strategy, 'current_even_streak'):
            print(f"   Even streak: {bot.strategy.current_even_streak}")
            print(f"   Odd streak: {bot.strategy.current_odd_streak}")
            print(f"   Cycle active: {bot.strategy.cycle_active}")
            print(f"   Streak length required: {bot.strategy.streak_length}")
    
    print(f"\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_bet_placement()

