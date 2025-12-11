"""
Test Coordinates in Browser
Moves mouse to each coordinate in config to verify they're correct.
"""

import pyautogui
import time
import json
import sys
from pathlib import Path


def test_browser_coordinates(config_path='config/default_config.json', click=False):
    """
    Test all coordinates from config file in browser.
    
    Args:
        config_path: Path to config file
        click: If True, will actually click (use with caution!)
    """
    print("=" * 80)
    print("BROWSER COORDINATE TESTER")
    print("=" * 80)
    print("\n  IMPORTANT:")
    print("   1. Open your roulette game in a browser")
    print("   2. Position the browser window where you want it")
    print("   3. Set browser zoom to 100% (Ctrl+0)")
    print("   4. Make sure the game is visible")
    print("   5. DO NOT move or resize the browser window")
    
    if click:
        print("\n  ⚠️  WARNING: Click mode enabled!")
        print("     The script will actually click on coordinates")
        print("     Make sure you're using a test account!")
    else:
        print("\n  ℹ️  Simulation mode: Mouse will move but NOT click")
    
    print("\n" + "-" * 80)
    
    # Load config
    print(f"\nLoading configuration from {config_path}...")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(" ✓ Configuration loaded")
    except FileNotFoundError:
        print(f" ✗ Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f" ✗ Config file error: {e}")
        sys.exit(1)
    
    # Get betting configuration
    betting = config.get('betting', {})
    areas = betting.get('betting_areas', {})
    confirm = betting.get('confirm_button')
    chip_selection = betting.get('chip_selection')
    chip_selection_coords = betting.get('chip_selection_coordinates', {})
    
    print("\n" + "=" * 80)
    print("COORDINATES TO TEST")
    print("=" * 80)
    
    coordinates_to_test = []
    
    # Betting areas
    if areas:
        print("\n📋 Betting Areas:")
        for bet_type, coords in areas.items():
            if isinstance(coords, list) and len(coords) >= 2:
                coordinates_to_test.append({
                    'name': f"{bet_type.upper()} betting area",
                    'coords': coords[:2],
                    'type': 'betting_area'
                })
                print(f"   {bet_type}: {coords[:2]}")
    
    # Confirm button
    if confirm:
        coordinates_to_test.append({
            'name': 'CONFIRM button',
            'coords': confirm,
            'type': 'confirm'
        })
        print(f"\n✓ Confirm button: {confirm}")
    
    # Chip selection coordinates (multiple chips)
    if chip_selection_coords:
        print(f"\n🎰 Chip Selection Coordinates ({len(chip_selection_coords)} chips):")
        for chip_value, coords in chip_selection_coords.items():
            if isinstance(coords, list) and len(coords) >= 2:
                coordinates_to_test.append({
                    'name': f'Chip {chip_value}',
                    'coords': coords[:2],
                    'type': 'chip'
                })
                print(f"   Chip {chip_value}: {coords[:2]}")
    # Fallback to single chip_selection
    elif chip_selection:
        coordinates_to_test.append({
            'name': 'Chip selection (single)',
            'coords': chip_selection,
            'type': 'chip'
        })
        print(f"\n🎰 Chip selection (single): {chip_selection}")
    
    if not coordinates_to_test:
        print("\n ✗ No coordinates found in config!")
        print("   Make sure betting_areas, confirm_button, or chip_selection are set")
        sys.exit(1)
    
    print(f"\n{'=' * 80}")
    print(f"Total coordinates to test: {len(coordinates_to_test)}")
    print(f"{'=' * 80}")
    
    print("\n⚠️  Make sure your browser game is visible and ready!")
    print("   The mouse will move to each coordinate.")
    if click:
        print("   The mouse will CLICK on each coordinate!")
    
    response = input("\nPress Enter to start testing, or Ctrl+C to cancel...")
    
    print("\n" + "=" * 80)
    print("STARTING TESTS")
    print("=" * 80)
    
    # Countdown
    print("\nStarting in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print("  GO!\n")
    
    results = []
    
    for idx, item in enumerate(coordinates_to_test, 1):
        name = item['name']
        x, y = item['coords']
        coord_type = item['type']
        
        print(f"\n{'=' * 80}")
        print(f"Test {idx}/{len(coordinates_to_test)}: {name}")
        print(f"{'=' * 80}")
        print(f"Coordinates: [{x}, {y}]")
        print(f"\nMoving mouse to ({x}, {y})...")
        
        try:
            # Move mouse (slowly so you can see it)
            pyautogui.moveTo(x, y, duration=1.0)
            print(f" ✓ Mouse moved to ({x}, {y})")
            
            # Wait so you can see the position
            time.sleep(2)
            
            # Ask user to verify
            print(f"\n👀 Look at your browser - is the mouse over the {name}?")
            if click:
                print("⚠️  About to CLICK in 2 seconds...")
                time.sleep(2)
                pyautogui.click()
                print(" ✓ Clicked!")
                time.sleep(1)
            
            response = input("   Is this correct? (y/n/skip): ").strip().lower()
            
            if response == 'y':
                print(f"   ✓ {name} coordinates are CORRECT")
                results.append({
                    'name': name,
                    'coords': [x, y],
                    'status': 'correct'
                })
            elif response == 'n':
                print(f"   ✗ {name} coordinates are INCORRECT")
                results.append({
                    'name': name,
                    'coords': [x, y],
                    'status': 'incorrect'
                })
            else:
                print(f"   ⊘ {name} test skipped")
                results.append({
                    'name': name,
                    'coords': [x, y],
                    'status': 'skipped'
                })
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            results.append({
                'name': name,
                'coords': [x, y],
                'status': 'error',
                'error': str(e)
            })
        
        # Pause between tests
        if idx < len(coordinates_to_test):
            print("\nMoving to next coordinate in 2 seconds...")
            time.sleep(2)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    correct = sum(1 for r in results if r['status'] == 'correct')
    incorrect = sum(1 for r in results if r['status'] == 'incorrect')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    
    print(f"\nTotal tested: {len(results)}")
    print(f"✓ Correct: {correct}")
    print(f"✗ Incorrect: {incorrect}")
    print(f"⊘ Skipped: {skipped}")
    
    if incorrect > 0:
        print("\n⚠️  INCORRECT COORDINATES FOUND:")
        for r in results:
            if r['status'] == 'incorrect':
                print(f"   - {r['name']}: {r['coords']}")
        print("\n💡 To fix:")
        print("   1. Run: python scripts/coordinate_capture_tool.py")
        print("   2. Recapture the incorrect coordinates")
        print("   3. Update config file with new coordinates")
    else:
        print("\n✓ All coordinates are correct!")
    
    print("\n" + "=" * 80)
    
    # Save results
    output_file = Path('coordinate_test_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'config_path': config_path,
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'click_mode': click,
            'results': results,
            'summary': {
                'total': len(results),
                'correct': correct,
                'incorrect': incorrect,
                'skipped': skipped
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Results saved to: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test coordinates from config file in browser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test coordinates (simulation mode - no clicking)
  python scripts/test_browser_coordinates.py
  
  # Test with actual clicking (use with caution!)
  python scripts/test_browser_coordinates.py --click
  
  # Test with custom config file
  python scripts/test_browser_coordinates.py --config config/my_config.json
        """
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to config file (default: config/default_config.json)'
    )
    parser.add_argument(
        '--click',
        action='store_true',
        help='Actually click on coordinates (use with caution!)'
    )
    
    args = parser.parse_args()
    
    # Check if config exists
    if not Path(args.config).exists():
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)
    
    test_browser_coordinates(args.config, args.click)

