"""
Capture Winning Number Snapshots
Takes on-demand screenshots of the winning-number display for template/OCR training.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List

import pyautogui


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture snapshots of the winning-number badge."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="winning_numbers",
        help="Directory to save snapshots (default: winning_numbers)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of captures to take (default: 1)",
    )
    parser.add_argument(
        "--region",
        type=int,
        nargs=4,
        metavar=("X", "Y", "WIDTH", "HEIGHT"),
        help="Winning-number region. Overrides config screen_region.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Seconds to wait before each capture (default: 3.0)",
    )
    return parser.parse_args()


def determine_region(cli_region: List[int]) -> List[int]:
    if cli_region:
        return cli_region

    # Fallback: prompt user or use config
    print("No region provided. Enter coordinates for the winning-number display.")
    try:
        x = int(input("  X (left): ").strip())
        y = int(input("  Y (top): ").strip())
        w = int(input("  Width: ").strip())
        h = int(input("  Height: ").strip())
        return [x, y, w, h]
    except (ValueError, KeyboardInterrupt):
        print("Invalid input. Aborting.")
        sys.exit(1)


def capture_single(region: List[int], path: Path, countdown: float) -> None:
    try:
        print(f"Move the cursor away. Capturing in {countdown:.1f} seconds...")
        time.sleep(countdown)
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(path)
        print(f"   Saved: {path}")
    except Exception as exc:
        print(f"   Failed to capture: {exc}")


def main() -> None:
    args = parse_args()

    region = determine_region(args.region)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("WINNING NUMBER SNAPSHOT CAPTURE")
    print("=" * 70)
    print(f"Region: {region}")
    print(f"Output directory: {output_dir.resolve()}")
    print("Press Ctrl+C to abort at any time.\n")

    for idx in range(1, args.count + 1):
        filename = output_dir / f"winning_{idx:02d}.png"
        print(f"[{idx}/{args.count}] Prepare the winning badge in the target region.")
        input("Press Enter when ready...")
        capture_single(region, filename, args.delay)

    print("\nCapture complete. Use these snapshots to build templates or feed OCR preprocessing.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCapture aborted by user.")

