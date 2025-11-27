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

import logging

from backend.app.detection import ScreenDetector
from backend.app.detection.frame_detector import FrameDetector
from backend.app.config_loader import ConfigLoader

# Enable debug logging for detection
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_video_detection(
    video_path: str,
    config_path: str = 'config/default_config.json',
    output_dir: str = 'test_results',
    frame_skip: int = 1,
    start_seconds: float = 0.0,
    end_seconds: Optional[float] = None,
    display_windows: bool = False,
    use_frame_detector: bool = False,
    max_frames: Optional[int] = None,
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
        use_frame_detector: Whether to use FrameDetector (for video files)
        max_frames: Maximum number of frames to process (None = unlimited)
    """
    # Load configuration
    print(f"Loading configuration from {config_path}...")
    config = ConfigLoader.load_config(config_path)
    
    # Initialize detector
    print("Initializing screen detector...")
    if use_frame_detector:
        detector = FrameDetector(config, video_path)
        cap = detector.cap
        
        # Get video info
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        if not cap.isOpened():
            print(f"Error: Could not open video file: {video_path}")
            sys.exit(1)
    else:
        # Screen mode: capture from desktop, not video file
        detector = ScreenDetector(config)
        cap = None  # No video file needed in screen mode
        
        # For screen mode, we don't have video metadata
        # Use default values or estimate based on timing
        fps = 30.0  # Default FPS for screen capture
        total_frames = None  # Unknown in screen mode
        duration = None
        
        print("  SCREEN MODE: Capturing from desktop, not video file")
        print("   Make sure your roulette game is visible on screen!")
    
    # Log template information
    print(f"\nTemplate Information:")
    print(f"  Templates directory: {detector.winning_templates_dir}")
    print(f"  Templates loaded: {len(detector.winning_templates)}")
    print(f"  Template threshold: {detector.winning_template_threshold}")
    if detector.winning_templates:
        numbers = sorted([num for num, _ in detector.winning_templates])
        print(f"  Template numbers: {numbers}")
    else:
        print("    WARNING: No winning templates loaded!")
    print()
    
    if use_frame_detector:
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
    else:
        # Screen mode: continuous capture
        start_frame = 0
        end_frame = None  # No end frame in screen mode
        print(f"Screen capture mode: Continuous detection")
        print(f"Processing every {frame_skip} capture(s)...")
        if max_frames is not None:
            print(f"Will process up to {max_frames} captures")
    
    print("-" * 60)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Results storage
    results = []
    frame_count = start_frame
    processed_count = 0
    successful_detections = 0
    last_detected_number = None  # Track last detected number to avoid duplicates
    
    # Calculate max frames to process
    if use_frame_detector:
        if max_frames is not None:
            max_frames_to_process = min(max_frames, end_frame - start_frame)
            print(f"Processing up to {max_frames_to_process} frames...")
        else:
            max_frames_to_process = None
    else:
        # Screen mode: use max_frames directly
        max_frames_to_process = max_frames
    
    # Process frames
    print("\nProcessing frames...")
    print("Press 'q' to quit, 's' to save current frame, 'p' to pause/resume\n")
    
    paused = False
    
    while True:
        if not paused:
            if use_frame_detector:
                # Frame mode: read from video file
                # Get actual frame number BEFORE reading (0-based from OpenCV)
                if hasattr(detector, 'get_current_frame_number'):
                    actual_frame_0based = detector.get_current_frame_number()
                    # Convert to 1-based for consistency with results
                    frame_count = actual_frame_0based + 1 if actual_frame_0based >= 0 else frame_count + 1
                else:
                    frame_count += 1
                
                frame = detector.capture_screen()
                if frame is None:
                    break
            else:
                # Screen mode: capture from desktop
                frame = detector.capture_screen()
                if frame is None:
                    print("Failed to capture screen")
                    break
                frame_count += 1

            if frame_count % frame_skip != 0:
                continue
            processed_count += 1

            try:
                # Detect result from frame
                result = detector.detect_result(frame)
                
                # Only process if we got a valid number
                should_count_as_success = False
                if result.get('number') is not None:
                    detected_number = result.get('number')
                    
                    # Skip if same number as last detection (number still on screen - normal in video)
                    if detected_number == last_detected_number:
                        status = " (duplicate)"
                    # Validate result (only validate when number changes)
                    elif not detector.validate_result(result):
                        # Validation failed - skip this detection
                        status = " (validation failed)"
                    else:
                        # Valid new detection
                        should_count_as_success = True
                        successful_detections += 1
                        last_detected_number = detected_number
                        status = ""
                else:
                    status = ""
                
                if use_frame_detector and total_frames:
                    print(f"Frame {frame_count}/{total_frames} ({processed_count} processed) {status}")
                else:
                    print(f"Capture {frame_count} ({processed_count} processed) {status}")
                print(f"  Number: {result.get('number', 'N/A')}")
                print(f"  Color: {result.get('color', 'N/A')}")
                print(f"  Zero: {result.get('zero', False)}")
                print(f"  Confidence: {result.get('confidence', 0):.2f}")
                print(f"  Method: {result.get('method', 'N/A')}")
                print()
                
                # Always add frame to results (even if duplicate or validation failed)
                # This ensures no gaps in the frame sequence
                timestamp = frame_count / fps if fps > 0 and use_frame_detector else frame_count
                results.append({
                    "frame_number": frame_count,
                    "timestamp": timestamp,
                    "result": result
                })
            except Exception as e:
                print(f"Frame {frame_count} - Error: {e}")
                timestamp = frame_count / fps if fps > 0 and use_frame_detector else frame_count
                results.append({
                    "frame_number": frame_count,
                    "timestamp": timestamp,
                    "error": str(e)
                })

            # Check max frames limit
            if max_frames_to_process is not None and processed_count >= max_frames_to_process:
                print(f"Reached max frames limit ({max_frames_to_process}).")
                break
            
            if use_frame_detector:
                # Frame mode: check video end
                if frame_count >= total_frames:
                    print("Reached end of video.")
                    break
                if end_frame is not None and frame_count >= end_frame:
                    print(f"Reached end frame {end_frame}.")
                    break
            # Screen mode: continue indefinitely (or until max_frames)
        
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
    # Screen mode: no video file to release
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
        result_data = {
            "mode": "frame" if use_frame_detector else "screen",
            "config_path": str(config_path),
            "processed_frames": processed_count,
            "successful_detections": successful_detections,
            "detection_rate": (successful_detections / processed_count * 100) if processed_count > 0 else 0,
            "results": results
        }
        if use_frame_detector:
            result_data["video_path"] = str(video_path)
            result_data["total_frames"] = total_frames
        else:
            result_data["source"] = "desktop_screen"
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {json_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    if use_frame_detector:
        print(f"Total frames in video: {total_frames}")
    else:
        print(f"Mode: Screen capture (desktop)")
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
    parser = argparse.ArgumentParser(
        description='Test roulette bot detection on video file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test from 30 seconds onwards
  python test_video.py video.mp4 --start 30
  
  # Test from 30s to 60s (30 seconds of video)
  python test_video.py video.mp4 --start 30 --end 60
  
  # Test from 30s, process every 5th frame
  python test_video.py video.mp4 --start 30 --skip 5
  
  # Test from 30s, limit to 100 frames
  python test_video.py video.mp4 --start 30 --max-frames 100
        """
    )
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
        help='Start processing at this timestamp in seconds (default: 0.0). Example: --start 30 to start from 30 seconds'
    )
    parser.add_argument(
        '--end',
        type=float,
        default=None,
        help='Stop processing at this timestamp in seconds (default: end of video)'
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
        default='frame',
        help='screen: capture desktop, frame: read from video file (default: frame)'
    )
    parser.add_argument(
        '--max-frames',
        type=int,
        default=None,
        dest='max_frames',
        help='Maximum number of frames to process (default: unlimited)'
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
        use_frame_detector=(args.mode == 'frame'),
        max_frames=args.max_frames
    )


if __name__ == '__main__':
    main()

