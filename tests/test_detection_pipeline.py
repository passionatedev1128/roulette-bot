"""
Test detection pipeline with video file.
This simulates the full bot cycle without placing actual bets.
"""

from backend.app.detection.screen_detector import ScreenDetector
from backend.app.strategy.martingale_strategy import MartingaleStrategy
from backend.app.config_loader import load_config
import cv2
import json
import sys
from pathlib import Path


def test_pipeline(video_path=None, frame_skip=30, max_frames=None):
    """
    Test detection + strategy logic with video.
    
    Args:
        video_path: Path to video file (default: roleta_brazileria.mp4)
        frame_skip: Process every Nth frame (default: 30)
        max_frames: Maximum frames to process (None = all)
    """
    print("=" * 70)
    print("TESTING DETECTION PIPELINE")
    print("=" * 70)
    print("\nThis simulates what the bot will do:")
    print("  - Detect numbers from video frames")
    print("  - Update strategy with results")
    print("  - Show when strategy wants to bet")
    print("  - NO ACTUAL BETS (just simulation)")
    print()
    
    # Default video path
    if video_path is None:
        video_path = "roleta_brazileria.mp4"
    
    # Check if video exists
    if not Path(video_path).exists():
        print(f" Error: Video file not found: {video_path}")
        print("\nPlease provide video path:")
        print("  python test_detection_pipeline.py <video_path>")
        print("\nOr place video file as: roleta_brazileria.mp4")
        return
    
    # Load config
    try:
        config = load_config()
        print(" Config loaded")
    except Exception as e:
        print(f" Error loading config: {e}")
        return
    
    # Create detector
    try:
        detector = ScreenDetector(config)
        print(" Detector created")
    except Exception as e:
        print(f" Error creating detector: {e}")
        return
    
    # Create strategy
    try:
        strategy = MartingaleStrategy(config)
        print(" Strategy created")
    except Exception as e:
        print(f" Error creating strategy: {e}")
        return
    
    # Open video
    print(f"\nOpening video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f" Error: Could not open video: {video_path}")
        return
    
    # Get video info
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f" Video opened")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Processing every {frame_skip} frames")
    if max_frames:
        print(f"  Max frames to process: {max_frames}")
    
    print("\n" + "=" * 70)
    print("PROCESSING FRAMES")
    print("=" * 70)
    print()
    
    results = []
    frame_count = 0
    processed_count = 0
    detection_count = 0
    last_detected_number = None  # Track last detected number to avoid duplicates
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Limit frames if specified
            if max_frames and processed_count >= max_frames:
                break
            
            # Skip frames
            if frame_count % frame_skip != 0:
                continue
            
            processed_count += 1
            
            # Detect result (pass frame directly to detector)
            result = detector.detect_result(frame)
            
            # Only process if we got a valid number
            if result.get('number') is not None:
                detected_number = result['number']
                
                # Skip if same number as last detection (number still on screen - normal in video)
                if detected_number == last_detected_number:
                    continue
                
                # Validate result (only validate when number changes)
                if not detector.validate_result(result):
                    # Validation failed - skip this detection
                    continue
                
                # Valid new detection
                last_detected_number = detected_number
                detection_count += 1
                print(f"Frame {frame_count}: Detected {result['number']} ({result['color']}) [Confidence: {result.get('confidence', 0):.2f}]")
                
                # Update strategy with result
                try:
                    strategy.update_history(result)
                    
                    # Check if strategy wants to bet
                    bet_signal = strategy.should_bet()
                    if bet_signal:
                        print(f"   Strategy says: BET {bet_signal.get('color', 'unknown').upper()} with R$ {bet_signal.get('amount', 0):.2f}")
                    else:
                        print(f"   Strategy says: WAIT (no entry condition met)")
                    
                    results.append({
                        'frame': frame_count,
                        'detected': {
                            'number': result['number'],
                            'color': result['color'],
                            'confidence': result.get('confidence', 0)
                        },
                        'bet_signal': bet_signal
                    })
                except Exception as e:
                    print(f"   Error in strategy: {e}")
                    results.append({
                        'frame': frame_count,
                        'detected': {
                            'number': result['number'],
                            'color': result['color'],
                            'confidence': result.get('confidence', 0)
                        },
                        'error': str(e)
                    })
            else:
                # No detection
                if processed_count % 10 == 0:  # Print every 10th processed frame
                    print(f"Frame {frame_count}: No detection")
    
    except KeyboardInterrupt:
        print("\n\n Interrupted by user")
    
    cap.release()
    
    # Summary
    print("\n" + "=" * 70)
    print("PIPELINE TEST COMPLETE")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  Total frames in video: {total_frames}")
    print(f"  Frames processed: {processed_count}")
    print(f"  Detections made: {detection_count}")
    if processed_count > 0:
        detection_rate = (detection_count / processed_count) * 100
        print(f"  Detection rate: {detection_rate:.1f}%")
    
    # Count bet signals
    bet_signals = [r for r in results if r.get('bet_signal')]
    print(f"  Strategy bet signals: {len(bet_signals)}")
    
    # Save results
    output_file = 'pipeline_test_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'video_path': video_path,
            'total_frames': total_frames,
            'frames_processed': processed_count,
            'detections': detection_count,
            'detection_rate': detection_count / processed_count * 100 if processed_count > 0 else 0,
            'bet_signals': len(bet_signals),
            'results': results
        }, f, indent=2)
    
    print(f"\n Results saved to: {output_file}")
    print("\nThis file contains:")
    print("  - All detections made")
    print("  - Strategy decisions (when to bet)")
    print("  - Full pipeline simulation")
    print("\nReview the file to see:")
    print("  - Detection accuracy")
    print("  - Strategy logic working")
    print("  - When bot would place bets")


if __name__ == '__main__':
    # Parse arguments
    video_path = sys.argv[1] if len(sys.argv) > 1 else None
    frame_skip = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    max_frames = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    test_pipeline(video_path, frame_skip, max_frames)

