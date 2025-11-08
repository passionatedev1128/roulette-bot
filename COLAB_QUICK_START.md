# Colab Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### Step 1: Open Colab
Go to: https://colab.research.google.com/
Click "New notebook"

### Step 2: Upload Notebook
1. Click "File" → "Upload notebook"
2. Upload `roulette_bot_test.ipynb` from this project
3. OR copy-paste the cells manually

### Step 3: Run Setup Cells
1. Run the first cell (install dependencies)
2. Run the upload cell (upload your video file)
3. Run the test cell

### Step 4: View Results
- Check detection rate
- View sample frames
- Download results JSON

---

## 📋 Manual Setup (If No Notebook)

### Cell 1: Install Dependencies
```python
!pip install opencv-python numpy pytesseract Pillow PyYAML pandas imutils -q
```

### Cell 2: Upload Video
```python
from google.colab import files
uploaded = files.upload()
video_file = list(uploaded.keys())[0]
```

### Cell 3: Run Test
```python
# Copy the test function from roulette_bot_test.ipynb
# Then run:
results = test_video_colab(video_file, config, frame_skip=5, max_frames=100)
```

---

## ⚙️ Configuration

### Adjust Test Parameters:

```python
results = test_video_colab(
    video_file,
    config,
    frame_skip=5,      # Process every 5th frame (1 = all frames)
    max_frames=100     # Limit to 100 frames (None = all frames)
)
```

### For Faster Testing:
- Increase `frame_skip` (e.g., 10 = every 10th frame)
- Decrease `max_frames` (e.g., 50 = only first 50 frames)

### For Thorough Testing:
- Set `frame_skip=1` (all frames)
- Set `max_frames=None` (all frames)

---

## 📊 Understanding Results

### Detection Rate
- **>90%**: Excellent - Ready for use
- **70-90%**: Good - May need minor calibration
- **<70%**: Needs improvement

### What Gets Tested
✅ Number detection (OCR)  
✅ Color detection  
✅ Zero detection  
❌ Betting automation (not available in Colab)

---

## 💡 Tips

1. **Start Small**: Test with 50-100 frames first
2. **Check Confidence**: Look at confidence scores
3. **Save Results**: Download JSON for analysis
4. **Visual Check**: Use sample frame display
5. **Adjust Config**: Modify color ranges if needed

---

## 🔧 Troubleshooting

### "Video file not found"
- Make sure you uploaded the file in the upload cell
- Check filename matches

### "Module not found"
- Run the install cell again
- Restart runtime: Runtime → Restart runtime

### "Low detection rate"
- Try different frame_skip values
- Check video quality
- Adjust color ranges in config

### "Out of memory"
- Reduce max_frames
- Increase frame_skip
- Use GPU runtime: Runtime → Change runtime type → GPU

---

## 📁 Files You'll Need

1. **Video file**: `roleta_brazileria.mp4` (or your video)
2. **Config file**: `config/default_config.json` (optional, has default)

---

## 🎯 Next Steps After Testing

1. **If detection rate >90%**: 
   - ✅ Ready for local testing
   - Configure betting areas
   - Test with small bets

2. **If detection rate <90%**:
   - Create number templates
   - Adjust color ranges
   - Test again

3. **Download results**:
   - Use download cell to get JSON
   - Analyze on local machine
   - Share with team

---

## 📞 Need Help?

- Check `VIDEO_TESTING_GUIDE.md` for detailed info
- Review `roulette_bot_test.ipynb` for complete code
- Check Colab console for error messages

