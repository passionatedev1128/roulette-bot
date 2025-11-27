# WebSocket Connection Troubleshooting

## Common Issues and Solutions

### Issue: "WebSocket connection to 'ws://localhost:8000/ws/events' failed"

This error means the frontend cannot connect to the backend WebSocket endpoint.

##  Quick Fixes

### 1. Verify Backend is Running

**Check backend is running:**
```powershell
# Test backend health
curl http://localhost:8000/ping
# Should return: {"status": "ok"}
```

**If backend is not running:**
```powershell
uvicorn backend.server.app:app --reload --port 8000
```

### 2. Verify WebSocket Endpoint

**Test WebSocket endpoint directly:**
```javascript
// In browser console (F12)
const ws = new WebSocket('ws://localhost:8000/ws/events');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
ws.onmessage = (msg) => console.log('Message:', msg.data);
```

### 3. Check Port Configuration

**Verify ports match:**
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- WebSocket: `ws://localhost:8000/ws/events`

### 4. Check Browser Console

**Open browser DevTools (F12)  Console:**
- Look for WebSocket connection messages
- Check for CORS errors
- Check for network errors

### 5. Verify Backend Logs

**Check backend terminal for:**
```
INFO: WebSocket client connected
```

If you don't see this, the WebSocket connection isn't reaching the backend.

## 🔧 Step-by-Step Debugging

### Step 1: Test Backend API

```powershell
# Test REST API
curl http://localhost:8000/api/status

# Test WebSocket endpoint (using wscat if installed)
# Install: npm install -g wscat
wscat -c ws://localhost:8000/ws/events
```

### Step 2: Check Frontend Configuration

**Verify WebSocket URL in `web/src/api/client.js`:**
```javascript
export const WS_EVENTS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/events';
```

**Check if environment variable is set:**
```powershell
# Should match backend port
echo $env:VITE_WS_URL
```

### Step 3: Check CORS Configuration

**Verify CORS allows your frontend origin:**
- Backend should allow: `http://localhost:3000`
- Check `backend/server/app.py` CORS settings

### Step 4: Check Firewall

**Windows Firewall might be blocking:**
- Allow Python/uvicorn through firewall
- Or temporarily disable firewall for testing

### Step 5: Check Network Tab

**In browser DevTools  Network tab:**
- Filter by "WS" (WebSocket)
- Look for connection attempts
- Check status codes
- Check error messages

## 🐛 Common Error Codes

### Error Code 1006 (Abnormal Closure)
- **Cause:** Connection closed unexpectedly
- **Solution:** Check backend is running and WebSocket endpoint is accessible

### Error Code 1002 (Protocol Error)
- **Cause:** Invalid WebSocket protocol
- **Solution:** Verify URL is correct: `ws://localhost:8000/ws/events` (not `http://`)

### Error Code 1000 (Normal Closure)
- **Cause:** Connection closed normally
- **Solution:** This is normal when page unloads

##  Verification Checklist

- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 3000
- [ ] WebSocket URL is correct: `ws://localhost:8000/ws/events`
- [ ] No firewall blocking connections
- [ ] Backend logs show "WebSocket client connected"
- [ ] Browser console shows "WebSocket connected"
- [ ] No CORS errors in browser console

## 🔍 Advanced Debugging

### Enable Detailed Logging

**Backend:**
```python
# Already added logging in websocket.py
# Check backend terminal for WebSocket logs
```

**Frontend:**
```javascript
// Already added logging in useWebSocket.js
// Check browser console for connection messages
```

### Test WebSocket Manually

**Using browser console:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events');

ws.onopen = () => {
  console.log(' Connected!');
};

ws.onmessage = (event) => {
  console.log('📨 Received:', JSON.parse(event.data));
};

ws.onerror = (error) => {
  console.error(' Error:', error);
};

ws.onclose = (event) => {
  console.log('🔌 Closed:', event.code, event.reason);
};
```

### Check Backend WebSocket Route

**Verify route is registered:**
```python
# In backend/server/app.py
app.include_router(websocket_router)  # Should be present
```

##  Tips

1. **Start backend first** - Always start backend before frontend
2. **Wait for backend to be ready** - Give backend a few seconds to initialize
3. **Check both terminals** - Monitor both backend and frontend logs
4. **Use browser DevTools** - Network tab shows WebSocket connections
5. **Test with curl/wscat** - Verify WebSocket works outside browser

## 🚀 Quick Test

**Terminal 1 - Backend:**
```powershell
uvicorn backend.server.app:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd web
npm run dev
```

**Browser:**
1. Open `http://localhost:3000`
2. Open DevTools (F12)  Console
3. Should see: "WebSocket connected: ws://localhost:8000/ws/events"
4. Backend terminal should show: "INFO: WebSocket client connected"

---

**If still having issues, check:**
1. Backend logs for errors
2. Browser console for errors
3. Network tab for connection attempts
4. Firewall settings
5. Port availability

