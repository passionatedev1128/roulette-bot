"""
Template Creation Helper
Assists in creating number templates from video or screenshots.
"""

import cv2
import os
import sys
from pathlib import Path


def extract_numbers_from_video(video_path, output_dir='template_frames', frame_skip=30):
    """Extract frames from video for template creation."""
    print(f"Extracting frames from: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    frame_count = 0
    extracted = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if frame_count % frame_skip == 0:
            output_path = os.path.join(output_dir, f"frame_{frame_count:05d}.png")
            cv2.imwrite(output_path, frame)
            extracted += 1
            print(f"Extracted frame {frame_count}")
    
    cap.release()
    print(f"\n Extracted {extracted} frames to {output_dir}/")
    print(f"\nNext steps:")
    print(f"1. Open frames in {output_dir}/")
    print(f"2. Crop individual numbers (0-36)")
    print(f"3. Save as templates/number_X.png")


def verify_templates(template_dir='templates'):
    """Verify all templates are present and valid."""
    print("=" * 70)
    print("TEMPLATE VERIFICATION")
    print("=" * 70)
    
    if not os.path.exists(template_dir):
        print(f" Templates directory not found: {template_dir}")
        print(f"\nCreate it with: mkdir {template_dir}")
        return False
    
    valid = []
    missing = []
    invalid = []
    
    for i in range(37):
        template_path = os.path.join(template_dir, f"number_{i}.png")
        
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
                print(f" number_{i}.png: {w}x{h} pixels, {size_kb:.1f} KB")
    
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
        return True
    else:
        print(f"\n Need {37 - len(valid)} more templates")
        print("\nTo create templates:")
        print("1. Take screenshots when numbers appear")
        print("2. Open in image editor")
        print("3. Crop each number (0-36)")
        print("4. Save as templates/number_X.png")
        return False


def create_template_from_region(image_path, region, output_path):
    """Extract number from specific region of image."""
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load {image_path}")
        return False
    
    x, y, w, h = region
    roi = img[y:y+h, x:x+w]
    
    cv2.imwrite(output_path, roi)
    print(f" Extracted to {output_path}")
    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python template_creation_helper.py extract <video_file> [output_dir]")
        print("  python template_creation_helper.py verify [template_dir]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'extract':
        video_path = sys.argv[2] if len(sys.argv) > 2 else None
        if not video_path:
            print("Error: Video path required")
            sys.exit(1)
        output_dir = sys.argv[3] if len(sys.argv) > 3 else 'template_frames'
        extract_numbers_from_video(video_path, output_dir)
    
    elif command == 'verify':
        template_dir = sys.argv[2] if len(sys.argv) > 2 else 'templates'
        verify_templates(template_dir)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()

