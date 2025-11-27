"""
Find Winning Number Region - Scan frame to locate where numbers appear
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# Colab compatibility
try:
    import pyautogui
except (ImportError, OSError, KeyError, RuntimeError):
    from unittest.mock import MagicMock
    sys.modules['pyautogui'] = MagicMock()

sys.path.insert(0, os.path.abspath('.'))

from backend.app.config_loader import ConfigLoader
from backend.app.detection.frame_detector import FrameDetector
from backend.app.detection.screen_detector import ScreenDetector


def scan_frame_for_text_regions(frame: np.ndarray, min_size: int = 30, max_size: int = 100) -> List[Tuple[int, int, int, int]]:
    """Scan frame to find regions that might contain numbers."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Use edge detection to find text-like regions
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter by size and aspect ratio
    text_regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter by size
        if min_size <= w <= max_size and min_size <= h <= max_size:
            # Filter by aspect ratio (numbers are roughly square or slightly rectangular)
            aspect_ratio = w / h
            if 0.5 <= aspect_ratio <= 2.0:
                # Check if region has good variance (not uniform)
                roi = gray[y:y+h, x:x+w]
                if roi.size > 0:
                    variance = np.var(roi)
                    if variance > 200:  # Has enough variation
                        text_regions.append((x, y, w, h))
    
    return text_regions


def test_region_with_templates(frame: np.ndarray, region: Tuple[int, int, int, int], 
                               templates: List, detector: ScreenDetector) -> float:
    """Test if a region matches any template."""
    x, y, w, h = region
    roi = frame[y:y+h, x:x+w]
    
    if roi.size == 0:
        return -1.0
    
    best_score = -1.0
    
    for num, template in templates:
        # Resize ROI to match template
        h_t, w_t = template.shape
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        # Try with preprocessing
        roi_processed = detector._preprocess_badge_image(roi_gray)
        roi_resized = cv2.resize(roi_processed, (w_t, h_t), interpolation=cv2.INTER_AREA)
        
        try:
            result = cv2.matchTemplate(roi_resized, template, cv2.TM_CCOEFF_NORMED)
            score = float(result[0][0])
            if score > best_score:
                best_score = score
        except:
            continue
    
    return best_score


def find_best_region(video_path: str, config: Dict, start_frame: int = 690, 
                     num_frames: Optional[int] = None, frame_skip: int = 1) -> Optional[Tuple[int, int, int, int]]:
    """Find the best region that matches templates across multiple frames.
    
    Args:
        video_path: Path to video file
        config: Configuration dictionary
        start_frame: Frame to start scanning from
        num_frames: Number of frames to scan (None = scan to end of video)
        frame_skip: Process every Nth frame (1 = all frames)
    """
    print("=" * 80)
    print("FINDING WINNING NUMBER REGION")
    print("=" * 80)
    
    detector = ScreenDetector(config)
    
    if len(detector.winning_templates) == 0:
        print(" No templates loaded")
        return None
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(" Cannot open video")
        return None
    
    # Get total frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Determine end frame
    if num_frames is None:
        end_frame = total_frames
        frames_to_scan = total_frames - start_frame
    else:
        end_frame = min(start_frame + num_frames, total_frames)
        frames_to_scan = num_frames
    
    print(f"\nVideo info:")
    print(f"   Total frames: {total_frames}")
    print(f"   FPS: {fps:.2f}")
    print(f"   Start frame: {start_frame}")
    print(f"   End frame: {end_frame}")
    print(f"   Frames to scan: {frames_to_scan}")
    print(f"   Frame skip: {frame_skip} (processing every {frame_skip} frame)")
    
    # Collect candidate regions from multiple frames
    all_candidates = []
    frame_scores = {}
    frames_processed = 0
    last_progress = 0
    
    print(f"\nScanning frames...")
    print("-" * 80)
    
    current_frame = start_frame
    while current_frame < end_frame:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()
        
        if not ret:
            break
        
        frames_processed += 1
        
        # Progress indicator
        progress = int((current_frame - start_frame) / frames_to_scan * 100)
        if progress >= last_progress + 5:  # Update every 5%
            print(f"   Progress: {progress}% (Frame {current_frame}/{end_frame})")
            last_progress = progress
        
        # Find text-like regions
        regions = scan_frame_for_text_regions(frame, min_size=30, max_size=100)
        
        # Test each region with templates
        for region in regions:
            score = test_region_with_templates(frame, region, detector.winning_templates, detector)
            x, y, w, h = region
            
            if score > -0.5:  # Only consider regions with reasonable scores
                all_candidates.append((region, score, current_frame))
        
        # Skip frames
        current_frame += frame_skip
    
    cap.release()
    
    print(f"\n Scanning complete!")
    print(f"   Processed {frames_processed} frames")
    print(f"   Found {len(all_candidates)} candidate region matches")
    
    if not all_candidates:
        print("\n No good regions found")
        return None
    
    # Find region that appears most often or has best average score
    region_scores = {}
    for region, score, frame_num in all_candidates:
        region_key = tuple(region)
        if region_key not in region_scores:
            region_scores[region_key] = []
        region_scores[region_key].append(score)
    
    # Calculate average score per region
    best_region = None
    best_avg_score = -1.0
    
    print(f"\n" + "=" * 80)
    print("TOP CANDIDATE REGIONS")
    print("=" * 80)
    
    sorted_regions = sorted(region_scores.items(), 
                          key=lambda x: np.mean(x[1]), 
                          reverse=True)
    
    for i, (region, scores) in enumerate(sorted_regions[:10], 1):
        avg_score = np.mean(scores)
        count = len(scores)
        x, y, w, h = region
        marker = "" if avg_score > 0.3 else "" if avg_score > 0 else ""
        print(f"{marker} {i}. Region [{x}, {y}, {w}, {h}]: "
              f"avg_score={avg_score:.3f}, found_in={count} frames")
        
        if avg_score > best_avg_score:
            best_avg_score = avg_score
            best_region = list(region)
    
    if best_region:
        print(f"\n Best region found: {best_region}")
        print(f"   Average score: {best_avg_score:.3f}")
        print(f"\n Update your config with:")
        print(f'   "screen_region": {best_region}')
    else:
        print(f"\n  No region found with positive scores")
        print(f"   This suggests templates don't match the video")
        print(f"   Consider recreating templates from this video")
    
    return best_region


def visualize_regions(video_path: str, config: Dict, start_frame: int = 690):
    """Visualize candidate regions on frame."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return
    
    # Find regions
    regions = scan_frame_for_text_regions(frame, min_size=30, max_size=100)
    
    # Draw regions on frame
    frame_marked = frame.copy()
    for i, (x, y, w, h) in enumerate(regions[:20]):  # Show first 20
        cv2.rectangle(frame_marked, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame_marked, str(i), (x, y-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imwrite('frame_with_candidate_regions.png', frame_marked)
    print(f"\n Saved frame with candidate regions: frame_with_candidate_regions.png")
    print(f"   Green rectangles show potential number regions")


def main():
    """Main function."""
    config_path = 'config/default_config.json'
    video_path = 'roleta_brazileria.mp4'
    start_frame = 690
    
    # Find video
    if not Path(video_path).exists():
        video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov'))]
        if video_files:
            video_path = video_files[0]
    
    # Load config
    config = ConfigLoader.load_config(config_path)
    
    # Visualize regions
    visualize_regions(video_path, config, start_frame)
    
    # Find best region - scan entire video (set num_frames=None to scan to end)
    # Use frame_skip to speed up (process every Nth frame)
    best_region = find_best_region(video_path, config, start_frame, num_frames=None, frame_skip=10)
    
    if best_region:
        # Test the best region
        print(f"\n" + "=" * 80)
        print("TESTING BEST REGION")
        print("=" * 80)
        
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            x, y, w, h = best_region
            roi = frame[y:y+h, x:x+w]
            cv2.imwrite('best_region_roi.png', roi)
            print(f" Saved ROI from best region: best_region_roi.png")
            print(f"   👀 CHECK THIS IMAGE - Does it show the winning number?")


if __name__ == '__main__':
    main()

