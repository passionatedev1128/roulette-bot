# Fix: Only Number 7 Detected Issue

## Problem

The bot is only detecting number 7, even when:
- There are no numbers in the frame
- All 37 numbers are visible
- Different numbers are shown

---

## Root Cause

**Bug in template matching logic:**

1. **Wrong initialization:** Started with `best_confidence = 0.75` (threshold) instead of `0.0`
2. **No second-best check:** Didn't verify if best match is significantly better
3. **Number 7 template might be too generic:** Could match everything

---

## Fixes Applied

### 1. Fixed Template Matching Logic

**Before (buggy):**
```python
best_confidence = 0.75  # Wrong! Starts with threshold
if max_val > best_confidence:  # Only updates if > 0.75
    best_confidence = max_val
    best_match = num
```

**After (fixed):**
```python
best_confidence = -1.0  # Start low to find actual best
second_best_confidence = -1.0  # Track second best

# Find best match
if max_val > best_confidence:
    second_best_confidence = best_confidence
    best_confidence = max_val
    best_match = num

# Validate at end
if best_confidence >= 0.75:  # Check threshold
    if (best_confidence - second_best_confidence) >= 0.1:  # Check difference
        return best_match
```

### 2. Added Ambiguity Check

Now checks if best match is significantly better than second best:
- If difference < 0.1  Reject (too ambiguous)
- Prevents false positives when multiple templates match

### 3. Added Screen Region Support

Now uses `screen_region` from config if specified:
- Only searches in the number display area
- Reduces false matches from betting grid

---

## How to Diagnose

**Run diagnostic tool:**

```bash
python diagnose_template_issue.py <your_image.png>
```

**This will show:**
- All template matches with confidence scores
- Which templates are matching
- If number 7 is always winning
- If best match is too close to second best

---

## Possible Issues

### Issue 1: Number 7 Template Too Generic

**Symptoms:**
- Number 7 always wins
- Number 7 matches everything
- Confidence is high but wrong

**Solution:**
1. Check template: `templates/number_7.png`
2. Is it too large? (includes too much background)
3. Does it match patterns in the image?
4. Recreate template from betting grid snapshot

### Issue 2: Templates Too Similar

**Symptoms:**
- Multiple templates match with similar confidence
- Ambiguity detected

**Solution:**
1. Make sure templates are cropped correctly
2. Only include the number, minimal background
3. Recreate from single grid snapshot

### Issue 3: Wrong Screen Region

**Symptoms:**
- Detecting numbers from betting grid instead of result display
- Multiple numbers match

**Solution:**
1. Set `screen_region` in config to number display area
2. Use coordinate tool to find number display location

---

## Testing After Fix

**Test with video:**
```bash
python test_video.py roleta_brazileria.mp4
```

**What to check:**
-  Detects different numbers (not just 7)
-  No detection when no number present
-  Correct numbers detected
-  No false positives

---

## Step-by-Step Fix

### Step 1: Run Diagnostic

```bash
python diagnose_template_issue.py betting_grid.png
```

**Check output:**
- Is number 7 always winning?
- Is confidence difference too small?
- Are multiple templates matching?

### Step 2: Check Number 7 Template

**Open:** `templates/number_7.png`

**Check:**
- Is it too large? (should be just the number)
- Does it include background? (should be minimal)
- Is it different from other templates?

**If problematic:**
- Recreate from betting grid snapshot
- Use: `python create_templates_from_grid.py betting_grid.png`

### Step 3: Verify Screen Region

**Check config:** `config/default_config.json`

```json
{
  "detection": {
    "screen_region": [x, y, width, height]
  }
}
```

**Make sure:**
- Region covers number display area (not betting grid)
- Region is correct size
- Use coordinate tool if needed

### Step 4: Test Again

```bash
python test_video.py roleta_brazileria.mp4
```

**Should now:**
- Detect different numbers correctly
- Not detect when no number present
- Have better accuracy

---

## Summary

**Fixes applied:**
1.  Fixed template matching logic (find best, then validate)
2.  Added ambiguity check (reject if too close)
3.  Added screen region support

**Next steps:**
1. Run diagnostic tool
2. Check number 7 template
3. Verify screen region
4. Test again

**The code is fixed - now verify your templates are correct!**

