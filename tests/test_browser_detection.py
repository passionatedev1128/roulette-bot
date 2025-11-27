"""
Test Browser Detection
Verifies that the bot can detect winning numbers from a real browser window.

IMPORTANT: 
- Open your roulette game in a browser before running this
- Position the browser window where you want it
- Set browser zoom to 100%
- Keep the browser window visible and don't move it
"""

import cv2
import sys
import time
from pathlib import Path
from datetime import datetime
import json

import logging

from backend.app.detection import ScreenDetector
from backend.app.config_loader import ConfigLoader

# Enable debug logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_browser_detection(
    config_path: str = 'config/default_config.json',
    num_tests: int = 20,
    delay_seconds: float = 2.0,
    save_samples: bool = True
):
    """
    Test detection from browser screen.
    
    Args:
        config_path: Path to configuration file
        num_tests: Number of detection attempts
        delay_seconds: Delay between attempts (seconds)
        save_samples: Whether to save sample captures
    """
    print("=" * 80)
    print("BROWSER DETECTION TEST")
    print("=" * 80)
    print("\n  IMPORTANT:")
    print("   1. Open your roulette game in a browser")
    print("   2. Position the browser window where you want it")
    print("   3. Set browser zoom to 100% (Ctrl+0)")
    print("   4. Make sure the winning number area is visible")
    print("   5. DO NOT move or resize the browser window")
    print("\n" + "-" * 80)
    
    # Load configuration
    print(f"\nLoading configuration from {config_path}...")
    try:
        config = ConfigLoader.load_config(config_path)
        print(" Configuration loaded")
    except Exception as e:
        print(f" Error loading config: {e}")
        sys.exit(1)
    
    # Initialize detector
    print("\nInitializing screen detector...")
    try:
        detector = ScreenDetector(config)
        print(" Detector initialized")
    except Exception as e:
        print(f" Error initializing detector: {e}")
        sys.exit(1)
    
    # Check configuration
    detection_config = config.get('detection', {})
    screen_region = detection_config.get('screen_region', None)
    
    print(f"\n📋 Configuration:")
    print(f"   Screen region: {screen_region}")
    print(f"   Templates directory: {detector.winning_templates_dir}")
    print(f"   Templates loaded: {len(detector.winning_templates)}")
    print(f"   Template threshold: {detector.winning_template_threshold}")
    
    if screen_region:
        x, y, w, h = screen_region
        print(f"   Region: x={x}, y={y}, width={w}, height={h}")
    else:
        print("     WARNING: screen_region is null - will capture full screen")
    
    if len(detector.winning_templates) == 0:
        print("\n     WARNING: No winning templates loaded!")
        print("      Detection may not work. Create templates first.")
    
    # Create output directory
    output_dir = Path("browser_test_results")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n{'=' * 80}")
    print(f"Starting {num_tests} detection tests...")
    print(f"Delay between tests: {delay_seconds} seconds")
    print(f"{'=' * 80}\n")
    
    # Countdown
    print("Starting in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print("  GO!\n")
    
    # Test results
    results = []
    successful_detections = 0
    failed_detections = 0
    
    for i in range(num_tests):
        print(f"Test {i+1}/{num_tests}: ", end="", flush=True)
        
        try:
            # Capture screen
            frame = detector.capture_screen()
            if frame is None:
                print(" Failed to capture screen")
                failed_detections += 1
                results.append({
                    "test": i + 1,
                    "timestamp": datetime.now().isoformat(),
                    "status": "capture_failed"
                })
                time.sleep(delay_seconds)
                continue
            
            # Save sample capture (first test only)
            if save_samples and i == 0:
                full_capture_path = output_dir / "full_screen_capture.png"
                cv2.imwrite(str(full_capture_path), frame)
                print(f"📸 Saved full capture to {full_capture_path}")
                
                # Save ROI if region is set
                if screen_region:
                    x, y, w, h = screen_region
                    roi = frame[y:y+h, x:x+w]
                    if roi.size > 0:
                        roi_path = output_dir / "roi_capture.png"
                        cv2.imwrite(str(roi_path), roi)
                        print(f"📸 Saved ROI to {roi_path}")
                        print(f"   👀 CHECK THIS IMAGE - Does it show the winning number?")
            
            # Detect result
            result = detector.detect_result(frame)
            
            if result.get('number') is not None:
                number = result.get('number')
                color = result.get('color', 'N/A')
                method = result.get('method', 'N/A')
                confidence = result.get('confidence', 0.0)
                
                successful_detections += 1
                print(f" Detected: {number} ({color}) - Method: {method}, Confidence: {confidence:.2f}")
                
                results.append({
                    "test": i + 1,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "number": number,
                    "color": color,
                    "method": method,
                    "confidence": confidence
                })
                
                # Save detection sample
                if save_samples and i < 3:  # Save first 3 successful detections
                    sample_path = output_dir / f"detection_sample_{i+1}_number_{number}.png"
                    if screen_region:
                        x, y, w, h = screen_region
                        roi = frame[y:y+h, x:x+w]
                        if roi.size > 0:
                            cv2.imwrite(str(sample_path), roi)
            else:
                failed_detections += 1
                print(" No detection")
                
                results.append({
                    "test": i + 1,
                    "timestamp": datetime.now().isoformat(),
                    "status": "no_detection"
                })
                
                # Save failed detection sample
                if save_samples and i < 3:  # Save first 3 failed detections
                    sample_path = output_dir / f"failed_detection_{i+1}.png"
                    if screen_region:
                        x, y, w, h = screen_region
                        roi = frame[y:y+h, x:x+w]
                        if roi.size > 0:
                            cv2.imwrite(str(sample_path), roi)
                            print(f"   📸 Saved failed detection sample to {sample_path}")
            
        except Exception as e:
            print(f" Error: {e}")
            failed_detections += 1
            results.append({
                "test": i + 1,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            })
        
        # Delay before next test
        if i < num_tests - 1:
            time.sleep(delay_seconds)
    
    # Save results
    print(f"\n{'=' * 80}")
    print("Saving results...")
    
    json_file = output_dir / f"browser_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "config": {
                "screen_region": screen_region,
                "templates_loaded": len(detector.winning_templates),
                "template_threshold": detector.winning_template_threshold
            },
            "test_summary": {
                "total_tests": num_tests,
                "successful_detections": successful_detections,
                "failed_detections": failed_detections,
                "detection_rate": (successful_detections / num_tests * 100) if num_tests > 0 else 0
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f" Results saved to: {json_file}")
    
    # Print summary
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total tests: {num_tests}")
    print(f"Successful detections: {successful_detections}")
    print(f"Failed detections: {failed_detections}")
    print(f"Detection rate: {(successful_detections / num_tests * 100) if num_tests > 0 else 0:.1f}%")
    print(f"{'=' * 80}\n")
    
    # Analysis
    if successful_detections > 0:
        methods = {}
        numbers = []
        confidences = []
        
        for r in results:
            if r.get('status') == 'success':
                method = r.get('method', 'unknown')
                methods[method] = methods.get(method, 0) + 1
                numbers.append(r.get('number'))
                confidences.append(r.get('confidence', 0))
        
        print("Detection Analysis:")
        print(f"  Methods used: {methods}")
        if numbers:
            print(f"  Numbers detected: {sorted(set(numbers))}")
            print(f"  Unique numbers: {len(set(numbers))}")
        if confidences:
            print(f"  Average confidence: {sum(confidences) / len(confidences):.2f}")
            print(f"  Min confidence: {min(confidences):.2f}")
            print(f"  Max confidence: {max(confidences):.2f}")
        print()
    
    # Recommendations
    detection_rate = (successful_detections / num_tests * 100) if num_tests > 0 else 0
    
    print("Recommendations:")
    if detection_rate >= 90:
        print("   EXCELLENT! Detection rate is > 90%")
        print("   Bot should work well in production")
        print("   Continue with strategy testing")
    elif detection_rate >= 70:
        print("    GOOD but could be better (70-90%)")
        print("    Check saved images to verify ROI is correct")
        print("    Consider adjusting template threshold")
        print("    Test more to ensure consistency")
    elif detection_rate >= 50:
        print("    POOR detection rate (50-70%)")
        print("    Check screen_region coordinates")
        print("    Verify templates match browser")
        print("    Check browser zoom is 100%")
        print("    Verify browser window position")
    else:
        print("   VERY POOR detection rate (< 50%)")
        print("   Detection is NOT working properly")
        print("   DO NOT use bot in production yet")
        print("   Check:")
        print("     - Screen region coordinates")
        print("     - Templates exist and match browser")
        print("     - Browser is visible and positioned correctly")
        print("     - Browser zoom is 100%")
        print("     - Winning number area is visible")
    
    print(f"\n{'=' * 80}")
    print("Next Steps:")
    print(f"  1. Check saved images in: {output_dir}")
    print(f"  2. Review ROI capture - does it show winning number?")
    print(f"  3. If ROI is wrong, adjust screen_region in config")
    print(f"  4. If ROI is correct but no detection, check templates")
    print(f"  5. Re-run test after fixes")
    print(f"{'=' * 80}\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test browser detection - verifies bot can detect from browser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic test (20 attempts, 2 second delay)
  python test_browser_detection.py
  
  # Quick test (10 attempts, 1 second delay)
  python test_browser_detection.py --num-tests 10 --delay 1.0
  
  # Extended test (50 attempts, 3 second delay)
  python test_browser_detection.py --num-tests 50 --delay 3.0
        """
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to configuration file (default: config/default_config.json)'
    )
    parser.add_argument(
        '--num-tests',
        type=int,
        default=20,
        help='Number of detection attempts (default: 20)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Delay between tests in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--no-save-samples',
        action='store_true',
        help='Do not save sample images'
    )
    
    args = parser.parse_args()
    
    # Check if config exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f" Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Run test
    test_browser_detection(
        str(config_path),
        args.num_tests,
        args.delay,
        save_samples=not args.no_save_samples
    )

