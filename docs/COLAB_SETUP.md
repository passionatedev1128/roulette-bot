# Testing in Google Colab - Setup Guide

## Quick Start

1. **Open Google Colab**: https://colab.research.google.com/
2. **Create a new notebook**
3. **Copy and run the cells** from `roulette_bot_test.ipynb` (or follow instructions below)

---

## Step-by-Step Instructions

### Step 1: Upload Your Project Files

**Option A: Upload via Colab (Recommended for testing)**
1. Upload your video file: `roleta_brazileria.mp4`
2. Upload key files: `config/default_config.json`
3. Upload the `backend` folder

**Option B: Use Google Drive**
1. Upload your project to Google Drive
2. Mount Drive in Colab
3. Navigate to project folder

### Step 2: Install Dependencies

Run this in a Colab cell:
```python
!pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils
```

**Note**: Tesseract OCR is pre-installed in Colab, so you don't need to install it separately!

### Step 3: Upload Video File

Use Colab's file upload widget or mount Google Drive.

### Step 4: Run Tests

Use the adapted test script (see below).

---

## Advantages of Colab

 **Free GPU/CPU** - Better performance  
 **Pre-installed tools** - Tesseract OCR included  
 **Easy file management** - Upload/download files easily  
 **No local setup** - Everything runs in browser  
 **Shareable** - Easy to share results

---

## Limitations

 **No screen automation** - Can't test betting automation (pyautogui)  
 **Video only** - Can only test detection, not live betting  
 **File upload size** - Large videos may take time to upload

---

## Next Steps

See `roulette_bot_test.ipynb` for a ready-to-use notebook, or follow the manual instructions below.

