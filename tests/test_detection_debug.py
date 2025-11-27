"""
Debug Detection - Test if winning numbers are being detected from desktop region
"""

import cv2
import numpy as np
from pathlib import Path
from backend.app.config_loader import ConfigLoader
from backend.app.detection.screen_detector import ScreenDetector
import pyautogui


def test_detection():
    """Test detection from desktop region."""
    config_path = 'config/default_config.json'
    config = ConfigLoader.load_config(config_path)
    
    detection_config = config.get('detection', {})
    screen_region = detection_config.get('screen_region')
    
    if not screen_region:
        print(" Error: screen_region not configured")
        return
    
    x, y, w, h = screen_region
    print("=" * 80)
    print("DETECTION DEBUG TEST")
    print("=" * 80)
    print(f"Config: {config_path}")
    print(f"Screen Region: {screen_region}")
    print(f"  Top-left: ({x}, {y})")
    print(f"  Size: {w} x {h} pixels")
    print()
    
    # Initialize detector
    detector = ScreenDetector(config)
    
    print("📸 Capturing screen region...")
    print("   (Make sure game window is visible!)")
    print()
    
    # Capture the region
    try:
        screenshot = pyautogui.screenshot(region=screen_region)
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        print(f" Captured frame shape: {frame.shape}")
        print()
        
        # Save captured region for inspection
        output_dir = Path('detection_debug')
        output_dir.mkdir(exist_ok=True)
        
        captured_path = output_dir / 'captured_region.png'
        cv2.imwrite(str(captured_path), frame)
        print(f" Saved captured region: {captured_path}")
        print()
        
        # Test detection
        print("=" * 80)
        print("TESTING DETECTION")
        print("=" * 80)
        
        result = detector.detect_result(frame)
        
        print(f"Detection Result:")
        print(f"  Number: {result.get('number')}")
        print(f"  Color: {result.get('color')}")
        print(f"  Confidence: {result.get('confidence', 0):.4f}")
        print(f"  Method: {result.get('method')}")
        print(f"  Zero: {result.get('zero', False)}")
        print()
        
        if result.get('number') is None:
            print(" No number detected!")
            print()
            print("Possible issues:")
            print("  1. Region doesn't contain winning number")
            print("  2. Templates don't match the number style")
            print("  3. OCR not working or confidence too low")
            print("  4. Region coordinates are wrong")
            print()
            print(f" Check the captured image: {captured_path}")
            print("   Does it show a winning number?")
        else:
            print(f" Successfully detected number: {result.get('number')}")
            print(f"   Method: {result.get('method')}")
            print(f"   Confidence: {result.get('confidence', 0):.4f}")
        
        # Test template matching directly
        print()
        print("=" * 80)
        print("TESTING TEMPLATE MATCHING")
        print("=" * 80)
        
        if hasattr(detector, 'winning_templates') and detector.winning_templates:
            print(f"Found {len(detector.winning_templates)} winning templates")
            
            # Try template matching
            badge_match = detector.detect_winning_number_template(frame)
            if badge_match:
                number, confidence = badge_match
                print(f" Template match found: Number {number}, Confidence {confidence:.4f}")
            else:
                print(" No template match found")
                print("   This could mean:")
                print("   - Templates don't match the current number style")
                print("   - Number in region is different from templates")
        else:
            print("  No winning templates loaded")
        
        # Test OCR
        print()
        print("=" * 80)
        print("TESTING OCR")
        print("=" * 80)
        
        ocr_result = detector.detect_number_ocr(frame)
        if ocr_result:
            number, confidence = ocr_result
            print(f" OCR result: Number {number}, Confidence {confidence:.4f}")
            if confidence >= detector.ocr_confidence_threshold:
                print(f"    Confidence above threshold ({detector.ocr_confidence_threshold})")
            else:
                print(f"     Confidence below threshold ({detector.ocr_confidence_threshold})")
        else:
            print(" OCR could not detect number")
        
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Captured image: {captured_path}")
        print(f"Detection result: {result}")
        print()
        print(" Next steps:")
        print("  1. Check the captured image to see if it shows a number")
        print("  2. If number is visible but not detected, check templates")
        print("  3. Adjust screen_region if coordinates are wrong")
        
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_detection()

