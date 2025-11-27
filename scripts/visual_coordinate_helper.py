"""
Visual Coordinate Helper
Uses screenshot to help identify betting areas and capture coordinates.
"""

import pyautogui
import cv2
import numpy as np
import time
from PIL import Image, ImageDraw, ImageFont
import os


def take_screenshot_and_analyze():
    """Take screenshot and help identify areas."""
    print("=" * 70)
    print("VISUAL COORDINATE HELPER")
    print("=" * 70)
    print("\nThis tool will:")
    print("1. Take a screenshot of your screen")
    print("2. Save it so you can mark areas")
    print("3. Help you identify where to capture coordinates")
    print("\nPress Enter to take screenshot...")
    input()
    
    # Take screenshot
    print("Taking screenshot...")
    screenshot = pyautogui.screenshot()
    screenshot_path = 'game_screenshot.png'
    screenshot.save(screenshot_path)
    print(f" Screenshot saved: {screenshot_path}")
    
    # Show image with instructions
    print("\n" + "=" * 70)
    print("SCREENSHOT ANALYSIS")
    print("=" * 70)
    print("\nLook at the screenshot and identify:")
    print("1. Where is the betting grid? (bottom center)")
    print("2. Where is 'Vermelho' (Red) betting area?")
    print("3. Where is 'Preto' (Black) betting area?")
    print("4. Where does the winning number appear? (center video area)")
    
    return screenshot_path


def mark_areas_on_screenshot(image_path):
    """Create annotated screenshot showing where to look."""
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Get image size
        width, height = img.size
        
        # Draw instructions
        instructions = [
            "1. Find VERMELHO (Red) betting area on betting grid",
            "2. Find PRETO (Black) betting area on betting grid",
            "3. Find where winning number appears (center video)",
            "4. Use coordinate_capture_tool.py to capture these"
        ]
        
        # Draw text boxes
        y_offset = 20
        for i, text in enumerate(instructions):
            draw.rectangle([10, y_offset, 500, y_offset + 30], fill=(0, 0, 0, 200))
            draw.text((15, y_offset + 5), text, fill=(255, 255, 0))
            y_offset += 40
        
        # Save annotated image
        annotated_path = 'game_screenshot_annotated.png'
        img.save(annotated_path)
        print(f"\n Annotated screenshot saved: {annotated_path}")
        print("Open this file to see where to look for betting areas")
        
        return annotated_path
    except Exception as e:
        print(f"Could not annotate image: {e}")
        return image_path


def interactive_coordinate_capture():
    """Interactive coordinate capture with visual guidance."""
    print("=" * 70)
    print("INTERACTIVE COORDINATE CAPTURE")
    print("=" * 70)
    
    # Take screenshot first
    screenshot_path = take_screenshot_and_analyze()
    
    # Mark areas
    annotated_path = mark_areas_on_screenshot(screenshot_path)
    
    print("\n" + "=" * 70)
    print("NOW CAPTURE COORDINATES")
    print("=" * 70)
    print("\nBased on your screenshot, we'll now capture coordinates.")
    print("Make sure your game is visible and in the same position!")
    print("\nPress Enter when ready...")
    input()
    
    coordinates = {}
    
    # Capture Red area
    print("\n" + "=" * 70)
    print("STEP 1: RED (Vermelho) Betting Area")
    print("=" * 70)
    print("\nOn your betting grid (bottom center), find:")
    print("- Look for 'Vermelho' text or red-colored betting area")
    print("- OR look for a red betting box/area")
    print("- Move mouse to CENTER of that area")
    print("\nYou have 5 seconds...")
    time.sleep(5)
    red_x, red_y = pyautogui.position()
    coordinates['red_bet_button'] = [red_x, red_y]
    print(f" Captured RED: [{red_x}, {red_y}]")
    
    # Capture Black area
    print("\n" + "=" * 70)
    print("STEP 2: BLACK (Preto) Betting Area")
    print("=" * 70)
    print("\nOn your betting grid (bottom center), find:")
    print("- Look for 'Preto' text or black-colored betting area")
    print("- OR look for a black betting box/area")
    print("- Move mouse to CENTER of that area")
    print("\nYou have 5 seconds...")
    time.sleep(5)
    black_x, black_y = pyautogui.position()
    coordinates['black_bet_button'] = [black_x, black_y]
    print(f" Captured BLACK: [{black_x}, {black_y}]")
    
    # Capture number display area (optional)
    print("\n" + "=" * 70)
    print("STEP 3: Number Display Area (Optional)")
    print("=" * 70)
    print("\nWhere does the winning number appear?")
    print("- Usually in the center video area")
    print("- Move mouse to center of number display")
    print("- Press Ctrl+C to skip if not needed")
    try:
        print("\nYou have 5 seconds...")
        time.sleep(5)
        num_x, num_y = pyautogui.position()
        coordinates['number_display_center'] = [num_x, num_y]
        print(f" Captured Number Display: [{num_x}, {num_y}]")
    except KeyboardInterrupt:
        print("   Skipped number display")
    
    # Save coordinates
    import json
    with open('game_coordinates.json', 'w') as f:
        json.dump(coordinates, f, indent=2)
    
    print("\n" + "=" * 70)
    print("COORDINATES SAVED")
    print("=" * 70)
    print(f"\nSaved to: game_coordinates.json")
    print("\nCaptured coordinates:")
    for key, value in coordinates.items():
        print(f"  {key}: {value}")
    
    # Generate config
    print("\n" + "=" * 70)
    print("CONFIG SNIPPET")
    print("=" * 70)
    print("\nCopy this into config/default_config.json:\n")
    print('"betting": {')
    print('  "betting_areas": {')
    if 'red_bet_button' in coordinates:
        print(f'    "red": {coordinates["red_bet_button"]},')
    if 'black_bet_button' in coordinates:
        print(f'    "black": {coordinates["black_bet_button"]},')
    print('  },')
    print('  // ... other betting settings')
    print('},')
    
    return coordinates


def analyze_game_interface():
    """Analyze game interface from description and provide guidance."""
    print("=" * 70)
    print("GAME INTERFACE ANALYSIS - LUCK.BET Roleta Brasileira")
    print("=" * 70)
    
    print("\nBased on your game, here's what to look for:")
    
    print("\n1. BETTING GRID (Bottom Center)")
    print("   - Located below the roulette wheel video")
    print("   - Contains numbers 0-36 in a grid")
    print("   - Has outside betting areas")
    
    print("\n2. RED/BLACK BETTING AREAS")
    print("   - Look for 'Vermelho/Preto' betting option")
    print("   - According to limits panel: 'Vermelho/Preto' = 1:1 payout")
    print("   - These are OUTSIDE bets (not individual numbers)")
    print("   - Location: On the betting grid, likely as separate betting boxes")
    
    print("\n3. CHIP SELECTION (Bottom)")
    print("   - Chips: 0.5, 1, 2.5, 5, 20, 50")
    print("   - Location: Bottom of screen, likely in a row")
    
    print("\n4. CONTROL BUTTONS")
    print("   - DESFAZER (Undo)")
    print("   - DOBRAR (Double)")
    print("   - JOGO AUTOMÁTICO (Auto Play)")
    
    print("\n5. NUMBER DISPLAY")
    print("   - Winning number appears in the center video area")
    print("   - Or may be displayed above/below the wheel")
    
    print("\n" + "=" * 70)
    print("HOW TO FIND BETTING AREAS")
    print("=" * 70)
    print("\nOn the betting grid, look for:")
    print("  - Betting boxes labeled 'Vermelho' or 'Preto'")
    print("  - OR colored betting areas (red box, black box)")
    print("  - These are separate from the number grid")
    print("  - Usually located on the sides or bottom of the grid")
    
    print("\n" + "=" * 70)
    print("NEXT STEP")
    print("=" * 70)
    print("\nRun: python visual_coordinate_helper.py")
    print("This will help you capture coordinates step by step.")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'analyze':
        analyze_game_interface()
    else:
        interactive_coordinate_capture()


if __name__ == '__main__':
    main()

