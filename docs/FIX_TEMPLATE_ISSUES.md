# Fix Template Detection Issues

## Problems Identified

1. **Templates from different frames** - Should be from single betting grid snapshot
2. **False positives** - Detecting numbers when none exist (e.g., number 1 with 0.9 confidence)

---

## Solution 1: Create Templates from Single Grid Snapshot

### Why This is Better

 **Consistent styling** - All numbers from same image  
 **Reduces false positives** - Same font, size, colors  
 **More accurate** - Templates match actual game display  

### How to Do It

**Step 1: Take a screenshot of your betting grid**

1. Open your roulette game
2. Make sure betting grid is visible (showing all numbers 0-36)
3. Take a screenshot
4. Save as `betting_grid.png` (or any name)

**Step 2: Extract templates from the snapshot**

```bash
python create_templates_from_grid.py betting_grid.png
```

**Step 3: Select each number**

- Tool shows the betting grid image
- For each number (0-36):
  - Find the number on the grid
  - Click and drag to select JUST that number
  - Press 's' to save
  - Press 'n' for next number
  - Press 'd' for previous number

**This ensures all templates are from the same source!**

---

## Solution 2: Fix False Positives

### Changes Made

1. **Increased confidence threshold:**
   - **Before:** 0.5 (too low, causes false positives)
   - **After:** 0.75 (higher threshold, fewer false positives)

2. **Better validation:**
   - Only accepts matches with confidence ≥ 0.75
   - Logs when confidence is too low

### How It Works Now

```python
# Old (too permissive):
best_confidence = 0.5  # Accepts weak matches

# New (stricter):
best_confidence = 0.75  # Only accepts strong matches
if best_confidence >= 0.75:
    return best_match  # Only return if confident
```

---

## Step-by-Step Fix

### Option A: Recreate Templates (Recommended)

**1. Take betting grid screenshot:**
- Open game
- Show betting grid with all numbers
- Take screenshot
- Save as `betting_grid.png`

**2. Extract templates:**
```bash
python create_templates_from_grid.py betting_grid.png
```

**3. Select all numbers (0-36):**
- Use interactive tool
- Select each number from the grid
- Save all templates

**4. Test detection:**
```bash
python test_video.py roleta_brazileria.mp4
```

**5. Check results:**
- Should have fewer false positives
- Better accuracy

---

### Option B: Adjust Confidence Threshold

**If you want to keep existing templates:**

**1. Update config:**
```json
{
  "detection": {
    "template_confidence_threshold": 0.75
  }
}
```

**2. Test again:**
```bash
python test_video.py roleta_brazileria.mp4
```

**Note:** This helps, but templates from single snapshot is still better!

---

## Why False Positives Happen

### Problem:
- Templates from different video frames
- Different lighting, angles, sizes
- Template matches random parts of frame
- Low threshold (0.5) accepts weak matches

### Solution:
- Templates from same image = consistent
- Higher threshold (0.75) = only strong matches
- Better validation = fewer errors

---

## Testing After Fix

**Run detection test:**
```bash
python test_video.py roleta_brazileria.mp4
```

**Check for:**
-  No false positives (detecting numbers when none exist)
-  Higher accuracy
-  Better confidence scores

**Expected improvement:**
- Before: False positives (number 1 with 0.9 when no number)
- After: No detection when no number present

---

## Summary

**To fix both issues:**

1. **Recreate templates from single grid snapshot:**
   ```bash
   python create_templates_from_grid.py betting_grid.png
   ```

2. **Confidence threshold already fixed** (0.75 instead of 0.5)

3. **Test detection:**
   ```bash
   python test_video.py roleta_brazileria.mp4
   ```

**This should eliminate false positives!** 

