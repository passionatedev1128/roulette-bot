"""
Diagnostic script to check why mouse isn't moving.
This will help identify if the issue is:
1. No detections
2. No betting decisions
3. Wrong coordinates
4. Other issues
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.app.config_loader import ConfigLoader
from backend.app.detection import ScreenDetector
from backend.app.strategy.even_odd_strategy import EvenOddStrategy
from backend.app.betting.bet_controller import BetController

def main():
    """Diagnose why mouse isn't moving."""
    config_path = "config/default_config.json"
    
    print("=" * 60)
    print("Mouse Movement Diagnostic")
    print("=" * 60)
    print()
    
    # Load config
    print("1. Loading config...")
    config = ConfigLoader.load_config(config_path)
    print(f"   Config loaded: {config_path}")
    print()
    
    # Check screen_region
    print("2. Checking screen_region...")
    screen_region = config.get('detection', {}).get('screen_region')
    if screen_region:
        x, y, w, h = screen_region
        print(f"   screen_region: [{x}, {y}, {w}, {h}]")
        print(f"   This captures {w}x{h} pixels at position ({x}, {y})")
    else:
        print("   WARNING: screen_region is null - will capture full screen")
    print()
    
    # Check betting_areas
    print("3. Checking betting_areas...")
    betting_areas = config.get('betting', {}).get('betting_areas', {})
    if betting_areas:
        print(f"   Found {len(betting_areas)} betting areas:")
        for bet_type, coords in list(betting_areas.items())[:5]:  # Show first 5
            print(f"     {bet_type}: {coords}")
        if len(betting_areas) > 5:
            print(f"     ... and {len(betting_areas) - 5} more")
    else:
        print("   ERROR: No betting_areas found in config!")
    print()
    
    # Test detection
    print("4. Testing detection (capturing one frame)...")
    try:
        detector = ScreenDetector(config)
        frame = detector.capture_screen()
        if frame is not None:
            print(f"   Frame captured: {frame.shape}")
            result = detector.detect_result(frame)
            if result and result.get('number') is not None:
                print(f"   Detection test: Number {result.get('number')} detected!")
                print(f"   Color: {result.get('color')}, Confidence: {result.get('confidence', 0):.2f}")
            else:
                print("   Detection test: No number detected in this frame")
                print("   This is normal if no winning number is visible")
        else:
            print("   ERROR: Could not capture frame!")
            print("   Make sure video/game is visible on screen")
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Test strategy
    print("5. Testing strategy...")
    try:
        strategy = EvenOddStrategy(config.get('strategy', {}))
        print(f"   Strategy type: {strategy.__class__.__name__}")
        print(f"   Base bet: {strategy.base_bet}")
        print(f"   Streak length required: {strategy.streak_length}")
        print(f"   Current even streak: {strategy.current_even_streak}")
        print(f"   Current odd streak: {strategy.current_odd_streak}")
        print("   Note: Strategy needs streak_length consecutive numbers to bet")
    except Exception as e:
        print(f"   ERROR: {e}")
    print()
    
    # Test betting controller
    print("6. Testing betting controller...")
    try:
        bet_controller = BetController(config)
        print(f"   Betting controller initialized")
        
        # Test finding coordinates
        test_bet_types = ['even', 'odd', 'red', 'black']
        for bet_type in test_bet_types:
            coords = bet_controller.find_betting_area(bet_type)
            if coords:
                print(f"   {bet_type}: coordinates found at {coords}")
            else:
                print(f"   {bet_type}: NO coordinates found!")
    except Exception as e:
        print(f"   ERROR: {e}")
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print("Mouse will move ONLY if:")
    print("  1. Numbers are detected (check detection test above)")
    print("  2. Strategy makes betting decision (needs streak_length consecutive)")
    print("  3. Betting coordinates are found (check betting_areas above)")
    print()
    print("If mouse doesn't move, check:")
    print("  - Are numbers being detected? (watch console for 'Detection: number=X')")
    print("  - Is strategy making decisions? (watch for 'Bet decision: ...')")
    print("  - Are coordinates correct? (check betting_areas in config)")
    print("=" * 60)

if __name__ == "__main__":
    main()

