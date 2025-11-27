# Quick Coordinate Guide - 2 Minutes

## You Only Need 2 Coordinates!

**NOT 36 numbers - just 2 areas:**

1.  Red (Vermelho) betting area
2.  Black (Preto) betting area

---

## How to Use the Tool (Super Simple)

### Step 1: Run the Tool
```bash
python coordinate_capture_tool.py
```

### Step 2: For RED Button
- Tool says: "Move mouse to RED betting button"
- **You:** Look at betting grid, find "Vermelho" area
- **You:** Move mouse to center of that area
- **You:** Wait 5 seconds (don't move mouse!)
- **Tool:** Captures automatically 

### Step 3: For BLACK Button
- Tool says: "Move mouse to BLACK betting button"
- **You:** Look at betting grid, find "Preto" area
- **You:** Move mouse to center of that area
- **You:** Wait 5 seconds
- **Tool:** Captures automatically 

### Step 4: Skip Others
- For Green/Confirm/Amount: Press **Ctrl+C** to skip
- (Most games don't need these)

### Step 5: Done!
- Tool saves coordinates
- Shows you what was captured
- Done!

---

## What You're Looking For

**On betting grid (bottom center):**

```
┌─────────────┬─────────────┐
│  VERMELHO   │    PRETO    │  ← These 2 areas!
│   (Red)     │   (Black)   │
└─────────────┴─────────────┘
```

**Move mouse to:**
- Center of VERMELHO box
- Center of PRETO box

**That's it! Only 2 places!**

---

## Example

```
Tool: "Move mouse to RED betting button"
You: [Move mouse to Vermelho area]
You: [Wait 5 seconds]
Tool: " Captured: [500, 400]"

Tool: "Move mouse to BLACK betting button"
You: [Move mouse to Preto area]
You: [Wait 5 seconds]
Tool: " Captured: [600, 400]"

Tool: "Move mouse to GREEN button"
You: [Press Ctrl+C to skip]

Done! Only 2 coordinates captured.
```

---

## Important Notes

-  **DON'T capture all 36 numbers**
-  **DO capture the 2 betting areas** (Vermelho and Preto)
-  **Move mouse to CENTER of the area**
-  **Wait 5 seconds without moving**
-  **Press Ctrl+C to skip if not needed**

---

**That's it! Super simple - just 2 coordinates!**

