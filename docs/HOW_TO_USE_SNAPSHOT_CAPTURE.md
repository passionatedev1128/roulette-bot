# How to Use capture_even_odd_from_snapshot_simple.py

Simple step-by-step guide for capturing Even/Odd coordinates from a snapshot image.

## Quick Start

```bash
python capture_even_odd_from_snapshot_simple.py your_snapshot.png
```

## Step-by-Step Instructions

### Step 1: Prepare Your Snapshot

1. **Make sure you have a snapshot image:**
   - Formats: `.png`, `.jpg`, `.jpeg`, `.bmp`
   - The image should show the roulette betting table
   - "Par" and "Ímpar" buttons should be visible

2. **Note the file path:**
   - Example: `snapshot.png`
   - Or: `C:\Users\You\Desktop\game_screenshot.png`
   - Or: `./snapshots/roulette_table.png`

### Step 2: Run the Script

**Option A: Pass image as argument**
```bash
python capture_even_odd_from_snapshot_simple.py snapshot.png
```

**Option B: Run and enter path when prompted**
```bash
python capture_even_odd_from_snapshot_simple.py
# Then when prompted, enter: snapshot.png
```

### Step 3: Wait for Window to Open

After pressing Enter, a window will open showing:
- Your snapshot image
- Instructions at the top
- Status bar at the bottom
- Control buttons

### Step 4: Click on PAR Button (Even)

1. **Look at the image** in the window
2. **Find the "Par" button** on the betting table
3. **Click on the center** of the "Par" button
4. **Green marker appears** - this confirms the click
5. **Status updates** to show coordinate was captured

### Step 5: Click on ÍMPAR Button (Odd)

1. **Find the "Ímpar" button** on the betting table
2. **Click on the center** of the "Ímpar" button
3. **Blue marker appears** - this confirms the click
4. **Status updates** to show both coordinates captured

### Step 6: Save and Exit

1. **Check the status bar** - it should say " Both captured!"
2. **Click "Save & Exit" button** (green button at bottom)
3. **Window closes** automatically
4. **Coordinates are saved** to `even_odd_coordinates.json`

## What You'll See

### Window Layout:
```
┌─────────────────────────────────────────────┐
│ Click on PAR button (Even), then ÍMPAR... │ ← Instructions
├─────────────────────────────────────────────┤
│                                             │
│         [Your Snapshot Image]               │
│                                             │
│    [Green marker] = PAR clicked            │
│    [Blue marker] = ÍMPAR clicked           │
│                                             │
├─────────────────────────────────────────────┤
│ Ready - Click on PAR button                │ ← Status
├─────────────────────────────────────────────┤
│ [Reset Even] [Reset Odd] [Save & Exit]     │ ← Buttons
└─────────────────────────────────────────────┘
```

### Status Messages:

**Step 1 - Capturing Even:**
```
Status: "Click on PAR button (Even) - Coordinates will appear here"
```

**Step 2 - Capturing Odd:**
```
Status: "Click on ÍMPAR button (Odd) - Coordinates will appear here"
```

**Step 3 - Both Captured:**
```
Status: " Both captured! Even: [x, y], Odd: [x, y] - Click 'Save & Exit'"
```

## Controls

### Buttons:
- **Reset Even** - Remove Even coordinate and capture again
- **Reset Odd** - Remove Odd coordinate and capture again
- **Save & Exit** - Save coordinates and close window

### Mouse:
- **Click** - Capture coordinate at click position
- **Green marker** - Shows where Even (Par) was clicked
- **Blue marker** - Shows where Odd (Ímpar) was clicked

## Example Session

```bash
$ python capture_even_odd_from_snapshot_simple.py game_snapshot.png

======================================================================
EVEN/ODD COORDINATE CAPTURE FROM SNAPSHOT
======================================================================

Image: game_snapshot.png

Instructions:
  1. A window will open showing your snapshot
  2. Click on the PAR button (Even)
  3. Click on the ÍMPAR button (Odd)
  4. Click 'Save & Exit' when done

Press Enter to start...
[Press Enter]

[Window opens]

[Click on PAR button]
   Captured EVEN: [1100, 904]

[Click on ÍMPAR button]
   Captured ODD: [1170, 906]

[Click Save & Exit]

======================================================================
COORDINATES SAVED
======================================================================

Saved to: E:\...\even_odd_coordinates.json

Coordinates:
  EVEN (Par): [1100, 904]
  ODD (Ímpar): [1170, 906]

======================================================================
CONFIG SNIPPET
======================================================================

Add this to your config file:
"betting": {
  "betting_areas": {
    // ... existing entries ...
    "even": [1100, 904],
    "odd": [1170, 906],
  },
}
```

## Troubleshooting

### Problem: Window doesn't open

**Solution:**
- Make sure tkinter is installed (comes with Python)
- Check if image path is correct
- Try running: `python -c "import tkinter; print('OK')"`

### Problem: Can't see the image clearly

**Solution:**
- The window is resizable - drag corners to make it bigger
- Image auto-scales to fit window
- Try maximizing the window

### Problem: Clicked wrong spot

**Solution:**
- Click "Reset Even" or "Reset Odd" button
- Click again on the correct spot
- Markers will update

### Problem: Image path not found

**Solution:**
- Use full path: `C:\full\path\to\image.png`
- Or put image in same folder as script
- Check file extension (.png, .jpg, etc.)

### Problem: "Pillow not found" error

**Solution:**
```bash
pip install Pillow
```

## Tips

1. **Click center of button:** Aim for the center of "Par" and "Ímpar" buttons
2. **Check markers:** Green/blue markers show where you clicked
3. **Use Reset if needed:** If you click wrong spot, use Reset button
4. **Maximize window:** Make window bigger to see image clearly
5. **Verify before saving:** Check status bar shows both coordinates

## Output Files

After saving, you'll get:

1. **`even_odd_coordinates.json`** - Contains coordinates:
   ```json
   {
     "even": [1100, 904],
     "odd": [1170, 906]
   }
   ```

2. **Config snippet** - Shown in terminal, ready to copy

## Next Steps

After capturing:

1.  Open your config file (e.g., `config/default_config.json`)
2.  Find `"betting_areas"` section
3.  Add the coordinates:
   ```json
   "betting_areas": {
     "red": [970, 904],
     "black": [1040, 906],
     "even": [1100, 904],    // ← Add this
     "odd": [1170, 906]      // ← Add this
   }
   ```
4.  Save config file
5.  Test with bot

## Quick Reference

```bash
# Basic usage
python capture_even_odd_from_snapshot_simple.py image.png

# With full path
python capture_even_odd_from_snapshot_simple.py "C:\Users\You\Desktop\snapshot.png"

# Interactive mode
python capture_even_odd_from_snapshot_simple.py
# Then enter: image.png
```

## Requirements

- Python 3.x
- Pillow: `pip install Pillow`
- Tkinter: Usually comes with Python (no install needed)

That's it! The script is simple and straightforward to use.

