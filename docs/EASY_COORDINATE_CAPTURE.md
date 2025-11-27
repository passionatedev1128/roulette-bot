# Easy Coordinate Capture - 2 Minutes

## Based on Your Screenshot

I've analyzed your game. Here's the **simplest way** to capture coordinates:

---

## Step 1: Open Your Game

1. Open **LUCK.BET Roleta Brasileira**
2. Make sure the game window is visible
3. You should see:
   - Live video (roulette wheel) at top
   - **Betting grid** at bottom center

---

## Step 2: Run the Tool

```bash
python coordinate_capture_tool.py
```

---

## Step 3: Capture Coordinates

### Target 1: VERMELHO (Red) Area

**Tool says:** "Move mouse to VERMELHO (Red) betting area"

**What to do:**
1. Look at your **betting grid** (bottom center)
2. Find the **"Vermelho"** betting area/box
   - It might say "Vermelho" or "Red"
   - OR it's a red-colored betting box
   - It's on the betting grid, separate from numbers
3. **Move mouse** to the **CENTER** of that area
4. **Wait 5 seconds** (don't move mouse!)
5. Tool captures: ` Captured: [x, y]`

### Target 2: PRETO (Black) Area

**Tool says:** "Move mouse to PRETO (Black) betting area"

**What to do:**
1. Look at your **betting grid** (bottom center)
2. Find the **"Preto"** betting area/box
   - It might say "Preto" or "Black"
   - OR it's a black-colored betting box
   - It's on the betting grid, separate from numbers
3. **Move mouse** to the **CENTER** of that area
4. **Wait 5 seconds** (don't move mouse!)
5. Tool captures: ` Captured: [x, y]`

### Skip Others

For all other prompts (Number display, Green, Confirm, Chip):
- **Press Ctrl+C** to skip
- Most games don't need these

---

## What You're Looking For

Based on your game screenshot:

### Betting Grid Layout:

```
Betting Grid (Bottom Center):
┌─────────────────────────────────────┐
│  [Number Grid: 0-36]                │
│                                     │
│  [Outside Betting Areas]            │
│  ┌─────────────┬─────────────┐    │
│  │  VERMELHO   │    PRETO     │    │ ← These 2 areas!
│  │   (Red)     │   (Black)    │    │
│  └─────────────┴─────────────┘    │
│  [1-18] [PAR] [ÍMPAR] [19-36]     │
└─────────────────────────────────────┘
```

**Look for:**
-  "Vermelho" or "Red" betting box/area
-  "Preto" or "Black" betting box/area

**These are OUTSIDE bets** (not individual numbers 1-36)

---

## Complete Example

```
You run: python coordinate_capture_tool.py

Tool: "Move mouse to VERMELHO (Red) betting area"
You: [Look at betting grid, find Vermelho area]
You: [Move mouse to center of Vermelho box]
You: [Wait 5 seconds - don't move!]
Tool: " Captured: [650, 550]"

Tool: "Move mouse to PRETO (Black) betting area"
You: [Look at betting grid, find Preto area]
You: [Move mouse to center of Preto box]
You: [Wait 5 seconds - don't move!]
Tool: " Captured: [750, 550]"

Tool: "Move mouse to Number display..."
You: [Press Ctrl+C to skip]

Done! Only 2 coordinates captured!
```

---

## After Capturing

The tool will:
1.  Save coordinates to `game_coordinates.json`
2.  Show you what was captured
3.  Give you config snippet to copy

**That's it! Only 2 clicks needed!**

---

## Troubleshooting

### Q: I don't see "Vermelho" or "Preto" areas
**A:** Look for:
- Red-colored betting boxes/areas
- Black-colored betting boxes/areas
- OR click on a representative red number (like 17) and black number (like 18)

### Q: Where exactly should I click?
**A:** The **CENTER** of the betting area/box, not the edge

### Q: What if I click wrong place?
**A:** No problem! Run the tool again, or test coordinates after with:
```bash
python coordinate_capture_tool.py test
```

---

## Summary

**You need:** 2 coordinates (Vermelho and Preto betting areas)

**How to capture:**
1. Run: `python coordinate_capture_tool.py`
2. Move mouse to Vermelho area  Wait 5 seconds
3. Move mouse to Preto area  Wait 5 seconds
4. Press Ctrl+C for others
5. Done!

**Total time: ~30 seconds!**

---

**Remember: You DON'T need all 36 numbers - just 2 betting areas!**

