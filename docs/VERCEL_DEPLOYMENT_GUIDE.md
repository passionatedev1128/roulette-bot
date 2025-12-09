# Vercel Deployment Guide

This guide explains how to deploy the frontend to Vercel while keeping the backend and bot running locally on your machine.

## Architecture Overview

- **Frontend**: Deployed on Vercel (publicly accessible)
- **Backend**: Running locally on your machine (exposed via ngrok tunnel)
- **Bot**: Running locally on your machine

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional): `npm install -g vercel`
3. **ngrok**: Install from [ngrok.com](https://ngrok.com) or via npm: `npm install -g ngrok`
   - Sign up for a free ngrok account
   - Get your authtoken from the ngrok dashboard

## Step-by-Step Deployment

### Step 1: Set Up ngrok Authentication

```bash
# Set your ngrok authtoken (get it from https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### Step 2: Start Your Local Backend

In one terminal, start your backend server:

```bash
# Make sure you're in the project root
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000
```

Verify it's working:
- Open http://localhost:8000/ping in your browser
- Should return: `{"status": "ok"}`

### Step 3: Expose Local Backend with ngrok

In another terminal, start ngrok to expose your local backend:

```bash
# Expose port 8000
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**IMPORTANT**: Copy the `https://` URL (e.g., `https://abc123.ngrok.io`). You'll need this for the frontend configuration.

### Step 4: Update Backend CORS

Set the CORS environment variable to allow your Vercel domain. You can do this in two ways:

#### Option A: Environment Variable (Recommended)

Before starting the backend, set the environment variable:

**Windows PowerShell:**
```powershell
$env:ROULETTE_WEB_CORS="https://roulette-bot-zeta.vercel.app,http://localhost:3000"
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000
```

**Windows CMD:**
```cmd
set ROULETTE_WEB_CORS="https://roulette-bot-zeta.vercel.app,http://localhost:3000"
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000
```

**Linux/Mac:**
```bash
export ROULETTE_WEB_CORS="https://roulette-bot-zeta.vercel.app,http://localhost:3000"
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000
```

**Note**: Replace `your-app.vercel.app` with your actual Vercel domain (you'll get this after deployment).

#### Option B: Update After Deployment

You can also update CORS after deploying to Vercel. Just restart your backend with the correct CORS origins.

### Step 5: Deploy Frontend to Vercel

#### Option A: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"New Project"**
3. Import your Git repository (GitHub, GitLab, or Bitbucket)
4. Configure the project:
   - **Root Directory**: Select `web` folder
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. **Set Environment Variables** (before deploying):
   - Go to **Settings** > **Environment Variables**
   - Add the following:
     ```
     VITE_API_URL = https://your-ngrok-url.ngrok.io
     VITE_WS_URL = wss://your-ngrok-url.ngrok.io/ws/events
     ```
     **Replace `your-ngrok-url.ngrok.io` with your actual ngrok URL from Step 3**

6. Click **"Deploy"**

#### Option B: Deploy via Vercel CLI

1. Navigate to the `web` directory:
   ```bash
   cd web
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel --prod
   ```

4. When prompted, set environment variables:
   - `VITE_API_URL`: Your ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`)
   - `VITE_WS_URL`: Your ngrok WebSocket URL (e.g., `wss://abc123.ngrok.io/ws/events`)

### Step 6: Update Environment Variables After Deployment

After deployment, Vercel will give you a URL like `https://roulette-bot-zeta.vercel.app`.

1. Go to your Vercel project dashboard
2. Navigate to **Settings** > **Environment Variables**
3. Update the backend CORS environment variable on your local machine:
   ```bash
   # Replace with your actual Vercel URL
   export ROULETTE_WEB_CORS="https://roulette-bot-zeta.vercel.app,http://localhost:3000"
   ```
4. Restart your backend server

### Step 7: Test the Deployment

1. Open your Vercel URL (e.g., `https://roulette-bot-zeta.vercel.app`)
2. Check browser console for any connection errors
3. Verify the frontend can connect to your backend:
   - Status should show "Connected"
   - API calls should work
   - WebSocket should connect

## Important Notes

### ngrok Free Tier Limitations

- **Temporary URLs**: Free ngrok URLs change every time you restart ngrok
- **Session Duration**: Free tier has connection limits
- **Solution**: Use ngrok's paid plans for static URLs, or update Vercel environment variables each time you restart ngrok

### Keeping ngrok Running

You must keep ngrok running while your backend is active. If ngrok stops:
1. Restart ngrok: `ngrok http 8000`
2. Get the new URL
3. Update Vercel environment variables with the new URL
4. Redeploy the frontend (or wait for automatic rebuild)

### Alternative: Use ngrok with Static Domain (Recommended for Production)

1. Sign up for ngrok paid plan (starts at $8/month)
2. Reserve a static domain in ngrok dashboard
3. Update ngrok config:
   ```yaml
   # ~/.ngrok2/ngrok.yml
   authtoken: YOUR_AUTHTOKEN
   tunnels:
     backend:
       proto: http
       addr: 8000
       domain: your-static-domain.ngrok.io
   ```
4. Start with: `ngrok start backend`
5. Use this static URL in Vercel environment variables (no need to update after restarts)

## Troubleshooting

### CORS Errors

**Symptom**: Browser console shows CORS errors

**Solution**:
1. Verify backend CORS environment variable includes your Vercel domain
2. Restart backend after updating CORS
3. Check that ngrok URL matches Vercel environment variables

### WebSocket Connection Failed

**Symptom**: WebSocket can't connect

**Solution**:
1. Verify `VITE_WS_URL` uses `wss://` (secure WebSocket) for HTTPS ngrok URL
2. Check ngrok is forwarding WebSocket connections (should work automatically)
3. Verify backend is running and accessible via ngrok

### Backend Not Accessible

**Symptom**: Frontend can't reach backend API

**Solution**:
1. Verify ngrok is running and shows "Online" status
2. Test ngrok URL directly: `https://your-ngrok-url.ngrok.io/ping`
3. Check Vercel environment variables are set correctly
4. Redeploy frontend after changing environment variables

### Environment Variables Not Working

**Symptom**: Frontend still uses localhost URLs

**Solution**:
1. Vercel environment variables require a **redeploy** to take effect
2. After setting/updating variables, trigger a new deployment
3. Check that variables are set for "Production" environment

## Quick Reference Commands

```bash
# Terminal 1: Start Backend
export ROULETTE_WEB_CORS="https://roulette-bot-zeta.vercel.app,http://localhost:3000"
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000

# Terminal 2: Start ngrok
ngrok http 8000

# Terminal 3: Start Bot (if needed)
python main.py --config config/default_config.json
```

## Production Checklist

- [ ] ngrok is running and accessible
- [ ] Backend CORS includes Vercel domain
- [ ] Vercel environment variables are set correctly
- [ ] Frontend is deployed and accessible
- [ ] WebSocket connection works
- [ ] API calls work from deployed frontend
- [ ] Bot can start/stop from deployed frontend

## Next Steps

Once deployed:
1. Share the Vercel URL with your client
2. Keep your local backend and ngrok running
3. Monitor ngrok dashboard for connection status
4. Consider setting up a service to auto-restart ngrok if it crashes

