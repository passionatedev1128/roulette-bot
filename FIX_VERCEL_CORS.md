# Fix CORS Error for Vercel Deployment

## Problem
The frontend at `https://roulette-bot-zeta.vercel.app` is trying to connect to `http://localhost:8000` instead of your ngrok URL, causing CORS errors.

## Solution

### Step 1: Get Your ngrok URL

Make sure ngrok is running and copy your HTTPS URL:

```bash
# If ngrok is running, check:
# - ngrok web interface: http://localhost:4040
# - Or run: ngrok http 8000
```

Your ngrok URL should look like: `https://abc123.ngrok.io`

### Step 2: Set Vercel Environment Variables

1. Go to your Vercel project: https://vercel.com/dashboard
2. Navigate to your project: **roulette-bot-zeta** (or your project name)
3. Go to **Settings** → **Environment Variables**
4. Add these two variables for **Production** environment:

   ```
   Name: VITE_API_URL
   Value: https://bafflingly-unprofaned-veronique.ngrok-free.dev
   
   Name: VITE_WS_URL
   Value: wss://bafflingly-unprofaned-veronique.ngrok-free.dev/ws/events
   ```

   **Important**: 
   - Replace with your actual ngrok URL (e.g., `bafflingly-unprofaned-veronique.ngrok-free.dev`)
   - For `VITE_API_URL`: Use `https://` + domain (NO trailing slash)
   - For `VITE_WS_URL`: Use `wss://` + domain + `/ws/events` (secure WebSocket)
   - **DO NOT** put `https://` in the WS URL - use `wss://` only
   - The code will automatically normalize the URL if there's a mistake, but best practice is to set it correctly

5. **Save** the environment variables

### Step 3: Redeploy Frontend

After setting environment variables, you must redeploy:

1. Go to **Deployments** tab in Vercel
2. Click **"..."** on the latest deployment
3. Click **"Redeploy"**
   
   OR
   
   Push a new commit to trigger automatic deployment:
   ```bash
   git commit --allow-empty -m "Trigger redeploy with env vars"
   git push
   ```

### Step 4: Update Backend CORS

Update your local backend to allow the Vercel domain:

**Windows PowerShell:**
```powershell
$env:ROULETTE_WEB_CORS="https://roulette-bot-zeta.vercel.app,http://localhost:3000,http://127.0.0.1:3000"
# Restart your backend server (CTRL+C and restart uvicorn)
```

**Windows CMD:**
```cmd
set ROULETTE_WEB_CORS=https://roulette-bot-zeta.vercel.app,http://localhost:3000
# Restart your backend server
```

**Linux/Mac:**
```bash
export ROULETTE_WEB_CORS="https://roulette-bot-zeta.vercel.app,http://localhost:3000"
# Restart your backend server
```

**If using the helper script:**
When running `python start_with_ngrok.py`, enter `roulette-bot-zeta.vercel.app` when prompted.

### Step 5: Restart Backend

After setting CORS, restart your backend:

```bash
# Stop current backend (CTRL+C)
# Then restart:
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000
```

**Or if using the helper script:**
```bash
python start_with_ngrok.py
# Enter: roulette-bot-zeta.vercel.app
```

### Step 6: Verify

1. Check Vercel deployment is complete
2. Open `https://roulette-bot-zeta.vercel.app`
3. Open browser DevTools (F12) → Console
4. Should see WebSocket connection successful
5. No CORS errors

## Quick Checklist

- [ ] ngrok is running and accessible
- [ ] ngrok HTTPS URL is copied
- [ ] Vercel environment variables are set (`VITE_API_URL`, `VITE_WS_URL`)
- [ ] Vercel deployment is redeployed
- [ ] Backend CORS includes `https://roulette-bot-zeta.vercel.app`
- [ ] Backend is restarted with new CORS
- [ ] Test frontend at Vercel URL

## Troubleshooting

### Still seeing localhost:8000?

- Environment variables weren't set before build
- Solution: Redeploy after setting variables

### CORS errors persist?

- Backend CORS doesn't include Vercel domain
- Solution: Check `ROULETTE_WEB_CORS` environment variable and restart backend

### ngrok URL changed?

- Free ngrok URLs change on restart
- Solution: Update Vercel environment variables with new URL and redeploy

### WebSocket not connecting?

- Check `VITE_WS_URL` uses `wss://` not `ws://`
- Verify ngrok is forwarding WebSocket connections

## Next Steps

Once everything works:
- Consider ngrok paid plan for static domain (no URL changes)
- Set up monitoring for ngrok connection
- Keep ngrok running while backend is active

