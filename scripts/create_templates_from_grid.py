"""
Create Number Templates from Betting Grid Snapshot
Extracts all numbers (0-36) from a single betting grid image.
This is the CORRECT way to create templates!
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path


def extract_from_grid_snapshot(image_path, templates_dir='templates'):
    """
    Extract all number templates from a single betting grid snapshot.
    
    This is the proper way - all numbers come from the same image,
    ensuring consistent styling and reducing false positives.
    
    Args:
        image_path: Path to betting grid screenshot
        templates_dir: Directory to save templates
    """
    print("=" * 70)
    print("EXTRACT TEMPLATES FROM BETTING GRID")
    print("=" * 70)
    print("\nThis tool extracts all numbers (0-36) from a single snapshot.")
    print("This ensures consistent styling and reduces false positives.")
    print()
    
    # Check image exists
    if not Path(image_path).exists():
        print(f" Error: Image file not found: {image_path}")
        print("\nPlease take a screenshot of your betting grid showing all numbers 0-36")
        return False
    
    # Create templates directory
    os.makedirs(templates_dir, exist_ok=True)
    
    # Load image
    print(f"Loading image: {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print(f" Error: Could not load image: {image_path}")
        return False
    
    print(f" Image loaded: {img.shape[1]}x{img.shape[0]} pixels")
    print()
    
    # Initialize window
    cv2.namedWindow('Select Number Region')
    
    # Mouse callback for selecting region
    drawing = False
    ix, iy = -1, -1
    fx, fy = -1, -1
    current_img = img.copy()
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal drawing, ix, iy, fx, fy, current_img
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                fx, fy = x, y
                display = current_img.copy()
                cv2.rectangle(display, (ix, iy), (fx, fy), (0, 255, 0), 2)
                cv2.imshow('Select Number Region', display)
        
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            fx, fy = x, y
    
    cv2.setMouseCallback('Select Number Region', mouse_callback)
    
    # Show image
    cv2.imshow('Select Number Region', img)
    
    print("=" * 70)
    print("INSTRUCTIONS")
    print("=" * 70)
    print("\nFor each number (0-36):")
    print("  1. Find the number on the betting grid")
    print("  2. Click and drag to select JUST that number")
    print("  3. Press 's' to save")
    print("  4. Press 'n' for next number")
    print("  5. Press 'd' for previous number")
    print("  6. Press 'q' to quit")
    print()
    print("  IMPORTANT:")
    print("  - Select ONLY the number, not background")
    print("  - Include a small border (2-5 pixels) around the number")
    print("  - Make sure selection is clear and not blurry")
    print()
    
    # Numbers to create templates for
    numbers = list(range(37))  # 0-36
    num_idx = 0
    
    def load_number(num):
        """Display current number status."""
        nonlocal current_img, ix, iy, fx, fy
        
        template_path = os.path.join(templates_dir, f"number_{num}.png")
        exists = os.path.exists(template_path)
        
        # Reset selection
        ix, iy, fx, fy = -1, -1, -1, -1
        
        # Show image
        current_img = img.copy()
        cv2.imshow('Select Number Region', current_img)
        
        # Print status
        status = "" if exists else " "
        print(f"\n[{num+1}/37] Number {num} {status}")
        if exists:
            print(f"  Template already exists: {template_path}")
        else:
            print(f"  Select this number on the betting grid")
        print("  Instructions:")
        print("    - Click and drag to select the number")
        print("    - Press 's' to save")
        print("    - Press 'n' for next number")
        print("    - Press 'd' for previous number")
        print("    - Press 'q' to quit")
        
        return True
    
    # Load first number
    load_number(numbers[num_idx])
    
    # Main loop
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            # Save cropped region
            num = numbers[num_idx]
            template_path = os.path.join(templates_dir, f"number_{num}.png")
            
            if ix != -1 and fx != -1 and iy != -1 and fy != -1:
                x1, x2 = min(ix, fx), max(ix, fx)
                y1, y2 = min(iy, fy), max(iy, fy)
                
                # Validate selection
                if x2 - x1 < 10 or y2 - y1 < 10:
                    print("   Selection too small, try again")
                    continue
                
                # Crop
                cropped = img[y1:y2, x1:x2]
                
                if cropped.size > 0:
                    cv2.imwrite(template_path, cropped)
                    h, w = cropped.shape[:2]
                    print(f"   Saved template: {template_path} ({w}x{h} pixels)")
                    load_number(num)  # Reload to show saved status
                else:
                    print("   Invalid selection, try again")
            else:
                print("   Please select a region first")
        
        elif key == ord('n'):
            # Next number
            num_idx = (num_idx + 1) % len(numbers)
            load_number(numbers[num_idx])
        
        elif key == ord('d'):
            # Previous number
            num_idx = (num_idx - 1) % len(numbers)
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
        print("\nThese templates are from the same image, so they:")
        print("  - Have consistent styling")
        print("  - Reduce false positives")
        print("  - Work better for detection")
        return True
    else:
        print(f"\n Need {37 - len(valid)} more templates")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("CREATE TEMPLATES FROM BETTING GRID")
        print("=" * 70)
        print("\nUsage:")
        print("  python create_templates_from_grid.py <betting_grid_image>")
        print()
        print("Example:")
        print("  python create_templates_from_grid.py betting_grid.png")
        print()
        print("Instructions:")
        print("  1. Take a screenshot of your betting grid showing all numbers 0-36")
        print("  2. Save it as an image file (PNG recommended)")
        print("  3. Run this script with the image path")
        print("  4. Select each number one by one")
        print()
        print("Why this method is better:")
        print("  - All templates from same image = consistent styling")
        print("  - Reduces false positives")
        print("  - More accurate detection")
        sys.exit(1)
    
    image_path = sys.argv[1]
    templates_dir = sys.argv[2] if len(sys.argv) > 2 else 'templates'
    
    extract_from_grid_snapshot(image_path, templates_dir)


if __name__ == '__main__':
    main()

