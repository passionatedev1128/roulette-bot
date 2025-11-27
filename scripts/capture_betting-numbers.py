"""
Capture Number Grid Coordinates
Collects the screen positions for roulette betting squares 0–36.
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


def prompt_number_list() -> List[str]:
    """Return the capture sequence (0-36 by default)."""
    default_numbers = [str(n) for n in range(37)]
    print("Default capture order: 0–36.")
    custom = input("Enter custom sequence separated by commas (or press Enter to accept default): ").strip()
    if not custom:
        return default_numbers

    cleaned = []
    for item in custom.split(","):
        num = item.strip()
        if num.isdigit() and 0 <= int(num) <= 36:
            cleaned.append(num)
    return cleaned or default_numbers


def capture_number_grid(output_file: str = "number_grid_coordinates.json") -> Dict[str, List[int]]:
    """Interactive capture routine for the betting grid."""
    print("=" * 70)
    print("NUMBER GRID COORDINATE CAPTURE")
    print("=" * 70)
    print("\nInstructions:")
    print("  1. Make sure the roulette betting grid is visible and unobstructed.")
    print("  2. You will be prompted for each number. Hover over the center of that square.")
    print("  3. Press Enter to capture after the 5-second countdown.")
    print("  4. Press 'n' to skip a number, 'p' to go back to the previous one.")
    print("  5. Press Ctrl+C at any time to abort.\n")

    sequence = prompt_number_list()
    coordinates: Dict[str, List[int]] = {}

    index = 0
    while index < len(sequence):
        current_number = sequence[index]
        print(f"\n{'=' * 70}")
        print(f"Number {current_number}  ({index + 1}/{len(sequence)})")
        print(f"{'=' * 70}")
        print("Move the cursor to the center of the betting square.")
        user_input = input("Press Enter to capture, 'n' to skip, 'p' for previous: ").strip().lower()

        if user_input == "n":
            print(f"   Skipped number {current_number}")
            index += 1
            continue
        if user_input == "p":
            if index == 0:
                print("   Already at the first number.")
            else:
                index -= 1
                print("   Returning to previous number.")
            continue

        try:
            print("Countdown starting; keep the mouse steady...")
            countdown(5)
            x, y = pyautogui.position()
            coordinates[current_number] = [x, y]
            print(f"   Captured number {current_number}: [{x}, {y}]")
            index += 1
        except KeyboardInterrupt:
            print("\n  Capture interrupted. Moving to the next number.")
            index += 1

    # Save results
    output_path = Path(output_file)
    output_path.write_text(json.dumps(coordinates, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    print("CAPTURE COMPLETE")
    print("=" * 70)
    print(f"\nSaved coordinates to: {output_path.resolve()}")
    print("\nConfig snippet:")
    print('"betting": {')
    print('  "betting_areas": {')
    for num in sorted(coordinates.keys(), key=lambda n: int(n)):
        coords = coordinates[num]
        print(f'    "{num}": {coords},')
    print('    // existing entries: "red": [...], "black": [...], ...')
    print('  },')
    print('  "chip_selection": [...],')
    print('  "confirm_button": [...],')
    print('}')

    return coordinates


if __name__ == "__main__":
    try:
        capture_number_grid()
    except KeyboardInterrupt:
        print("\nCapture aborted by user.")

