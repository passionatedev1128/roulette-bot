"""
Diagnose Template Matching Issue
Helps identify why only number 7 is being detected.
"""

import cv2
import numpy as np
import sys
from pathlib import Path
import json

def diagnose_templates(image_path, templates_dir='templates'):
    """
    Diagnose template matching to see why only number 7 is detected.
    """
    print("=" * 70)
    print("TEMPLATE MATCHING DIAGNOSTIC")
    print("=" * 70)
    print()
    
    # Check image exists
    if not Path(image_path).exists():
        print(f" Error: Image file not found: {image_path}")
        return
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f" Error: Could not load image: {image_path}")
        return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(f" Image loaded: {image.shape[1]}x{image.shape[0]} pixels")
    print()
    
    # Test all templates
    print("Testing all templates...")
    print()
    
    matches = []
    
    for num in range(37):
        template_path = Path(templates_dir) / f"number_{num}.png"
        if not template_path.exists():
            continue
        
        try:
            template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
            if template is None:
                continue
            
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            matches.append({
                'number': num,
                'confidence': float(max_val),
                'location': max_loc
            })
            
        except Exception as e:
            print(f" Error testing number {num}: {e}")
    
    # Sort by confidence
    matches.sort(key=lambda x: x['confidence'], reverse=True)
    
    print("=" * 70)
    print("ALL TEMPLATE MATCHES (Sorted by Confidence)")
    print("=" * 70)
    print()
    
    for i, match in enumerate(matches):
        num = match['number']
        conf = match['confidence']
        status = " ACCEPTED" if conf >= 0.75 else " REJECTED"
        marker = ">>>" if i == 0 else "   "
        print(f"{marker} {i+1:2d}. Number {num:2d}: {conf:.4f} - {status}")
    
    print()
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print()
    
    if matches:
        best = matches[0]
        second = matches[1] if len(matches) > 1 else None
        
        print(f"Best match: Number {best['number']} (confidence: {best['confidence']:.4f})")
        
        if second:
            diff = best['confidence'] - second['confidence']
            print(f"Second best: Number {second['number']} (confidence: {second['confidence']:.4f})")
            print(f"Difference: {diff:.4f}")
            
            if diff < 0.1:
                print()
                print("  PROBLEM DETECTED:")
                print("   Best match is too close to second best!")
                print("   This suggests ambiguity or a generic template.")
                print()
                print("   Possible causes:")
                print("   - Number 7 template is too generic (matches everything)")
                print("   - Templates are too similar")
                print("   - Image contains multiple numbers")
                print()
                print("   Solution:")
                print("   - Check number 7 template - is it too large/generic?")
                print("   - Recreate templates from betting grid snapshot")
                print("   - Make sure templates only include the number, not background")
        
        if best['confidence'] >= 0.75:
            print()
            print(f" Confidence meets threshold (≥ 0.75)")
        else:
            print()
            print(f" Confidence below threshold (need ≥ 0.75, got {best['confidence']:.4f})")
        
        # Check if number 7 is always winning
        if best['number'] == 7:
            print()
            print("  NUMBER 7 IS WINNING")
            print("   This could mean:")
            print("   - Number 7 template is too generic")
            print("   - Number 7 template matches background/patterns")
            print("   - Number 7 template is larger than others")
            print()
            print("   Check number 7 template:")
            print(f"   {templates_dir}/number_7.png")
            print("   - Is it too large?")
            print("   - Does it include too much background?")
            print("   - Is it different from other templates?")
    
    # Save detailed results
    output_file = 'template_diagnostic_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'image_path': str(image_path),
            'matches': matches,
            'best_match': matches[0] if matches else None,
            'second_best': matches[1] if len(matches) > 1 else None
        }, f, indent=2)
    
    print()
    print(f" Detailed results saved to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python diagnose_template_issue.py <image_path> [templates_dir]")
        print()
        print("Example:")
        print("  python diagnose_template_issue.py betting_grid.png")
        print("  python diagnose_template_issue.py game_screenshot.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    templates_dir = sys.argv[2] if len(sys.argv) > 2 else 'templates'
    
    diagnose_templates(image_path, templates_dir)

