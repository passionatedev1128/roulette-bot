"""
Coordinate Capture Tool
Helps you find exact coordinates for betting buttons.
"""

import pyautogui
import time
import json
import sys
from pathlib import Path


def capture_coordinates():
    """Interactive coordinate capture tool."""
    print("=" * 70)
    print("COORDINATE CAPTURE TOOL - LUCK.BET Roleta Brasileira")
    print("=" * 70)
    print("\nYOU ONLY NEED 2 COORDINATES:")
    print("  1. Vermelho (Red) betting area - ON BETTING GRID")
    print("  2. Preto (Black) betting area - ON BETTING GRID")
    print("\nInstructions:")
    print("  1. Open your game (LUCK.BET Roleta Brasileira)")
    print("  2. Look at BETTING GRID (bottom center, below video)")
    print("  3. Find 'Vermelho' or red betting box/area")
    print("  4. Move mouse to CENTER of that area")
    print("  5. Wait 5 seconds (coordinates captured automatically)")
    print("  6. Repeat for 'Preto' (Black) area")
    print("  7. Press Ctrl+C to skip other targets\n")
    print("=" * 70)
    
    coordinates = {}
    
    targets = [
        ("red_bet_button", "VERMELHO (Red) betting area - On betting grid, look for 'Vermelho' box or red betting area"),
        ("black_bet_button", "PRETO (Black) betting area - On betting grid, look for 'Preto' box or black betting area"),
        ("number_display_center", "Number display area (center video, where winning number appears) - Press Ctrl+C to skip"),
        ("green_bet_button", "GREEN/Zero betting button (if exists) - Press Ctrl+C to skip"),
        ("confirm_button", "CONFIRM button (most games auto-confirm, press Ctrl+C to skip)"),
        ("chip_selection", "Chip selection (0.5, 1, 2.5, 5, 20, 50) - Press Ctrl+C to skip"),
    ]
    
    index = 0
    total_targets = len(targets)
    
    while index < total_targets:
        key, description = targets[index]
        print(f"\n{'=' * 70}")
        print(f"Target {index + 1}/{total_targets}: {description}")
        print(f"{'=' * 70}")
        print("\nMove your mouse to the target location.")
        print("Press Enter to start the 5-second capture countdown.")
        print("Press 'n' to skip this target and move to the next.")
        print("Press 'p' to go back and recapture the previous target.\n")
        
        try:
            user_input = input("Command (Enter/n/p): ").strip().lower()
        except KeyboardInterrupt:
            print("\n   Capture cancelled by user. Moving on.")
            index += 1
            continue
        
        if user_input == 'n':
            print(f"   Skipped: {key}")
            index += 1
            continue
        
        if user_input == 'p':
            if index == 0:
                print("   Already at the first target; cannot go back further.")
            else:
                index -= 1
                print("   Returning to previous target.")
            continue
        
        try:
            print("\nMove your mouse now... countdown starting (current position shown each second):")
            for countdown in range(5, 0, -1):
                pos_x, pos_y = pyautogui.position()
                print(f"  {countdown}... Current position: [{pos_x}, {pos_y}]", end='\r')
                time.sleep(1)
            print()
            
            print("  Capturing coordinates...")
            x, y = pyautogui.position()
            coordinates[key] = [x, y]
            print(f"   Captured: [{x}, {y}]")
            index += 1
        except KeyboardInterrupt:
            print(f"\n   Skipped: {key}")
            index += 1
            continue
    
    # Calculate regions if we have center points
    if 'number_display_center' in coordinates:
        print("\n" + "=" * 70)
        print("NUMBER DISPLAY REGION")
        print("=" * 70)
        print("To set the detection region, you need width and height.")
        print("Estimate the size of the number display area:")
        
        try:
            center_x, center_y = coordinates['number_display_center']
            print(f"\nDisplay center is at: [{center_x}, {center_y}]")
            
            width = input("Enter display width (pixels, default 200): ").strip()
            width = int(width) if width else 200
            
            height = input("Enter display height (pixels, default 100): ").strip()
            height = int(height) if height else 100
            
            # Calculate region: [x, y, width, height]
            x = center_x - width // 2
            y = center_y - height // 2
            
            coordinates['number_display_region'] = [x, y, width, height]
            print(f"   Display region: [{x}, {y}, {width}, {height}]")
        except (ValueError, KeyboardInterrupt):
            print("   Skipped region calculation")
    
    # Save coordinates
    output_file = 'game_coordinates.json'
    with open(output_file, 'w') as f:
        json.dump(coordinates, f, indent=2)
    
    print("\n" + "=" * 70)
    print("COORDINATES SAVED")
    print("=" * 70)
    print(f"\nSaved to: {output_file}")
    print("\nCaptured coordinates:")
    for key, value in coordinates.items():
        if isinstance(value, list) and len(value) == 2:
            print(f"  {key}: {value}")
        elif isinstance(value, list) and len(value) == 4:
            print(f"  {key}: {value} (region)")
    
    # Generate config snippet
    print("\n" + "=" * 70)
    print("CONFIG SNIPPET")
    print("=" * 70)
    print("\nCopy this into your config file:\n")
    
    print('"detection": {')
    if 'number_display_region' in coordinates:
        region = coordinates['number_display_region']
        print(f'  "screen_region": {region},  // [x, y, width, height]')
    else:
        print('  "screen_region": null,  // Set after capturing region')
    print('  // ... other detection settings')
    print('},')
    
    print('\n"betting": {')
    print('  "betting_areas": {')
    if 'red_bet_button' in coordinates:
        print(f'    "red": {coordinates["red_bet_button"]},')
    if 'black_bet_button' in coordinates:
        print(f'    "black": {coordinates["black_bet_button"]},')
    if 'green_bet_button' in coordinates:
        print(f'    "green": {coordinates["green_bet_button"]},')
    print('  },')
    if 'confirm_button' in coordinates:
        print(f'  "confirm_button": {coordinates["confirm_button"]},')
    if 'amount_input' in coordinates:
        print(f'  "amount_input": {coordinates["amount_input"]},')
    print('  // ... other betting settings')
    print('},')
    
    print("\n" + "=" * 70)
    
    return coordinates


def test_coordinates(config_path='config/default_config.json'):
    """Test if coordinates in config are correct."""
    print("=" * 70)
    print("COORDINATE TESTING TOOL")
    print("=" * 70)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f" Config file not found: {config_path}")
        return
    except json.JSONDecodeError as e:
        print(f" Config file error: {e}")
        return
    
    betting = config.get('betting', {})
    areas = betting.get('betting_areas', {})
    confirm = betting.get('confirm_button')
    
    print("\nMake sure your game window is visible and ready!")
    print("Mouse will move to each coordinate - verify they're correct")
    print("\nPress Enter to start, Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    all_correct = True
    
    # Test red button
    if 'red' in areas:
        x, y = areas['red']
        print(f"\n1. Moving to RED button: [{x}, {y}]")
        pyautogui.moveTo(x, y, duration=1)
        time.sleep(2)
        response = input("   Is this the RED betting button? (y/n): ").lower()
        if response != 'y':
            print("    RED coordinates incorrect!")
            all_correct = False
        else:
            print("    RED coordinates correct")
    else:
        print("    RED coordinates not set")
        all_correct = False
    
    # Test black button
    if 'black' in areas:
        x, y = areas['black']
        print(f"\n2. Moving to BLACK button: [{x}, {y}]")
        pyautogui.moveTo(x, y, duration=1)
        time.sleep(2)
        response = input("   Is this the BLACK betting button? (y/n): ").lower()
        if response != 'y':
            print("    BLACK coordinates incorrect!")
            all_correct = False
        else:
            print("    BLACK coordinates correct")
    else:
        print("    BLACK coordinates not set")
        all_correct = False
    
    # Test confirm button
    if confirm:
        x, y = confirm
        print(f"\n3. Moving to CONFIRM button: [{x}, {y}]")
        pyautogui.moveTo(x, y, duration=1)
        time.sleep(2)
        response = input("   Is this the CONFIRM button? (y/n): ").lower()
        if response != 'y':
            print("    CONFIRM coordinates incorrect!")
            all_correct = False
        else:
            print("    CONFIRM coordinates correct")
    else:
        print("    CONFIRM coordinates not set")
    
    print("\n" + "=" * 70)
    if all_correct:
        print(" All coordinates verified!")
    else:
        print(" Some coordinates need correction")
        print("\nRun coordinate_capture_tool.py again to recapture.")
    print("=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        config_path = sys.argv[2] if len(sys.argv) > 2 else 'config/default_config.json'
        test_coordinates(config_path)
    else:
        capture_coordinates()


if __name__ == '__main__':
    main()

