"""
Test script to identify and fix errors in the bot.
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test all critical imports."""
    print("Testing imports...")
    try:
        from backend.app.bot import RouletteBot
        from backend.app.config_loader import ConfigLoader
        from backend.app.strategy import EvenOddStrategy, MartingaleStrategy
        from backend.app.betting import BetController
        from backend.app.detection import ScreenDetector
        from backend.app.logging import RouletteLogger
        print("[OK] All imports successful")
        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        traceback.print_exc()
        return False

def test_config_loading():
    """Test configuration loading."""
    print("\nTesting config loading...")
    try:
        from backend.app.config_loader import ConfigLoader
        config = ConfigLoader.load_config('config/default_config.json')
        
        # Check required sections
        required_sections = ['detection', 'strategy', 'betting', 'risk']
        for section in required_sections:
            if section not in config:
                print(f"[ERROR] Missing config section: {section}")
                return False
        
        # Check strategy type
        strategy_type = config.get('strategy', {}).get('type')
        if not strategy_type:
            print("[ERROR] Missing strategy type in config")
            return False
        
        print(f"[OK] Config loaded successfully (strategy: {strategy_type})")
        return True
    except Exception as e:
        print(f"[ERROR] Config loading error: {e}")
        traceback.print_exc()
        return False

def test_bot_initialization():
    """Test bot initialization."""
    print("\nTesting bot initialization...")
    try:
        from backend.app.bot import RouletteBot
        
        bot = RouletteBot('config/default_config.json', test_mode=True)
        
        # Check required attributes
        required_attrs = ['config', 'detector', 'strategy', 'bet_controller', 'logger']
        for attr in required_attrs:
            if not hasattr(bot, attr):
                print(f"[ERROR] Missing attribute: {attr}")
                return False
        
        print("[OK] Bot initialized successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Bot initialization error: {e}")
        traceback.print_exc()
        return False

def test_strategy_creation():
    """Test strategy creation."""
    print("\nTesting strategy creation...")
    try:
        from backend.app.config_loader import ConfigLoader
        from backend.app.bot import RouletteBot
        
        config = ConfigLoader.load_config('config/default_config.json')
        bot = RouletteBot('config/default_config.json', test_mode=True)
        
        strategy = bot.strategy
        strategy_type = config.get('strategy', {}).get('type')
        
        if not strategy:
            print("[ERROR] Strategy not created")
            return False
        
        if not hasattr(strategy, 'calculate_bet'):
            print("[ERROR] Strategy missing calculate_bet method")
            return False
        
        print(f"[OK] Strategy created successfully ({strategy_type})")
        return True
    except Exception as e:
        print(f"[ERROR] Strategy creation error: {e}")
        traceback.print_exc()
        return False

def test_detector_initialization():
    """Test detector initialization."""
    print("\nTesting detector initialization...")
    try:
        from backend.app.config_loader import ConfigLoader
        from backend.app.detection import ScreenDetector
        
        config = ConfigLoader.load_config('config/default_config.json')
        detector = ScreenDetector(config)
        
        if not hasattr(detector, 'detect_result'):
            print("[ERROR] Detector missing detect_result method")
            return False
        
        print("[OK] Detector initialized successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Detector initialization error: {e}")
        traceback.print_exc()
        return False

def test_betting_controller():
    """Test betting controller."""
    print("\nTesting betting controller...")
    try:
        from backend.app.config_loader import ConfigLoader
        from backend.app.betting import BetController
        
        config = ConfigLoader.load_config('config/default_config.json')
        controller = BetController(config)
        
        if not hasattr(controller, 'place_bet'):
            print("[ERROR] BetController missing place_bet method")
            return False
        
        # Check betting areas
        betting_areas = config.get('betting', {}).get('betting_areas', {})
        if 'even' not in betting_areas or 'odd' not in betting_areas:
            print("[WARNING] Even/Odd betting areas not configured")
        else:
            print("[OK] Even/Odd betting areas configured")
        
        print("[OK] Betting controller initialized successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Betting controller error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("BOT ERROR CHECKER")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Config Loading", test_config_loading()))
    results.append(("Bot Initialization", test_bot_initialization()))
    results.append(("Strategy Creation", test_strategy_creation()))
    results.append(("Detector Initialization", test_detector_initialization()))
    results.append(("Betting Controller", test_betting_controller()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Bot should work correctly.")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed. Please fix the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

