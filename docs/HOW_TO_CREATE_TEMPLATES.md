# How to Create Number Templates - Step by Step

## Why Templates Are Important

**Templates improve detection accuracy significantly!**

-  More reliable than OCR for stylized fonts
-  Works even with different lighting
-  Faster detection
-  Better accuracy (often 90%+)

---

## Quick Start (3 Steps)

### Step 1: Extract Frames from Video

```bash
python create_templates_from_video.py extract roleta_brazileria.mp4
```

**What this does:**
- Extracts frames from your video
- Saves them to `template_frames/` directory
- You'll get ~50 frames to work with

**Output:**
```
template_frames/
  frame_00030.png
  frame_00060.png
  frame_00090.png
  ...
```

---

### Step 2: Interactive Cropping

```bash
python create_templates_from_video.py crop
```

**What this does:**
- Shows you frames one by one
- You select each number (0-36) by drawing a rectangle
- Saves cropped numbers as templates

**How to use:**
1. Tool shows a frame from video
2. **Click and drag** to select the number area
3. Press **'s'** to save
4. Press **'n'** to go to next number (increases)
5. Press **'d'** to go to previous number (decreases)
6. Press **'f'** to show next frame
7. Press **'q'** to quit

**Note:** The window stays open when navigating between numbers!

**Example:**
```
[1/37] Creating template for number: 0
  Showing frame 1/50
  Instructions:
    - Click and drag to select the number
    - Press 's' to save
    - Press 'n' to skip this number
    - Press 'f' to show next frame
    - Press 'q' to quit
```

---

### Step 3: Verify Templates

```bash
python create_templates_from_video.py verify
```

**What this does:**
- Checks if all 37 templates (0-36) exist
- Verifies they're valid images
- Shows which ones are missing

**Output:**
```
 number_0.png: 45x60 pixels, 2.3 KB
 number_1.png: 45x60 pixels, 2.1 KB
...
 number_36.png: 45x60 pixels, 2.4 KB

 All templates valid and ready!
```

---

## Detailed Instructions

### Step 1: Extract Frames

**Command:**
```bash
python create_templates_from_video.py extract roleta_brazileria.mp4
```

**Options:**
- Default: Extracts every 30th frame, max 50 frames
- To extract more frames:
  ```bash
  python create_templates_from_video.py extract roleta_brazileria.mp4 template_frames 10 100
  ```
  - `10` = process every 10th frame (more frames)
  - `100` = extract up to 100 frames

**What to look for:**
- Frames where numbers are clearly visible
- Different numbers (0, 1, 17, 36, etc.)
- Good lighting/contrast

---

### Step 2: Create Templates (Interactive)

**Command:**
```bash
python create_templates_from_video.py crop
```

**Process for each number (0-36):**

1. **Tool shows a frame**
   - Look for the number you need
   - If number not visible, press **'f'** for next frame

2. **Select the number**
   - **Click** where the number starts (top-left)
   - **Drag** to where it ends (bottom-right)
   - You'll see a green rectangle

3. **Save the template**
   - Press **'s'** to save
   - Template saved as `templates/number_X.png`

4. **Move to next number**
   - Tool automatically moves to next number
   - Repeat for all 37 numbers (0-36)

**Tips:**
-  Select just the number, not background
-  Include a small border around the number
-  Make sure number is clear and not blurry
-  If number looks bad, press **'f'** for next frame

**Keyboard shortcuts:**
- **'s'** = Save current selection
- **'n'** = Next number (increases, window stays open)
- **'d'** = Previous number (decreases, window stays open)
- **'f'** = Show next frame (for current number)
- **'q'** = Quit (saves progress)

---

### Step 3: Verify

**Command:**
```bash
python create_templates_from_video.py verify
```

**What it checks:**
-  All 37 templates exist (0-36)
-  Templates are valid images
-  Shows size and dimensions

**If templates are missing:**
- Run `crop` command again
- It will skip existing templates
- Only create missing ones

---

## Alternative: Manual Method

If interactive tool doesn't work, you can create templates manually:

### 1. Extract Frames
```bash
python create_templates_from_video.py extract roleta_brazileria.mp4
```

### 2. Open Frames in Image Editor
- Open `template_frames/` folder
- Use any image editor (Paint, GIMP, Photoshop, etc.)

### 3. Crop Each Number
- For each number (0-36):
  - Find a frame showing that number
  - Crop just the number area
  - Save as `templates/number_X.png`

### 4. Verify
```bash
python create_templates_from_video.py verify
```

---

## Template Requirements

**File naming:**
- Must be: `number_0.png`, `number_1.png`, ... `number_36.png`
- Location: `templates/` directory

**Image requirements:**
-  PNG format (recommended)
-  Clear, not blurry
-  Just the number (minimal background)
-  Consistent size (recommended, but not required)

**Size recommendations:**
- Width: 30-100 pixels
- Height: 40-120 pixels
- Doesn't have to be exact, but similar sizes work better

---

## Troubleshooting

### Problem: "No frame files found"
**Solution:**
- Run extract command first:
  ```bash
  python create_templates_from_video.py extract roleta_brazileria.mp4
  ```

### Problem: "Can't see numbers in frames"
**Solution:**
- Extract more frames with smaller skip:
  ```bash
  python create_templates_from_video.py extract roleta_brazileria.mp4 template_frames 10 200
  ```
- This extracts every 10th frame, up to 200 frames

### Problem: "Template not matching correctly"
**Solution:**
- Make sure you crop just the number
- Include a small border (2-5 pixels)
- Try different frames for the same number
- Ensure good contrast

### Problem: "Interactive tool not working"
**Solution:**
- Use manual method instead
- Extract frames, then crop manually in image editor

---

## After Creating Templates

### 1. Update Config

Make sure your config uses template matching:

```json
{
  "detection": {
    "method": "template",  // or "ocr", "hybrid"
    "template_dir": "templates",
    "screen_region": [x, y, width, height]
  }
}
```

### 2. Test Detection

```bash
python test_video.py roleta_brazileria.mp4
```

**Expected improvement:**
- Detection accuracy should increase
- More reliable number detection
- Faster processing

---

## Complete Workflow Example

```bash
# Step 1: Extract frames
python create_templates_from_video.py extract roleta_brazileria.mp4

# Step 2: Create templates (interactive)
python create_templates_from_video.py crop

# Step 3: Verify
python create_templates_from_video.py verify

# Step 4: Test detection
python test_video.py roleta_brazileria.mp4

# Step 5: Check accuracy
python analyze_results.py
```

---

## Time Estimate

**Creating all 37 templates:**
- Interactive method: 15-30 minutes
- Manual method: 30-60 minutes

**Worth it?**
-  Yes! Templates significantly improve accuracy
-  One-time setup
-  Can reuse templates for future videos

---

## Summary

**3 Simple Steps:**

1. **Extract:** `python create_templates_from_video.py extract <video>`
2. **Crop:** `python create_templates_from_video.py crop`
3. **Verify:** `python create_templates_from_video.py verify`

**That's it!** You'll have templates ready for accurate detection! 

