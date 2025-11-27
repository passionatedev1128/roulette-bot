"""
Verification script to check if frames 5534-5574 are present in test results.
"""
import json
import sys
from pathlib import Path
from typing import List, Tuple


def find_gaps(frames: List[int]) -> List[Tuple[int, int, int]]:
    """Find gaps in frame sequence. Returns list of (start, end, count) tuples."""
    gaps = []
    if not frames:
        return gaps
    
    frames_sorted = sorted(frames)
    prev = frames_sorted[0]
    
    for f in frames_sorted[1:]:
        if f - prev > 1:
            gaps.append((prev + 1, f - 1, f - prev - 1))
        prev = f
    
    return gaps


def verify_specific_range(frames: List[int], start: int, end: int) -> Tuple[bool, List[int]]:
    """Check if all frames in a specific range are present."""
    expected = set(range(start, end + 1))
    found = set(frames)
    missing = sorted(list(expected - found))
    return len(missing) == 0, missing


def analyze_results(json_path: str):
    """Analyze test results JSON file."""
    print("=" * 80)
    print("FRAME VERIFICATION REPORT")
    print("=" * 80)
    print(f"Analyzing: {json_path}\n")
    
    # Load results
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON file: {e}")
        sys.exit(1)
    
    # Extract frame numbers
    results = data.get('results', [])
    frames = [r['frame_number'] for r in results]
    
    if not frames:
        print("ERROR: No frames found in results!")
        sys.exit(1)
    
    # Basic statistics
    print("BASIC STATISTICS")
    print("-" * 80)
    print(f"Total frames in results: {len(frames)}")
    print(f"Frame range: {min(frames)} to {max(frames)}")
    print(f"Total frames in video: {data.get('total_frames', 'N/A')}")
    print(f"Processed frames: {data.get('processed_frames', 'N/A')}")
    print(f"Successful detections: {data.get('successful_detections', 'N/A')}")
    print(f"Detection rate: {data.get('detection_rate', 0):.2f}%")
    print()
    
    # Find all gaps
    gaps = find_gaps(frames)
    print("GAP ANALYSIS")
    print("-" * 80)
    if gaps:
        print(f"Found {len(gaps)} gap(s) in frame sequence:\n")
        for start, end, count in gaps:
            print(f"  Gap: frames {start} to {end} ({count} frames missing)")
        print()
    else:
        print("OK: No gaps found in frame sequence!")
        print()
    
    # Check specific range: 5534-5574
    print("SPECIFIC RANGE CHECK: Frames 5534-5574")
    print("-" * 80)
    all_present, missing = verify_specific_range(frames, 5534, 5574)
    
    if all_present:
        print("OK: All frames 5534-5574 are present in results!")
        # Show some sample frames
        sample_frames = [f for f in frames if 5534 <= f <= 5574][:5]
        print(f"   Sample frames found: {sample_frames}")
    else:
        print(f"FAILED: Missing {len(missing)} frames in range 5534-5574:")
        if len(missing) <= 20:
            print(f"   Missing: {missing}")
        else:
            print(f"   Missing: {missing[:10]} ... {missing[-10:]}")
            print(f"   (Total: {len(missing)} frames)")
    
    print()
    
    # Check frames around the gap
    print("CONTEXT: Frames around 5534-5574")
    print("-" * 80)
    context_frames = [f for f in frames if 5520 <= f <= 5580]
    if context_frames:
        print(f"Found {len(context_frames)} frames in range 5520-5580:")
        print(f"   Range: {min(context_frames)} to {max(context_frames)}")
        
        # Check for the specific gap
        if 5533 in frames and 5575 in frames:
            gap_size = 5575 - 5533 - 1
            print(f"   Gap between 5533 and 5575: {gap_size} frames")
            if gap_size == 41:
                print("   WARNING: Original gap still present (41 frames missing)")
            elif gap_size == 0:
                print("   OK: Gap fixed! All frames present.")
            else:
                print(f"   WARNING: Gap size changed to {gap_size} frames")
        else:
            print("   WARNING: Cannot verify gap (frames 5533 or 5575 not found)")
    else:
        print("   WARNING: No frames found in range 5520-5580")
        print("   This might mean the test didn't cover this range.")
    
    print()
    print("=" * 80)
    
    # Summary
    print("SUMMARY")
    print("-" * 80)
    if all_present and len(gaps) == 0:
        print("PERFECT: All frames present, no gaps detected!")
    elif all_present:
        print("GOOD: Frames 5534-5574 are present, but other gaps exist.")
        print(f"   Total gaps: {len(gaps)}")
    elif len(missing) < 41:
        print(f"PARTIAL: Some frames 5534-5574 are present ({41 - len(missing)}/{41})")
        print(f"   Still missing: {len(missing)} frames")
    else:
        print("FAILED: Frames 5534-5574 are still missing!")
        print(f"   Missing: {len(missing)} frames")
    
    print("=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python verify_frames.py <test_results_json_file>")
        print("\nExample:")
        print("  python verify_frames.py test_results/test_results_20251123_125838.json")
        sys.exit(1)
    
    json_path = sys.argv[1]
    
    if not Path(json_path).exists():
        print(f"ERROR: File not found: {json_path}")
        sys.exit(1)
    
    analyze_results(json_path)


if __name__ == '__main__':
    main()

