"""
Show Winning Number Detection Region on Desktop
Displays a visual indicator showing where the bot detects winning numbers.
"""

import pyautogui
import cv2
import numpy as np
import time
from pathlib import Path
from backend.app.config_loader import ConfigLoader


def capture_region_with_border(screen_region, border_size=5):
    """
    Capture a larger region to show context around the detection area.
    
    Args:
        screen_region: [x, y, w, h] detection region
        border_size: How many pixels to expand around the region
    
    Returns:
        Expanded region coordinates and the captured frame
    """
    x, y, w, h = screen_region
    
    # Expand region to show context
    expanded_x = max(0, x - border_size * 10)
    expanded_y = max(0, y - border_size * 10)
    expanded_w = min(pyautogui.size()[0] - expanded_x, w + border_size * 20)
    expanded_h = min(pyautogui.size()[1] - expanded_y, h + border_size * 20)
    
    # Calculate relative position of detection region within expanded region
    rel_x = x - expanded_x
    rel_y = y - expanded_y
    
    # Capture expanded region
    expanded_region = [expanded_x, expanded_y, expanded_w, expanded_h]
    screenshot = pyautogui.screenshot(region=expanded_region)
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    return frame, (rel_x, rel_y, w, h), expanded_region


def show_detection_region(config_path: str = 'config/default_config.json', duration: int = 10):
    """
    Show the winning number detection region on desktop.
    
    Args:
        config_path: Path to config file
        duration: How long to show the region (seconds)
    """
    # Load config
    config = ConfigLoader.load_config(config_path)
    screen_region = config.get('detection', {}).get('screen_region')
    
    if not screen_region:
        print(" Error: screen_region not configured in config file")
        print("   Please set detection.screen_region in your config")
        return
    
    x, y, w, h = screen_region
    
    print("=" * 80)
    print("WINNING NUMBER DETECTION REGION")
    print("=" * 80)
    print(f"Config: {config_path}")
    print(f"Region: x={x}, y={y}, width={w}, height={h}")
    print(f"Coordinates: Top-left ({x}, {y}), Bottom-right ({x+w}, {y+h})")
    print()
    print("⏳ Starting in 3 seconds...")
    print("   Please position your game window so the detection region is visible!")
    print()
    
    # Countdown
    for i in range(3, 0, -1):
        print(f"   {i}...", end='', flush=True)
        time.sleep(1)
    print("   GO!")
    print()
    print("📸 Taking screenshot of detection region...")
    print()
    
    # Capture the region
    try:
        # Capture the exact detection region
        screenshot = pyautogui.screenshot(region=screen_region)
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Capture expanded region for context view
        context_frame, rel_coords, expanded_region = capture_region_with_border(screen_region)
        rel_x, rel_y, rel_w, rel_h = rel_coords
        
        # Create a full screen overlay to show the region
        screen_width, screen_height = pyautogui.size()
        overlay = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        
        # Draw rectangle on overlay (bright green with red border)
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 4)  # Green rectangle
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red border
        
        # Add text labels with background
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        thickness = 2
        
        # Title
        text = "WINNING NUMBER DETECTION REGION"
        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        cv2.rectangle(overlay, (x, y - text_h - 30), (x + text_w + 10, y - 5), (0, 0, 0), -1)
        cv2.putText(overlay, text, (x + 5, y - 15), font, font_scale, (0, 255, 0), thickness)
        
        # Coordinates
        coord_text = f"Top-left: ({x}, {y})"
        (coord_w, coord_h), _ = cv2.getTextSize(coord_text, font, 0.6, 1)
        cv2.rectangle(overlay, (x, y + h + 5), (x + coord_w + 10, y + h + coord_h + 15), (0, 0, 0), -1)
        cv2.putText(overlay, coord_text, (x + 5, y + h + coord_h + 10), font, 0.6, (255, 255, 255), 1)
        
        # Size
        size_text = f"Size: {w} x {h} pixels"
        (size_w, size_h), _ = cv2.getTextSize(size_text, font, 0.6, 1)
        cv2.rectangle(overlay, (x, y + h + coord_h + 20), (x + size_w + 10, y + h + coord_h + size_h + 30), (0, 0, 0), -1)
        cv2.putText(overlay, size_text, (x + 5, y + h + coord_h + size_h + 25), font, 0.6, (255, 255, 255), 1)
        
        # Draw on context frame
        context_with_rect = context_frame.copy()
        cv2.rectangle(context_with_rect, (rel_x, rel_y), (rel_x + rel_w, rel_y + rel_h), (0, 255, 0), 3)
        cv2.rectangle(context_with_rect, (rel_x, rel_y), (rel_x + rel_w, rel_y + rel_h), (0, 0, 255), 1)
        cv2.putText(context_with_rect, "Detection Region", (rel_x, rel_y - 10), 
                   font, 0.7, (0, 255, 0), 2)
        
        # Draw on close-up frame
        frame_with_rect = frame.copy()
        cv2.rectangle(frame_with_rect, (0, 0), (w-1, h-1), (0, 255, 0), 3)
        cv2.rectangle(frame_with_rect, (0, 0), (w-1, h-1), (0, 0, 255), 1)
        cv2.putText(frame_with_rect, f"Detection Region: {w}x{h}px", (5, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame_with_rect, f"Coordinates: ({x}, {y})", (5, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        print(" Detection region captured!")
        print()
        
        # Save all images
        output_dir = Path('detection_region_output')
        output_dir.mkdir(exist_ok=True)
        
        # 1. Save close-up of exact detection region
        closeup_path = output_dir / '1_closeup_exact_region.png'
        cv2.imwrite(str(closeup_path), frame_with_rect)
        print(f" 1. Close-up saved: {closeup_path}")
        
        # 2. Save context view
        context_output = output_dir / '2_context_with_surrounding.png'
        cv2.imwrite(str(context_output), context_with_rect)
        print(f" 2. Context view saved: {context_output}")
        
        # 3. Save full screen overlay
        overlay_path = output_dir / '3_fullscreen_overlay.png'
        cv2.imwrite(str(overlay_path), overlay)
        print(f" 3. Full screen overlay saved: {overlay_path}")
        
        # 4. Save original region (no annotations)
        original_path = output_dir / '4_original_region.png'
        cv2.imwrite(str(original_path), frame)
        print(f" 4. Original region saved: {original_path}")
        
        # 5. Create a combined visualization using PIL
        try:
            # Create a side-by-side comparison
            screen_width, screen_height = pyautogui.size()
            full_screenshot = pyautogui.screenshot()
            full_frame = cv2.cvtColor(np.array(full_screenshot), cv2.COLOR_RGB2BGR)
            
            # Draw rectangle on full screenshot
            full_with_rect = full_frame.copy()
            cv2.rectangle(full_with_rect, (x, y), (x + w, y + h), (0, 255, 0), 4)
            cv2.rectangle(full_with_rect, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # Add text
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(full_with_rect, f"WINNING NUMBER REGION: ({x}, {y}) - {w}x{h}px", 
                       (x, y - 10), font, 0.8, (0, 255, 0), 2)
            
            combined_path = output_dir / '5_full_screen_with_region.png'
            cv2.imwrite(str(combined_path), full_with_rect)
            print(f" 5. Full screen with region saved: {combined_path}")
        except Exception as e:
            print(f"  Could not create full screen visualization: {e}")
        
        print()
        print("=" * 80)
        print("IMAGES SAVED")
        print("=" * 80)
        print(f"All images saved to: {output_dir.absolute()}")
        print()
        print("📁 Files created:")
        print(f"  1. {closeup_path.name} - Close-up of exact detection region (8x zoom)")
        print(f"  2. {context_output.name} - Region with surrounding area")
        print(f"  3. {overlay_path.name} - Full screen overlay")
        print(f"  4. {original_path.name} - Original region (no annotations)")
        if 'combined_path' in locals():
            print(f"  5. {combined_path.name} - Full screen screenshot with region marked")
        print()
        print(" Open these images to see the detection region!")
        print(f"   Location: {output_dir.absolute()}")
        print()
        print("=" * 80)
        print("REGION INFORMATION")
        print("=" * 80)
        print(f"Top-left corner: ({x}, {y})")
        print(f"Bottom-right corner: ({x+w}, {y+h})")
        print(f"Size: {w} x {h} pixels")
        print()
        print(" Tips:")
        print("  - Make sure the game window is positioned so this region")
        print("    shows the winning number display")
        print("  - The region should be visible and not covered by other windows")
        print("  - Adjust screen_region in config if needed")
        
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Show winning number detection region on desktop')
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to config file'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='How long to show the region (seconds, default: 10)'
    )
    
    args = parser.parse_args()
    
    show_detection_region(args.config, args.duration)

