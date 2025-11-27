"""
Quick diagnostic script to identify why bot doesn't detect many numbers.
Run this to get a detailed analysis of detection issues.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from backend.app.config_loader import ConfigLoader
    from backend.app.detection import ScreenDetector
except ImportError:
    print(" Error: Cannot import bot modules. Make sure you're in the project root directory.")
    sys.exit(1)


def check_templates(config: Dict) -> Tuple[bool, List[int], List[int]]:
    """Check template coverage."""
    print("\n" + "=" * 80)
    print("1. TEMPLATE COVERAGE CHECK")
    print("=" * 80)
    
    detector = ScreenDetector(config)
    loaded_numbers = sorted([t[0] for t in detector.winning_templates])
    all_numbers = list(range(37))  # 0-36
    missing_numbers = [n for n in all_numbers if n not in loaded_numbers]
    
    print(f" Templates loaded: {len(loaded_numbers)}")
    print(f"   Numbers with templates: {loaded_numbers}")
    print(f"\n Missing templates: {len(missing_numbers)} numbers")
    print(f"   Missing: {missing_numbers}")
    
    coverage_percent = (len(loaded_numbers) / 37) * 100
    print(f"\n📊 Coverage: {coverage_percent:.1f}% ({len(loaded_numbers)}/37)")
    
    if coverage_percent < 50:
        print("  CRITICAL: Less than 50% coverage - bot can only detect these numbers!")
        return False, loaded_numbers, missing_numbers
    elif coverage_percent < 90:
        print("  WARNING: Less than 90% coverage - many numbers will be missed")
        return False, loaded_numbers, missing_numbers
    else:
        print(" Good coverage - most numbers can be detected")
        return True, loaded_numbers, missing_numbers


def check_thresholds(config: Dict) -> Tuple[bool, Dict]:
    """Check detection thresholds."""
    print("\n" + "=" * 80)
    print("2. THRESHOLD CHECK")
    print("=" * 80)
    
    detection = config.get('detection', {})
    template_threshold = detection.get('winning_template_threshold', 0.75)
    ocr_threshold = detection.get('ocr_confidence_threshold', 0.9)
    
    print(f"Template matching threshold: {template_threshold}")
    print(f"OCR confidence threshold: {ocr_threshold}")
    
    issues = []
    if template_threshold > 0.8:
        issues.append("Template threshold is very high (>0.8) - may reject valid matches")
    if ocr_threshold > 0.85:
        issues.append("OCR threshold is very high (>0.85) - may reject valid OCR results")
    
    if issues:
        print("\n  Potential issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n Suggestion: Try lowering thresholds temporarily:")
        print(f"   - winning_template_threshold: {max(0.65, template_threshold - 0.1):.2f}")
        print(f"   - ocr_confidence_threshold: {max(0.75, ocr_threshold - 0.1):.2f}")
        return False, {"template": template_threshold, "ocr": ocr_threshold}
    else:
        print(" Thresholds are reasonable")
        return True, {"template": template_threshold, "ocr": ocr_threshold}


def check_screen_region(config: Dict) -> Tuple[bool, List[int]]:
    """Check screen region configuration."""
    print("\n" + "=" * 80)
    print("3. SCREEN REGION CHECK")
    print("=" * 80)
    
    detection = config.get('detection', {})
    screen_region = detection.get('screen_region')
    
    if screen_region is None:
        print("  WARNING: screen_region is not set")
        print("   Bot will capture full screen (slower, less accurate)")
        return False, []
    
    if not isinstance(screen_region, list) or len(screen_region) != 4:
        print(" ERROR: screen_region format is invalid")
        print(f"   Current value: {screen_region}")
        print("   Expected: [x, y, width, height]")
        return False, screen_region
    
    x, y, w, h = screen_region
    area = w * h
    
    print(f"Screen region: [{x}, {y}, {w}, {h}]")
    print(f"Region size: {w}x{h} = {area} pixels")
    
    issues = []
    if area < 2000:
        issues.append(f"Region is very small ({area} pixels) - may be hard to capture accurately")
    if w < 50 or h < 50:
        issues.append(f"Region dimensions are small ({w}x{h}) - may miss badge edges")
    
    if issues:
        print("\n  Potential issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n Suggestion: Run 'python show_detection_region.py' to visualize the region")
        print("   Verify the red box covers the entire winning number badge")
        return False, screen_region
    else:
        print(" Screen region looks reasonable")
        return True, screen_region


def check_frame_skip(config: Dict) -> Tuple[bool, Dict]:
    """Check frame skipping configuration."""
    print("\n" + "=" * 80)
    print("4. FRAME SKIP CHECK")
    print("=" * 80)
    
    detection = config.get('detection', {})
    frame_skip = detection.get('frame_skip_interval', 30)
    video_frame_skip = detection.get('video_frame_skip_interval', 30)
    
    print(f"Real-time frame skip: {frame_skip} (process every {frame_skip} frames)")
    print(f"Video frame skip: {video_frame_skip} (process every {video_frame_skip} frames)")
    
    # At 30fps, 30 frames = 1 second
    real_time_interval = frame_skip / 30.0
    video_interval = video_frame_skip / 30.0
    
    print(f"Real-time detection interval: {real_time_interval:.2f} seconds")
    print(f"Video detection interval: {video_interval:.2f} seconds")
    
    issues = []
    if frame_skip > 30:
        issues.append(f"Frame skip is high ({frame_skip}) - may miss short-lived numbers")
    if video_frame_skip > 30:
        issues.append(f"Video frame skip is high ({video_frame_skip}) - may miss short-lived numbers")
    
    if issues:
        print("\n  Potential issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n Suggestion: Try reducing frame skip intervals:")
        print(f"   - frame_skip_interval: {max(10, frame_skip - 10)}")
        print(f"   - video_frame_skip_interval: {max(10, video_frame_skip - 10)}")
        return False, {"real_time": frame_skip, "video": video_frame_skip}
    else:
        print(" Frame skip intervals are reasonable")
        return True, {"real_time": frame_skip, "video": video_frame_skip}


def check_ocr_config(config: Dict) -> Tuple[bool, Dict]:
    """Check OCR configuration."""
    print("\n" + "=" * 80)
    print("5. OCR CONFIGURATION CHECK")
    print("=" * 80)
    
    detection = config.get('detection', {})
    enable_ocr = detection.get('enable_ocr_fallback', True)
    ocr_only_if_no_templates = detection.get('ocr_only_if_no_templates', False)
    
    print(f"OCR fallback enabled: {enable_ocr}")
    print(f"OCR only if no templates: {ocr_only_if_no_templates}")
    
    if not enable_ocr:
        print("  OCR is disabled - only template matching will be used")
        print("   If templates are missing, those numbers cannot be detected")
        return False, {"enabled": False, "only_if_no_templates": ocr_only_if_no_templates}
    
    if ocr_only_if_no_templates:
        print("  OCR only runs when no templates exist")
        print("   This means OCR won't help with missing templates")
        return False, {"enabled": True, "only_if_no_templates": True}
    
    print(" OCR is enabled and will be used as fallback")
    return True, {"enabled": True, "only_if_no_templates": ocr_only_if_no_templates}


def generate_summary(results: Dict):
    """Generate summary report."""
    print("\n" + "=" * 80)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    
    critical_issues = []
    warnings = []
    
    # Check template coverage
    template_ok, loaded, missing = results['templates']
    if not template_ok:
        critical_issues.append(f"Only {len(loaded)}/37 templates available - {len(missing)} numbers cannot be detected")
    
    # Check thresholds
    threshold_ok, thresholds = results['thresholds']
    if not threshold_ok:
        warnings.append("Detection thresholds may be too high")
    
    # Check screen region
    region_ok, region = results['screen_region']
    if not region_ok:
        warnings.append("Screen region may need verification")
    
    # Check frame skip
    frame_skip_ok, frame_skip = results['frame_skip']
    if not frame_skip_ok:
        warnings.append("Frame skip intervals may be too high")
    
    # Check OCR
    ocr_ok, ocr_config = results['ocr']
    if not ocr_ok:
        warnings.append("OCR configuration may limit detection")
    
    # Print summary
    if critical_issues:
        print("\n🚨 CRITICAL ISSUES (Must Fix):")
        for i, issue in enumerate(critical_issues, 1):
            print(f"   {i}. {issue}")
    
    if warnings:
        print("\n  WARNINGS (Should Review):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    if not critical_issues and not warnings:
        print("\n No major issues detected!")
        print("   If detection is still poor, check:")
        print("   - Template quality (are templates clear and match game style?)")
        print("   - Screen region accuracy (run 'python show_detection_region.py')")
        print("   - Game window position (has it moved?)")
    
    # Priority recommendations
    print("\n📋 PRIORITY FIXES:")
    priority = 1
    
    if not template_ok:
        print(f"\n   {priority}. CREATE MISSING TEMPLATES (CRITICAL)")
        print(f"      - Missing: {len(missing)} numbers")
        print(f"      - Use: python capture_winning-numbers.py")
        print(f"      - Or: python create_templates_from_video.py")
        priority += 1
    
    if not region_ok:
        print(f"\n   {priority}. VERIFY SCREEN REGION")
        print(f"      - Run: python show_detection_region.py")
        print(f"      - Verify red box covers winning number badge")
        priority += 1
    
    if not threshold_ok:
        print(f"\n   {priority}. LOWER THRESHOLDS (TEST)")
        print(f"      - Try: winning_template_threshold: {max(0.65, thresholds['template'] - 0.1):.2f}")
        print(f"      - Try: ocr_confidence_threshold: {max(0.75, thresholds['ocr'] - 0.1):.2f}")
        priority += 1
    
    if not frame_skip_ok:
        print(f"\n   {priority}. REDUCE FRAME SKIP")
        print(f"      - Try: frame_skip_interval: {max(10, frame_skip['real_time'] - 10)}")
        priority += 1
    
    print("\n" + "=" * 80)
    print("For detailed analysis, see: DETECTION_ISSUES_ANALYSIS.md")
    print("=" * 80)


def main():
    """Main diagnostic function."""
    print("=" * 80)
    print("BOT DETECTION PROBLEMS DIAGNOSTIC")
    print("=" * 80)
    
    config_path = Path("config/default_config.json")
    if not config_path.exists():
        print(f" Error: Config file not found: {config_path}")
        print("   Please run this script from the project root directory")
        sys.exit(1)
    
    try:
        config = ConfigLoader.load_config(str(config_path))
    except Exception as e:
        print(f" Error loading config: {e}")
        sys.exit(1)
    
    print(f"Config file: {config_path.absolute()}")
    
    # Run all checks
    results = {
        'templates': check_templates(config),
        'thresholds': check_thresholds(config),
        'screen_region': check_screen_region(config),
        'frame_skip': check_frame_skip(config),
        'ocr': check_ocr_config(config),
    }
    
    # Generate summary
    generate_summary(results)


if __name__ == "__main__":
    main()

