"""
Test Number Templates with Snapshot
Tests template matching on a single image/snapshot.
"""

import cv2
import numpy as np
import sys
from pathlib import Path
import json
from datetime import datetime

from backend.app.detection.screen_detector import ScreenDetector
from backend.app.config_loader import ConfigLoader


def test_templates_on_snapshot(image_path, config_path='config/default_config.json', templates_dir='templates'):
    """
    Test template matching on a single snapshot image.
    
    Args:
        image_path: Path to snapshot image
        config_path: Path to config file
        templates_dir: Directory containing templates
    """
    print("=" * 70)
    print("TESTING TEMPLATES WITH SNAPSHOT")
    print("=" * 70)
    print()
    
    # Check image exists
    if not Path(image_path).exists():
        print(f" Error: Image file not found: {image_path}")
        return False
    
    # Load config
    try:
        config = ConfigLoader.load_config(config_path)
        print(" Config loaded")
    except Exception as e:
        print(f" Error loading config: {e}")
        return False
    
    # Create detector
    try:
        detector = ScreenDetector(config)
        print(" Detector created")
    except Exception as e:
        print(f" Error creating detector: {e}")
        return False
    
    # Load image
    print(f"\nLoading image: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print(f" Error: Could not load image: {image_path}")
        return False
    
    print(f" Image loaded: {image.shape[1]}x{image.shape[0]} pixels")
    
    # Check templates exist
    print(f"\nChecking templates in: {templates_dir}/")
    template_count = 0
    for i in range(37):
        template_path = Path(templates_dir) / f"number_{i}.png"
        if template_path.exists():
            template_count += 1
    
    print(f" Found {template_count}/37 templates")
    
    if template_count == 0:
        print(" Error: No templates found!")
        print(f"   Create templates first using:")
        print(f"   python create_templates_from_grid.py <betting_grid_image>")
        return False
    
    if template_count < 37:
        print(f" Warning: Only {template_count}/37 templates found")
        print("   Some numbers may not be detected")
    
    print("\n" + "=" * 70)
    print("TESTING TEMPLATE MATCHING")
    print("=" * 70)
    print()
    
    # Test detection
    print("Detecting number in snapshot...")
    result = detector.detect_result(image)
    
    print("\n" + "=" * 70)
    print("DETECTION RESULTS")
    print("=" * 70)
    print()
    
    if result.get('number') is not None:
        print(f" Number detected: {result['number']}")
        print(f"  Color: {result.get('color', 'unknown')}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Method: {result.get('method', 'unknown')}")
        print(f"  Zero: {result.get('zero', False)}")
    else:
        print(" No number detected")
        print("  This could mean:")
        print("    - No number is visible in the snapshot")
        print("    - Templates don't match (need to recreate)")
        print("    - Confidence threshold too high")
    
    # Test all templates individually
    print("\n" + "=" * 70)
    print("TESTING ALL TEMPLATES")
    print("=" * 70)
    print("\nTesting each template to see which ones match...")
    print()
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    matches = []
    
    for num in range(37):
        template_path = Path(templates_dir) / f"number_{num}.png"
        if not template_path.exists():
            continue
        
        try:
            template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
            if template is None:
                continue
            
            # Template matching
            result_match = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_match)
            
            matches.append({
                'number': num,
                'confidence': float(max_val),
                'location': max_loc
            })
            
            # Show matches above threshold
            if max_val >= 0.5:  # Show all potential matches
                status = "" if max_val >= 0.75 else ""
                print(f"  {status} Number {num:2d}: confidence = {max_val:.3f}")
        
        except Exception as e:
            print(f"   Number {num}: Error - {e}")
    
    # Sort by confidence
    matches.sort(key=lambda x: x['confidence'], reverse=True)
    
    print("\n" + "=" * 70)
    print("TOP MATCHES")
    print("=" * 70)
    print("\nBest matches (sorted by confidence):")
    print()
    
    if matches:
        for i, match in enumerate(matches[:10]):  # Top 10
            conf = match['confidence']
            num = match['number']
            status = " ACCEPTED" if conf >= 0.75 else " REJECTED (too low)"
            print(f"  {i+1:2d}. Number {num:2d}: {conf:.3f} - {status}")
    else:
        print("  No matches found")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    if matches:
        best_match = matches[0]
        print(f"Best match: Number {best_match['number']} (confidence: {best_match['confidence']:.3f})")
        
        if best_match['confidence'] >= 0.75:
            print(" Confidence is high enough - detection accepted")
        else:
            print(" Confidence too low - detection rejected")
            print(f"  Need confidence ≥ 0.75, got {best_match['confidence']:.3f}")
        
        # Count matches above threshold
        high_conf = [m for m in matches if m['confidence'] >= 0.75]
        print(f"\nMatches with confidence ≥ 0.75: {len(high_conf)}")
        
        if len(high_conf) > 1:
            print(" Warning: Multiple high-confidence matches found!")
            print("  This might indicate:")
            print("    - Templates are too similar")
            print("    - Image contains multiple numbers")
    else:
        print(" No template matches found")
        print("  Possible reasons:")
        print("    - Templates don't match the snapshot")
        print("    - Snapshot doesn't contain numbers")
        print("    - Need to recreate templates from this snapshot")
    
    # Visualize matches (optional)
    print("\n" + "=" * 70)
    print("VISUALIZATION")
    print("=" * 70)
    print("\nShowing image with detection results...")
    print("Press any key to close the window")
    
    # Create visualization
    vis_image = image.copy()
    
    if matches and matches[0]['confidence'] >= 0.75:
        best = matches[0]
        template_path = Path(templates_dir) / f"number_{best['number']}.png"
        template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
        
        if template is not None:
            h, w = template.shape
            x, y = best['location']
            
            # Draw rectangle around match
            cv2.rectangle(vis_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Add text
            label = f"Number {best['number']} ({best['confidence']:.2f})"
            cv2.putText(vis_image, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Show image
    cv2.imshow('Template Test Results', vis_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Save results
    output_file = f"template_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'image_path': str(image_path),
            'detection_result': result,
            'all_matches': matches,
            'best_match': matches[0] if matches else None,
            'template_count': template_count
        }, f, indent=2)
    
    print(f"\n Results saved to: {output_file}")
    
    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("TEST TEMPLATES WITH SNAPSHOT")
        print("=" * 70)
        print("\nUsage:")
        print("  python test_templates_with_snapshot.py <snapshot_image>")
        print()
        print("Example:")
        print("  python test_templates_with_snapshot.py betting_grid.png")
        print("  python test_templates_with_snapshot.py game_screenshot.png")
        print()
        print("This will:")
        print("  - Test all templates against the snapshot")
        print("  - Show which numbers match")
        print("  - Display confidence scores")
        print("  - Visualize the best match")
        print("  - Save results to JSON file")
        sys.exit(1)
    
    image_path = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else 'config/default_config.json'
    templates_dir = sys.argv[3] if len(sys.argv) > 3 else 'templates'
    
    test_templates_on_snapshot(image_path, config_path, templates_dir)


if __name__ == '__main__':
    main()

