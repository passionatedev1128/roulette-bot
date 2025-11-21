# Fix: Frontend Not Reading Configuration

## Problem
WebSocket connection works in Vercel, but the frontend doesn't read/display the configuration.

## Possible Causes

1. **API call failing silently** - Config fetch might be failing without visible errors
2. **Response format mismatch** - Backend response might not match frontend expectations
3. **Network/CORS issues** - API calls might be blocked
4. **Missing error handling** - Errors might not be displayed to user

## Fixes Applied

### 1. Added Error Handling and Logging
- Added retry logic (3 retries) to config query
- Added console logging to track config fetch process
- Added error callbacks to see what's failing

### 2. Improved ConfigForm Component
- Added logging to see what data is received
- Added fallback handling for unexpected data structures
- Better error messages

### 3. Added UI Error Display
- Shows loading state while fetching config
- Displays error message if config fails to load
- Provides "Retry" button to manually retry

### 4. Enhanced API Client
- Added try-catch in fetchConfig
- Better error logging with response details
- Validates response format

## How to Debug

1. **Open Browser Console** (F12)
   - Check for "Config fetched successfully" or "Failed to fetch config" messages
   - Look for any API errors or CORS issues
   - Check Network tab to see if `/api/config/` request is being made

2. **Check Network Tab**
   - Filter for "config"
   - Check if request to `https://your-ngrok-url/api/config/` is being made
   - Verify status code (should be 200)
   - Check response body structure

3. **Verify Backend**
   - Test backend directly: `https://your-ngrok-url/api/config/`
   - Should return: `{"config": {...}}`
   - Check backend logs for errors

4. **Check Environment Variables**
   - Verify `VITE_API_URL` is set correctly in Vercel
   - Should be your ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`)
   - Redeploy after setting/changing environment variables

## Expected Behavior

1. **On Page Load:**
   - Console shows: "Config fetched successfully: {config: {...}}"
   - ConfigForm shows: "ConfigForm received configData: {config: {...}}"

2. **If Config Fails:**
   - UI shows red error box with error message
   - "Retry" button appears
   - Console shows error details

3. **If Loading:**
   - UI shows "Carregando configuração..." message

## Testing Checklist

- [ ] Open browser DevTools (F12) → Console
- [ ] Check for config fetch logs
- [ ] Open Network tab → Filter "config"
- [ ] Verify `/api/config/` request succeeds
- [ ] Check response has `{"config": {...}}` structure
- [ ] Verify ConfigForm displays configuration fields
- [ ] Test saving configuration works

## Common Issues

### Issue: "Failed to fetch config" Error

**Causes:**
- Backend not accessible via ngrok URL
- CORS not configured correctly
- API endpoint returning error

**Solution:**
1. Test backend URL directly: `https://your-ngrok-url/api/config/`
2. Check backend CORS includes Vercel domain
3. Check backend logs for errors

### Issue: Config Data is Empty/Undefined

**Causes:**
- Response structure doesn't match expectations
- Backend returning empty config

**Solution:**
1. Check backend response in Network tab
2. Verify backend `bot_manager.get_config()` returns valid config
3. Check console logs for "ConfigForm received configData" message

### Issue: Config Loads but Form is Empty

**Causes:**
- Config structure mismatch
- ConfigForm not parsing data correctly

**Solution:**
1. Check console for "ConfigForm received configData" log
2. Verify data has `config` property
3. Check ConfigForm useEffect is running

## Next Steps

1. Deploy the updated frontend to Vercel
2. Check browser console for logs
3. Test config loading
4. Report any errors found in console

## Manual Test

Test the API endpoint directly:
```bash
# Replace with your ngrok URL
curl https://your-ngrok-url.ngrok.io/api/config/
```

Should return:
```json
{
  "config": {
    "detection": {...},
    "strategy": {...},
    ...
  }
}
```

