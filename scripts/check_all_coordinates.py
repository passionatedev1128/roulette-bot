"""
Check All Coordinates
Comprehensive tool to verify all coordinates in config file.
"""

import pyautogui
import cv2
import numpy as np
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    from backend.app.config_loader import ConfigLoader
except ImportError:
    print("Warning: Could not import ConfigLoader, using direct JSON loading")
    ConfigLoader = None


def load_config(config_path: str) -> Dict:
    """Load configuration file."""
    try:
        if ConfigLoader:
            return ConfigLoader.load_config(config_path)
        else:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def check_screen_region(config: Dict, save_images: bool = True) -> Dict:
    """Check screen region (detection region)."""
    print("\n" + "=" * 80)
    print("1. CHECKING SCREEN REGION (Detection Region)")
    print("=" * 80)
    
    detection_config = config.get('detection', {})
    screen_region = detection_config.get('screen_region')
    
    result = {
        'exists': False,
        'valid': False,
        'coordinates': None,
        'issues': []
    }
    
    if not screen_region:
        print("  Screen region not configured")
        result['issues'].append("Screen region not set in config")
        return result
    
    result['exists'] = True
    
    if not isinstance(screen_region, list) or len(screen_region) != 4:
        print(f"  Invalid format. Expected [x, y, width, height], got: {screen_region}")
        result['issues'].append("Invalid format")
        return result
    
    x, y, w, h = screen_region
    result['coordinates'] = {'x': x, 'y': y, 'width': w, 'height': h}
    
    # Check screen bounds
    screen_width, screen_height = pyautogui.size()
    print(f"\n Screen Region Info:")
    print(f"   Coordinates: x={x}, y={y}, width={w}, height={h}")
    print(f"   Screen size: {screen_width}x{screen_height}")
    
    if x < 0 or y < 0:
        print(f"  Coordinates are negative!")
        result['issues'].append("Negative coordinates")
    
    if x + w > screen_width or y + h > screen_height:
        print(f"  Region extends beyond screen bounds!")
        print(f"   Region ends at: ({x+w}, {y+h})")
        print(f"   Screen size: ({screen_width}, {screen_height})")
        result['issues'].append("Region out of bounds")
    else:
        print(f" ✓ Region is within screen bounds")
    
    # Capture and save region
    if save_images:
        try:
            screenshot = pyautogui.screenshot(region=screen_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            output_dir = Path('coordinate_check_output')
            output_dir.mkdir(exist_ok=True)
            
            # Save exact region
            region_path = output_dir / '1_screen_region_exact.png'
            cv2.imwrite(str(region_path), frame)
            print(f"  Saved exact region to: {region_path}")
            
            # Save full screen with region marked
            full_screenshot = pyautogui.screenshot()
            full_frame = cv2.cvtColor(np.array(full_screenshot), cv2.COLOR_RGB2BGR)
            cv2.rectangle(full_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.rectangle(full_frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
            cv2.putText(full_frame, f"Detection Region: ({x}, {y}) - {w}x{h}", 
                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            full_path = output_dir / '2_screen_region_marked.png'
            cv2.imwrite(str(full_path), full_frame)
            print(f"  Saved full screen with region marked to: {full_path}")
            print(f"    CHECK THIS IMAGE - Does the green rectangle show the winning number area?")
            
        except Exception as e:
            print(f"   Could not capture region: {e}")
            result['issues'].append(f"Capture error: {e}")
    
    if not result['issues']:
        result['valid'] = True
        print(f"\n ✓ Screen region is valid!")
    else:
        print(f"\n   Issues found: {result['issues']}")
    
    return result


def check_betting_coordinates(config: Dict) -> Dict:
    """Check betting area coordinates."""
    print("\n" + "=" * 80)
    print("2. CHECKING BETTING AREA COORDINATES")
    print("=" * 80)
    
    betting_config = config.get('betting', {})
    betting_areas = betting_config.get('betting_areas', {})
    
    result = {
        'exists': False,
        'valid': False,
        'coordinates': {},
        'issues': []
    }
    
    if not betting_areas:
        print("  No betting areas configured")
        result['issues'].append("No betting areas set")
        return result
    
    result['exists'] = True
    screen_width, screen_height = pyautogui.size()
    
    print(f"\n Betting Areas Found: {len(betting_areas)}")
    
    for bet_type, coords in betting_areas.items():
        if not isinstance(coords, list) or len(coords) < 2:
            print(f"  {bet_type}: Invalid format {coords}")
            result['issues'].append(f"{bet_type}: Invalid format")
            continue
        
        x, y = coords[0], coords[1]
        result['coordinates'][bet_type] = {'x': x, 'y': y}
        
        # Check bounds
        if x < 0 or y < 0:
            print(f"  {bet_type}: Negative coordinates [{x}, {y}]")
            result['issues'].append(f"{bet_type}: Negative coordinates")
        elif x > screen_width or y > screen_height:
            print(f"  {bet_type}: Out of bounds [{x}, {y}] (screen: {screen_width}x{screen_height})")
            result['issues'].append(f"{bet_type}: Out of bounds")
        else:
            print(f" ✓ {bet_type}: [{x}, {y}]")
    
    if not result['issues']:
        result['valid'] = True
        print(f"\n ✓ All betting coordinates are valid!")
    else:
        print(f"\n   Issues found: {len(result['issues'])}")
    
    return result


def check_chip_coordinates(config: Dict) -> Dict:
    """Check chip selection coordinates."""
    print("\n" + "=" * 80)
    print("3. CHECKING CHIP SELECTION COORDINATES")
    print("=" * 80)
    
    betting_config = config.get('betting', {})
    chip_coords = betting_config.get('chip_selection_coordinates', {})
    single_chip = betting_config.get('chip_selection')
    
    result = {
        'exists': False,
        'valid': False,
        'coordinates': {},
        'issues': []
    }
    
    if chip_coords:
        result['exists'] = True
        screen_width, screen_height = pyautogui.size()
        
        print(f"\n Chip Coordinates Found: {len(chip_coords)} chips")
        
        for chip_value, coords in chip_coords.items():
            if not isinstance(coords, list) or len(coords) < 2:
                print(f"  Chip {chip_value}: Invalid format {coords}")
                result['issues'].append(f"Chip {chip_value}: Invalid format")
                continue
            
            x, y = coords[0], coords[1]
            result['coordinates'][chip_value] = {'x': x, 'y': y}
            
            # Check bounds
            if x < 0 or y < 0:
                print(f"  Chip {chip_value}: Negative coordinates [{x}, {y}]")
                result['issues'].append(f"Chip {chip_value}: Negative coordinates")
            elif x > screen_width or y > screen_height:
                print(f"  Chip {chip_value}: Out of bounds [{x}, {y}]")
                result['issues'].append(f"Chip {chip_value}: Out of bounds")
            else:
                print(f" ✓ Chip {chip_value}: [{x}, {y}]")
    
    elif single_chip:
        result['exists'] = True
        print(f"\n Single chip selection coordinate found (legacy mode)")
        if isinstance(single_chip, list) and len(single_chip) >= 2:
            x, y = single_chip[0], single_chip[1]
            result['coordinates']['single'] = {'x': x, 'y': y}
            print(f" ✓ Chip selection: [{x}, {y}]")
        else:
            print(f"  Invalid format: {single_chip}")
            result['issues'].append("Invalid single chip format")
    else:
        print("   No chip selection coordinates configured")
        result['issues'].append("No chip coordinates set")
    
    if not result['issues'] and result['exists']:
        result['valid'] = True
        print(f"\n ✓ All chip coordinates are valid!")
    
    return result


def check_confirm_button(config: Dict) -> Dict:
    """Check confirm button coordinate."""
    print("\n" + "=" * 80)
    print("4. CHECKING CONFIRM BUTTON COORDINATE")
    print("=" * 80)
    
    betting_config = config.get('betting', {})
    confirm = betting_config.get('confirm_button')
    
    result = {
        'exists': False,
        'valid': False,
        'coordinates': None,
        'issues': []
    }
    
    if not confirm:
        print("   Confirm button not configured (may auto-confirm)")
        result['issues'].append("Confirm button not set")
        return result
    
    result['exists'] = True
    
    if not isinstance(confirm, list) or len(confirm) < 2:
        print(f"  Invalid format: {confirm}")
        result['issues'].append("Invalid format")
        return result
    
    x, y = confirm[0], confirm[1]
    result['coordinates'] = {'x': x, 'y': y}
    
    screen_width, screen_height = pyautogui.size()
    
    # Check bounds
    if x < 0 or y < 0:
        print(f"  Negative coordinates [{x}, {y}]")
        result['issues'].append("Negative coordinates")
    elif x > screen_width or y > screen_height:
        print(f"  Out of bounds [{x}, {y}]")
        result['issues'].append("Out of bounds")
    else:
        print(f" ✓ Confirm button: [{x}, {y}]")
        result['valid'] = True
    
    return result


def generate_summary(all_results: Dict):
    """Generate summary of all checks."""
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    screen_region = all_results.get('screen_region', {})
    betting = all_results.get('betting', {})
    chips = all_results.get('chips', {})
    confirm = all_results.get('confirm', {})
    
    print(f"\n Screen Region:")
    if screen_region.get('valid'):
        print(f"   ✓ Valid")
    elif screen_region.get('exists'):
        print(f"    Has issues: {screen_region.get('issues', [])}")
    else:
        print(f"    Not configured")
    
    print(f"\n Betting Areas:")
    if betting.get('valid'):
        print(f"   ✓ Valid ({len(betting.get('coordinates', {}))} areas)")
    elif betting.get('exists'):
        print(f"    Has issues: {betting.get('issues', [])}")
    else:
        print(f"    Not configured")
    
    print(f"\n Chip Selection:")
    if chips.get('valid'):
        chip_count = len(chips.get('coordinates', {}))
        print(f"   ✓ Valid ({chip_count} chip{'s' if chip_count != 1 else ''})")
    elif chips.get('exists'):
        print(f"     Has issues: {chips.get('issues', [])}")
    else:
        print(f"     Not configured (may use single chip)")
    
    print(f"\n Confirm Button:")
    if confirm.get('valid'):
        print(f"   ✓ Valid")
    elif confirm.get('exists'):
        print(f"    Has issues: {confirm.get('issues', [])}")
    else:
        print(f"     Not configured (may auto-confirm)")
    
    # Overall status
    all_valid = (
        screen_region.get('valid', False) and
        betting.get('valid', False) and
        (chips.get('valid', False) or not chips.get('exists', False)) and
        (confirm.get('valid', False) or not confirm.get('exists', False))
    )
    
    print(f"\n{'=' * 80}")
    if all_valid:
        print(" ALL COORDINATES ARE VALID!")
    else:
        print("  SOME COORDINATES NEED ATTENTION")
        print("\n Next steps:")
        if not screen_region.get('valid') and screen_region.get('exists'):
            print("   - Fix screen region coordinates")
        if not betting.get('valid') and betting.get('exists'):
            print("   - Fix betting area coordinates")
        if chips.get('exists') and not chips.get('valid'):
            print("   - Fix chip selection coordinates")
    print("=" * 80)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Check all coordinates in config file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all coordinates
  python scripts/check_all_coordinates.py
  
  # Check with custom config
  python scripts/check_all_coordinates.py --config config/my_config.json
  
  # Don't save images
  python scripts/check_all_coordinates.py --no-images
        """
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to config file (default: config/default_config.json)'
    )
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Don\'t save images'
    )
    
    args = parser.parse_args()
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    print("=" * 80)
    print("COORDINATE CHECKER")
    print("=" * 80)
    print(f"Config file: {config_path}")
    print(f"Screen size: {pyautogui.size()[0]}x{pyautogui.size()[1]}")
    
    # Load config
    config = load_config(str(config_path))
    
    # Run all checks
    results = {
        'screen_region': check_screen_region(config, save_images=not args.no_images),
        'betting': check_betting_coordinates(config),
        'chips': check_chip_coordinates(config),
        'confirm': check_confirm_button(config)
    }
    
    # Generate summary
    generate_summary(results)
    
    if not args.no_images:
        print(f"\n Images saved to: coordinate_check_output/")
        print(f"   Check these images to visually verify coordinates!")


if __name__ == '__main__':
    main()

