"""
Test winning number detection from frame 1000 to frame 1020
"""

import cv2
import argparse
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Optional

import logging

from backend.app.detection.frame_detector import FrameDetector
from backend.app.config_loader import ConfigLoader

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_frames_1000_1020(
    video_path: str,
    config_path: str = 'config/default_config.json',
    start_frame: int = 1000,
    end_frame: int = 1020,
    output_dir: str = 'test_results',
    save_frames: bool = False,
):
    """
    Test detection on frames 1000-1020 specifically.
    
    Args:
        video_path: Path to video file
        config_path: Path to configuration file
        start_frame: Starting frame number (default: 1000)
        end_frame: Ending frame number (default: 1020)
        output_dir: Directory to save test results
        save_frames: Whether to save frame images
    """
    # Load configuration
    print(f"Loading configuration from {config_path}...")
    config = ConfigLoader.load_config(config_path)
    
    # Initialize FrameDetector starting from frame 1000
    print(f"Initializing FrameDetector starting from frame {start_frame}...")
    detector = FrameDetector(config, video_path, start_frame=start_frame)
    
    # Get video info
    cap = detector.cap
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"\nVideo info:")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Start frame: {start_frame}")
    print(f"  End frame: {end_frame}")
    print(f"  Testing range: frames {start_frame} to {end_frame} ({end_frame - start_frame + 1} frames)")
    
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
    
    print("\n" + "=" * 80)
    print("TESTING FRAMES 1000-1020")
    print("=" * 80)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Results storage
    results = []
    successful_detections = 0
    
    # Process frames from 1000 to 1020
    current_frame = start_frame
    processed_count = 0
    
    print(f"\nProcessing frames {start_frame} to {end_frame}...\n")
    
    while current_frame <= end_frame:
        # Capture frame
        frame = detector.capture_screen()
        
        if frame is None:
            print(f"  Frame {current_frame}: Failed to capture (end of video or error)")
            results.append({
                "frame_number": current_frame,
                "status": "failed_capture",
                "result": None
            })
            break
        
        # Get actual frame number
        actual_frame_number = detector.get_current_frame_number()
        if actual_frame_number != current_frame:
            print(f"  Frame number mismatch: expected {current_frame}, got {actual_frame_number}")
            current_frame = actual_frame_number
        
        processed_count += 1
        
        # Detect result from frame
        try:
            result = detector.detect_result(frame)
            
            # Check if we got a valid number
            detected_number = result.get('number') if result else None
            detected_color = result.get('color') if result else None
            confidence = result.get('confidence', 0) if result else 0
            method = result.get('method', 'N/A') if result else 'N/A'
            
            if detected_number is not None:
                successful_detections += 1
                status = " DETECTED"
                # Validate result
                is_valid = detector.validate_result(result) if result else False
                validation_status = " Valid" if is_valid else " Invalid"
            else:
                status = " NO DETECTION"
                validation_status = "N/A"
            
            # Print frame result
            print(f"Frame {current_frame:4d}: {status}")
            if detected_number is not None:
                print(f"  Number: {detected_number}")
                print(f"  Color: {detected_color}")
                print(f"  Confidence: {confidence:.2f}")
                print(f"  Method: {method}")
                print(f"  Validation: {validation_status}")
                
                # Highlight frame 1004 specifically
                if current_frame == 1004:
                    print(f"   FRAME 1004 - Looking for number 33")
                    if detected_number == 33:
                        print(f"   SUCCESS! Number 33 detected in frame 1004!")
                    else:
                        print(f"    Expected 33, but detected {detected_number}")
            else:
                print(f"  No number detected")
                # Highlight frame 1004 specifically
                if current_frame == 1004:
                    print(f"    FRAME 1004 - Expected number 33, but nothing detected!")
            
            print()
            
            # Save frame image if requested
            if save_frames:
                frame_file = output_path / f"frame_{current_frame}.png"
                cv2.imwrite(str(frame_file), frame)
            
            # Store result
            results.append({
                "frame_number": current_frame,
                "actual_frame_number": actual_frame_number,
                "status": "detected" if detected_number is not None else "no_detection",
                "result": result,
                "validation_passed": detector.validate_result(result) if result and detected_number is not None else None
            })
            
        except Exception as e:
            logger.error(f"Error processing frame {current_frame}: {e}", exc_info=True)
            print(f"Frame {current_frame:4d}:  ERROR - {e}\n")
            results.append({
                "frame_number": current_frame,
                "status": "error",
                "error": str(e),
                "result": None
            })
        
        # Move to next frame
        current_frame += 1
        
        # Check if we've reached the end frame
        if current_frame > end_frame:
            break
    
    # Cleanup
    detector.release()
    
    # Save results
    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    
    json_file = output_path / f"test_frames_{start_frame}_to_{end_frame}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        result_data = {
            "test_range": {
                "start_frame": start_frame,
                "end_frame": end_frame,
                "total_frames_tested": processed_count
            },
            "video_info": {
                "video_path": str(video_path),
                "total_frames": total_frames,
                "fps": fps
            },
            "statistics": {
                "frames_processed": processed_count,
                "successful_detections": successful_detections,
                "detection_rate": (successful_detections / processed_count * 100) if processed_count > 0 else 0
            },
            "results": results
        }
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {json_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Frames tested: {processed_count} (frames {start_frame} to {end_frame})")
    print(f"Successful detections: {successful_detections}")
    print(f"Detection rate: {(successful_detections / processed_count * 100) if processed_count > 0 else 0:.2f}%")
    print(f"Results saved to: {json_file}")
    
    # Detailed frame-by-frame summary
    print("\n" + "-" * 80)
    print("FRAME-BY-FRAME SUMMARY")
    print("-" * 80)
    for r in results:
        frame_num = r['frame_number']
        if r['status'] == 'detected' and r.get('result'):
            num = r['result'].get('number')
            color = r['result'].get('color')
            conf = r['result'].get('confidence', 0)
            print(f"Frame {frame_num:4d}:  Number {num}, Color {color}, Confidence {conf:.2f}")
        elif r['status'] == 'no_detection':
            print(f"Frame {frame_num:4d}:  No detection")
        elif r['status'] == 'error':
            print(f"Frame {frame_num:4d}:   Error: {r.get('error', 'Unknown error')}")
        else:
            print(f"Frame {frame_num:4d}: ? Status: {r['status']}")
    
    # Check frame 1004 specifically
    frame_1004_result = next((r for r in results if r['frame_number'] == 1004), None)
    if frame_1004_result:
        print("\n" + "-" * 80)
        print("FRAME 1004 ANALYSIS (Expected: Number 33)")
        print("-" * 80)
        if frame_1004_result['status'] == 'detected' and frame_1004_result.get('result'):
            num = frame_1004_result['result'].get('number')
            if num == 33:
                print(" SUCCESS: Number 33 detected in frame 1004!")
            else:
                print(f"  MISMATCH: Expected 33, but detected {num}")
            print(f"   Color: {frame_1004_result['result'].get('color')}")
            print(f"   Confidence: {frame_1004_result['result'].get('confidence', 0):.2f}")
            print(f"   Method: {frame_1004_result['result'].get('method', 'N/A')}")
        else:
            print(" FAILED: No number detected in frame 1004")
            if frame_1004_result['status'] == 'error':
                print(f"   Error: {frame_1004_result.get('error', 'Unknown error')}")
    
    print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test winning number detection on frames 1000-1020',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test frames 1000-1020
  python test_frames_1000_1020.py video.mp4
  
  # Test different range
  python test_frames_1000_1020.py video.mp4 --start 1000 --end 1010
  
  # Save frame images
  python test_frames_1000_1020.py video.mp4 --save-frames
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
        '--start',
        type=int,
        default=1000,
        help='Starting frame number (default: 1000)'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=1020,
        help='Ending frame number (default: 1020)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='test_results',
        help='Output directory for test results (default: test_results)'
    )
    parser.add_argument(
        '--save-frames',
        action='store_true',
        help='Save frame images to output directory'
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
    
    # Validate frame range
    if args.start < 0:
        print(f"Error: Start frame must be >= 0, got {args.start}")
        sys.exit(1)
    if args.end < args.start:
        print(f"Error: End frame ({args.end}) must be >= start frame ({args.start})")
        sys.exit(1)
    
    # Run test
    test_frames_1000_1020(
        str(video_path),
        str(config_path),
        args.start,
        args.end,
        args.output,
        args.save_frames
    )


if __name__ == '__main__':
    main()

