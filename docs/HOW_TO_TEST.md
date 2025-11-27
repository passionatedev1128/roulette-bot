# How to Test with Video File

## Quick Command

```bash
python test_video.py your_video.mp4
```

Replace `your_video.mp4` with the path to your video file.

---

## What It Does

1. **Opens your video file**
2. **Processes each frame** and tries to detect roulette results
3. **Shows results in real-time**:
   -  or  for each frame
   - Detected number, color, confidence
4. **Saves results** to `test_results/` folder
5. **Shows summary** at the end with detection rate

---

## Example Usage

### Basic Test (All Frames)
```bash
python test_video.py roulette_video.mp4
```

### Faster Test (Every 5th Frame)
```bash
python test_video.py roulette_video.mp4 --skip 5
```

### Custom Config File
```bash
python test_video.py roulette_video.mp4 --config config/my_config.json
```

---

## Interactive Controls

While the video is playing:
- **`q`** - Quit and save results
- **`s`** - Save current frame as image
- **`p`** - Pause/resume processing

---

## What You'll See

```
Frame 1/1200 (1 processed) 
  Number: 17
  Color: black
  Zero: False
  Confidence: 0.95
  Method: template

Frame 2/1200 (2 processed) 
  Number: 3
  Color: red
  Zero: False
  Confidence: 0.92
  Method: template
```

At the end:
```
Detection rate: 90.00%
```

**Good**: >90% detection rate means ready for live use
**Needs work**: <70% means you need to calibrate

---

## Results Saved

After testing, check:
- `test_results/test_results_TIMESTAMP.json` - All detection results
- `test_results/frame_X.png` - Frames you saved (if you pressed 's')

---

## Tips

1. **First time?** Use `--skip 5` to process faster
2. **Low detection rate?** Create number templates (see VIDEO_TESTING_GUIDE.md)
3. **Wrong colors?** Adjust color ranges in config
4. **Save frames** with 's' key to analyze problematic frames

---

## Full Guide

See `VIDEO_TESTING_GUIDE.md` for detailed instructions, troubleshooting, and best practices.

