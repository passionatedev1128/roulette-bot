# What Are Coordinates and Why Capture Them?

## What Are Coordinates?

**Coordinates** are pixel positions on your screen, represented as **[X, Y]**.

- **X** = horizontal position (left to right)
- **Y** = vertical position (top to bottom)

**Example:** `[500, 400]` means:
- 500 pixels from the left edge
- 400 pixels from the top edge

---

## Why Do We Need Coordinates?

The bot needs to know **exactly where** to click on your screen to:
- Click the **RED betting button**
- Click the **BLACK betting button**
- Click the **CONFIRM button**
- Detect the **winning number** location

Without coordinates, the bot doesn't know where these elements are on your screen!

---

## Visual Example

```
Screen (1920x1080 example):
┌─────────────────────────────────────────────────┐
│ 0,0                                            │
│                                                 │
│         ┌─────────┐                            │
│         │ RED     │  ← This is at [500, 400]  │
│         │ BUTTON  │                            │
│         └─────────┘                            │
│                                                 │
│         ┌─────────┐                            │
│         │ BLACK   │  ← This is at [600, 400]  │
│         │ BUTTON  │                            │
│         └─────────┘                            │
│                                                 │
│         ┌─────────┐                            │
│         │ CONFIRM │  ← This is at [550, 500]  │
│         └─────────┘                            │
│                                                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## What Coordinates You Need to Capture

### 1. Red Betting Button
- **What:** The button/area where you click to bet on RED
- **Why:** Bot needs to click here to place red bets
- **Example:** `[500, 400]`

### 2. Black Betting Button
- **What:** The button/area where you click to bet on BLACK
- **Why:** Bot needs to click here to place black bets
- **Example:** `[600, 400]`

### 3. Confirm Button
- **What:** The button that confirms/places your bet
- **Why:** Bot needs to click here to finalize the bet
- **Example:** `[550, 500]`

### 4. Number Display Center (Optional but Recommended)
- **What:** Center of where the winning number appears
- **Why:** Helps focus detection on the right area
- **Example:** `[960, 300]`

### 5. Green/Zero Button (If Your Game Has It)
- **What:** Button to bet on green/zero
- **Why:** For zero betting if needed
- **Example:** `[550, 350]`

---

## How to Capture Coordinates

### Method 1: Using the Coordinate Capture Tool (Easiest)

**Step 1: Run the tool**
```bash
python coordinate_capture_tool.py
```

**Step 2: Follow instructions**
1. Tool will ask you to move mouse to RED button
2. Move your mouse to the RED betting button
3. Wait 5 seconds
4. Tool captures the coordinates automatically
5. Repeat for BLACK, CONFIRM, etc.

**Step 3: Tool saves coordinates**
- Saves to `game_coordinates.json`
- Shows you the coordinates
- Generates config snippet for you

**This is the EASIEST method!**

---

### Method 2: Manual Method (Python Script)

**Step 1: Create a script**
```python
import pyautogui
import time

print("Move mouse to RED button and wait 5 seconds...")
time.sleep(5)
red_x, red_y = pyautogui.position()
print(f"Red button: [{red_x}, {red_y}]")

print("\nMove mouse to BLACK button and wait 5 seconds...")
time.sleep(5)
black_x, black_y = pyautogui.position()
print(f"Black button: [{black_x}, {black_y}]")

print("\nMove mouse to CONFIRM button and wait 5 seconds...")
time.sleep(5)
confirm_x, confirm_y = pyautogui.position()
print(f"Confirm button: [{confirm_x}, {confirm_y}]")
```

**Step 2: Run the script**
- Move mouse to each location
- Script captures coordinates
- Copy coordinates to config

---

### Method 3: Using Screenshot Tools

**Step 1: Take screenshot of game**
- Use Windows Snipping Tool, or
- Use Print Screen, or
- Use any screenshot tool

**Step 2: Open in image editor**
- Paint, GIMP, Photoshop, etc.

**Step 3: Find coordinates**
- Hover over button location
- Check pixel coordinates (usually shown at bottom)
- Note the X, Y values

**Example in Paint:**
- Hover over button
- Bottom shows: "X: 500, Y: 400"
- That's your coordinate: `[500, 400]`

---

## Where Coordinates Go in Config

After capturing, update your config file:

```json
{
  "betting": {
    "betting_areas": {
      "red": [500, 400],      // ← Your captured coordinates
      "black": [600, 400],    // ← Your captured coordinates
      "green": [550, 350]     // ← Your captured coordinates (if needed)
    },
    "confirm_button": [550, 500]  // ← Your captured coordinates
  }
}
```

---

## Important Notes

### 1. Screen Resolution Matters
- Coordinates are **absolute pixel positions**
- If you change screen resolution, coordinates change
- Use same resolution for capture and running

### 2. Game Window Position Matters
- If game window moves, coordinates may be wrong
- Keep game window in same position
- Or use relative coordinates (more advanced)

### 3. Accuracy Matters
- Click the **center** of the button
- Not the edge, not nearby
- Center gives best click accuracy

### 4. Test Coordinates
After capturing, **always test**:
```bash
python coordinate_capture_tool.py test
```
This moves mouse to each coordinate so you can verify they're correct.

---

## Step-by-Step: Capture Coordinates

### Quick Steps:

1. **Open your roulette game**
   - Make sure it's visible on screen
   - Game window should be in normal position

2. **Run coordinate capture tool**
   ```bash
   python coordinate_capture_tool.py
   ```

3. **For each target:**
   - Read the prompt (e.g., "Move mouse to RED button")
   - Move mouse to the target location
   - Wait 5 seconds
   - Coordinates are captured automatically

4. **Verify coordinates**
   ```bash
   python coordinate_capture_tool.py test
   ```
   - Mouse moves to each coordinate
   - Verify it's pointing at the correct button

5. **Update config file**
   - Copy coordinates from output
   - Paste into `config/default_config.json`

---

## Example: Complete Capture Process

### What You'll See:

```
======================================================================
COORDINATE CAPTURE TOOL
======================================================================

Move your mouse to RED betting button NOW...
You have 5 seconds...
  5... 4... 3... 2... 1...
  Capturing coordinates...
   Captured: [500, 400]

======================================================================
Target: BLACK betting button
======================================================================

Move your mouse to BLACK betting button NOW...
You have 5 seconds...
  5... 4... 3... 2... 1...
  Capturing coordinates...
   Captured: [600, 400]

... (and so on)

======================================================================
COORDINATES SAVED
======================================================================

Saved to: game_coordinates.json

Captured coordinates:
  red_bet_button: [500, 400]
  black_bet_button: [600, 400]
  confirm_button: [550, 500]
```

---

## Common Questions

### Q: Why do I need coordinates?
**A:** The bot needs to know exactly where to click. Without coordinates, it can't place bets.

### Q: What if I get wrong coordinates?
**A:** Run the tool again and capture them correctly. Then test with `python coordinate_capture_tool.py test`

### Q: Do coordinates change?
**A:** Only if you change screen resolution or move the game window. Keep them the same.

### Q: Can I use relative coordinates?
**A:** The current bot uses absolute coordinates. Relative coordinates would require code changes.

### Q: What if my game has different buttons?
**A:** Capture whatever buttons your game uses. The config supports custom button locations.

---

## Visual Guide

### Finding Coordinates on Screen:

```
Your Screen:
┌────────────────────────────────────────┐
│                                        │
│  [0,0]  ← Top-left corner             │
│    │                                    │
│    │    X increases                   │
│    │                                    │
│    ↓                                    │
│  Y increases                           │
│                                        │
│         ┌─────┐                        │
│         │ RED │ ← [500, 400]           │
│         └─────┘                        │
│                                        │
│         ┌───────┐                      │
│         │ BLACK │ ← [600, 400]        │
│         └───────┘                      │
│                                        │
│         ┌────────┐                     │
│         │CONFIRM │ ← [550, 500]       │
│         └────────┘                     │
│                                        │
└────────────────────────────────────────┘
```

---

## Summary

**"Capture coordinates" means:**
1. Finding the exact pixel positions of betting buttons
2. Using a tool to record those positions
3. Saving them to your config file
4. So the bot knows where to click

**It's like giving the bot a map of where everything is on your screen!**

---

## Quick Start

**To capture coordinates right now:**

```bash
# Run the tool
python coordinate_capture_tool.py

# Follow the prompts
# Move mouse to each button
# Wait 5 seconds each time

# Test coordinates
python coordinate_capture_tool.py test

# Update config file with captured coordinates
```

**That's it! The tool does everything for you.**

---

## Need Help?

If you have trouble:
1. Make sure game window is visible
2. Move mouse to center of button (not edge)
3. Wait full 5 seconds
4. Test coordinates after capture
5. Verify in config file

**The coordinate capture tool makes this easy - just follow the prompts!**

