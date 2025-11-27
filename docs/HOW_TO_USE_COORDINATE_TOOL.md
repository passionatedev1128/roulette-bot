# How to Use Coordinate Capture Tool - Simple Guide

## Important: You DON'T Need All 36 Numbers!

**You only need to capture 2-3 coordinates:**
1.  **Red (Vermelho) betting area** - ONE coordinate
2.  **Black (Preto) betting area** - ONE coordinate
3.  **Confirm button** (if needed) - ONE coordinate

**You DO NOT need to capture all 36 numbers!**

---

## What You're Looking For

### On Your Betting Grid (Bottom Center):

Look for betting AREAS, not individual numbers:

```
Betting Grid:
┌─────────────────────────────┐
│  [VERMELHO]  [PRETO]  [0]   │ ← These are the AREAS
│                             │
│  [Numbers 1-36 in grid]     │ ← You DON'T need these
└─────────────────────────────┘
```

**What to capture:**
-  **VERMELHO area** (the entire red betting box/area)
-  **PRETO area** (the entire black betting box/area)
-  **NOT individual numbers** (1, 2, 3, etc.)

---

## Step-by-Step: Using the Tool

### Step 1: Open Your Game

1. Open your Brazilian roulette game
2. Make sure the betting grid is visible
3. Keep the game window open and visible

### Step 2: Run the Tool

```bash
python coordinate_capture_tool.py
```

### Step 3: Follow the Prompts

**The tool will ask you for each target one by one:**

#### Prompt 1: "Move mouse to RED betting button"
1. **Look at your betting grid** (bottom center)
2. **Find "Vermelho" area** (red betting box/area)
3. **Move your mouse** to the CENTER of that area
4. **Keep mouse still** - wait 5 seconds
5. Tool captures automatically - you'll see: ` Captured: [500, 400]`

#### Prompt 2: "Move mouse to BLACK betting button"
1. **Look at your betting grid** (bottom center)
2. **Find "Preto" area** (black betting box/area)
3. **Move your mouse** to the CENTER of that area
4. **Keep mouse still** - wait 5 seconds
5. Tool captures automatically - you'll see: ` Captured: [600, 400]`

#### Prompt 3: "Move mouse to GREEN betting button"
- **Press Ctrl+C** to skip if you don't need it
- OR move mouse to Zero area if you want to capture it

#### Prompt 4: "Move mouse to CONFIRM button"
- **If your game has auto-confirm:** Press Ctrl+C to skip
- **If you need confirm button:** Move mouse to confirm button and wait

#### Prompt 5: "Move mouse to amount input field"
- **Press Ctrl+C** to skip (usually not needed)

### Step 4: Done!

The tool will:
- Save coordinates to `game_coordinates.json`
- Show you all captured coordinates
- Generate config snippet for you

---

## Visual Example

### What You're Looking For:

```
Your Game Screen:
┌─────────────────────────────────────┐
│                                     │
│         Live Video                  │
│                                     │
├─────────────────────────────────────┤
│  Betting Grid (Bottom Center)      │
│                                     │
│  ┌──────────┐  ┌──────────┐        │
│  │ VERMELHO │  │  PRETO   │        │
│  │  (Red)   │  │ (Black)  │        │
│  └──────────┘  └──────────┘        │
│      ↑              ↑              │
│   Move mouse     Move mouse        │
│   here for      here for           │
│   RED button    BLACK button       │
│                                     │
│  [Numbers 1-36 arranged below]     │
│  (You DON'T need these!)            │
└─────────────────────────────────────┘
```

---

## Common Questions

### Q: Do I need to capture all 36 numbers?
**A: NO!** You only need the Red (Vermelho) and Black (Preto) betting AREAS, not individual numbers.

### Q: What if I don't see "Vermelho" or "Preto" areas?
**A:** Then click on a representative red number (like 17) and black number (like 18) on the grid. The bot will click those specific numbers.

### Q: How do I know where to move the mouse?
**A:** 
- Look for "Vermelho" (Red) text/area on the betting grid
- Look for "Preto" (Black) text/area on the betting grid
- Move mouse to the CENTER of that area

### Q: What if I move mouse to wrong place?
**A:** No problem! You can run the tool again. Or you can test coordinates later with:
```bash
python coordinate_capture_tool.py test
```

### Q: How long do I wait?
**A:** The tool counts down: 5... 4... 3... 2... 1... Just keep mouse still during countdown.

---

## Complete Example Session

```
You run: python coordinate_capture_tool.py

Tool shows:
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

======================================================================
Target: GREEN betting button (press Ctrl+C to skip)
======================================================================

(You press Ctrl+C to skip)

======================================================================
Target: CONFIRM button
======================================================================

(You press Ctrl+C to skip - auto-confirm game)

======================================================================
COORDINATES SAVED
======================================================================

Saved to: game_coordinates.json

Captured coordinates:
  red_bet_button: [500, 400]
  black_bet_button: [600, 400]
```

**That's it! Only 2 coordinates needed!**

---

## After Capturing

### Step 1: Test Coordinates

```bash
python coordinate_capture_tool.py test
```

This will move your mouse to each coordinate so you can verify they're correct.

### Step 2: Update Config

Copy the coordinates into your config file:

```json
{
  "betting": {
    "betting_areas": {
      "red": [500, 400],      // From captured coordinates
      "black": [600, 400]     // From captured coordinates
    }
  }
}
```

---

## Troubleshooting

### Problem: "I don't see Vermelho/Preto areas"
**Solution:** 
- Look for red-colored boxes/areas on the grid
- OR use a red number (like 17) as the coordinate
- OR use a black number (like 18) as the coordinate

### Problem: "Tool says wrong coordinates"
**Solution:**
- Run the tool again
- Make sure mouse is on the CENTER of the button/area
- Test coordinates after capture

### Problem: "I don't understand the prompts"
**Solution:**
- Just move mouse to the target location
- Wait 5 seconds
- Tool does everything automatically
- Press Ctrl+C to skip if you don't need that target

---

## Summary

**You need to capture:**
-  **1 coordinate** for Red (Vermelho area)
-  **1 coordinate** for Black (Preto area)
-  **Total: 2 coordinates** (not 36!)

**How to use tool:**
1. Run: `python coordinate_capture_tool.py`
2. Move mouse to target
3. Wait 5 seconds
4. Repeat for next target
5. Done!

**That's it - simple!**

