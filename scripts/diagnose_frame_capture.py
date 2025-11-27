"""
Diagnostic tool to check why frames aren't being detected.
Tests frame capture, ROI extraction, and detection step-by-step.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict

try:
    from backend.app.config_loader import ConfigLoader
    from backend.app.detection import ScreenDetector
    from backend.app.detection.frame_detector import FrameDetector
except ImportError:
    print(" Error: Cannot import bot modules. Make sure you're in the project root directory.")
    sys.exit(1)


def test_frame_capture(detector, mode: str = "screen") -> Optional[np.ndarray]:
    """Test if frame capture works."""
    print("\n" + "=" * 80)
    print("STEP 1: TESTING FRAME CAPTURE")
    print("=" * 80)
    
    try:
        print(f"Attempting to capture frame ({mode} mode)...")
        frame = detector.capture_screen()
        
        if frame is None:
            print(" Frame capture returned None!")
            print("\nPossible reasons:")
            if mode == "video":
                print("   - Video file ended")
                print("   - Video file cannot be opened")
                print("   - Video file is corrupted")
            else:
                print("   - Screen region is invalid")
                print("   - Screen capture failed (permissions?)")
                print("   - Window is minimized or not visible")
            return None
        
        print(f" Frame captured successfully!")
        print(f"   Frame shape: {frame.shape}")
        print(f"   Frame dtype: {frame.dtype}")
        print(f"   Frame size: {frame.size} pixels")
        
        # Check if frame is valid
        if frame.size == 0:
            print(" Frame is empty (size = 0)")
            return None
        
        if len(frame.shape) < 2:
            print(" Frame has invalid shape")
            return None
        
        return frame
        
    except Exception as e:
        print(f" Error during frame capture: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_roi_extraction(frame: np.ndarray, detector, config: Dict) -> Optional[np.ndarray]:
    """Test ROI extraction."""
    print("\n" + "=" * 80)
    print("STEP 2: TESTING ROI EXTRACTION")
    print("=" * 80)
    
    screen_region = config.get('detection', {}).get('screen_region')
    is_video_frame = hasattr(detector, 'cap') and hasattr(detector, 'video_path')
    
    print(f"Screen region config: {screen_region}")
    print(f"Is video frame: {is_video_frame}")
    print(f"Input frame shape: {frame.shape}")
    
    # Simulate ROI extraction logic from detect_result()
    if screen_region:
        if is_video_frame:
            # For video frames, extract screen_region from the full frame
            x, y, w, h = screen_region
            frame_h, frame_w = frame.shape[:2]
            
            print(f"\nExtracting ROI from video frame:")
            print(f"   Region: x={x}, y={y}, width={w}, height={h}")
            print(f"   Frame size: {frame_w}x{frame_h}")
            
            # Validate coordinates
            if x < 0 or y < 0 or x + w > frame_w or y + h > frame_h:
                print(f" Invalid screen_region coordinates!")
                print(f"   Region extends beyond frame: ({x}, {y}, {w}, {h}) vs frame ({frame_w}, {frame_h})")
                return None
            
            roi = frame[y:y + h, x:x + w]
            print(f" ROI extracted successfully!")
            print(f"   ROI shape: {roi.shape}")
            return roi
        else:
            # For real-time screen capture, frame is already cropped
            print(" Frame is already cropped to screen_region (desktop mode)")
            print(f"   ROI shape: {frame.shape}")
            return frame
    else:
        # No screen_region - use full frame
        print("  No screen_region configured - using full frame")
        print(f"   This may cause detection issues (templates are small, frame is large)")
        return frame


def test_template_matching(roi: np.ndarray, detector) -> Dict:
    """Test template matching on ROI."""
    print("\n" + "=" * 80)
    print("STEP 3: TESTING TEMPLATE MATCHING")
    print("=" * 80)
    
    if not detector.winning_templates:
        print(" No templates loaded!")
        print("   Check: winning-number_templates/ directory exists and has PNG files")
        return {"success": False, "reason": "No templates"}
    
    print(f" Templates loaded: {len(detector.winning_templates)}")
    template_numbers = sorted([t[0] for t in detector.winning_templates])
    print(f"   Template numbers: {template_numbers}")
    
    print(f"\nROI shape: {roi.shape}")
    print(f"Template threshold: {detector.winning_template_threshold}")
    
    # Try template matching
    print("\nAttempting template matching...")
    try:
        result = detector.detect_winning_number_template(roi)
        
        if result is None:
            print(" Template matching returned None")
            print("\nPossible reasons:")
            print("   - ROI too small for templates")
            print("   - No template matches above threshold")
            print("   - ROI doesn't contain winning number badge")
            print("   - Templates don't match current game style")
            return {"success": False, "reason": "No match"}
        
        number, confidence = result
        print(f" Template match found!")
        print(f"   Number: {number}")
        print(f"   Confidence: {confidence:.3f}")
        print(f"   Threshold: {detector.winning_template_threshold}")
        
        if confidence < detector.winning_template_threshold:
            print(f"  Confidence ({confidence:.3f}) below threshold ({detector.winning_template_threshold})")
            print("   Match would be rejected")
            return {"success": False, "reason": "Low confidence", "number": number, "confidence": confidence}
        
        return {"success": True, "number": number, "confidence": confidence}
        
    except Exception as e:
        print(f" Error during template matching: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "reason": f"Error: {e}"}


def test_full_detection(detector, config: Dict) -> Dict:
    """Test full detection pipeline."""
    print("\n" + "=" * 80)
    print("STEP 4: TESTING FULL DETECTION PIPELINE")
    print("=" * 80)
    
    try:
        result = detector.detect_result()
        
        if result is None:
            print(" detect_result() returned None")
            return {"success": False}
        
        number = result.get("number")
        color = result.get("color")
        confidence = result.get("confidence", 0.0)
        method = result.get("method")
        
        if number is None:
            print(" No number detected")
            print(f"   Method: {method}")
            print(f"   Confidence: {confidence}")
            return {"success": False, "result": result}
        
        print(f" Detection successful!")
        print(f"   Number: {number}")
        print(f"   Color: {color}")
        print(f"   Confidence: {confidence:.3f}")
        print(f"   Method: {method}")
        return {"success": True, "result": result}
        
    except Exception as e:
        print(f" Error during full detection: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def main():
    """Main diagnostic function."""
    print("=" * 80)
    print("FRAME CAPTURE & DETECTION DIAGNOSTIC")
    print("=" * 80)
    
    # Check for video file
    video_path = None
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if not Path(video_path).exists():
            print(f" Video file not found: {video_path}")
            sys.exit(1)
    
    config_path = Path("config/default_config.json")
    if not config_path.exists():
        print(f" Config file not found: {config_path}")
        sys.exit(1)
    
    config = ConfigLoader.load_config(str(config_path))
    print(f"Config: {config_path.absolute()}")
    
    # Initialize detector
    if video_path:
        print(f"\nUsing video file: {video_path}")
        start_frame = int(os.environ.get('BOT_START_FRAME', '1000'))
        detector = FrameDetector(config, video_path, start_frame=start_frame)
        mode = "video"
    else:
        print("\nUsing screen capture (desktop)")
        detector = ScreenDetector(config)
        mode = "screen"
    
    # Step 1: Test frame capture
    frame = test_frame_capture(detector, mode)
    if frame is None:
        print("\n" + "=" * 80)
        print(" DIAGNOSIS: Frame capture is failing")
        print("=" * 80)
        print("\nFix frame capture first before testing detection.")
        if mode == "screen":
            print("\nSuggestions:")
            print("1. Run: python show_detection_region.py")
            print("2. Verify screen_region in config matches your screen")
            print("3. Make sure game window is visible and not minimized")
        else:
            print("\nSuggestions:")
            print("1. Verify video file is valid and can be opened")
            print("2. Check video file path is correct")
            print("3. Try opening video in a video player to verify it works")
        return
    
    # Step 2: Test ROI extraction
    roi = test_roi_extraction(frame, detector, config)
    if roi is None:
        print("\n" + "=" * 80)
        print(" DIAGNOSIS: ROI extraction is failing")
        print("=" * 80)
        print("\nFix ROI extraction first.")
        print("\nSuggestions:")
        print("1. Check screen_region coordinates in config")
        print("2. Verify screen_region is within frame bounds")
        print("3. For video mode, ensure screen_region matches video frame size")
        return
    
    # Step 3: Test template matching
    template_result = test_template_matching(roi, detector)
    if not template_result.get("success"):
        print("\n" + "=" * 80)
        print(" DIAGNOSIS: Template matching is failing")
        print("=" * 80)
        print(f"\nReason: {template_result.get('reason')}")
        print("\nSuggestions:")
        print("1. Check templates exist in winning-number_templates/")
        print("2. Verify templates match current game style")
        print("3. Lower winning_template_threshold in config (try 0.65)")
        print("4. Verify ROI contains the winning number badge")
        print("5. Check ROI size is appropriate for templates")
        return
    
    # Step 4: Test full detection
    detection_result = test_full_detection(detector, config)
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    if detection_result.get("success"):
        print(" All checks passed!")
        print("   Frame capture: ")
        print("   ROI extraction: ")
        print("   Template matching: ")
        print("   Full detection: ")
        print("\nBot should be able to detect numbers.")
    else:
        print(" Detection is failing")
        print("\nCheck the errors above for specific issues.")
        print("\nMost common issues:")
        print("1. Screen region incorrect")
        print("2. Templates don't match game style")
        print("3. Threshold too high")
        print("4. ROI extraction failing")


if __name__ == "__main__":
    import os
    main()

