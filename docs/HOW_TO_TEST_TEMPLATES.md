# How to Test Number Templates with Snapshot

## Quick Test

**Test your templates on a snapshot:**

```bash
python test_templates_with_snapshot.py <your_snapshot.png>
```

**Example:**
```bash
python test_templates_with_snapshot.py betting_grid.png
python test_templates_with_snapshot.py game_screenshot.png
```

---

## What This Test Does

1.  **Loads your snapshot image**
2.  **Tests all templates** (0-36) against the image
3.  **Shows confidence scores** for each template
4.  **Displays best match** with visualization
5.  **Saves results** to JSON file

---

## What You'll See

### Detection Results
```
 Number detected: 17
  Color: black
  Confidence: 0.85
  Method: template
```

### All Template Matches
```
 Number  0: confidence = 0.234
 Number  1: confidence = 0.189
 Number 17: confidence = 0.852  ← Best match!
 Number 18: confidence = 0.623
```

### Top Matches
```
Best matches (sorted by confidence):
  1. Number 17: 0.852 -  ACCEPTED
  2. Number 18: 0.623 -  REJECTED (too low)
  3. Number 16: 0.512 -  REJECTED (too low)
```

### Visualization
- Opens image window
- Shows green rectangle around detected number
- Displays number and confidence
- Press any key to close

---

## What to Check

###  Good Results
- **Best match confidence ≥ 0.75** - Detection accepted
- **Only one high-confidence match** - No ambiguity
- **Correct number detected** - Matches what you see in image

###  Issues to Watch For

1. **Multiple high-confidence matches:**
   - Templates might be too similar
   - Need to recreate templates

2. **Confidence too low (< 0.75):**
   - Templates don't match snapshot
   - Need to recreate templates from this snapshot

3. **No matches found:**
   - Templates don't match image
   - Wrong templates for this game
   - Need to recreate templates

4. **Wrong number detected:**
   - Templates are incorrect
   - Need to recreate templates

---

## Step-by-Step Testing

### Step 1: Prepare Snapshot

**Option A: Use betting grid snapshot**
- Take screenshot of betting grid
- Save as `betting_grid.png`
- This is what you used to create templates

**Option B: Use game screenshot**
- Take screenshot during game
- Should show a number result
- Save as `game_screenshot.png`
- Test if templates work on actual game

### Step 2: Run Test

```bash
python test_templates_with_snapshot.py betting_grid.png
```

### Step 3: Review Results

**Check:**
-  Best match confidence ≥ 0.75
-  Correct number detected
-  Only one high-confidence match

### Step 4: Fix Issues (If Needed)

**If confidence too low:**
- Recreate templates from this snapshot
- Use: `python create_templates_from_grid.py <snapshot>`

**If multiple matches:**
- Templates might be too similar
- Make sure templates are cropped correctly
- Only include the number, minimal background

**If wrong number:**
- Templates are incorrect
- Recreate templates

---

## Example Workflow

### Test 1: Test on Betting Grid (Template Source)

```bash
# Test on the same image you used to create templates
python test_templates_with_snapshot.py betting_grid.png
```

**Expected:**
- Should detect numbers correctly
- High confidence scores
- Multiple numbers might match (since all are visible)

### Test 2: Test on Game Screenshot

```bash
# Test on actual game screenshot
python test_templates_with_snapshot.py game_screenshot.png
```

**Expected:**
- Should detect the winning number
- High confidence for correct number
- Low confidence for others

---

## Understanding Confidence Scores

**Confidence Range:**
- **0.0 - 0.5:** Very weak match (likely false positive)
- **0.5 - 0.75:** Weak match (rejected)
- **0.75 - 0.85:** Good match (accepted)
- **0.85 - 1.0:** Excellent match (accepted)

**Threshold:**
- **Current threshold: 0.75**
- Only matches ≥ 0.75 are accepted
- This prevents false positives

---

## Troubleshooting

### Problem: "No templates found"
**Solution:**
```bash
# Create templates first
python create_templates_from_grid.py betting_grid.png
```

### Problem: "Confidence too low"
**Solution:**
- Templates don't match the snapshot
- Recreate templates from this snapshot:
  ```bash
  python create_templates_from_grid.py <snapshot>
  ```

### Problem: "Multiple high-confidence matches"
**Solution:**
- Templates might be too similar
- Make sure templates are cropped correctly
- Only include the number, not background

### Problem: "Wrong number detected"
**Solution:**
- Templates are incorrect
- Recreate templates carefully
- Make sure you select the correct number

---

## Summary

**Quick test:**
```bash
python test_templates_with_snapshot.py <snapshot.png>
```

**What it shows:**
- Which templates match
- Confidence scores
- Best match
- Visualization

**What to check:**
- Confidence ≥ 0.75
- Correct number detected
- Only one high-confidence match

**If issues:**
- Recreate templates from snapshot
- Use: `python create_templates_from_grid.py <snapshot>`

---

**This test helps you verify your templates work correctly!** 

