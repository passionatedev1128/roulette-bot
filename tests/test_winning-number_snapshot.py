"""
Test Winning Number Snapshot
Runs ScreenDetector on a snapshot to verify winning-number OCR.
"""

import argparse
from pathlib import Path

import cv2

from backend.app.detection.screen_detector import ScreenDetector
from backend.app.config_loader import ConfigLoader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test winning-number detection on a snapshot.")
    parser.add_argument("snapshot", type=str, help="Path to the snapshot image.")
    parser.add_argument(
        "--config",
        type=str,
        default="config/default_config.json",
        help="Path to configuration file (default: config/default_config.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    snapshot_path = Path(args.snapshot)
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")

    # print("Prepare the snapshot/window. Starting in 5 seconds...")
    # import time
    # for remaining in range(5, 0, -1):
    #     print(f"  {remaining}", end="\r")
    #     time.sleep(1)
    # print()

    config = ConfigLoader.load_config(args.config)
    detector = ScreenDetector(config)
    image = cv2.imread(str(snapshot_path))
    if image is None:
        raise RuntimeError(f"Failed to load image: {snapshot_path}")

    result = detector.detect_result(image)

    print("=" * 60)
    print("WINNING NUMBER SNAPSHOT TEST")
    print("=" * 60)
    print(f"Snapshot: {snapshot_path}")
    print(f"Config:   {args.config}")
    print("-" * 60)
    print(f"Number:     {result.get('number')}")
    print(f"Color:      {result.get('color')}")
    print(f"Zero:       {result.get('zero')}")
    print(f"Confidence: {result.get('confidence'):.2f}")
    print(f"Method:     {result.get('method')}")
    print("=" * 60)


if __name__ == "__main__":
    main()

