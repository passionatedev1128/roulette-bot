# Game Interface Analysis - Brazilian Roulette

## Interface Overview

Based on your game screenshot, this is a **live Brazilian roulette** game with a betting grid interface.

---

## Button Locations

### 1. Red Betting

**Important:** This game doesn't have a simple "RED" button. Instead, you have **two options**:

#### Option A: Click Red Numbers on Grid
- **Location:** Bottom center - roulette betting grid
- **What to click:** Individual red numbers (1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36)
- **Coordinates:** Need to capture for each red number OR find a red color betting area

#### Option B: Red Color Betting Area (If Available)
- **Location:** Possibly in the betting grid area as "Vermelho" (Red in Portuguese)
- **Look for:** A red-colored betting box or area
- **Coordinates:** Need to capture this location

**Recommendation:** Look for a "Vermelho" or red-colored betting area on the grid. If it exists, that's easier than clicking individual numbers.

---

### 2. Black Betting

**Similar to red:**

#### Option A: Click Black Numbers on Grid
- **Location:** Bottom center - roulette betting grid
- **What to click:** Individual black numbers (2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35)
- **Coordinates:** Need to capture for each black number OR find black color betting area

#### Option B: Black Color Betting Area (If Available)
- **Location:** Possibly in the betting grid area as "Preto" (Black in Portuguese)
- **Look for:** A black-colored betting box or area
- **Coordinates:** Need to capture this location

**Recommendation:** Look for a "Preto" or black-colored betting area on the grid.

---

### 3. Confirm Button

**Important:** The green checkmark button at bottom right is the **"JOGO AUTOMÁTICO" (Automatic Play)** button, NOT the confirm button!

**How betting works in this game:**
- **Option A: Auto-Confirm** - Bets may be placed automatically when you click on the betting grid (no separate confirm needed)
- **Option B: Separate Confirm** - There may be a different confirm button elsewhere
- **Option C: Timer-Based** - Bets may auto-confirm when betting timer ends

**You need to identify:**
1. Does clicking a number on the grid immediately place the bet? (No confirm needed)
2. Is there a separate "Confirm" or "Apostar" (Bet) button?
3. Do bets confirm automatically when the timer runs out?

**How to capture:**
1. Move mouse to the green checkmark button (bottom right)
2. Use coordinate capture tool to get exact position

---

## Chip Selection Area

**Location:** Bottom right
- **Chips visible:** 0.5, 1, 2.5, 5, 20, 50
- **Purpose:** Select bet amount before placing bet

**Note:** If your game requires selecting a chip first, you'll need coordinates for:
- Chip selection (e.g., the "5" chip)
- Then betting area
- Then confirm button

---

## Betting Grid Area

**Location:** Bottom center
- **Contains:** All roulette numbers (0-36) arranged in a grid
- **Red numbers:** Clickable on the grid
- **Black numbers:** Clickable on the grid
- **Green number:** 0 (zero)

---

## How to Adapt Bot for This Interface

### Option 1: Use Color Betting Areas (Easier)

If the game has "Vermelho" (Red) and "Preto" (Black) betting areas:

1. **Capture coordinates for:**
   - Vermelho (Red) betting area
   - Preto (Black) betting area
   - Confirm button (green checkmark)

2. **Update config:**
   ```json
   {
     "betting": {
       "betting_areas": {
         "red": [x, y],      // Vermelho area coordinates
         "black": [x, y],    // Preto area coordinates
         "green": [x, y]     // Zero area (if needed)
       },
       "confirm_button": [x, y],  // Green checkmark button
       "requires_chip_selection": true,  // If you need to select chip first
       "chip_selection": [x, y]   // Chip coordinates (e.g., "5" chip)
     }
   }
   ```

### Option 2: Click Individual Numbers (More Complex)

If you must click individual numbers:

1. **Capture coordinates for:**
   - Center of red number area (e.g., number 17)
   - Center of black number area (e.g., number 18)
   - Confirm button

2. **Bot will need to:**
   - Click on a red number on the grid
   - Or click on a black number on the grid
   - Then confirm

---

## Step-by-Step: Find Your Buttons

### Step 1: Identify Red Betting Area

**Look for:**
- A red-colored box/area labeled "Vermelho" or "Red"
- OR a prominent red number on the grid (like number 17)

**Use coordinate capture tool:**
```bash
python coordinate_capture_tool.py
```
When it asks for "RED betting button", move mouse to:
- The "Vermelho" area, OR
- A red number on the grid (center of the number)

### Step 2: Identify Black Betting Area

**Look for:**
- A black-colored box/area labeled "Preto" or "Black"
- OR a prominent black number on the grid (like number 18)

**Use coordinate capture tool:**
When it asks for "BLACK betting button", move mouse to:
- The "Preto" area, OR
- A black number on the grid (center of the number)

### Step 3: Identify Confirm Button

**Found it!** The green checkmark button at bottom right.

**Use coordinate capture tool:**
When it asks for "CONFIRM button", move mouse to:
- The green circular button with white checkmark (bottom right)

---

## Quick Reference: What to Look For

### Red Button
- **Look for:** "Vermelho" area OR red number on grid
- **Location:** Bottom center (betting grid area)
- **Color:** Red

### Black Button
- **Look for:** "Preto" area OR black number on grid
- **Location:** Bottom center (betting grid area)
- **Color:** Black

### Confirm Button
- **Found:** Green circular button with checkmark
- **Location:** Bottom right (near chip selection)
- **Color:** Green with white checkmark

---

## Special Considerations for This Game

### 1. Chip Selection (May Be Required)

If the game requires selecting a chip before betting:
- Capture coordinates for chip selection (e.g., "5" chip)
- Bot will need to: Select chip  Click bet area  Confirm

### 2. Betting Grid vs. Color Areas

**Best approach:** Find if there are dedicated "Vermelho" and "Preto" betting areas on the grid. These are easier than clicking individual numbers.

**If no color areas exist:**
- You'll need to click individual numbers
- Capture coordinates for a representative red number and black number
- Bot will click those specific numbers

### 3. Auto-Confirm Feature

**Note:** The description mentions "bets are confirmed automatically when the betting timer runs out". This means:
- You might not need a confirm button click
- But it's safer to have it in case

---

## Recommended Implementation

### Step 1: Examine Your Game Closely

1. **Open the game**
2. **Look for:**
   - "Vermelho" or red betting area
   - "Preto" or black betting area
   - Green checkmark button (bottom right)

### Step 2: Capture Coordinates

```bash
python coordinate_capture_tool.py
```

**For each:**
- Move mouse to red betting area/number
- Move mouse to black betting area/number
- Move mouse to green checkmark button

### Step 3: Test Coordinates

```bash
python coordinate_capture_tool.py test
```

Verify mouse moves to correct locations.

### Step 4: Update Config

Copy captured coordinates to config file.

---

## Visual Guide Based on Description

```
Game Screen Layout:
┌─────────────────────────────────────────────────┐
│ Top Navigation Bar                              │
├─────────────┬───────────────────┬──────────────┤
│ Left Panel  │  Live Video Feed  │              │
│ (Limits &   │  (Roulette Wheel) │              │
│  Payments)  │                   │              │
│             │                   │              │
│ Vermelho/   │                   │              │
│ Preto: 1:1  │                   │              │
├─────────────┴───────────────────┴──────────────┤
│ Betting Grid (Bottom Center)                   │
│  [Red Numbers] [Black Numbers] [0]            │
│  OR                                            │
│  [Vermelho] [Preto] [0]                        │
├─────────────────────────────────────────────────┤
│ Controls: DESFAZER DOBRAR JOGO AUTOMÁTICO      │
├─────────────────────────────────────────────────┤
│ Chips: 0.5  1  2.5  5  20  50  [] ← Confirm  │
└─────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Run coordinate capture tool:**
   ```bash
   python coordinate_capture_tool.py
   ```

2. **For RED button:**
   - Look for "Vermelho" area on betting grid
   - OR use a red number (like 17)
   - Capture its center coordinates

3. **For BLACK button:**
   - Look for "Preto" area on betting grid
   - OR use a black number (like 18)
   - Capture its center coordinates

4. **For CONFIRM button:**
   - Green checkmark button (bottom right)
   - Capture its center coordinates

5. **Test coordinates:**
   ```bash
   python coordinate_capture_tool.py test
   ```

---

## Important Notes

- **No simple "Red" and "Black" buttons** - This game uses a betting grid
- **Look for color betting areas** - "Vermelho" and "Preto" areas would be ideal
- **Confirm button is the green checkmark** - Bottom right, near chips
- **May need chip selection** - If required, capture chip coordinates too

---

**Run the coordinate capture tool now and I'll help you identify the exact locations!**

