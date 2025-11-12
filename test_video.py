"""
Video Testing Script
Test the bot's detection capabilities using a video file.
"""

import cv2
import argparse
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Optional

from backend.app.detection import ScreenDetector
from backend.app.detection.frame_detector import FrameDetector
from backend.app.config_loader import ConfigLoader


def test_video_detection(
    video_path: str,
    config_path: str = 'config/default_config.json',
    output_dir: str = 'test_results',
    frame_skip: int = 1,
    start_seconds: float = 0.0,
    end_seconds: Optional[float] = None,
    display_windows: bool = False,
    use_frame_detector: bool = False,
):
    """
    Test detection on video file.
    
    Args:
        video_path: Path to video file
        config_path: Path to configuration file
        output_dir: Directory to save test results
        frame_skip: Process every Nth frame (1 = all frames)
        start_seconds: Start processing from this timestamp (seconds)
        end_seconds: Stop processing at this timestamp (seconds)
        display_windows: Whether to show video frames in a window
    """
    # Load configuration
    print(f"Loading configuration from {config_path}...")
    config = ConfigLoader.load_config(config_path)
    
    # Initialize detector
    print("Initializing screen detector...")
    if use_frame_detector:
        detector = FrameDetector(config, video_path)
        cap = detector.cap
    else:
        detector = ScreenDetector(config)
        cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_path}")
        sys.exit(1)
    
    # Get video info
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"Video info: {total_frames} frames, {fps:.2f} FPS, {duration:.2f} seconds")
    print(f"Processing every {frame_skip} frame(s)...")
    
    # Calculate end frame if requested
    start_frame = 0
    end_frame = total_frames if end_seconds is None else min(int(end_seconds * fps), total_frames)

    if start_seconds > 0 and fps > 0:
        start_frame = int(start_seconds * fps)
        start_frame = min(start_frame, max(total_frames - 1, 0))
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        print(f"Starting from {start_seconds:.2f}s (frame {start_frame})")
    if end_seconds is not None:
        print(f"Ending at {end_seconds:.2f}s (frame {end_frame})")
    print("-" * 60)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Results storage
    results = []
    frame_count = start_frame
    processed_count = 0
    successful_detections = 0
    
    # Process frames
    print("\nProcessing frames...")
    print("Press 'q' to quit, 's' to save current frame, 'p' to pause/resume\n")
    
    paused = False
    
    while True:
        if not paused:
            if use_frame_detector:
                frame = detector.capture_screen()
                if frame is None:
                    break
            else:
                ret, frame = cap.read()
                if not ret:
                    break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue
            processed_count += 1

            try:
                result = detector.detect_result(frame)
                
                if result.get('number') is not None:
                    successful_detections += 1
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"Frame {frame_count}/{total_frames} ({processed_count} processed) {status}")
                print(f"  Number: {result.get('number', 'N/A')}")
                print(f"  Color: {result.get('color', 'N/A')}")
                print(f"  Zero: {result.get('zero', False)}")
                print(f"  Confidence: {result.get('confidence', 0):.2f}")
                print(f"  Method: {result.get('method', 'N/A')}")
                print()
                
                results.append({
                    "frame_number": frame_count,
                    "timestamp": frame_count / fps if fps > 0 else frame_count,
                    "result": result
                })
            except Exception as e:
                print(f"Frame {frame_count} - Error: {e}")
                results.append({
                    "frame_number": frame_count,
                    "timestamp": frame_count / fps if fps > 0 else frame_count,
                    "error": str(e)
                })

            if use_frame_detector and frame_count >= total_frames:
                print("Reached end of video.")
                break
            if frame_count >= end_frame:
                print(f"Reached end frame {end_frame}.")
                break
        
        if display_windows and frame is not None:
            if detector.screen_region:
                x, y, w, h = detector.screen_region
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            try:
                cv2.imshow('Video Test', frame)
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\nStopped by user")
                    break
                elif key == ord('s'):
                    frame_file = output_path / f"frame_{frame_count}.png"
                    cv2.imwrite(str(frame_file), frame)
                    print(f"Saved frame to {frame_file}")
                elif key == ord('p'):
                    paused = not paused
                    print("Paused" if paused else "Resumed")
            except cv2.error as e:
                print(f"Display error: {e}")
                display_windows = False
    
    # Cleanup
    if use_frame_detector:
        detector.release()
    else:
        cap.release()
    if display_windows:
        try:
            cv2.destroyAllWindows()
        except cv2.error as e:
            print(f"Window cleanup error: {e}")
    
    # Save results
    print("\n" + "-" * 60)
    print("Saving results...")
    
    # Save JSON results
    json_file = output_path / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "video_path": str(video_path),
            "config_path": str(config_path),
            "total_frames": total_frames,
            "processed_frames": processed_count,
            "successful_detections": successful_detections,
            "detection_rate": (successful_detections / processed_count * 100) if processed_count > 0 else 0,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {json_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total frames in video: {total_frames}")
    print(f"Frames processed: {processed_count}")
    print(f"Successful detections: {successful_detections}")
    print(f"Detection rate: {(successful_detections / processed_count * 100) if processed_count > 0 else 0:.2f}%")
    print(f"Results saved to: {json_file}")
    print("=" * 60)
    
    # Analyze results
    if results:
        print("\nDetection Analysis:")
        
        # Count by method
        methods = {}
        colors = {}
        numbers_detected = []
        
        for r in results:
            if 'result' in r:
                method = r['result'].get('method', 'unknown')
                methods[method] = methods.get(method, 0) + 1
                
                color = r['result'].get('color', 'unknown')
                colors[color] = colors.get(color, 0) + 1
                
                num = r['result'].get('number')
                if num is not None:
                    numbers_detected.append(num)
        
        print("\nDetection Methods:")
        for method, count in methods.items():
            print(f"  {method}: {count}")
        
        print("\nColors Detected:")
        for color, count in colors.items():
            print(f"  {color}: {count}")
        
        if numbers_detected:
            print(f"\nNumbers Detected: {len(numbers_detected)}")
            print(f"  Range: {min(numbers_detected)} - {max(numbers_detected)}")
            print(f"  Unique numbers: {len(set(numbers_detected))}")
        
        # Confidence analysis
        confidences = [r['result'].get('confidence', 0) for r in results if 'result' in r]
        if confidences:
            print(f"\nConfidence Statistics:")
            print(f"  Average: {sum(confidences) / len(confidences):.2f}")
            print(f"  Min: {min(confidences):.2f}")
            print(f"  Max: {max(confidences):.2f}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Test roulette bot detection on video file')
    parser.add_argument(
        'video',
        type=str,
        help='Path to video file'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to configuration file (default: config/default_config.json)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='test_results',
        help='Output directory for test results (default: test_results)'
    )
    parser.add_argument(
        '--skip',
        type=int,
        default=1,
        help='Process every Nth frame (default: 1 = all frames)'
    )
    parser.add_argument(
        '--start',
        type=float,
        default=0.0,
        help='Start processing at this timestamp (seconds, default: 0)'
    )
    parser.add_argument(
        '--end',
        type=float,
        default=None,
        help='Stop processing at this timestamp (seconds)'
    )
    parser.add_argument(
        '--display',
        action='store_true',
        help='Show video frames in a window (requires GUI support)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['screen', 'frame'],
        default='screen',
        help='screen: capture desktop, frame: read from video file'
    )
    
    args = parser.parse_args()
    
    # Check if video exists
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Check if config exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Run test
    test_video_detection(
        str(video_path),
        str(config_path),
        args.output,
        args.skip,
        args.start,
        args.end,
        args.display,
        use_frame_detector=(args.mode == 'frame')
    )


if __name__ == '__main__':
    main()

