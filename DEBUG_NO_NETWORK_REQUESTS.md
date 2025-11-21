# Debug: No Network Requests Showing

## Problem
After refreshing the page, no requests/responses appear in the Network tab.

## Possible Causes

### 1. **Demo Mode Enabled** (Most Likely)
If demo mode is enabled, the app uses mock data instead of making API calls.

**Check:**
- Open browser console (F12)
- Look for: "Demo mode check:" or "App initialized:"
- Check localStorage: `localStorage.getItem('demoMode')`

**Solution:**
- Disable demo mode: `localStorage.removeItem('demoMode')`
- Refresh page
- Or add `?demo=false` to URL

### 2. **Environment Variables Not Set**
Vercel environment variables might not be set correctly.

**Check:**
- Open browser console
- Look for: "API Configuration:"
- Verify `API_BASE_URL` is not `http://localhost:8000`

**Solution:**
1. Go to Vercel → Settings → Environment Variables
2. Set `VITE_API_URL` = `https://your-ngrok-url.ngrok.io`
3. Redeploy frontend

### 3. **CORS/Network Errors Blocking Requests**
Requests might be failing before they appear in Network tab.

**Check:**
- Open browser console (F12)
- Look for error messages
- Check Network tab → Filter → "Failed" or "Blocked"

**Solution:**
- Verify backend CORS includes Vercel domain
- Check ngrok is running
- Test backend directly: `https://your-ngrok-url/api/config/`

### 4. **React Query Not Enabled**
Queries might be disabled.

**Check:**
- Check console for query errors
- Look for React Query logs

**Solution:**
- Queries should auto-enable on mount
- Check if demo mode is preventing queries

## Debugging Steps

### Step 1: Check Console Logs

After refreshing, open browser console (F12) and look for:

1. **API Configuration:**
   ```
   API Configuration: { VITE_API_URL: "...", API_BASE_URL: "..." }
   ```
   - Should show your ngrok URL, not localhost

2. **App Initialized:**
   ```
   App initialized: { demoMode: false, willMakeAPICalls: true, ... }
   ```
   - `demoMode` should be `false`
   - `willMakeAPICalls` should be `true`

3. **API Request Logs:**
   ```
   [API Request] GET https://your-ngrok-url/api/status
   ```
   - Should see requests being made

4. **Demo Mode Check:**
   ```
   Demo mode check: { isDemo: false, ... }
   ```
   - Should show `isDemo: false`

### Step 2: Check Network Tab

1. Open DevTools (F12) → Network tab
2. Refresh page (F5)
3. Filter by "XHR" or "Fetch"
4. Look for requests to `/api/status`, `/api/config`, etc.
5. Check if requests are:
   - **Pending** - Request is stuck
   - **Failed** - Request failed (check error)
   - **Blocked** - CORS or network blocked
   - **No requests** - Nothing being sent

### Step 3: Check LocalStorage

Open browser console and run:
```javascript
console.log('Demo mode:', localStorage.getItem('demoMode'));
console.log('All localStorage:', {...localStorage});
```

**If demo mode is set:**
```javascript
localStorage.removeItem('demoMode');
location.reload();
```

### Step 4: Check Environment Variables

Open browser console and run:
```javascript
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
console.log('VITE_WS_URL:', import.meta.env.VITE_WS_URL);
```

**Expected:**
- Should show your ngrok URLs (not undefined or localhost)

**If undefined:**
- Environment variables not set in Vercel
- Need to set them and redeploy

### Step 5: Test Backend Directly

Test if backend is accessible:
```bash
# Replace with your ngrok URL
curl https://your-ngrok-url.ngrok.io/api/config/
```

**Expected:**
- Returns JSON: `{"config": {...}}`

**If fails:**
- Backend not accessible via ngrok
- ngrok might not be running
- Check ngrok URL is correct

## Quick Fixes

### Fix 1: Disable Demo Mode
```javascript
// In browser console:
localStorage.removeItem('demoMode');
location.reload();
```

### Fix 2: Clear All Demo Data
```javascript
// In browser console:
localStorage.clear();
location.reload();
```

### Fix 3: Force API Calls
```javascript
// In browser console:
// This will trigger a manual API call
fetch('https://your-ngrok-url.ngrok.io/api/config/')
  .then(r => r.json())
  .then(d => console.log('Config:', d))
  .catch(e => console.error('Error:', e));
```

### Fix 4: Check URL Parameters
Remove any `?demo=true` from URL:
- Change: `https://your-app.vercel.app/?demo=true`
- To: `https://your-app.vercel.app/`

## Expected Behavior After Fix

1. **Console shows:**
   - "API Configuration:" with ngrok URL
   - "App initialized:" with `demoMode: false`
   - "[API Request]" messages for each API call

2. **Network tab shows:**
   - Multiple requests to `/api/status`, `/api/config`, `/api/balance`, etc.
   - All requests with status 200 (or appropriate status codes)
   - Response data visible in Network tab

3. **App works:**
   - Config loads and displays
   - Status updates
   - Data appears in UI

## Common Issues

### Issue: Console shows "API_BASE_URL: http://localhost:8000"

**Cause:** Environment variable not set in Vercel

**Fix:**
1. Go to Vercel → Settings → Environment Variables
2. Add `VITE_API_URL` = `https://your-ngrok-url.ngrok.io`
3. Redeploy

### Issue: Console shows "demoMode: true"

**Cause:** Demo mode enabled in localStorage or URL

**Fix:**
```javascript
localStorage.removeItem('demoMode');
location.reload();
```

### Issue: Network tab shows requests but all failed

**Cause:** Backend not accessible or CORS issue

**Fix:**
1. Check ngrok is running
2. Test backend directly
3. Check backend CORS includes Vercel domain

### Issue: No requests at all, no console errors

**Cause:** Queries not enabled or demo mode blocking

**Fix:**
1. Check console for "Demo mode check:" log
2. Disable demo mode
3. Check queries have `enabled: true`

## What I Added

1. **Enhanced Logging:**
   - API configuration logged on load
   - All API requests logged
   - All API responses logged
   - Demo mode status logged
   - Query errors logged

2. **Better Error Handling:**
   - Error callbacks on all queries
   - Interceptors on axios for request/response logging

3. **Debug Information:**
   - App initialization status
   - Demo mode detection
   - Environment variable status

## Next Steps

1. Deploy updated frontend to Vercel
2. Open browser console (F12)
3. Check logs for:
   - API configuration
   - Demo mode status
   - API requests being made
4. Check Network tab for requests
5. Report what you see in console

