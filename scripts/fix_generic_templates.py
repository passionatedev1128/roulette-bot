"""
Fix Generic Templates (7 and 9)
Helps identify and fix templates that are too generic.
"""

import cv2
import numpy as np
import sys
from pathlib import Path
import json

def analyze_template(template_path, test_image_path):
    """
    Analyze a template to see if it's too generic.
    """
    print(f"\nAnalyzing template: {template_path}")
    
    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    if template is None:
        print("   Could not load template")
        return None
    
    test_image = cv2.imread(str(test_image_path), cv2.IMREAD_GRAYSCALE)
    if test_image is None:
        print("   Could not load test image")
        return None
    
    # Get template size
    h, w = template.shape
    print(f"  Template size: {w}x{h} pixels")
    
    # Check template characteristics
    # 1. Check if template is mostly empty/background
    non_zero = np.count_nonzero(template)
    total_pixels = template.size
    fill_ratio = non_zero / total_pixels
    print(f"  Fill ratio: {fill_ratio:.2%} (non-zero pixels)")
    
    if fill_ratio < 0.1:
        print("    WARNING: Template has very few non-zero pixels")
        print("     This might be too generic (mostly background)")
    
    # 2. Check variance (low variance = uniform = generic)
    variance = np.var(template)
    print(f"  Variance: {variance:.2f}")
    
    if variance < 100:
        print("    WARNING: Low variance - template might be too uniform/generic")
    
    # 3. Test matching on image with no numbers
    result = cv2.matchTemplate(test_image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f"  Match on test image: {max_val:.4f}")
    
    if max_val > 0.75:
        print("    WARNING: High match on image with no numbers!")
        print("     This template is TOO GENERIC - it matches everything")
        return {
            'too_generic': True,
            'confidence': max_val,
            'fill_ratio': fill_ratio,
            'variance': variance
        }
    else:
        print("   Template seems specific enough")
        return {
            'too_generic': False,
            'confidence': max_val,
            'fill_ratio': fill_ratio,
            'variance': variance
        }


def compare_templates(templates_dir='templates'):
    """
    Compare all templates to find which ones are too generic.
    """
    print("=" * 70)
    print("ANALYZING TEMPLATES FOR GENERIC PATTERNS")
    print("=" * 70)
    
    templates_path = Path(templates_dir)
    if not templates_path.exists():
        print(f" Templates directory not found: {templates_dir}")
        return
    
    # Find a test image (preferably one with no numbers visible)
    # User should provide this
    print("\nTo analyze templates, you need:")
    print("  1. A test image with NO numbers visible")
    print("  2. This will show which templates match even when no numbers exist")
    print()
    
    # For now, analyze template characteristics
    print("Analyzing template characteristics...")
    print()
    
    problematic = []
    good = []
    
    for num in range(37):
        template_path = templates_path / f"number_{num}.png"
        if not template_path.exists():
            continue
        
        template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
        if template is None:
            continue
        
        h, w = template.shape
        fill_ratio = np.count_nonzero(template) / template.size
        variance = np.var(template)
        
        # Flags for potential issues
        issues = []
        if fill_ratio < 0.1:
            issues.append("low fill")
        if variance < 100:
            issues.append("low variance")
        if w > 100 or h > 100:
            issues.append("too large")
        
        if issues:
            problematic.append({
                'number': num,
                'size': f"{w}x{h}",
                'fill_ratio': fill_ratio,
                'variance': variance,
                'issues': issues
            })
        else:
            good.append(num)
    
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    
    if problematic:
        print("  POTENTIALLY PROBLEMATIC TEMPLATES:")
        print()
        for p in problematic:
            print(f"  Number {p['number']:2d}: {p['size']} pixels")
            print(f"    Fill ratio: {p['fill_ratio']:.2%}")
            print(f"    Variance: {p['variance']:.2f}")
            print(f"    Issues: {', '.join(p['issues'])}")
            print()
    else:
        print(" All templates look good based on characteristics")
    
    print(f"\n Templates analyzed: {len(problematic)} potentially problematic, {len(good)} look good")
    
    # Save results
    output = {
        'problematic': problematic,
        'good': good
    }
    
    with open('template_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n Results saved to: template_analysis.json")
    
    if problematic:
        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)
        print("\nFor problematic templates:")
        print("  1. Recreate from betting grid snapshot")
        print("  2. Make sure to crop ONLY the number")
        print("  3. Include minimal background (2-5 pixels)")
        print("  4. Don't include surrounding elements")
        print("\nRun:")
        print("  python create_templates_from_grid.py betting_grid.png")
        print("\nThen carefully crop numbers 7 and 9 (and any others flagged)")


def test_template_on_blank_image(template_path, blank_image_path):
    """
    Test if a template matches a blank image (should not match).
    """
    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    blank = cv2.imread(str(blank_image_path), cv2.IMREAD_GRAYSCALE)
    
    if template is None or blank is None:
        return None
    
    result = cv2.matchTemplate(blank, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    return max_val


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("=" * 70)
        print("FIX GENERIC TEMPLATES")
        print("=" * 70)
        print("\nUsage:")
        print("  python fix_generic_templates.py analyze [templates_dir]")
        print("  python fix_generic_templates.py test <template_number> <blank_image>")
        print()
        print("Examples:")
        print("  python fix_generic_templates.py analyze")
        print("  python fix_generic_templates.py test 7 blank_screen.png")
        print()
        print("This tool helps identify templates that are too generic")
        print("(match even when no numbers are present)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'analyze':
        templates_dir = sys.argv[2] if len(sys.argv) > 2 else 'templates'
        compare_templates(templates_dir)
    
    elif command == 'test':
        if len(sys.argv) < 4:
            print("Usage: python fix_generic_templates.py test <number> <blank_image>")
            sys.exit(1)
        
        num = int(sys.argv[2])
        blank_image = sys.argv[3]
        
        template_path = Path('templates') / f"number_{num}.png"
        result = analyze_template(template_path, blank_image)
        
        if result and result['too_generic']:
            print(f"\n Template {num} is TOO GENERIC!")
            print("   It matches even when no numbers are present.")
            print("\nSolution: Recreate this template from betting grid snapshot")
            print("  python create_templates_from_grid.py betting_grid.png")
    
    else:
        print(f"Unknown command: {command}")

