"""
Capture Even/Odd Betting Coordinates
Collects the screen positions for Even and Odd betting areas.
"""

import json
import time
from pathlib import Path
from typing import Dict, List

import pyautogui


def countdown(seconds: int) -> None:
    """Display a countdown, showing live cursor coordinates."""
    for remaining in range(seconds, 0, -1):
        x, y = pyautogui.position()
        print(f"  {remaining}... cursor at [{x}, {y}]", end="\r")
        time.sleep(1)
    print()


def capture_even_odd_coordinates(output_file: str = "even_odd_coordinates.json") -> Dict[str, List[int]]:
    """Interactive capture routine for Even/Odd betting areas."""
    print("=" * 70)
    print("EVEN/ODD BETTING COORDINATE CAPTURE")
    print("=" * 70)
    print("\nInstructions:")
    print("  1. Make sure the roulette betting table is visible.")
    print("  2. You will be prompted for Even and Odd betting areas.")
    print("  3. Hover over the center of the betting area.")
    print("  4. Press Enter to capture after the 5-second countdown.")
    print("  5. Press 'n' to skip, 'p' to go back to the previous one.")
    print("  6. Press Ctrl+C at any time to abort.\n")
    
    sequence = ["even", "odd"]
    coordinates: Dict[str, List[int]] = {}
    
    index = 0
    while index < len(sequence):
        current_bet_type = sequence[index]
        print(f"\n{'=' * 70}")
        print(f"Betting Area: {current_bet_type.upper()}  ({index + 1}/{len(sequence)})")
        print(f"{'=' * 70}")
        print(f"Move the cursor to the center of the {current_bet_type.upper()} betting area.")
        print("(This is typically a button or area labeled 'Even' or 'Odd' on the table)")
        user_input = input("Press Enter to capture, 'n' to skip, 'p' for previous: ").strip().lower()
        
        if user_input == "n":
            print(f"   Skipped {current_bet_type}")
            index += 1
            continue
        if user_input == "p":
            if index == 0:
                print("   Already at the first betting area.")
            else:
                index -= 1
                print("   Returning to previous betting area.")
            continue
        
        try:
            print("Countdown starting; keep the mouse steady...")
            countdown(5)
            x, y = pyautogui.position()
            coordinates[current_bet_type] = [x, y]
            print(f"   Captured {current_bet_type.upper()}: [{x}, {y}]")
            index += 1
        except KeyboardInterrupt:
            print("\n  Capture interrupted. Moving to the next betting area.")
            index += 1
    
    # Save results
    output_path = Path(output_file)
    output_path.write_text(json.dumps(coordinates, indent=2), encoding="utf-8")
    
    print("\n" + "=" * 70)
    print("CAPTURE COMPLETE")
    print("=" * 70)
    print(f"\nSaved coordinates to: {output_path.resolve()}")
    print("\nConfig snippet to add to your config file:")
    print('"betting": {')
    print('  "betting_areas": {')
    print('    // ... existing entries (numbers, red, black, etc.) ...')
    for bet_type in sorted(coordinates.keys()):
        coords = coordinates[bet_type]
        print(f'    "{bet_type}": {coords},')
    print('  },')
    print('  // ... rest of betting config ...')
    print('}')
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Open your config file (e.g., config/default_config.json)")
    print("2. Find the 'betting_areas' section")
    print("3. Add the coordinates above to the 'betting_areas' object")
    print("4. Save the config file")
    print("\nExample:")
    print('  "betting_areas": {')
    print('    "red": [970, 904],')
    print('    "black": [1040, 906],')
    if "even" in coordinates:
        print(f'    "even": {coordinates["even"]},')
    if "odd" in coordinates:
        print(f'    "odd": {coordinates["odd"]},')
    print('    // ... other entries ...')
    print('  }')
    
    return coordinates


if __name__ == "__main__":
    try:
        capture_even_odd_coordinates()
    except KeyboardInterrupt:
        print("\n\nCapture aborted by user.")
    except Exception as e:
        print(f"\n\nError during capture: {e}")
        import traceback
        traceback.print_exc()

