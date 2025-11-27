# Web Interface Testing Guide

This guide explains how to test the Roulette Bot web interface, including both the backend API and frontend dashboard.

## Prerequisites

### 1. Install Backend Dependencies

```bash
# Make sure you're in the project root directory
pip install -r requirements.txt
```

Key dependencies:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket support

### 2. Install Frontend Dependencies

```bash
# Navigate to web directory
cd web
npm install
```

This installs:
- React
- Vite (build tool)
- Axios (HTTP client)
- Recharts (charts)
- React Query (data fetching)

## Starting the Web Interface

### Step 1: Start the Backend Server

Open a terminal in the project root and run:

```bash
# Start FastAPI server with uvicorn
uvicorn backend.server.app:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test the backend:**
- Open browser: http://localhost:8000/ping
- Should return: `{"status": "ok"}`
- API docs: http://localhost:8000/docs (Swagger UI)

### Step 2: Start the Frontend Development Server

Open a **new terminal** (keep backend running) and run:

```bash
# Navigate to web directory
cd web

# Start Vite dev server
npm run dev
```

**Expected output:**
```
  VITE v4.4.11  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**Access the dashboard:**
- Open browser: http://localhost:3000
- The React app should load automatically

## Testing Checklist

### 1. Backend API Testing

#### Test Basic Endpoints

```bash
# Test health check
curl http://localhost:8000/ping

# Test bot status
curl http://localhost:8000/api/status

# Test balance
curl http://localhost:8000/api/balance

# Test configuration
curl http://localhost:8000/api/config

# Test results history
curl http://localhost:8000/api/results/latest?limit=10

# Test active bets
curl http://localhost:8000/api/bets/active

# Test bet history
curl http://localhost:8000/api/bets/history?limit=10

# Test statistics
curl http://localhost:8000/api/stats
```

#### Test API with Browser

1. **Swagger UI (Interactive API Docs)**
   - Visit: http://localhost:8000/docs
   - Test endpoints directly from the browser
   - See request/response schemas

2. **Alternative API Docs**
   - Visit: http://localhost:8000/redoc
   - Alternative documentation interface

### 2. Frontend Dashboard Testing

#### Visual Checks

1. **Dashboard Loads**
   -  Page loads without errors
   -  No console errors (check browser DevTools)
   -  All components render

2. **Status Bar**
   -  Shows bot status (Idle/Running/Error)
   -  Shows connection status
   -  Updates in real-time

3. **Balance Cards**
   -  Shows current balance
   -  Shows profit/loss
   -  Shows win rate

4. **Live Results**
   -  Displays recent game results
   -  Shows number and color
   -  Updates automatically

5. **Active Bets Panel**
   -  Shows pending bets
   -  Shows bet details (type, amount, color)
   -  Updates when bets are placed

6. **Bet History Table**
   -  Displays bet history
   -  Shows all columns (timestamp, bet, result, profit/loss)
   -  Can scroll through history

7. **Performance Charts**
   -  Balance over time chart
   -  Win rate chart
   -  Updates with new data

8. **Configuration Form**
   -  All fields are editable
   -  Can change strategy settings
   -  Can change bet amounts
   -  Save button works

9. **Mode Controls**
   -  Start/Stop buttons work
   -  Mode selector works
   -  Status updates when mode changes

### 3. WebSocket Testing

#### Check WebSocket Connection

1. **Open Browser DevTools** (F12)
2. **Go to Console tab**
3. **Look for WebSocket messages:**
   ```
   WebSocket connected
   Received: {"event": "status_update", "data": {...}}
   ```

#### Test Real-time Updates

1. **Start the bot** (via dashboard or API)
2. **Watch for real-time updates:**
   - New results appear automatically
   - Balance updates without refresh
   - Status changes immediately

#### Test WebSocket Events

The bot should emit these events:
- `status_update` - Bot status changes
- `new_result` - New game result detected
- `bet_placed` - Bet was placed
- `error` - Error occurred

### 4. Integration Testing

#### Test Complete Flow

1. **Start Backend**
   ```bash
   uvicorn backend.server.app:app --reload --port 8000
   ```

2. **Start Frontend**
   ```bash
   cd web && npm run dev
   ```

3. **Open Dashboard**
   - Visit: http://localhost:3000

4. **Test Bot Control**
   - Click "Start" button
   - Verify status changes to "Running"
   - Check console for WebSocket messages

5. **Test Configuration**
   - Change strategy settings
   - Click "Save Configuration"
   - Verify settings are saved

6. **Test with Video (Simulation)**
   ```bash
   # In another terminal, run simulation
   python simulate_strategy.py your_video.mp4 --config config/default_config.json
   ```
   - Watch dashboard update in real-time
   - See results appear automatically
   - See bets being placed

## Common Issues & Solutions

### Issue 1: Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install fastapi uvicorn websockets
```

### Issue 2: Frontend Won't Start

**Error:** `command not found: npm`

**Solution:**
- Install Node.js: https://nodejs.org/
- Then run: `npm install` in the `web/` directory

### Issue 3: CORS Errors

**Error:** `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution:**
- Check `backend/server/app.py` - CORS should allow `http://localhost:3000`
- Verify backend is running on port 8000
- Verify frontend is running on port 3000

### Issue 4: WebSocket Connection Failed

**Error:** `WebSocket connection failed`

**Solution:**
1. Check backend is running
2. Check WebSocket endpoint: `ws://localhost:8000/ws`
3. Check browser console for errors
4. Verify firewall isn't blocking WebSocket connections

### Issue 5: API Returns 404

**Error:** `404 Not Found` when accessing API endpoints

**Solution:**
- Check endpoint URL: should be `/api/status`, not `/status`
- Verify routes are registered in `backend/server/app.py`
- Check uvicorn is running with `--reload` flag

## Testing with Real Bot

### Option 1: Test Mode (Recommended for Testing)

```bash
# Start bot in test mode (no real bets)
python -m backend.app.bot config/default_config.json --test-mode
```

Then:
1. Start backend server
2. Start frontend
3. Open dashboard
4. Watch real-time updates

### Option 2: Video Simulation

```bash
# Run simulation with video
python simulate_strategy.py your_video.mp4 --config config/default_config.json
```

While simulation runs:
1. Start backend server
2. Start frontend
3. Open dashboard
4. Watch results and bets appear in real-time

## Production Testing

### Build Frontend for Production

```bash
cd web
npm run build
```

This creates a `dist/` folder with production-ready files.

### Serve Production Build

```bash
# Option 1: Use Vite preview
cd web
npm run preview

# Option 2: Serve with Python
cd web/dist
python -m http.server 8080
```

### Test Production Setup

1. Backend: `uvicorn backend.server.app:app --host 0.0.0.0 --port 8000`
2. Frontend: Serve from `web/dist/` or use `npm run preview`
3. Access: http://localhost:8080 (or preview port)

## API Endpoints Reference

### Status Endpoints
- `GET /api/status` - Get bot status
- `GET /api/stats` - Get statistics

### Control Endpoints
- `POST /api/bot/start` - Start bot
- `POST /api/bot/stop` - Stop bot
- `POST /api/bot/mode` - Change mode

### Data Endpoints
- `GET /api/results/latest?limit=10` - Get game results
- `GET /api/bets/active` - Get active bet
- `GET /api/bets/history?limit=10` - Get bet history
- `GET /api/balance` - Get balance and performance
- `GET /api/config/` - Get configuration
- `PUT /api/config/` - Update configuration

### WebSocket
- `WS /ws` - WebSocket connection for real-time updates

## Browser DevTools Tips

### Check Network Tab
- See API requests
- Check WebSocket messages
- Verify responses

### Check Console Tab
- See JavaScript errors
- See WebSocket connection status
- See API call logs

### Check Application Tab
- See WebSocket connections
- Check local storage
- Verify session data

## Next Steps

After testing the web interface:

1. **Verify all features work** - Complete the checklist above
2. **Test with real bot** - Run bot and verify dashboard updates
3. **Test error handling** - Stop bot, check error messages display
4. **Test configuration** - Change settings, verify they persist
5. **Test on different browsers** - Chrome, Firefox, Edge
6. **Test on mobile** - Check responsive design

## Quick Start Commands

```bash
# Terminal 1: Backend
uvicorn backend.server.app:app --reload --port 8000

# Terminal 2: Frontend
cd web && npm run dev

# Terminal 3: Bot (optional, for testing)
python simulate_strategy.py video.mp4 --config config/default_config.json
```

Then open: http://localhost:3000

