# Quick Implementation Checklist

## Setup (5-10 minutes)

- [ ] Install Python 3.12+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Install Tesseract OCR (optional)
- [ ] Verify installation: `python check_setup.py`

## Configuration (15-20 minutes)

- [ ] Open `config/default_config.json`
- [ ] Set betting area coordinates (RED, BLACK, CONFIRM buttons) - **CRITICAL**
- [ ] Configure strategy (martingale/fibonacci/custom)
- [ ] Set base bet amount
- [ ] Set stop loss limit
- [ ] Configure maintenance bet interval (1800 seconds = 30 min)

## Testing (30-60 minutes)

- [ ] Test detection with video: `python test_video.py video.mp4`
- [ ] Verify detection rate >70% (ideally >90%)
- [ ] Test betting coordinates manually
- [ ] Create number templates (0-36) - **Recommended**

## Production (Ready to Run)

- [ ] Review all settings
- [ ] Test with minimum bets first
- [ ] Understand failsafe (mouse to corner)
- [ ] Monitor logs folder
- [ ] Run: `python main.py`

## Critical Items

**Must Do:**
1.  Set betting area coordinates
2.  Configure stop loss
3.  Test detection accuracy

**Highly Recommended:**
1.  Create number templates
2.  Set screen region
3.  Test with video first

## Quick Commands

```bash
# Install
pip install -r requirements.txt

# Test setup
python check_setup.py

# Test video
python test_video.py video.mp4

# Analyze results
python analyze_results.py test_results/results_*.json

# Run bot
python main.py
```

## Need Help?

- See `COMPLETE_IMPLEMENTATION_GUIDE.md` for detailed steps
- Check `IMPROVE_DETECTION_RATE.md` for accuracy issues
- Review `HOW_TO_ANALYZE_RESULTS.md` for analysis

