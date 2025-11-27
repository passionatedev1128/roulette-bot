"""
Capture Even/Odd Betting Coordinates from Snapshot
Allows capturing coordinates by clicking on a snapshot image.
"""

import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pyautogui


class CoordinateCapture:
    """Interactive coordinate capture from snapshot image."""
    
    def __init__(self, image_path: str):
        """
        Initialize with snapshot image.
        
        Args:
            image_path: Path to snapshot image file
        """
        self.image_path = Path(image_path)
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        self.image = cv2.imread(str(self.image_path))
        if self.image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        self.coordinates: Dict[str, List[int]] = {}
        self.current_target = None
        self.window_name = "Even/Odd Coordinate Capture - Click on the betting areas"
        
        # Scale factor for display (if image is too large)
        self.scale = 1.0
        self.display_image = self.image.copy()
        
    def _resize_for_display(self, max_width: int = 1920, max_height: int = 1080):
        """Resize image for display if too large."""
        h, w = self.image.shape[:2]
        if w > max_width or h > max_height:
            scale_w = max_width / w
            scale_h = max_height / h
            self.scale = min(scale_w, scale_h)
            new_w = int(w * self.scale)
            new_h = int(h * self.scale)
            self.display_image = cv2.resize(self.image, (new_w, new_h))
        else:
            self.scale = 1.0
            self.display_image = self.image.copy()
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Mouse callback for clicking on image."""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Convert display coordinates to original image coordinates
            if self.scale != 1.0:
                orig_x = int(x / self.scale)
                orig_y = int(y / self.scale)
            else:
                orig_x = x
                orig_y = y
            
            if self.current_target:
                self.coordinates[self.current_target] = [orig_x, orig_y]
                print(f"   Captured {self.current_target.upper()}: [{orig_x}, {orig_y}]")
                
                # Draw marker on image
                cv2.circle(self.display_image, (x, y), 10, (0, 255, 0), -1)
                cv2.putText(
                    self.display_image,
                    self.current_target.upper(),
                    (x + 15, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                cv2.imshow(self.window_name, self.display_image)
    
    def capture(self) -> Dict[str, List[int]]:
        """
        Interactive capture from snapshot.
        
        Returns:
            Dictionary with 'even' and 'odd' coordinates
        """
        print("=" * 70)
        print("EVEN/ODD COORDINATE CAPTURE FROM SNAPSHOT")
        print("=" * 70)
        print(f"\nImage: {self.image_path}")
        print("\nInstructions:")
        print("  1. The snapshot image will open in a window")
        print("  2. Click on the Even betting area")
        print("  3. Click on the Odd betting area")
        print("  4. Press 'r' to reset a coordinate")
        print("  5. Press 's' to save and finish")
        print("  6. Press 'q' or ESC to quit without saving")
        print("\nPress Enter to start...")
        input()
        
        # Resize for display
        self._resize_for_display()
        
        # Create window and set mouse callback
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
        
        # Show image
        cv2.imshow(self.window_name, self.display_image)
        
        print("\n" + "=" * 70)
        print("CAPTURE MODE")
        print("=" * 70)
        print("\nClick on the betting areas in the image window:")
        print("  1. Click on EVEN betting area")
        print("  2. Click on ODD betting area")
        print("\nControls:")
        print("  'r' - Reset current coordinate")
        print("  's' - Save and finish")
        print("  'q' or ESC - Quit without saving")
        print("=" * 70 + "\n")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # ESC
                print("\nCapture cancelled.")
                cv2.destroyAllWindows()
                return {}
            
            elif key == ord('s'):
                if 'even' in self.coordinates and 'odd' in self.coordinates:
                    print("\n Both coordinates captured!")
                    cv2.destroyAllWindows()
                    break
                else:
                    missing = [k for k in ['even', 'odd'] if k not in self.coordinates]
                    print(f"\n Missing coordinates: {', '.join(missing)}")
                    print("Capture them before saving, or press 'q' to quit.")
            
            elif key == ord('r'):
                if self.current_target:
                    if self.current_target in self.coordinates:
                        del self.coordinates[self.current_target]
                        print(f"  ↻ Reset {self.current_target}")
                        # Reload image to remove markers
                        self._resize_for_display()
                        cv2.imshow(self.window_name, self.display_image)
            
            # Prompt for next target
            if not self.current_target or self.current_target in self.coordinates:
                if 'even' not in self.coordinates:
                    self.current_target = 'even'
                    print(f"\n Click on EVEN betting area...")
                elif 'odd' not in self.coordinates:
                    self.current_target = 'odd'
                    print(f" Click on ODD betting area...")
                else:
                    # Both captured, wait for save
                    pass
        
        return self.coordinates
    
    def save(self, output_file: str = "even_odd_coordinates.json"):
        """Save coordinates to JSON file."""
        output_path = Path(output_file)
        output_path.write_text(json.dumps(self.coordinates, indent=2), encoding="utf-8")
        
        print("\n" + "=" * 70)
        print("COORDINATES SAVED")
        print("=" * 70)
        print(f"\nSaved to: {output_path.resolve()}")
        print("\nCoordinates:")
        for bet_type, coords in sorted(self.coordinates.items()):
            print(f"  {bet_type.upper()}: {coords}")
        
        print("\n" + "=" * 70)
        print("CONFIG SNIPPET")
        print("=" * 70)
        print("\nAdd this to your config file:")
        print('"betting": {')
        print('  "betting_areas": {')
        print('    // ... existing entries ...')
        for bet_type in sorted(self.coordinates.keys()):
            coords = self.coordinates[bet_type]
            print(f'    "{bet_type}": {coords},')
        print('  },')
        print('}')
        
        return output_path


def capture_from_snapshot(image_path: str, output_file: str = "even_odd_coordinates.json"):
    """
    Capture Even/Odd coordinates from a snapshot image.
    
    Args:
        image_path: Path to snapshot image file
        output_file: Output JSON file path
        
    Returns:
        Dictionary with coordinates
    """
    try:
        capturer = CoordinateCapture(image_path)
        coordinates = capturer.capture()
        
        if coordinates:
            capturer.save(output_file)
            return coordinates
        else:
            print("\nNo coordinates captured.")
            return {}
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return {}


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python capture_even_odd_from_snapshot.py <image_path>")
        print("\nExample:")
        print("  python capture_even_odd_from_snapshot.py snapshot.png")
        print("\nOr enter image path when prompted:")
        image_path = input("Enter path to snapshot image: ").strip()
    else:
        image_path = sys.argv[1]
    
    if not image_path:
        print("Error: No image path provided.")
        sys.exit(1)
    
    try:
        capture_from_snapshot(image_path)
    except KeyboardInterrupt:
        print("\n\nCapture aborted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

