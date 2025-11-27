"""
Create Number Templates from Video
Extracts number images from video frames to create templates for detection.
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path
import json
from datetime import datetime


def extract_frames_with_numbers(video_path, output_dir='template_frames', frame_skip=30, max_frames=50):
    """
    Extract frames from video that likely contain numbers.
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save extracted frames
        frame_skip: Process every Nth frame
        max_frames: Maximum frames to extract
    """
    print("=" * 70)
    print("EXTRACTING FRAMES FROM VIDEO")
    print("=" * 70)
    print(f"\nVideo: {video_path}")
    print(f"Output: {output_dir}/")
    print(f"Extracting every {frame_skip} frames (max {max_frames} frames)")
    print()
    
    # Check video exists
    if not Path(video_path).exists():
        print(f" Error: Video file not found: {video_path}")
        return False
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f" Error: Could not open video: {video_path}")
        return False
    
    # Get video info
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f" Video opened")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Duration: {total_frames/fps:.1f} seconds")
    print()
    
    # Extract frames
    frame_count = 0
    extracted = 0
    
    print("Extracting frames...")
    while cap.isOpened() and extracted < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Skip frames
        if frame_count % frame_skip != 0:
            continue
        
        # Save frame
        output_path = os.path.join(output_dir, f"frame_{frame_count:05d}.png")
        cv2.imwrite(output_path, frame)
        extracted += 1
        
        if extracted % 10 == 0:
            print(f"  Extracted {extracted} frames...")
    
    cap.release()
    
    print(f"\n Extracted {extracted} frames to {output_dir}/")
    print(f"\nNext steps:")
    print(f"  1. Open frames in {output_dir}/")
    print(f"  2. Find frames that show numbers clearly")
    print(f"  3. Use interactive tool to crop numbers:")
    print(f"     python create_templates_from_video.py crop {output_dir}")
    
    return True


def interactive_crop_numbers(frames_dir='template_frames', templates_dir='templates'):
    """
    Interactive tool to crop numbers from frames and save as templates.
    """
    print("=" * 70)
    print("INTERACTIVE NUMBER TEMPLATE CREATION")
    print("=" * 70)
    print("\nThis tool helps you crop numbers from frames.")
    print("You'll select frames and crop regions for each number (0-36).")
    print()
    
    # Check frames directory
    if not os.path.exists(frames_dir):
        print(f" Error: Frames directory not found: {frames_dir}")
        print(f"\nFirst extract frames:")
        print(f"  python create_templates_from_video.py extract <video_file>")
        return False
    
    # Create templates directory
    os.makedirs(templates_dir, exist_ok=True)
    
    # Get list of frames
    frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
    if not frame_files:
        print(f" No frame files found in {frames_dir}/")
        return False
    
    print(f" Found {len(frame_files)} frames")
    print(f"\nInstructions:")
    print(f"  1. For each number (0-36), you'll select a frame")
    print(f"  2. Draw a rectangle around the number")
    print(f"  3. Press 's' to save, 'n' for next number, 'd' for previous number, 'q' to quit")
    print()
    
    # Numbers to create templates for
    numbers = list(range(37))  # 0-36
    
    # Check which templates already exist
    existing = []
    for num in numbers:
        template_path = os.path.join(templates_dir, f"number_{num}.png")
        if os.path.exists(template_path):
            existing.append(num)
    
    if existing:
        print(f" Already have templates for: {existing}")
        response = input("Continue anyway? (y/n): ").lower()
        if response != 'y':
            return False
    
    print("\n" + "=" * 70)
    print("STARTING INTERACTIVE CROPPING")
    print("=" * 70)
    print("\nFor each number, you'll:")
    print("  1. See a frame from the video")
    print("  2. Click and drag to select the number")
    print("  3. Press 's' to save, 'n' for next number, 'd' for previous number, 'q' to quit")
    print()
    
    # Mouse callback for selecting region
    drawing = False
    ix, iy = -1, -1
    fx, fy = -1, -1
    current_frame = None
    current_frame_path = None
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal drawing, ix, iy, fx, fy, current_frame
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                fx, fy = x, y
                # Draw rectangle on copy
                display = current_frame.copy()
                cv2.rectangle(display, (ix, iy), (fx, fy), (0, 255, 0), 2)
                cv2.imshow('Select Number Region', display)
        
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            fx, fy = x, y
    
    # Initialize window
    cv2.namedWindow('Select Number Region')
    cv2.setMouseCallback('Select Number Region', mouse_callback)
    
    # Process numbers with navigation
    num_idx = 0  # Current number index
    frame_idx = 0  # Current frame index
    
    def load_number(num):
        """Load and display frame for a specific number."""
        nonlocal current_frame, frame_idx, ix, iy, fx, fy
        
        template_path = os.path.join(templates_dir, f"number_{num}.png")
        
        # Load frame
        frame_path = os.path.join(frames_dir, frame_files[frame_idx])
        current_frame = cv2.imread(frame_path)
        
        if current_frame is None:
            print(f"   Could not load frame: {frame_path}")
            return False
        
        # Reset selection
        ix, iy, fx, fy = -1, -1, -1, -1
        
        # Show frame
        cv2.imshow('Select Number Region', current_frame)
        
        # Print status
        exists = "" if os.path.exists(template_path) else " "
        print(f"\n[{num+1}/37] Number {num} {exists}")
        print(f"  Showing frame {frame_idx + 1}/{len(frame_files)}")
        print("  Instructions:")
        print("    - Click and drag to select the number")
        print("    - Press 's' to save")
        print("    - Press 'n' for next number")
        print("    - Press 'd' for previous number")
        print("    - Press 'f' to show next frame")
        print("    - Press 'q' to quit")
        
        return True
    
    # Load first number
    if not load_number(numbers[num_idx]):
        cv2.destroyAllWindows()
        return False
    
    # Main loop - navigate between numbers
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            # Save cropped region
            num = numbers[num_idx]
            template_path = os.path.join(templates_dir, f"number_{num}.png")
            
            if ix != -1 and fx != -1 and iy != -1 and fy != -1:
                x1, x2 = min(ix, fx), max(ix, fx)
                y1, y2 = min(iy, fy), max(iy, fy)
                
                # Crop
                cropped = current_frame[y1:y2, x1:x2]
                
                if cropped.size > 0:
                    cv2.imwrite(template_path, cropped)
                    print(f"   Saved template: {template_path} ({x2-x1}x{y2-y1} pixels)")
                    frame_idx = (frame_idx + 1) % len(frame_files)
                    # Reload to show saved status
                    load_number(num)
                else:
                    print("   Invalid selection, try again")
            else:
                print("   Please select a region first")
        
        elif key == ord('n'):
            # Next number (increase)
            num_idx = (num_idx + 1) % len(numbers)
            frame_idx = (frame_idx + 1) % len(frame_files)
            load_number(numbers[num_idx])
        
        elif key == ord('d'):
            # Previous number (decrease)
            num_idx = (num_idx - 1) % len(numbers)
            frame_idx = (frame_idx - 1) % len(frame_files)
            load_number(numbers[num_idx])
        
        elif key == ord('f'):
            # Next frame (for current number)
            frame_idx = (frame_idx + 1) % len(frame_files)
            load_number(numbers[num_idx])
        
        elif key == ord('q'):
            print("\n Quitting...")
            break
    
    cv2.destroyAllWindows()
    
    # Verify templates
    print("\n" + "=" * 70)
    print("TEMPLATE CREATION COMPLETE")
    print("=" * 70)
    
    verify_templates(templates_dir)
    
    return True


def verify_templates(templates_dir='templates'):
    """Verify all templates are present and valid."""
    print("\nVerifying templates...")
    
    if not os.path.exists(templates_dir):
        print(f" Templates directory not found: {templates_dir}")
        return False
    
    valid = []
    missing = []
    invalid = []
    
    for i in range(37):
        template_path = os.path.join(templates_dir, f"number_{i}.png")
        
        if not os.path.exists(template_path):
            missing.append(i)
        else:
            img = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                invalid.append(i)
            else:
                valid.append(i)
                h, w = img.shape[:2]
                size_kb = os.path.getsize(template_path) / 1024
                print(f"   number_{i}.png: {w}x{h} pixels, {size_kb:.1f} KB")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Valid templates: {len(valid)}/37")
    
    if missing:
        print(f"\n Missing ({len(missing)}): {missing[:10]}{'...' if len(missing) > 10 else ''}")
    
    if invalid:
        print(f"\n Invalid ({len(invalid)}): {invalid}")
    
    if len(valid) == 37:
        print("\n All templates valid and ready!")
        print("\nYou can now use template matching for detection!")
        return True
    else:
        print(f"\n Need {37 - len(valid)} more templates")
        return False


def auto_extract_numbers(video_path, templates_dir='templates', screen_region=None):
    """
    Attempt to automatically extract numbers from video.
    This is experimental and may not work perfectly.
    """
    print("=" * 70)
    print("AUTO-EXTRACTING NUMBER TEMPLATES")
    print("=" * 70)
    print("\n This is experimental and may not work perfectly.")
    print("Manual cropping is recommended for best results.")
    print()
    
    # This would require more advanced image processing
    # For now, just guide user to manual method
    print("Auto-extraction not yet implemented.")
    print("Please use the interactive cropping method:")
    print("  1. python create_templates_from_video.py extract <video>")
    print("  2. python create_templates_from_video.py crop")
    
    return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("CREATE NUMBER TEMPLATES FROM VIDEO")
        print("=" * 70)
        print("\nUsage:")
        print("  1. Extract frames from video:")
        print("     python create_templates_from_video.py extract <video_file>")
        print()
        print("  2. Interactive cropping (create templates):")
        print("     python create_templates_from_video.py crop [frames_dir]")
        print()
        print("  3. Verify templates:")
        print("     python create_templates_from_video.py verify [templates_dir]")
        print()
        print("Example workflow:")
        print("  python create_templates_from_video.py extract roleta_brazileria.mp4")
        print("  python create_templates_from_video.py crop")
        print("  python create_templates_from_video.py verify")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'extract':
        video_path = sys.argv[2] if len(sys.argv) > 2 else None
        if not video_path:
            print(" Error: Video path required")
            print("Usage: python create_templates_from_video.py extract <video_file>")
            sys.exit(1)
        
        output_dir = sys.argv[3] if len(sys.argv) > 3 else 'template_frames'
        frame_skip = int(sys.argv[4]) if len(sys.argv) > 4 else 30
        max_frames = int(sys.argv[5]) if len(sys.argv) > 5 else 50
        
        extract_frames_with_numbers(video_path, output_dir, frame_skip, max_frames)
    
    elif command == 'crop':
        frames_dir = sys.argv[2] if len(sys.argv) > 2 else 'template_frames'
        templates_dir = sys.argv[3] if len(sys.argv) > 3 else 'templates'
        interactive_crop_numbers(frames_dir, templates_dir)
    
    elif command == 'verify':
        templates_dir = sys.argv[2] if len(sys.argv) > 2 else 'templates'
        verify_templates(templates_dir)
    
    elif command == 'auto':
        video_path = sys.argv[2] if len(sys.argv) > 2 else None
        if not video_path:
            print(" Error: Video path required")
            sys.exit(1)
        auto_extract_numbers(video_path)
    
    else:
        print(f" Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()

