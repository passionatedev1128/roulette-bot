"""Quick setup check script"""
import sys

print("Checking dependencies...\n")

# Check Python packages
try:
    import cv2
    print("[OK] OpenCV installed")
except ImportError:
    print(" OpenCV not installed")

try:
    import numpy
    print("[OK] NumPy installed")
except ImportError:
    print(" NumPy not installed")

try:
    import pytesseract
    print("[OK] pytesseract installed")
except ImportError:
    print(" pytesseract not installed")

try:
    import pyautogui
    print("[OK] pyautogui installed")
except ImportError:
    print(" pyautogui not installed")

# Check Tesseract OCR
print("\nChecking Tesseract OCR...")
try:
    import pytesseract
    pytesseract.get_tesseract_version()
    print("[OK] Tesseract OCR installed and accessible")
except Exception as e:
    print(f"[!] Tesseract OCR not found or not in PATH: {e}")
    print("   Note: Bot will work but template matching is recommended")

# Check if video file exists
import os
video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
if video_files:
    print(f"\n[OK] Found video files in current directory:")
    for f in video_files:
        print(f"   - {f}")
else:
    print("\n[!] No video files found in current directory")
    print("   Place your video file here or use full path")

print("\n" + "="*50)
print("Setup check complete!")
print("="*50)

