# Quick Deploy to Vercel - Step by Step

## Prerequisites Checklist
- [ ] ngrok installed (`npm install -g ngrok` or download from ngrok.com)
- [ ] ngrok authtoken configured (`ngrok config add-authtoken YOUR_TOKEN`)
- [ ] Vercel account created (vercel.com)
- [ ] Git repository pushed (GitHub/GitLab/Bitbucket)

## Deployment Steps

### 1. Start Backend with ngrok (Terminal 1)

**Option A: Use helper script (Recommended)**
```bash
python start_with_ngrok.py
```

**Option B: Manual**
```bash
# Terminal 1a: Start ngrok
ngrok http 8000

# Terminal 1b: Start backend (in another terminal)
# Windows PowerShell:
$env:ROULETTE_WEB_CORS="http://localhost:3000"  # Add Vercel domain later
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000

# Windows CMD:
set ROULETTE_WEB_CORS=http://localhost:3000
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000

# Linux/Mac:
export ROULETTE_WEB_CORS="http://localhost:3000"
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000
```

**Copy the ngrok HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### 2. Deploy Frontend to Vercel

#### Via Vercel Dashboard:

1. Go to [vercel.com](https://vercel.com) → **New Project**
2. Import your Git repository
3. Configure:
   - **Root Directory**: `web` (click "Edit" and set to `web`)
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. **Before clicking Deploy**, go to **Environment Variables**:
   - Click "Add New"
   - Name: `VITE_API_URL`, Value: `https://abc123.ngrok.io` (your ngrok URL)
   - Click "Add New" again
   - Name: `VITE_WS_URL`, Value: `wss://abc123.ngrok.io/ws/events` (replace `https` with `wss`)
   - Make sure both are set for **Production** environment
5. Click **Deploy**

#### Via Vercel CLI:

```bash
cd web
npm install -g vercel
vercel login
vercel --prod
```

When prompted for environment variables, enter:
- `VITE_API_URL`: `https://abc123.ngrok.io`
- `VITE_WS_URL`: `wss://abc123.ngrok.io/ws/events`

### 3. Update Backend CORS

After deployment, Vercel gives you a URL like `https://your-app.vercel.app`

Update CORS on your local backend:

**Windows PowerShell:**
```powershell
$env:ROULETTE_WEB_CORS="https://your-app.vercel.app,http://localhost:3000"
# Restart backend server (CTRL+C and restart)
```

**Linux/Mac:**
```bash
export ROULETTE_WEB_CORS="https://your-app.vercel.app,http://localhost:3000"
# Restart backend server (CTRL+C and restart)
```

### 4. Test

1. Open your Vercel URL: `https://your-app.vercel.app`
2. Check browser console (F12) for errors
3. Verify status shows "Connected"
4. Test bot controls

## Important Notes

⚠️ **ngrok Free Tier**:
- URL changes every time you restart ngrok
- You must update Vercel environment variables and redeploy after each ngrok restart

💡 **Solution**: Use ngrok static domain (paid plan) for production, or keep ngrok running continuously

## Troubleshooting

**CORS Error?**
- Check backend CORS includes Vercel domain
- Restart backend after updating CORS

**WebSocket Error?**
- Verify `VITE_WS_URL` uses `wss://` (secure WebSocket)
- Check ngrok is running

**API Not Working?**
- Test ngrok URL directly: `https://your-ngrok-url.ngrok.io/ping`
- Verify Vercel environment variables are set
- Redeploy after changing environment variables

## Next Steps

See `VERCEL_DEPLOYMENT_GUIDE.md` for detailed documentation.

