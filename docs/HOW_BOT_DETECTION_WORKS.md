# How Bot Detection Actually Works

## 🔍 Clarification: Desktop Screen Capture, NOT Browser UI

**Important:** The bot detects by taking **screenshots of your desktop**, not by accessing the browser's internal structure (DOM).

---

## 📸 How It Actually Works

### Method: Desktop Screen Capture

```
┌─────────────────────────────────────┐
│  Your Desktop Screen                │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  Browser Window              │   │
│  │  (Showing Roulette Game)     │   │
│  │                              │   │
│  │  ┌──────────────┐            │   │
│  │  │  Winning: 17 │  ← Bot     │   │
│  │  └──────────────┘    captures│   │
│  │                              │   │
│  └──────────────────────────────┘   │
│                                      │
│  Bot takes screenshot of this area   │
│  (pyautogui.screenshot)             │
└─────────────────────────────────────┘
```

**What the bot does:**
1. Takes a screenshot of your desktop using `pyautogui.screenshot()`
2. Extracts a small region (e.g., `[953, 511, 57, 55]` pixels)
3. Analyzes the image using:
   - Template matching (compares with saved number images)
   - OCR (reads numbers from image)
4. Detects the winning number from the image

**What the bot does NOT do:**
-  Access browser's DOM (HTML structure)
-  Use browser extensions
-  Inject JavaScript
-  Access browser's internal APIs
-  Read browser's memory

---

## 🖥️ Desktop Screen Capture Explained

### Step-by-Step Process

**1. Bot Takes Screenshot:**
```python
# In screen_detector.py
screenshot = pyautogui.screenshot(region=[953, 511, 57, 55])
# This captures a 57x55 pixel region of your desktop
```

**What this captures:**
- Whatever is displayed on your screen at those coordinates
- If browser is showing the game at that location  captures browser content
- If something else is there  captures that instead
- It's just a picture of your screen!

**2. Bot Analyzes Image:**
```python
# Convert to OpenCV format
frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

# Try template matching
result = detect_winning_number_template(frame)

# Or try OCR
result = detect_number_ocr(frame)
```

**3. Bot Gets Number:**
- Template matching: Compares image with saved templates (0.png, 1.png, etc.)
- OCR: Reads numbers from the image using pytesseract/EasyOCR
- Returns detected number

---

## 🆚 Comparison: Desktop Capture vs Browser UI

### Desktop Screen Capture (What Bot Uses) 

**How it works:**
- Takes screenshot of desktop
- Analyzes the image
- Works with any application (browser, video player, etc.)

**Pros:**
-  Works with any game (browser, desktop app, etc.)
-  No browser-specific code needed
-  Works even if game is in video player
-  Simple and universal

**Cons:**
-  Requires accurate screen coordinates
-  Affected by window position/zoom
-  Slower than DOM access (but still fast enough)

**Code:**
```python
screenshot = pyautogui.screenshot(region=[x, y, w, h])
# Just takes a picture!
```

### Browser UI/DOM Access (What Bot Does NOT Use) 

**How it would work:**
- Access browser's DOM (HTML structure)
- Read element values directly
- Use browser extensions/APIs

**Pros:**
-  More reliable (direct access)
-  Faster (no image processing)
-  Not affected by screen position

**Cons:**
-  Requires browser-specific code
-  May need browser extensions
-  Only works with web games
-  More complex implementation

**Code (if it did this - but it doesn't):**
```javascript
// This is NOT what the bot does
const winningNumber = document.querySelector('.winning-number').textContent;
```

---

##  Why Desktop Capture?

### 1. **Universal Approach**
- Works with any game display method
- Browser, desktop app, video player - all the same
- No special setup needed

### 2. **Simple Implementation**
- Just takes screenshots
- No browser integration needed
- No extensions required

### 3. **Works Everywhere**
- Same code works on Windows, Mac, Linux
- Works with any browser (Chrome, Firefox, Edge, etc.)
- Works even if game is in a video

---

## 📋 What This Means

### For You:

** What You Need:**
- Browser window showing the game
- Window positioned where bot expects it
- Screen region configured correctly
- Templates that match what's displayed

** Important:**
- Browser window position matters
- Zoom level matters (should be 100%)
- Screen resolution matters
- Window must be visible (not minimized)

** What You DON'T Need:**
- Browser extensions
- Special browser setup
- JavaScript injection
- DOM access permissions

---

## 🔧 How It Actually Works (Technical)

### Detection Flow

```
1. Bot calls: detector.capture_screen()
   ↓
2. pyautogui.screenshot(region=[953, 511, 57, 55])
   ↓
3. Takes screenshot of desktop at those coordinates
   ↓
4. Converts to OpenCV image format
   ↓
5. Extracts region of interest (ROI)
   ↓
6. Tries template matching:
   - Compares ROI with saved templates (0.png, 1.png, ...)
   - Finds best match
   ↓
7. If no match, tries OCR:
   - Uses pytesseract/EasyOCR to read numbers
   - Extracts digits from image
   ↓
8. Returns detected number
```

### Example: Detecting Number 17

```
Desktop Screen:
┌─────────────────────────────────┐
│ Browser Window                  │
│ ┌─────────────────────────────┐ │
│ │ Roulette Game               │ │
│ │                             │ │
│ │  Winning: 17  ← This area   │ │
│ │  [953, 511, 57, 55]         │ │
│ │                             │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘

Bot captures this region:
┌──────────┐
│    17    │  ← 57x55 pixel image
└──────────┘

Bot compares with templates:
- 0.png  No match
- 1.png  No match
- ...
- 17.png  Match! (confidence: 0.85)

Bot returns: 17
```

---

## 🎬 Real-World Example

### Scenario: Game in Browser

**Setup:**
1. You open roulette game in Chrome
2. Game shows winning number: "17"
3. Bot is configured with `screen_region: [953, 511, 57, 55]`

**What happens:**
1. Bot calls `pyautogui.screenshot(region=[953, 511, 57, 55])`
2. This captures whatever is at those screen coordinates
3. If browser window is at that position  captures "17" from browser
4. Bot analyzes the captured image
5. Bot detects: 17

**Key point:** Bot doesn't know or care it's a browser. It just sees pixels on your screen!

---

##  Important Implications

### 1. **Window Position Matters**

**If browser window moves:**
- Bot captures wrong area
- Detection fails
- Need to recalibrate coordinates

**Solution:**
- Keep browser window in fixed position
- Or use fullscreen mode
- Or recalibrate if window moves

### 2. **Zoom Level Matters**

**If browser zoom changes:**
- Numbers appear different size
- Templates don't match
- Detection fails

**Solution:**
- Always use 100% zoom (Ctrl+0)
- Don't change zoom after calibration

### 3. **Screen Resolution Matters**

**If resolution changes:**
- Coordinates become wrong
- Detection fails

**Solution:**
- Keep same resolution
- Or recalibrate if resolution changes

### 4. **Anything Can Be There**

**Bot captures whatever is at those coordinates:**
- If browser is there  captures browser
- If video player is there  captures video
- If another window is there  captures that
- Bot doesn't distinguish!

**Solution:**
- Make sure game is visible at configured coordinates
- Don't cover the area with other windows

---

##  Summary

**Bot Detection Method:**
-  **Desktop screen capture** (screenshot)
-  Takes picture of screen at specific coordinates
-  Analyzes image using template matching/OCR
-  Works with any display method (browser, video, etc.)

**Bot Does NOT:**
-  Access browser DOM
-  Use browser extensions
-  Inject JavaScript
-  Access browser APIs

**Key Point:**
- Bot sees your screen as pixels, not as browser content
- It's like taking a photo and analyzing it
- Browser is just one way to display the game

**Why This Matters:**
- Window position/zoom/resolution affect detection
- But it works universally (browser, video, desktop app)
- Simple and reliable approach

---

**The bot detects via desktop screen capture, not browser UI!** 📸

