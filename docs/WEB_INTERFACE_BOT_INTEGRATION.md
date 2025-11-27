# Web Interface & Bot Integration

##  Yes, the Bot Fully Cooperates with the Web Interface!

The bot and web interface are **fully integrated** and work together seamlessly. Here's how:

---

## 🔗 How They Connect

### Architecture Overview

```
┌─────────────────┐
│  Web Interface  │  (React Frontend)
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP REST API
         │ WebSocket (real-time)
         ▼
┌─────────────────┐
│  FastAPI Server │  (Backend API)
│  (Port 8000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  BotManager     │  (Orchestrator)
└────────┬────────┘
         │
         │ Creates & Controls
         ▼
┌─────────────────┐
│  RouletteBot    │  (The Actual Bot)
└─────────────────┘
```

---

## 🔄 Integration Points

### 1. **Bot Creation & Control**

The `BotManager` creates and controls the `RouletteBot`:

```python
# BotManager creates bot with event dispatcher
bot = RouletteBot(
    config_path,
    event_dispatcher=bot_manager.event_dispatcher,  # ← WebSocket events
    state_callback=bot_manager._state_callback,    # ← State updates
    test_mode=test_mode
)
```

**Web Interface Can:**
-  Start bot: `POST /api/bot/start`
-  Stop bot: `POST /api/bot/stop`
-  Change mode: `POST /api/bot/mode`
-  Get status: `GET /api/status`

### 2. **Real-Time Events (WebSocket)**

The bot emits events that the web interface receives in real-time:

**Bot Emits Events:**
```python
# In RouletteBot class
self._emit_event("new_result", {...})      # New number detected
self._emit_event("bet_placed", {...})      # Bet was placed
self._emit_event("bet_resolved", {...})     # Bet won/lost
self._emit_event("balance_update", {...})   # Balance changed
self._emit_event("status_change", {...})   # Status changed
self._emit_event("error", {...})           # Error occurred
```

**Web Interface Receives:**
- WebSocket connection: `ws://localhost:8000/ws/events`
- Real-time updates appear instantly in dashboard
- No page refresh needed

### 3. **State Synchronization**

The `BotManager` tracks bot state and syncs with web interface:

**Tracked State:**
-  Bot running status
-  Current mode (Full Auto, Manual, etc.)
-  Balance (current, initial, profit/loss)
-  Win/loss counts
-  Active bets
-  Bet history
-  Recent results
-  Statistics

**Web Interface Can:**
- View all state in real-time
- See live updates as bot runs
- View historical data

### 4. **Configuration Management**

**Web Interface Can:**
-  Get config: `GET /api/config/`
-  Update config: `PUT /api/config/`
-  Save presets: `POST /api/config/presets`
-  Load presets: `GET /api/config/presets/{slug}`

**Bot Receives:**
- Config updates applied to bot
- Bot recreated with new config when idle
- Changes persist to `config/default_config.json`

---

## 📡 Real-Time Event Flow

### Example: New Result Detected

```
1. Bot detects winning number
   ↓
2. Bot._emit_event("new_result", {...})
   ↓
3. EventDispatcher.publish("new_result", {...})
   ↓
4. WebSocket sends to all connected clients
   ↓
5. Web Interface receives event
   ↓
6. Dashboard updates automatically:
   - Live results panel shows new number
   - Balance updates (if bet resolved)
   - Active bets panel updates
   - Charts update
```

### Example: Bet Placed

```
1. Bot places bet
   ↓
2. Bot._emit_event("bet_placed", {...})
   ↓
3. BotManager._state_callback updates state
   ↓
4. EventDispatcher publishes to WebSocket
   ↓
5. Web Interface shows:
   - Active bet in "Active Bets" panel
   - Bet amount and type
   - Timestamp
```

---

## 🎮 Web Interface Features

### Control Panel

**Start/Stop Bot:**
```javascript
// Web interface can start bot
POST /api/bot/start
{
  "mode": "Full Auto Mode",
  "test_mode": false
}

// Stop bot
POST /api/bot/stop
```

### Real-Time Dashboard

**Live Updates:**
-  New results appear automatically
-  Balance updates in real-time
-  Active bets show immediately
-  Status changes instantly
-  Charts update live

**No Refresh Needed:**
- WebSocket keeps connection open
- Events stream continuously
- Dashboard stays synchronized

### Configuration UI

**Manage Settings:**
-  Strategy settings (base bet, max gales, etc.)
-  Risk settings (stop loss, stop win)
-  Detection settings (screen region, thresholds)
-  Betting coordinates
-  Save/load presets

**Changes Applied:**
- Config saved to file
- Bot uses new config on next start
- Or bot recreated if idle

### Statistics & History

**View Data:**
-  Recent results (last 20 spins)
-  Bet history (last 50 bets)
-  Daily statistics
-  Strategy performance
-  Gale statistics
-  Balance history

---

## 🚀 How to Use

### Step 1: Start Backend Server

```powershell
# Option A: Use start script
python start_web_interface.py
# Choose option 1: Start Backend

# Option B: Manual
uvicorn backend.server.app:app --reload --port 8000
```

### Step 2: Start Frontend

```powershell
# Option A: Use start script
python start_web_interface.py
# Choose option 2: Start Frontend

# Option B: Manual
cd web
npm run dev
```

### Step 3: Open Dashboard

Open browser: `http://localhost:3000`

### Step 4: Start Bot from Dashboard

1. Click "Start Bot" button
2. Select mode (Full Auto, Manual, etc.)
3. Bot starts and connects
4. Watch real-time updates!

---

##  Integration Checklist

### Bot  Web Interface

-  Bot emits events  WebSocket  Dashboard
-  Bot state  BotManager  API  Dashboard
-  Bot logs  Statistics  Dashboard
-  Bot config  API  Configuration UI

### Web Interface  Bot

-  Start/Stop commands  API  BotManager  Bot
-  Config changes  API  BotManager  Bot config
-  Mode changes  API  BotManager  Bot mode

---

## 🔍 Verification

### Check Integration is Working

1. **Start Backend:**
   ```powershell
   uvicorn backend.server.app:app --reload --port 8000
   ```
   Should see: `Application startup complete`

2. **Start Frontend:**
   ```powershell
   cd web && npm run dev
   ```
   Should see: `Local: http://localhost:3000`

3. **Open Dashboard:**
   - Go to `http://localhost:3000`
   - Should see dashboard loading

4. **Start Bot:**
   - Click "Start Bot" button
   - Check console for WebSocket connection
   - Bot should start running

5. **Verify Real-Time Updates:**
   - Bot detects numbers  Dashboard updates
   - Bot places bets  Active bets panel updates
   - Bot resolves bets  Balance updates

### Check WebSocket Connection

**In Browser DevTools (F12):**
```javascript
// Console should show:
WebSocket connected
Received: {"type": "status_change", "payload": {...}}
Received: {"type": "new_result", "payload": {...}}
```

### Check API Endpoints

**Test Status:**
```powershell
curl http://localhost:8000/api/status
```

**Test Start Bot:**
```powershell
curl -X POST http://localhost:8000/api/bot/start \
  -H "Content-Type: application/json" \
  -d '{"mode": "Full Auto Mode", "test_mode": false}'
```

---

## 🐛 Troubleshooting

### Issue: WebSocket Not Connecting

**Symptoms:**
- Dashboard shows "Disconnected"
- No real-time updates

**Solutions:**
1. Check backend is running: `http://localhost:8000/ping`
2. Check WebSocket endpoint: `ws://localhost:8000/ws/events`
3. Check browser console for errors
4. Verify CORS settings in `backend/server/app.py`

### Issue: Bot Not Starting from Dashboard

**Symptoms:**
- Click "Start" but nothing happens
- Error in console

**Solutions:**
1. Check backend logs for errors
2. Verify bot can start manually: `python backend/app/bot.py --test`
3. Check config file exists: `config/default_config.json`
4. Verify dependencies installed

### Issue: No Real-Time Updates

**Symptoms:**
- Bot running but dashboard not updating
- WebSocket connected but no events

**Solutions:**
1. Check bot is emitting events (check bot logs)
2. Verify EventDispatcher is bound to event loop
3. Check WebSocket connection in browser DevTools
4. Restart backend server

---

## 📊 Event Types

### Events Bot Emits

| Event Type | When Emitted | Payload |
|------------|--------------|---------|
| `status_change` | Bot status changes | `{status, mode, error?}` |
| `new_result` | New number detected | `{spin_data, bet_decision?}` |
| `bet_placed` | Bet was placed | `{bet_type, bet_amount, gale_step}` |
| `bet_resolved` | Bet won/lost | `{result, profit_loss, balance}` |
| `balance_update` | Balance changed | `{balance}` |
| `error` | Error occurred | `{message, context?}` |

### Events Web Interface Handles

All events are received via WebSocket and update the dashboard:
- Status bar updates
- Live results panel
- Active bets panel
- Balance cards
- Performance charts
- Bet history table

---

##  Summary

** Full Integration:**
- Bot and web interface are fully integrated
- Real-time communication via WebSocket
- REST API for control and data
- State synchronization
- Configuration management

** Working Together:**
- Web interface controls bot (start/stop/mode)
- Bot sends events to web interface (real-time updates)
- Web interface displays bot state (status, results, stats)
- Web interface manages bot config (settings, presets)

** Ready to Use:**
- Start backend: `uvicorn backend.server.app:app --reload --port 8000`
- Start frontend: `cd web && npm run dev`
- Open dashboard: `http://localhost:3000`
- Start bot from dashboard!

---

**The bot and web interface work together seamlessly!** 🎉

