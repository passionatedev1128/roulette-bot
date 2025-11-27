# Running Web Interface & Bot on Same Computer

##  Yes! Everything Runs on the Same Computer

The web interface, backend API, and bot are all designed to run together on **one computer**. This is the standard setup and how it's meant to be used.

---

## 🖥️ Architecture on Same Computer

```
┌─────────────────────────────────────────┐
│         YOUR COMPUTER                     │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Browser (Chrome/Firefox/Edge)   │   │
│  │  http://localhost:3000            │   │
│  │  (Web Interface Dashboard)        │   │
│  └──────────────┬───────────────────┘   │
│                 │ HTTP/WebSocket         │
│                 ▼                        │
│  ┌──────────────────────────────────┐   │
│  │  Frontend Server (Vite)          │   │
│  │  Port 3000                       │   │
│  │  (React App)                     │   │
│  └──────────────┬───────────────────┘   │
│                 │ API Calls              │
│                 ▼                        │
│  ┌──────────────────────────────────┐   │
│  │  Backend Server (FastAPI)       │   │
│  │  Port 8000                      │   │
│  │  (REST API + WebSocket)          │   │
│  └──────────────┬───────────────────┘   │
│                 │                        │
│                 ▼                        │
│  ┌──────────────────────────────────┐   │
│  │  BotManager                      │   │
│  │  (Orchestrates Bot)              │   │
│  └──────────────┬───────────────────┘   │
│                 │                        │
│                 ▼                        │
│  ┌──────────────────────────────────┐   │
│  │  RouletteBot                     │   │
│  │  (The Actual Bot)                │   │
│  │  - Detects from screen           │   │
│  │  - Places bets                   │   │
│  │  - Runs strategy                 │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Roulette Game Browser          │   │
│  │  (Where bot detects from)       │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**All on the same computer!**

---

## 🚀 Quick Start (Same Computer)

### Step 1: Start Backend Server

**Terminal 1:**
```powershell
# Option A: Use start script
python start_web_interface.py
# Choose option 1: Start Backend

# Option B: Manual
uvicorn backend.server.app:app --reload --port 8000
```

**What this does:**
- Starts FastAPI backend on `http://localhost:8000`
- Creates BotManager (ready to control bot)
- Sets up WebSocket for real-time updates
- API available at `http://localhost:8000/api/...`

### Step 2: Start Frontend Server

**Terminal 2:**
```powershell
# Option A: Use start script
python start_web_interface.py
# Choose option 2: Start Frontend

# Option B: Manual
cd web
npm run dev
```

**What this does:**
- Starts Vite dev server on `http://localhost:3000`
- Serves React frontend
- Proxies API calls to `http://localhost:8000`
- WebSocket connects to `ws://localhost:8000`

### Step 3: Open Dashboard

**Browser:**
```
http://localhost:3000
```

**What you see:**
- Dashboard loads
- Connects to backend automatically
- Ready to control bot

### Step 4: Start Bot from Dashboard

1. Click "Start Bot" button
2. Bot starts running (in same computer)
3. Bot detects from your screen
4. Real-time updates appear in dashboard

---

## 📋 Port Configuration

### Default Ports (Same Computer)

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **Frontend** | 3000 | `http://localhost:3000` | Web dashboard |
| **Backend API** | 8000 | `http://localhost:8000` | REST API |
| **WebSocket** | 8000 | `ws://localhost:8000/ws/events` | Real-time events |

### Why These Ports?

- **Port 3000**: Standard React/Vite dev server port
- **Port 8000**: Standard FastAPI/uvicorn port
- **localhost**: All services on same computer

### Can You Change Ports?

**Yes, but not recommended:**

**Backend:**
```powershell
uvicorn backend.server.app:app --reload --port 9000
```

**Frontend:**
Edit `web/vite.config.js`:
```javascript
server: {
  port: 4000,
  proxy: {
    '/api': {
      target: 'http://localhost:9000',  // Match backend port
    }
  }
}
```

**But keep using 3000 and 8000 - it's simpler!**

---

## 🔧 How It Works (Same Computer)

### 1. All Services Local

**Everything runs locally:**
-  Frontend: `localhost:3000`
-  Backend: `localhost:8000`
-  Bot: Same process as backend
-  Browser: Same computer

**No network needed:**
- All communication is local
- Fast and secure
- No external dependencies

### 2. Communication Flow

**Browser  Frontend  Backend  Bot:**
```
Browser (localhost:3000)
  ↓ HTTP request
Frontend Server (localhost:3000)
  ↓ Proxy to
Backend API (localhost:8000)
  ↓ Control
BotManager  RouletteBot
```

**Bot  Backend  Frontend  Browser:**
```
RouletteBot
  ↓ Emit event
BotManager
  ↓ Publish
EventDispatcher
  ↓ WebSocket
Backend (localhost:8000)
  ↓ WebSocket
Frontend (localhost:3000)
  ↓ Update UI
Browser (localhost:3000)
```

### 3. File System Access

**All on same computer:**
-  Config files: `config/default_config.json`
-  Logs: `logs/` directory
-  Templates: `winning-number_templates/`
-  All accessible locally

---

##  Benefits of Same Computer Setup

### 1. **Simple Setup**
- No network configuration needed
- No firewall issues
- No remote access setup
- Just start and go!

### 2. **Fast Performance**
- Local communication (very fast)
- No network latency
- Real-time updates instant
- Low overhead

### 3. **Secure**
- All traffic stays local
- No external exposure
- No security concerns
- Private to your computer

### 4. **Easy Debugging**
- All logs in one place
- Easy to monitor
- Simple troubleshooting
- Direct access to files

### 5. **Resource Efficient**
- Single computer handles everything
- No need for multiple machines
- Shared resources
- Efficient memory usage

---

##  Typical Usage (Same Computer)

### Scenario: Running Bot with Dashboard

**Setup:**
1. **Terminal 1**: Backend server running
2. **Terminal 2**: Frontend server running
3. **Browser**: Dashboard open at `localhost:3000`
4. **Game Browser**: Roulette game open (for bot to detect)

**What happens:**
- Bot detects from game browser (same computer)
- Bot places bets (same computer)
- Dashboard shows updates (same computer)
- All in real-time (same computer)

**Everything on one computer!**

---

## 🔍 Verification

### Check Everything is Local

**1. Check Backend:**
```powershell
curl http://localhost:8000/ping
# Should return: {"status": "ok"}
```

**2. Check Frontend:**
```
Open: http://localhost:3000
Should see: Dashboard loads
```

**3. Check WebSocket:**
```
Browser DevTools (F12)  Console
Should see: "WebSocket connected"
```

**4. Check Bot:**
```
Dashboard  Click "Start Bot"
Should see: Status changes to "Running"
```

### All on Same Computer 

---

## 🐛 Troubleshooting (Same Computer)

### Issue: Port Already in Use

**Error:**
```
Address already in use: 8000
```

**Solution:**
1. Find what's using the port:
   ```powershell
   # Windows
   netstat -ano | findstr :8000
   
   # Kill the process or use different port
   ```

2. Or stop the conflicting service

### Issue: Can't Connect to Backend

**Error:**
```
Failed to fetch: http://localhost:8000/api/status
```

**Solutions:**
1. Check backend is running: `http://localhost:8000/ping`
2. Check frontend proxy config in `web/vite.config.js`
3. Check CORS settings in `backend/server/app.py`

### Issue: WebSocket Not Connecting

**Error:**
```
WebSocket connection failed
```

**Solutions:**
1. Verify backend is running
2. Check WebSocket endpoint: `ws://localhost:8000/ws/events`
3. Check browser console for errors
4. Verify firewall isn't blocking (unlikely on localhost)

---

## 📊 Resource Usage (Same Computer)

### Typical Resource Usage

**Backend Server:**
- CPU: Low (~5-10%)
- Memory: ~50-100 MB
- Network: Minimal (local only)

**Frontend Server:**
- CPU: Low (~2-5%)
- Memory: ~30-50 MB
- Network: Minimal (local only)

**Bot (when running):**
- CPU: Medium (~10-20%)
- Memory: ~100-200 MB
- Screen capture: Minimal overhead

**Total:**
- CPU: ~20-35% (when bot running)
- Memory: ~200-350 MB
- Very manageable on modern computers!

---

## 🌐 Can You Access from Other Computers?

### Option 1: Keep Everything Local (Recommended)

**Current setup:**
- Everything on `localhost`
- Only accessible from same computer
- Most secure and simple

### Option 2: Allow Remote Access

**If you want to access dashboard from another computer:**

**Backend:**
```powershell
# Already configured! (--host 0.0.0.0)
uvicorn backend.server.app:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
Edit `web/vite.config.js`:
```javascript
server: {
  host: "0.0.0.0",  // Allow external access
  port: 3000,
}
```

**Then access from other computer:**
```
http://YOUR_COMPUTER_IP:3000
```

**But bot still runs on original computer!**

---

##  Summary

** Everything on Same Computer:**
- Frontend: `localhost:3000`
- Backend: `localhost:8000`
- Bot: Same process as backend
- Browser: Same computer
- Game: Same computer

** Simple Setup:**
1. Start backend (Terminal 1)
2. Start frontend (Terminal 2)
3. Open dashboard in browser
4. Start bot from dashboard

** All Local:**
- Fast performance
- Secure (no network exposure)
- Easy to debug
- Resource efficient

** Ready to Use:**
- Just run the start script
- Everything works together
- No complex configuration needed

---

**The web system and bot are designed to work together on the same computer!** 🎉

