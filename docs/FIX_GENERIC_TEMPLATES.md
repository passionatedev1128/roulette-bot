# Fix Generic Templates (7 and 9)

## Problem

**Templates 7 and 9 are too generic:**
- Match even when NO numbers are present
- Match background/patterns instead of actual numbers
- Cause false positives

**Also:**
- Detection is matching the betting grid (all numbers visible)
- Should only match the winning number display area

---

## Solution 1: Fix Templates 7 and 9

### Step 1: Identify Problematic Templates

**Run analysis:**
```bash
python fix_generic_templates.py analyze
```

**This will show:**
- Which templates have issues (low fill, low variance, too large)
- Characteristics of each template
- Recommendations

### Step 2: Recreate Templates 7 and 9

**The problem:** Templates are too generic (include too much background or are too large)

**Solution:** Recreate from betting grid snapshot

```bash
python create_templates_from_grid.py betting_grid.png
```

**When cropping:**
- **For number 7:**
  - Select ONLY the number 7
  - Include minimal background (2-5 pixels)
  - Don't include surrounding elements
  - Make it the same size as other templates

- **For number 9:**
  - Select ONLY the number 9
  - Include minimal background (2-5 pixels)
  - Don't include surrounding elements
  - Make it the same size as other templates

**Important:**
- Templates should be similar in size
- Should only include the number, not background patterns
- Should match the actual number display area, not betting grid

### Step 3: Test Templates

**Test on blank image (no numbers):**
```bash
python fix_generic_templates.py test 7 blank_screen.png
python fix_generic_templates.py test 9 blank_screen.png
```

**Should show:**
- Low confidence (< 0.5) on blank image
- If high confidence (> 0.75), template is still too generic

---

## Solution 2: Fix Detection Area

### Problem: Matching Betting Grid Instead of Result Display

**The detection is matching the betting grid (where all numbers are visible) instead of the winning number display area.**

### Fix: Set Correct Screen Region

**File:** `config/default_config.json`

**Update:**
```json
{
  "detection": {
    "screen_region": [x, y, width, height]
  }
}
```

**Important:**
- `screen_region` should point to **winning number display area** (center video area)
- NOT the betting grid (bottom area)
- Should be small region where only ONE number appears at a time

**How to find it:**
1. Use coordinate tool to find number display area
2. Or take screenshot and identify where winning number appears
3. Set region to that area only

**Example:**
```json
{
  "detection": {
    "screen_region": [883, 390, 200, 300]  // Adjust to your number display area
  }
}
```

---

## Solution 3: Improved Detection Logic

**Already fixed in code:**
- Now checks if too many templates match (> 5)
- If many templates match, likely matching betting grid  reject
- Better validation to prevent false positives

---

## Step-by-Step Fix

### Step 1: Analyze Templates

```bash
python fix_generic_templates.py analyze
```

**Check output:**
- Which templates are problematic
- Characteristics of templates 7 and 9

### Step 2: Recreate Templates 7 and 9

```bash
python create_templates_from_grid.py betting_grid.png
```

**When cropping:**
- Select ONLY the number (not background)
- Make it same size as other templates
- Include minimal border (2-5 pixels)

### Step 3: Verify Screen Region

**Check config:** `config/default_config.json`

**Make sure `screen_region` points to:**
- Winning number display area (center)
- NOT betting grid (bottom)
- Small region (200x300 or similar)

**If wrong:**
- Use coordinate tool to find correct area
- Update config

### Step 4: Test Detection

```bash
python test_video.py roleta_brazileria.mp4
```

**Check:**
-  No detection when no numbers present
-  Only detects actual winning number
-  Doesn't detect from betting grid

---

## Why Templates 7 and 9 Are Generic

**Possible reasons:**

1. **Too large:**
   - Includes too much background
   - Matches patterns in background

2. **Low variance:**
   - Template is too uniform
   - Matches many different patterns

3. **Wrong source:**
   - Created from wrong area
   - Includes betting grid elements

4. **Background included:**
   - Template includes background patterns
   - Those patterns exist everywhere

---

## How to Create Good Templates

**Best practices:**

1. **Crop from winning number display area** (not betting grid)
2. **Select ONLY the number** (minimal background)
3. **Consistent size** (all templates similar size)
4. **Same source** (all from same snapshot)
5. **Clear and sharp** (not blurry)

**Example good template:**
- Size: 40-60 pixels wide, 50-80 pixels tall
- Includes: Just the number + 2-5 pixel border
- Source: Winning number display area

**Example bad template:**
- Size: 100+ pixels (too large)
- Includes: Background patterns, surrounding elements
- Source: Betting grid (wrong area)

---

## Testing After Fix

**Test 1: Blank image (no numbers)**
```bash
python fix_generic_templates.py test 7 blank_screen.png
python fix_generic_templates.py test 9 blank_screen.png
```

**Should show:** Low confidence (< 0.5)

**Test 2: Video with numbers**
```bash
python test_video.py roleta_brazileria.mp4
```

**Should show:**
-  Detects actual winning numbers
-  No false positives
-  Doesn't match betting grid

---

## Summary

**To fix:**

1. **Recreate templates 7 and 9:**
   - Use `create_templates_from_grid.py`
   - Crop carefully (only number, minimal background)
   - Make same size as other templates

2. **Set correct screen_region:**
   - Point to winning number display area
   - NOT betting grid
   - Small region (200x300)

3. **Test:**
   - Test on blank image (should not match)
   - Test on video (should detect correctly)

**The code is already improved to reject when too many templates match (betting grid detection).**

---

**Start by recreating templates 7 and 9 - that's the main fix!**

