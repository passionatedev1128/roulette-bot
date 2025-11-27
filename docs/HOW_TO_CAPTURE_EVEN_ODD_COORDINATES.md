# How to Capture Even/Odd Betting Coordinates

This guide explains how to capture the screen coordinates for Even and Odd betting areas on the roulette table.

## Quick Start

1. **Run the capture script:**
   ```bash
   python capture_even_odd_coordinates.py
   ```

2. **Follow the on-screen instructions:**
   - Move your mouse to the Even betting area
   - Press Enter after the countdown
   - Repeat for Odd betting area

3. **Add coordinates to config:**
   - Open your config file
   - Add the coordinates to `betting_areas` section

## Step-by-Step Instructions

### Step 1: Prepare the Game Window

1. Open the roulette game in your browser
2. Make sure the betting table is fully visible
3. Don't minimize or cover the game window
4. The Even and Odd betting areas should be visible on the table

### Step 2: Run the Capture Script

```bash
python capture_even_odd_coordinates.py
```

You'll see:
```
======================================================================
EVEN/ODD BETTING COORDINATE CAPTURE
======================================================================

Instructions:
  1. Make sure the roulette betting table is visible.
  2. You will be prompted for Even and Odd betting areas.
  ...
```

### Step 3: Capture Even Coordinates

1. **Move your mouse** to the center of the **Even** betting area
   - This is typically a button or area labeled "Even" or "Par" (Portuguese)
   - Hover over the center/clickable area

2. **Press Enter** to start the countdown

3. **Keep the mouse steady** during the 5-second countdown
   - The script shows live coordinates: `5... cursor at [x, y]`
   - Don't move the mouse!

4. **After countdown**, coordinates are captured automatically

### Step 4: Capture Odd Coordinates

1. **Move your mouse** to the center of the **Odd** betting area
   - This is typically a button or area labeled "Odd" or "Ímpar" (Portuguese)
   - Hover over the center/clickable area

2. **Press Enter** to start the countdown

3. **Keep the mouse steady** during the countdown

4. **After countdown**, coordinates are captured

### Step 5: Review and Save

The script will:
- Save coordinates to `even_odd_coordinates.json`
- Display the coordinates
- Show you how to add them to your config

## Adding Coordinates to Config

### Option 1: Manual Edit

1. Open your config file (e.g., `config/default_config.json`)

2. Find the `betting_areas` section:
   ```json
   {
     "betting": {
       "betting_areas": {
         "red": [970, 904],
         "black": [1040, 906],
         // ... other entries ...
       }
     }
   }
   ```

3. Add the Even/Odd coordinates:
   ```json
   {
     "betting": {
       "betting_areas": {
         "red": [970, 904],
         "black": [1040, 906],
         "even": [x, y],    // Add your Even coordinates here
         "odd": [x, y],     // Add your Odd coordinates here
         // ... other entries ...
       }
     }
   }
   ```

4. Save the file

### Option 2: Use the Output File

The script saves coordinates to `even_odd_coordinates.json`:
```json
{
  "even": [x, y],
  "odd": [x, y]
}
```

You can copy these values directly into your config file.

## Finding Even/Odd Betting Areas

### Common Locations

Even/Odd betting areas are typically located:

1. **On the main betting table:**
   - Usually near the number grid
   - Labeled "Even" / "Par" or "Odd" / "Ímpar"
   - May be buttons or clickable areas

2. **In a side panel:**
   - Some tables have side panels with betting options
   - Look for Even/Odd buttons there

3. **Near Red/Black areas:**
   - Sometimes grouped with color betting options
   - Check around Red/Black betting areas

### Visual Guide

```
Roulette Table Layout (example):
┌─────────────────────────────────────┐
│  [Numbers Grid: 0-36]              │
│                                     │
│  [Red] [Black] [Even] [Odd]        │  ← Betting areas
│                                     │
│  [Confirm Button]                   │
└─────────────────────────────────────┘
```

### Tips for Finding the Right Spot

- **Hover test:** Move mouse around - if it highlights or shows a tooltip, that's the area
- **Click test:** Click the area - if it selects Even/Odd, that's correct
- **Center point:** Aim for the center of the button/area, not the edge
- **Multiple monitors:** Make sure you're capturing on the correct monitor

## Troubleshooting

### Problem: Coordinates seem wrong

**Solution:**
- Make sure you're hovering over the center of the betting area
- Check that the game window is not minimized or covered
- Try capturing again with the mouse more precisely positioned

### Problem: Can't find Even/Odd areas

**Solution:**
- Check if the table uses different labels (Par/Ímpar in Portuguese)
- Look for buttons with "E" or "O" symbols
- Check if Even/Odd betting is available on your table
- Some tables may not have Even/Odd betting - verify with the game

### Problem: Script crashes or freezes

**Solution:**
- Make sure `pyautogui` is installed: `pip install pyautogui`
- Check that you have permission to control the mouse
- Try running as administrator (Windows) or with sudo (Linux/Mac)

### Problem: Coordinates don't work when betting

**Solution:**
- Verify coordinates are correct (run capture again)
- Check if the game window position changed
- Make sure screen resolution hasn't changed
- Test manually: Move mouse to those coordinates and click

## Testing the Coordinates

After adding coordinates to your config:

1. **Test manually:**
   ```python
   import pyautogui
   import time
   
   # Test Even
   even_coords = [x, y]  # Your Even coordinates
   pyautogui.moveTo(even_coords[0], even_coords[1])
   time.sleep(1)
   pyautogui.click()
   
   # Test Odd
   odd_coords = [x, y]  # Your Odd coordinates
   pyautogui.moveTo(odd_coords[0], odd_coords[1])
   time.sleep(1)
   pyautogui.click()
   ```

2. **Test with bot:**
   - Run the bot in test mode
   - Watch if it clicks the correct areas
   - Check logs for any coordinate errors

## Example Config

Here's a complete example with Even/Odd coordinates:

```json
{
  "betting": {
    "betting_areas": {
      "0": [786, 825],
      "1": [818, 858],
      // ... numbers 2-36 ...
      "red": [970, 904],
      "black": [1040, 906],
      "even": [1100, 904],
      "odd": [1170, 906]
    },
    "confirm_button": [1044, 949],
    "chip_selection": [1309, 947]
  }
}
```

## Next Steps

After capturing coordinates:

1.  Add to config file
2.  Test coordinates manually
3.  Test with bot in test mode
4.  Verify Even/Odd bets are placed correctly
5.  Run full strategy test

## Notes

- **Coordinate format:** `[x, y]` where x is horizontal, y is vertical
- **Screen resolution:** Coordinates are absolute screen positions
- **Multiple monitors:** Coordinates are relative to primary monitor
- **Window position:** If game window moves, coordinates may need updating

