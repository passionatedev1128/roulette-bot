# Local Testing Guide: Frontend, Backend & Bot Cooperation

This guide explains how to test the full integration between the frontend dashboard, backend API, and the bot on your local machine.

## 🎯 Quick Start

### Option 1: Using the Start Script (Easiest)

**Terminal 1 - Backend:**
```powershell
python start_web_interface.py
# Choose option 1: Start Backend
```

**Terminal 2 - Frontend:**
```powershell
python start_web_interface.py
# Choose option 2: Start Frontend
```

**Then open:** `http://localhost:3000`

### Option 2: Manual Start

**Terminal 1 - Backend:**
```powershell
uvicorn backend.server.app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd web
npm run dev
```

**Then open:** `http://localhost:3000`

---

## 📋 Prerequisites

### 1. Install Backend Dependencies
```powershell
pip install -r requirements.txt
```

Required packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket support

### 2. Install Frontend Dependencies
```powershell
cd web
npm install
```

This installs:
- React
- Vite (build tool)
- Axios (HTTP client)
- Recharts (charts)
- React Query (data fetching)

---

## ✅ Step-by-Step Testing

### Step 1: Verify Backend is Running

**Check backend health:**
```powershell
curl http://localhost:8000/ping
# Should return: {"status": "ok"}
```

**Or open in browser:**
- Health: http://localhost:8000/ping
- API Docs: http://localhost:8000/docs (Swagger UI)

**Expected backend output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 2: Verify Frontend is Running

**Open browser:**
- Dashboard: http://localhost:3000

**Expected frontend output:**
```
VITE v4.4.11  ready in 500 ms
➜  Local:   http://localhost:3000/
```

**What you should see:**
- Dashboard loads successfully
- Status bar shows "Inativo" (idle)
- All panels visible (Balance, Charts, etc.)

### Step 3: Test API Connection

**In browser DevTools (F12) → Console:**
- Should see: API calls being made
- Should see: WebSocket connection established
- No CORS errors

**Test API endpoints manually:**
```powershell
# Get status
curl http://localhost:8000/api/status

# Get balance
curl http://localhost:8000/api/balance

# Get config
curl http://localhost:8000/api/config/
```

### Step 4: Test WebSocket Connection

**In browser DevTools (F12) → Console:**
- Should see: "WebSocket connected" or similar
- Check Network tab → WS filter → Should see connection to `ws://localhost:8000/ws/events`

**Test WebSocket manually:**
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/events');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (event) => console.log('Received:', JSON.parse(event.data));
```

### Step 5: Test Bot Control from Dashboard

**1. Start Bot:**
- Click "Iniciar bot" button
- Select mode (e.g., "Modo totalmente automático")
- Check "Modo de teste (simulação)" for safe testing
- Click "Iniciar bot"

**Expected:**
- Status changes to "Em execução" (running)
- Backend console shows bot starting
- Dashboard updates in real-time

**2. Monitor Real-Time Updates:**
- Watch "Resultados ao vivo" panel for new numbers
- Watch "Aposta ativa" panel for bet placement
- Watch balance cards for updates
- Watch charts for performance data

**3. Stop Bot:**
- Click "Parar bot" button
- Status changes to "Inativo" (idle)
- Bot stops running

---

## 🔍 Verification Checklist

### ✅ Backend Verification

- [ ] Backend starts without errors
- [ ] `http://localhost:8000/ping` returns `{"status": "ok"}`
- [ ] API docs accessible at `http://localhost:8000/docs`
- [ ] No port conflicts (8000 is free)

### ✅ Frontend Verification

- [ ] Frontend starts without errors
- [ ] Dashboard loads at `http://localhost:3000`
- [ ] No console errors in browser DevTools
- [ ] All UI components render correctly

### ✅ Integration Verification

- [ ] WebSocket connects successfully
- [ ] API calls work (check Network tab)
- [ ] No CORS errors
- [ ] Real-time updates appear in dashboard

### ✅ Bot Control Verification

- [ ] Can start bot from dashboard
- [ ] Can stop bot from dashboard
- [ ] Can change bot mode
- [ ] Status updates in real-time
- [ ] Events appear in dashboard

### ✅ Data Flow Verification

- [ ] Bot events → WebSocket → Dashboard
- [ ] Dashboard actions → API → Bot
- [ ] Config changes → API → Bot config
- [ ] Balance updates appear correctly
- [ ] Bet history updates correctly

---

## 🧪 Testing Scenarios

### Scenario 1: Test Mode (Safe Testing)

**Start bot in test mode:**
1. Open dashboard
2. Select "Modo totalmente automático"
3. Check "Modo de teste (simulação)"
4. Click "Iniciar bot"

**What to verify:**
- Bot starts without placing real bets
- Dashboard shows simulated activity
- All panels update correctly
- Can stop bot successfully

### Scenario 2: Real Bot Testing

**Start bot with real detection:**
1. Open roulette game in browser (for bot to detect)
2. Open dashboard
3. Start bot (without test mode)
4. Bot detects numbers and places bets

**What to verify:**
- Bot detects numbers from screen
- Bets are placed correctly
- Results appear in dashboard
- Balance updates correctly
- Bet history records correctly

### Scenario 3: Configuration Testing

**Change configuration:**
1. Open dashboard
2. Go to "Configuração da estratégia"
3. Change base bet amount
4. Click "Salvar configurações"

**What to verify:**
- Config saves successfully
- Bot uses new config on next start
- Changes persist after restart

### Scenario 4: Error Handling

**Test error scenarios:**
1. Stop backend while frontend is running
2. Check dashboard shows error/disconnected state
3. Restart backend
4. Check dashboard reconnects

**What to verify:**
- Error messages display correctly
- Dashboard handles disconnections gracefully
- Reconnection works automatically

---

## 🐛 Troubleshooting

### Issue: Backend Won't Start

**Error:** `Address already in use: 8000`

**Solution:**
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process or use different port
uvicorn backend.server.app:app --reload --port 9000
```

### Issue: Frontend Won't Start

**Error:** `npm not found`

**Solution:**
- Install Node.js from https://nodejs.org/
- Restart terminal
- Run `cd web && npm install`

### Issue: CORS Errors

**Error:** `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution:**
- Check `backend/server/app.py` - CORS should allow `http://localhost:3000`
- Verify backend is running on port 8000
- Verify frontend is running on port 3000

### Issue: WebSocket Not Connecting

**Error:** `WebSocket connection failed`

**Solution:**
1. Check backend is running: `http://localhost:8000/ping`
2. Check WebSocket endpoint: `ws://localhost:8000/ws/events`
3. Check browser console for errors
4. Verify firewall isn't blocking WebSocket connections

### Issue: No Real-Time Updates

**Symptoms:**
- Bot running but dashboard not updating
- WebSocket connected but no events

**Solution:**
1. Check bot is emitting events (check backend logs)
2. Verify EventDispatcher is working
3. Check WebSocket connection in browser DevTools
4. Restart backend server

### Issue: Bot Won't Start from Dashboard

**Symptoms:**
- Click "Start" but nothing happens
- Error in console

**Solution:**
1. Check backend logs for errors
2. Verify bot can start manually: `python -m backend.app.bot config/default_config.json --test`
3. Check config file exists: `config/default_config.json`
4. Verify dependencies installed

---

## 📊 Monitoring During Testing

### Backend Logs

**Watch for:**
- Bot starting/stopping
- Events being emitted
- API requests
- Errors or warnings

### Frontend Console

**Watch for:**
- WebSocket connection status
- API call responses
- React errors
- State updates

### Browser Network Tab

**Watch for:**
- API requests (should be 200 OK)
- WebSocket messages (should see events)
- Failed requests (check why)

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

### Test Frontend
```powershell
# Check if frontend is serving
curl http://localhost:3000
```

---

## 📝 Testing Checklist Summary

**Before Testing:**
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Config file exists (`config/default_config.json`)
- [ ] Ports 3000 and 8000 are free

**During Testing:**
- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Dashboard loads correctly
- [ ] WebSocket connects
- [ ] Can start bot from dashboard
- [ ] Real-time updates appear
- [ ] Can stop bot from dashboard
- [ ] Config changes work
- [ ] Error handling works

**After Testing:**
- [ ] All features work as expected
- [ ] No errors in logs
- [ ] Performance is acceptable
- [ ] UI is responsive

---

## 🚀 Next Steps

After successful local testing:

1. **Test with real game** - Run bot against actual roulette game
2. **Test error scenarios** - Verify error handling works
3. **Test configuration** - Verify all config options work
4. **Test on different browsers** - Chrome, Firefox, Edge
5. **Test performance** - Monitor resource usage
6. **Document issues** - Note any problems found

---

## 💡 Tips

1. **Use test mode first** - Always test with "Modo de teste" enabled initially
2. **Check browser console** - Most issues show up there first
3. **Monitor backend logs** - They show what the bot is doing
4. **Use DevTools Network tab** - See all API calls and WebSocket messages
5. **Start simple** - Test basic features first, then complex ones

---

**Happy Testing! 🎉**

