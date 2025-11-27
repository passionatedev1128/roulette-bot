"""
Debug script to test winning number template matching on video frames.
Shows confidence scores for each template to identify detection issues.
"""

import cv2
import argparse
from pathlib import Path
import sys
from backend.app.config_loader import ConfigLoader
from backend.app.detection.frame_detector import FrameDetector


def test_templates_on_video(video_path: str, config_path: str, max_frames: int = 100):
    """Test all winning templates on video frames and show confidence scores."""
    
    # Load config
    config = ConfigLoader.load_config(config_path)
    
    # Initialize frame detector
    frame_detector = FrameDetector(config, video_path)
    
    # Get the detector's template matching method
    detector = frame_detector
    
    print("=" * 80)
    print("WINNING TEMPLATE DETECTION DEBUG")
    print("=" * 80)
    print(f"Video: {video_path}")
    print(f"Templates directory: {detector.winning_templates_dir}")
    print(f"Template threshold: {detector.winning_template_threshold}")
    print(f"Loaded templates: {len(detector.winning_templates)}")
    for num, _ in detector.winning_templates:
        print(f"  - Number {num}")
    print("-" * 80)
    
    frame_count = 0
    detection_count = 0
    no_detection_count = 0
    
    # Track all confidence scores per template
    template_scores = {num: [] for num, _ in detector.winning_templates}
    
    try:
        while frame_count < max_frames:
            frame = frame_detector.capture_screen()
            if frame is None:
                print("\nEnd of video reached.")
                break
            
            frame_count += 1
            
            # Get ROI
            if detector.screen_region:
                x, y, w, h = detector.screen_region
                roi = frame[y:y+h, x:x+w]
            else:
                roi = frame
            
            # Test template matching
            if detector.winning_templates:
                processed = detector._preprocess_badge_image(roi)
                best_number = None
                best_score = -1.0
                all_scores = {}
                
                for number, template in detector.winning_templates:
                    h, w = template.shape
                    resized = cv2.resize(processed, (w, h), interpolation=cv2.INTER_AREA)
                    try:
                        result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
                        score = float(result[0][0])
                        all_scores[number] = score
                        template_scores[number].append(score)
                        
                        if score > best_score:
                            best_score = score
                            best_number = number
                    except cv2.error as e:
                        print(f"Error matching template {number}: {e}")
                        continue
                
                # Show results
                if best_number is not None and best_score >= detector.winning_template_threshold:
                    detection_count += 1
                    print(f"\n[Frame {frame_count}]  DETECTED: Number {best_number} (confidence: {best_score:.3f})")
                    print(f"  All scores: {', '.join([f'{n}={s:.3f}' for n, s in sorted(all_scores.items(), key=lambda x: x[1], reverse=True)])}")
                else:
                    no_detection_count += 1
                    if frame_count % 10 == 0 or best_score > 0.5:  # Show every 10th frame or if close to threshold
                        print(f"\n[Frame {frame_count}]  NO DETECTION (best: {best_number}={best_score:.3f} < {detector.winning_template_threshold})")
                        if best_score > 0.5:
                            print(f"  All scores: {', '.join([f'{n}={s:.3f}' for n, s in sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:3]])}")
            else:
                print(f"[Frame {frame_count}] No templates loaded!")
    
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        frame_detector.release()
    
    # Print statistics
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total frames processed: {frame_count}")
    print(f"Successful detections: {detection_count}")
    print(f"No detections: {no_detection_count}")
    print(f"Detection rate: {detection_count/frame_count*100:.1f}%" if frame_count > 0 else "N/A")
    
    print("\nTemplate confidence statistics:")
    print("-" * 80)
    for number in sorted(template_scores.keys()):
        scores = template_scores[number]
        if scores:
            avg = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            above_threshold = sum(1 for s in scores if s >= detector.winning_template_threshold)
            print(f"Number {number:2d}: avg={avg:.3f}, max={max_score:.3f}, min={min_score:.3f}, "
                  f"above_threshold={above_threshold}/{len(scores)} ({above_threshold/len(scores)*100:.1f}%)")
        else:
            print(f"Number {number:2d}: No matches found")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    # Check if threshold might be too high
    all_max_scores = []
    for scores in template_scores.values():
        if scores:
            all_max_scores.extend(scores)
    
    if all_max_scores:
        overall_max = max(all_max_scores)
        overall_avg = sum(all_max_scores) / len(all_max_scores)
        print(f"Overall max confidence: {overall_max:.3f}")
        print(f"Overall avg confidence: {overall_avg:.3f}")
        
        if overall_max < detector.winning_template_threshold:
            print(f" WARNING: Maximum confidence ({overall_max:.3f}) is below threshold ({detector.winning_template_threshold})")
            print(f"  Consider lowering threshold to {overall_max * 0.95:.3f}")
        elif overall_avg < detector.winning_template_threshold * 0.8:
            print(f" WARNING: Average confidence ({overall_avg:.3f}) is well below threshold")
            print(f"  Consider lowering threshold to {overall_avg * 1.1:.3f}")


def main():
    parser = argparse.ArgumentParser(description='Debug winning template matching on video')
    parser.add_argument('video', type=str, help='Path to video file')
    parser.add_argument('--config', type=str, default='config/default_config.json', help='Config file path')
    parser.add_argument('--max-frames', type=int, default=100, help='Maximum frames to process')
    
    args = parser.parse_args()
    
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    test_templates_on_video(str(video_path), str(config_path), args.max_frames)


if __name__ == '__main__':
    main()

