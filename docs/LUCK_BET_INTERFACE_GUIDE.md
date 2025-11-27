# LUCK.BET Roleta Brasileira - Interface Guide

## Based on Your Screenshot Analysis

I've analyzed your game interface. Here's exactly where to find everything:

---

## Betting Areas Location

### Red (Vermelho) and Black (Preto) Betting Areas

**Location:** On the betting grid (below the roulette wheel video)

**What to look for:**
- **Outside betting boxes** on the betting grid
- These are separate from the number grid (0-36)
- Look for boxes labeled "Vermelho" or "Preto"
- OR colored betting boxes (red box, black box)

**According to your game's payout table:**
- "Vermelho/Preto" = 1:1 payout
- This confirms Red/Black betting areas exist

**Typical location on betting grid:**
```
Betting Grid Layout:
┌─────────────────────────────────┐
│  [Numbers 0-36 in grid]          │
│                                  │
│  [Outside Bets]                  │
│  ┌─────────┬─────────┐          │
│  │VERMELHO │  PRETO  │          │ ← Look here!
│  │  (Red)  │ (Black) │          │
│  └─────────┴─────────┘          │
│  [1-18] [PAR] [ÍMPAR] [19-36]   │
└─────────────────────────────────┘
```

---

## Chip Selection Area

**Location:** Bottom of screen (in a row)

**Chips available:** 0.5, 1, 2.5, 5, 20, 50

**What to capture:**
- Coordinates of the chip you want to use (usually minimum: 0.5 or 1)

---

## Number Display (For Detection)

**Location:** Center video area (where roulette wheel is shown)

**What to look for:**
- Winning number appears in the video area
- Usually displayed prominently when result is shown
- May be overlaid on the video or shown below it

---

## Step-by-Step: Capture Coordinates

### Option 1: Use Visual Helper (Recommended)

```bash
python visual_coordinate_helper.py
```

This tool will:
1. Take a screenshot
2. Guide you to mark areas
3. Help you capture coordinates step by step

### Option 2: Manual Capture

```bash
python coordinate_capture_tool.py
```

**For RED button:**
- Look at betting grid (bottom center)
- Find "Vermelho" betting box/area
- Move mouse to center of that box
- Wait 5 seconds

**For BLACK button:**
- Look at betting grid (bottom center)
- Find "Preto" betting box/area
- Move mouse to center of that box
- Wait 5 seconds

---

## What Your Game Has

Based on the screenshot:

 **Betting Grid** - Bottom center, with numbers 0-36
 **Outside Bets** - Including "Vermelho/Preto" (Red/Black)
 **Chip Selection** - 0.5, 1, 2.5, 5, 20, 50
 **Control Buttons** - DESFAZER, DOBRAR, JOGO AUTOMÁTICO
 **Number Display** - In center video area

---

## Important Notes

### 1. Red/Black Betting Areas
- These are OUTSIDE bets (not individual numbers)
- Located on the betting grid
- Separate from the number grid
- Look for labeled boxes or colored areas

### 2. Chip Selection May Be Required
- Your game might require selecting a chip first
- Then clicking betting area
- Capture chip coordinates if needed

### 3. Auto-Confirm Likely
- Most Brazilian roulette games auto-confirm bets
- No separate confirm button usually needed
- Bets place when you click the betting area

---

## Quick Capture Guide

**Run this:**
```bash
python visual_coordinate_helper.py
```

**Or manually:**
```bash
python coordinate_capture_tool.py
```

**You need to capture:**
1.  Vermelho (Red) betting area - ON BETTING GRID
2.  Preto (Black) betting area - ON BETTING GRID
3.  Chip (if required) - Bottom chip selection area

**Total: 2-3 coordinates only!**

---

## Visual Guide

Based on typical Brazilian roulette layout:

```
Your Game Screen:
┌──────────────────────────────────────┐
│  Live Video (Roulette Wheel)         │
│  [Number appears here when result]  │
├──────────────────────────────────────┤
│  Betting Grid (Bottom Center)         │
│                                      │
│  [Number Grid: 0-36]                 │
│                                      │
│  [Outside Bets]                      │
│  ┌──────────┐  ┌──────────┐        │
│  │VERMELHO  │  │  PRETO   │        │ ← Capture these!
│  │  (Red)   │  │ (Black)  │        │
│  └──────────┘  └──────────┘        │
│  [1-18] [PAR] [ÍMPAR] [19-36]      │
├──────────────────────────────────────┤
│  Chips: 0.5  1  2.5  5  20  50       │
└──────────────────────────────────────┘
```

---

## Next Steps

1. **Run the visual helper:**
   ```bash
   python visual_coordinate_helper.py
   ```

2. **Or use coordinate tool:**
   ```bash
   python coordinate_capture_tool.py
   ```

3. **Look for:**
   - Vermelho area on betting grid
   - Preto area on betting grid

4. **Capture coordinates** (2 clicks total)

5. **Done!**

---

**Remember: You only need 2 coordinates (Red and Black areas), not all 36 numbers!**

