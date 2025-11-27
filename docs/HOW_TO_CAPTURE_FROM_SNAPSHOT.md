# How to Capture Even/Odd Coordinates from Snapshot

If you only have a snapshot (screenshot) of the game instead of a live window, use this method.

## Quick Start

```bash
python capture_even_odd_from_snapshot.py snapshot.png
```

Or run without arguments and enter the path when prompted:
```bash
python capture_even_odd_from_snapshot.py
# Then enter: snapshot.png
```

## Step-by-Step Instructions

### Step 1: Prepare Your Snapshot

1. **Save your snapshot image:**
   - Formats supported: `.png`, `.jpg`, `.jpeg`, `.bmp`
   - Make sure the image shows the full betting table
   - Even and Odd betting areas should be visible

2. **Note the image location:**
   - Example: `C:\Users\You\Desktop\roulette_snapshot.png`
   - Or: `./snapshots/game_screenshot.png`

### Step 2: Run the Capture Script

```bash
python capture_even_odd_from_snapshot.py your_snapshot.png
```

### Step 3: Click on the Betting Areas

1. **An image window will open** showing your snapshot

2. **Click on EVEN betting area:**
   - Move mouse over the Even/Par button/area
   - Click once
   - A green marker will appear

3. **Click on ODD betting area:**
   - Move mouse over the Odd/Ímpar button/area
   - Click once
   - A green marker will appear

4. **Press 's' to save** when both are captured

### Step 4: Add to Config

The script will:
- Save coordinates to `even_odd_coordinates.json`
- Show you the config snippet to add

## Controls

While the image window is open:

- **Click** - Capture coordinate at click position
- **'s'** - Save and finish
- **'r'** - Reset current coordinate
- **'q' or ESC** - Quit without saving

## Example Usage

```bash
# Method 1: Pass image as argument
python capture_even_odd_from_snapshot.py game_snapshot.png

# Method 2: Run and enter path when prompted
python capture_even_odd_from_snapshot.py
# Enter: game_snapshot.png
```

## What You'll See

```
======================================================================
EVEN/ODD COORDINATE CAPTURE FROM SNAPSHOT
======================================================================

Image: game_snapshot.png

Instructions:
  1. The snapshot image will open in a window
  2. Click on the Even betting area
  3. Click on the Odd betting area
  ...

Press Enter to start...
```

Then an image window opens. Click on the areas, and you'll see:
```
 Click on EVEN betting area...
   Captured EVEN: [1100, 904]
 Click on ODD betting area...
   Captured ODD: [1170, 906]
```

## Output

After saving, you'll get:

1. **JSON file:** `even_odd_coordinates.json`
   ```json
   {
     "even": [1100, 904],
     "odd": [1170, 906]
   }
   ```

2. **Config snippet:**
   ```
   "betting": {
     "betting_areas": {
       "even": [1100, 904],
       "odd": [1170, 906]
     }
   }
   ```

## Troubleshooting

### Problem: Image won't open

**Solution:**
- Check image path is correct
- Make sure image format is supported (.png, .jpg, etc.)
- Try using full path: `C:\full\path\to\image.png`

### Problem: Can't see the image window

**Solution:**
- Check if window opened behind other windows
- Look for "Even/Odd Coordinate Capture" window
- Try Alt+Tab to find it

### Problem: Coordinates seem wrong

**Solution:**
- Make sure you clicked the center of the betting area
- Click should be on the actual button/clickable area
- Press 'r' to reset and try again

### Problem: OpenCV not installed

**Solution:**
```bash
pip install opencv-python
```

### Problem: Image is too large/small

**Solution:**
- The script automatically resizes large images for display
- Coordinates are always saved in original image resolution
- You can resize the window manually if needed

## Alternative: Manual Coordinate Entry

If clicking doesn't work, you can manually enter coordinates:

1. **Open your snapshot in an image viewer**
2. **Hover over the Even betting area**
3. **Note the X, Y coordinates** (some viewers show this)
4. **Edit the config directly:**

```json
{
  "betting": {
    "betting_areas": {
      "even": [x, y],  // Replace with your coordinates
      "odd": [x, y]   // Replace with your coordinates
    }
  }
}
```

## Finding Coordinates Manually

If you need to find coordinates manually:

### Using Windows Paint:
1. Open image in Paint
2. Hover over the area
3. Check bottom-left corner for coordinates

### Using ImageJ (free):
1. Open image in ImageJ
2. Hover shows coordinates in status bar

### Using Python:
```python
import cv2
import numpy as np

# Load image
img = cv2.imread('snapshot.png')

# Display and get click coordinates
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Coordinates: [{x}, {y}]")

cv2.imshow('Image', img)
cv2.setMouseCallback('Image', click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

## Tips

1. **Use high-quality snapshot:** Clear image makes it easier to find the right spot
2. **Zoom in if needed:** Some image viewers let you zoom for precision
3. **Check multiple times:** Verify coordinates by clicking again
4. **Test after adding:** Test the coordinates work with the bot

## Next Steps

After capturing coordinates:

1.  Add to config file
2.  Verify coordinates are correct
3.  Test with bot in test mode
4.  Run full strategy test

## Notes

- **Coordinate system:** Top-left is (0, 0), X increases right, Y increases down
- **Image resolution:** Coordinates are relative to the image, not screen
- **Multiple snapshots:** If game layout changes, capture new coordinates
- **Backup:** Keep your snapshot file for reference

