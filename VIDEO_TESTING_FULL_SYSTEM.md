# Testing Full System with Video File

This guide explains how to test the complete system (frontend, backend, and bot) using a video file instead of a live game account.

## 🎯 Overview

Since you don't have a game account, you can test the entire system using a video file. The bot will:
- Read frames from the video file
- Detect numbers from video frames
- Run the strategy logic
- Send events to the web interface
- Display results in the dashboard

---

## 📋 Prerequisites

1. **Video file** - A video of the roulette game (MP4, AVI, MOV, etc.)
2. **Backend dependencies** - `pip install -r requirements.txt`
3. **Frontend dependencies** - `cd web && npm install`

---

## 🚀 Method 1: Use Video File with Web Interface (✅ IMPLEMENTED)

**This method is already implemented!** The BotManager now automatically uses video input if the `BOT_VIDEO_PATH` environment variable is set.

### Step 1: Set Video Path Environment Variable

**Windows PowerShell:**
```powershell
$env:BOT_VIDEO_PATH = "path\to\your\video.mp4"
```

**Windows CMD:**
```cmd
set BOT_VIDEO_PATH=path\to\your\video.mp4
```

**Linux/Mac:**
```bash
export BOT_VIDEO_PATH="path/to/your/video.mp4"
```

### Step 2: Start the System

**Terminal 1 - Backend:**
```powershell
# Set video path (use absolute path for best results)
$env:BOT_VIDEO_PATH = "C:\full\path\to\your_video.mp4"

# Start backend
uvicorn backend.server.app:app --reload --port 8000
```

**You should see in backend logs:**
```
INFO: Using video file for input: C:\full\path\to\your_video.mp4
```

**Terminal 2 - Frontend:**
```powershell
cd web
npm run dev
```

**Terminal 3 - Open Dashboard:**
- Open browser: `http://localhost:3000`
- Click "Iniciar bot" (with "Modo de teste" checked)
- Watch the bot process video frames!

---

## 🚀 Method 2: Use simulate_strategy.py with WebSocket Bridge

This method uses the existing `simulate_strategy.py` script but connects it to the web interface.

### Step 1: Create a Video Bridge Script

Create `test_video_with_web_interface.py`:

```python
"""
Test bot with video file while web interface is running.
This script runs the bot with video input and connects to the web interface.
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Optional

from backend.app.config_loader import ConfigLoader
from backend.app.bot import RouletteBot
from backend.app.detection.frame_detector import FrameDetector

# Import web interface components
from backend.server.events import EventDispatcher
import asyncio

def run_bot_with_video(
    video_path: str,
    config_path: str = 'config/default_config.json',
    test_mode: bool = True,
    max_spins: Optional[int] = None,
):
    """
    Run bot with video file and connect to web interface.
    """
    print(f"Loading configuration from {config_path}...")
    config = ConfigLoader.load_config(config_path)
    
    # Create event dispatcher (same as web interface uses)
    event_dispatcher = EventDispatcher()
    
    # Initialize bot
    print("Initializing bot...")
    bot = RouletteBot(
        config_path,
        event_dispatcher=event_dispatcher,
        test_mode=test_mode,
    )
    
    # Replace detector with frame detector
    print(f"Loading video: {video_path}")
    frame_detector = FrameDetector(config, video_path)
    bot.detector = frame_detector
    
    # Bind event loop for WebSocket publishing
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    event_dispatcher.bind_loop(loop)
    
    print("\n" + "=" * 60)
    print("BOT STARTED WITH VIDEO INPUT")
    print("=" * 60)
    print(f"Video: {video_path}")
    print(f"Test mode: {test_mode}")
    print(f"Max spins: {max_spins or 'unlimited'}")
    print("-" * 60 + "\n")
    
    # Run bot
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nStopping bot...")
        bot.stop()
    finally:
        loop.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run bot with video file')
    parser.add_argument('video', type=str, help='Path to video file')
    parser.add_argument('--config', type=str, default='config/default_config.json',
                       help='Path to configuration file')
    parser.add_argument('--test', action='store_true', default=True,
                       help='Run in test mode (no real bets)')
    parser.add_argument('--max-spins', type=int, default=None,
                       help='Maximum number of spins to process')
    
    args = parser.parse_args()
    
    if not Path(args.video).exists():
        print(f"Error: Video file not found: {args.video}")
        sys.exit(1)
    
    run_bot_with_video(
        args.video,
        args.config,
        args.test,
        args.max_spins
    )
```

### Step 2: Run the System

**Terminal 1 - Backend:**
```powershell
uvicorn backend.server.app:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd web
npm run dev
```

**Terminal 3 - Bot with Video:**
```powershell
python test_video_with_web_interface.py your_video.mp4 --test
```

**Browser:**
- Open `http://localhost:3000`
- The bot is already running and processing video
- Watch real-time updates in the dashboard!

---

## 🚀 Method 3: Quick Test with simulate_strategy.py

This is the simplest method but doesn't connect to the web interface directly.

### Step 1: Run Strategy Simulation

```powershell
python simulate_strategy.py your_video.mp4 --config config/default_config.json
```

### Step 2: Monitor in Separate Terminal

While simulation runs, you can:
- Check logs in `logs/` directory
- Monitor console output
- See detection results

**Note:** This method doesn't connect to the web interface, but it's good for testing detection and strategy logic.

---

## ✅ Recommended Approach

**For full system testing, use Method 1** - it's the cleanest integration:

1. Modify `bot_manager.py` to support video (one-time change)
2. Set environment variable with video path
3. Start backend and frontend normally
4. Use web interface to start/stop bot
5. Bot processes video frames automatically

---

## 🔧 Configuration Tips

### Video File Location

Place your video file in the project root or specify full path:
```powershell
$env:BOT_VIDEO_PATH = "C:\Users\YourName\Videos\roulette_game.mp4"
```

### Video Requirements

- **Format:** MP4, AVI, MOV, MKV (any OpenCV-supported format)
- **Content:** Should show roulette table with winning numbers
- **Quality:** Clear view of numbers and colors
- **Resolution:** Any resolution (bot will adapt)

### Test Mode

Always use test mode when testing with video:
- Check "Modo de teste (simulação)" in dashboard
- Or set `test_mode=True` in code
- This prevents any accidental real bets

---

## 📊 What to Expect

When testing with video:

1. **Backend starts** - BotManager initializes
2. **Video loads** - FrameDetector opens video file
3. **Bot starts** - From dashboard, click "Iniciar bot"
4. **Frames process** - Bot reads frames from video
5. **Detections** - Numbers detected from video frames
6. **Events sent** - Real-time updates to dashboard
7. **Dashboard updates** - Live results, bets, balance, etc.

---

## 🐛 Troubleshooting

### Issue: Video Not Found

**Error:** `Unable to open video source`

**Solution:**
- Check video path is correct
- Use absolute path: `C:\full\path\to\video.mp4`
- Verify video file exists
- Check file permissions

### Issue: No Detections

**Symptoms:** Bot runs but no numbers detected

**Solution:**
1. Test video detection first:
   ```powershell
   python test_video.py your_video.mp4
   ```
2. Check video quality - numbers should be visible
3. Adjust detection settings in config
4. Verify templates exist in `winning-number_templates/`

### Issue: Video Ends Too Quickly

**Symptoms:** Bot stops after processing all frames

**Solution:**
- Video will end when all frames are processed
- This is normal behavior
- To loop video, modify `FrameDetector.restart_video()` to auto-loop
- Or use a longer video file

### Issue: Web Interface Not Updating

**Symptoms:** Bot runs but dashboard doesn't update

**Solution:**
1. Check WebSocket connection in browser DevTools
2. Verify backend is running
3. Check backend logs for errors
4. Ensure EventDispatcher is bound to event loop

---

## 📝 Testing Checklist

- [ ] Video file exists and is accessible
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Dashboard loads at `http://localhost:3000`
- [ ] Video path set in environment variable (Method 1)
- [ ] Bot starts from dashboard
- [ ] Numbers detected from video
- [ ] Real-time updates appear in dashboard
- [ ] Bet history updates
- [ ] Balance updates (in test mode)
- [ ] Charts update with performance data

---

## 🎯 Next Steps

After successful video testing:

1. **Test with different videos** - Try various game scenarios
2. **Adjust detection settings** - Fine-tune for your video quality
3. **Test strategy logic** - Verify betting decisions are correct
4. **Monitor performance** - Check detection accuracy
5. **Prepare for live testing** - When you get a game account

---

## 💡 Tips

1. **Use test mode** - Always test with "Modo de teste" enabled
2. **Start with short videos** - Test with 30-60 second clips first
3. **Check detection accuracy** - Use `test_video.py` first to verify detection
4. **Monitor backend logs** - See what the bot is doing
5. **Watch dashboard** - Real-time updates show bot activity

---

**Happy Testing! 🎉**

