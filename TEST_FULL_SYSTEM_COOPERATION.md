# Testing Full System Cooperation: Bot, Frontend & Backend

This guide provides step-by-step instructions for testing how the bot, frontend, and backend work together.

## 🎯 Overview

The system consists of three components that need to work together:
1. **Backend** (FastAPI) - API server and bot manager
2. **Frontend** (React) - Web dashboard
3. **Bot** (RouletteBot) - The actual bot that detects and places bets

---

## 📋 Prerequisites

### 1. Install Dependencies

**Backend:**
```powershell
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd web
npm install
```

### 2. Prepare Video File (Optional - for testing without game account)

If you don't have a game account, prepare a video file:
- Format: MP4, AVI, MOV, etc.
- Content: Roulette game with visible numbers
- Location: Place in project root or note the full path

---

## 🚀 Step-by-Step Testing

### Step 1: Start Backend Server

**Terminal 1:**
```powershell
# IMPORTANT: Set video path for testing (if using video)
# The bot will NOT place bets if it can't detect results from screen capture
# For video testing, you MUST set this environment variable:
$env:BOT_VIDEO_PATH = "roleta_brazileria.mp4"

# Alternative: Place video file named "roleta_brazileria.mp4" in project root
# The bot will auto-detect it

# Start backend
uvicorn backend.server.app:app --reload --port 8000
```

**⚠️ CRITICAL:** If `BOT_VIDEO_PATH` is not set and no video file is found, the bot will try to use screen capture. If screen capture fails (game window not visible, wrong coordinates, etc.), the bot will NOT detect results and therefore will NOT place bets.

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000   
INFO:     Application startup complete.
```

**Verify backend is running:**
```powershell
# Test in another terminal or browser
curl http://localhost:8000/ping
# Should return: {"status": "ok"}
```

**Or open in browser:**
- Health: http://localhost:8000/ping
- API Docs: http://localhost:8000/docs

---

### Step 2: Start Frontend Server

**Terminal 2:**
```powershell
cd web
npm run dev
```

**Expected output:**
```
VITE v4.4.11  ready in 500 ms
➜  Local:   http://localhost:3000/
```

**Open dashboard:**
- Browser: http://localhost:3000
- Dashboard should load

---

### Step 3: Verify Initial Connection

**Check in browser console (F12):**

1. **Open DevTools (F12) → Console tab**
2. **Look for:**
   - ✅ `"WebSocket connected: ws://localhost:8000/ws/events"`
   - ✅ API calls being made
   - ❌ No CORS errors
   - ❌ No WebSocket errors

**Check backend terminal:**
- Should see: `INFO: WebSocket client connected`

**Check dashboard:**
- Status bar shows "Inativo" (idle)
- Balance cards visible
- All panels loaded

---

### Step 4: Test Configuration Loading

**In dashboard:**
1. Scroll to "Configuração da estratégia" section
2. Verify configuration loads
3. Check that form fields are populated

**Backend terminal should show:**
```
INFO: GET /api/config/ HTTP/1.1 200 OK
```

**If configuration doesn't load:**
- Check backend logs for errors
- Verify `config/default_config.json` exists
- Check browser console for API errors

---

### Step 5: Test Bot Control (Start/Stop)

#### 5.1 Start Bot

**In dashboard:**
1. Go to "Controles do bot" section
2. Select mode: "Modo totalmente automático"
3. **Check "Modo de teste (simulação)"** (important for safe testing)
4. Click "Iniciar bot"

**Expected behavior:**
- Button changes to "Iniciando…" then back to "Iniciar bot" (disabled)
- Status bar changes to "Em execução" (running)
- Status chip turns green

**Backend terminal should show:**
```
INFO: Starting roulette bot...
INFO: Using video file for input: C:\path\to\video.mp4  (if using video)
```

**Browser console should show:**
- WebSocket messages with `status_change` events
- Status updates

#### 5.2 Verify Bot is Running

**Check dashboard:**
- Status: "Em execução"
- Mode: Shows selected mode
- Last activity: Updates with current time

**Check backend logs:**
- Bot detection messages (if video is set)
- Bot activity logs

#### 5.3 Stop Bot

**In dashboard:**
1. Click "Parar bot" button

**Expected behavior:**
- Status changes to "Inativo" (idle)
- Status chip turns gray
- Bot stops processing

**Backend terminal should show:**
```
INFO: Bot stopped
```

---

### Step 6: Test Real-Time Updates

#### 6.1 With Video File

**If using video file:**
1. Set `BOT_VIDEO_PATH` environment variable
2. Start bot from dashboard
3. Watch for real-time updates:
   - **Live Results** panel: New numbers appear
   - **Active Bet** panel: Shows when bets are placed
   - **Balance Cards**: Update when bets resolve
   - **Bet History**: New entries appear
   - **Charts**: Update with performance data

#### 6.2 With Live Game (if you have account)

**If testing with live game:**
1. Open roulette game in browser
2. Start bot from dashboard
3. Bot detects from screen
4. Watch real-time updates in dashboard

#### 6.3 What to Monitor

**Dashboard updates:**
- ✅ New results appear in "Resultados ao vivo"
- ✅ Active bets show in "Aposta ativa"
- ✅ Balance updates in balance cards
- ✅ Bet history updates in table
- ✅ Charts update with new data

**Backend logs:**
- Detection messages
- Bet placement logs
- Event emissions

**Browser console:**
- WebSocket messages with event types:
  - `new_result` - New number detected
  - `bet_placed` - Bet was placed
  - `bet_resolved` - Bet won/lost
  - `balance_update` - Balance changed
  - `status_change` - Status changed

---

### Step 7: Test Configuration Changes

#### 7.1 Update Configuration

**In dashboard:**
1. Go to "Configuração da estratégia"
2. Change a value (e.g., "Aposta base")
3. Click "Salvar configurações"

**Expected:**
- Success message or no error
- Configuration persists

**Backend terminal:**
```
INFO: PUT /api/config/ HTTP/1.1 200 OK
```

#### 7.2 Verify Changes Applied

**Restart bot:**
1. Stop bot
2. Start bot again
3. Verify bot uses new configuration

---

### Step 8: Test Mode Switching

**In dashboard:**
1. While bot is running, change mode dropdown
2. Select different mode (e.g., "Modo de manutenção")
3. Verify status updates

**Backend terminal:**
```
INFO: POST /api/bot/mode HTTP/1.1 200 OK
```

**Dashboard:**
- Status bar shows new mode
- Bot continues running with new mode

---

### Step 9: Test Error Handling

#### 9.1 Stop Backend While Frontend is Running

**Test:**
1. Stop backend (Ctrl+C in Terminal 1)
2. Check dashboard:
   - Should show error or disconnected state
   - WebSocket should attempt reconnection

**Restart backend:**
1. Start backend again
2. Dashboard should reconnect automatically
3. WebSocket should reconnect

#### 9.2 Test Invalid Operations

**Test:**
1. Try to start bot when already running
2. Should show error or prevent duplicate start

---

## ✅ Verification Checklist

### Backend Verification
- [ ] Backend starts without errors
- [ ] API responds to `/ping`
- [ ] API docs accessible at `/docs`
- [ ] WebSocket endpoint accessible
- [ ] Bot can be created
- [ ] Events are dispatched

### Frontend Verification
- [ ] Frontend starts without errors
- [ ] Dashboard loads at `http://localhost:3000`
- [ ] No console errors
- [ ] WebSocket connects successfully
- [ ] API calls work
- [ ] All UI components render

### Integration Verification
- [ ] WebSocket connection established
- [ ] Can start bot from dashboard
- [ ] Can stop bot from dashboard
- [ ] Status updates in real-time
- [ ] Events appear in dashboard
- [ ] Configuration loads and saves
- [ ] Mode changes work

### Bot Verification
- [ ] Bot starts successfully
- [ ] Bot detects numbers (from video or screen)
- [ ] Bot places bets (in test mode)
- [ ] Bot emits events
- [ ] Events reach frontend
- [ ] Dashboard shows bot activity

---

## 🧪 Testing Scenarios

### Scenario 1: Full Flow Test

**Steps:**
1. Start backend
2. Start frontend
3. Open dashboard
4. Verify connection
5. Start bot (test mode)
6. Watch real-time updates
7. Stop bot
8. Verify all components work together

**Expected:**
- All components communicate
- Real-time updates work
- No errors in logs

### Scenario 2: Configuration Test

**Steps:**
1. Load dashboard
2. Change configuration
3. Save configuration
4. Restart bot
5. Verify new config is used

**Expected:**
- Config saves successfully
- Bot uses new config
- Changes persist

### Scenario 3: Error Recovery Test

**Steps:**
1. Start all components
2. Stop backend
3. Verify frontend handles disconnection
4. Restart backend
5. Verify reconnection

**Expected:**
- Frontend handles errors gracefully
- Reconnection works automatically
- System recovers

### Scenario 4: Video Testing (No Game Account)

**Steps:**
1. Set `BOT_VIDEO_PATH` environment variable
2. Start backend
3. Start frontend
4. Start bot from dashboard
5. Watch bot process video frames
6. Verify real-time updates

**Expected:**
- Bot reads from video file
- Detections appear in dashboard
- All updates work correctly

---

## 📊 Monitoring During Testing

### Backend Logs

**Watch for:**
- Bot starting/stopping
- Detection messages
- Event emissions
- API requests
- Errors or warnings

**Example logs:**
```
INFO: Starting roulette bot...
INFO: Using video file for input: video.mp4
INFO: WebSocket client connected
INFO: Detected number: 15
INFO: Bet placed: even, amount: 10.0
```

### Frontend Console

**Watch for:**
- WebSocket connection status
- API call responses
- React errors
- State updates

**Example console:**
```
WebSocket connected: ws://localhost:8000/ws/events
Received: {"type": "new_result", "payload": {...}}
Received: {"type": "bet_placed", "payload": {...}}
```

### Browser Network Tab

**Watch for:**
- API requests (should be 200 OK)
- WebSocket connection (should be 101 Switching Protocols)
- Failed requests (check why)

---

## 🐛 Troubleshooting

### Issue: Backend Won't Start

**Error:** Port already in use

**Solution:**
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill process or use different port
uvicorn backend.server.app:app --reload --port 9000
```

### Issue: Frontend Can't Connect to Backend

**Error:** Failed to fetch

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/ping`
2. Check CORS settings in `backend/server/app.py`
3. Verify frontend proxy in `web/vite.config.js`

### Issue: WebSocket Not Connecting

**Error:** WebSocket connection failed

**Solution:**
1. Check backend is running
2. Verify WebSocket endpoint: `ws://localhost:8000/ws/events`
3. Check browser console for errors
4. Verify firewall isn't blocking

### Issue: Bot Won't Start

**Error:** Bot start fails

**Solution:**
1. Check backend logs for errors
2. Verify config file exists: `config/default_config.json`
3. Check video path (if using video)
4. Verify dependencies installed

### Issue: No Real-Time Updates

**Symptoms:** Bot runs but dashboard doesn't update

**Solution:**
1. Check WebSocket connection in browser DevTools
2. Verify bot is emitting events (check backend logs)
3. Check EventDispatcher is bound to event loop
4. Restart backend server

---

## 🎯 Quick Test Commands

### Test Backend API
```powershell
# Health check
curl http://localhost:8000/ping

# Get status
curl http://localhost:8000/api/status

# Get balance
curl http://localhost:8000/api/balance

# Start bot (test mode)
curl -X POST http://localhost:8000/api/bot/start -H "Content-Type: application/json" -d "{\"mode\": \"Full Auto Mode\", \"test_mode\": true}"

# Stop bot
curl -X POST http://localhost:8000/api/bot/stop
```

### Test WebSocket
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/events');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
ws.onerror = (e) => console.error('Error:', e);
```

---

## 💡 Tips for Successful Testing

1. **Start in order:** Backend → Frontend → Dashboard
2. **Use test mode:** Always test with "Modo de teste" enabled first
3. **Monitor logs:** Watch both backend and frontend logs
4. **Check console:** Browser DevTools shows connection status
5. **Test incrementally:** Test one feature at a time
6. **Use video first:** Test with video file before live game
7. **Verify each step:** Don't skip verification steps

---

## 📝 Testing Summary

**Complete Test Flow:**
1. ✅ Backend starts
2. ✅ Frontend starts
3. ✅ Dashboard loads
4. ✅ WebSocket connects
5. ✅ Configuration loads
6. ✅ Bot starts
7. ✅ Real-time updates work
8. ✅ Bot stops
9. ✅ All components cooperate

**If all steps pass, the system is working correctly!** 🎉

---

## 🚀 Next Steps

After successful testing:
1. Test with different configurations
2. Test error scenarios
3. Test with longer video files
4. Test performance under load
5. Prepare for live game testing (when you have account)

---

**Happy Testing! 🎉**

