# Deployment Setup Summary

This document summarizes the changes made to enable Vercel deployment with local backend.

## What Was Changed

### 1. Backend CORS Configuration (`backend/server/app.py`)
- Updated CORS to support environment variable `ROULETTE_WEB_CORS`
- Now accepts Vercel domain origins
- Default still includes localhost for development

### 2. Vercel Configuration (`web/vercel.json`)
- Added Vercel configuration file
- Configured for Vite framework
- Set up proper rewrites for SPA routing

### 3. Environment Variables Setup
- Created `web/ENV_TEMPLATE.md` with instructions
- Environment variables are configured via Vercel dashboard
- Uses `VITE_API_URL` and `VITE_WS_URL` (already in code)

### 4. Helper Scripts
- **`start_with_ngrok.py`**: Automated script to start backend + ngrok
  - Checks ngrok installation
  - Starts ngrok tunnel
  - Detects ngrok URL automatically
  - Sets CORS environment variable
  - Starts backend server

### 5. Documentation
- **`VERCEL_DEPLOYMENT_GUIDE.md`**: Comprehensive deployment guide
- **`QUICK_DEPLOY.md`**: Quick reference for deployment steps

## How to Use

### Quick Start

1. **Install ngrok** (if not installed):
   ```bash
   npm install -g ngrok
   # Or download from ngrok.com
   ngrok config add-authtoken YOUR_TOKEN
   ```

2. **Start backend with ngrok**:
   ```bash
   python start_with_ngrok.py
   ```
   This will:
   - Start ngrok tunnel
   - Show you the public URL
   - Start backend server with proper CORS

3. **Deploy to Vercel**:
   - Go to vercel.com
   - Import your repository
   - Set root directory to `web`
   - Add environment variables (see ngrok URL from step 2)
   - Deploy

4. **Update CORS after deployment**:
   - Get your Vercel URL (e.g., `https://your-app.vercel.app`)
   - Update backend CORS environment variable
   - Restart backend

### Manual Process

See `QUICK_DEPLOY.md` for step-by-step manual instructions.

## Architecture

```
┌─────────────────┐
│   Vercel        │  Frontend (React/Vite)
│   (Public)      │  └─> Connects to ─┐
└─────────────────┘                   │
                                      │
                              ┌───────▼──────────┐
                              │   ngrok Tunnel   │
                              │  (Public HTTPS)  │
                              └───────┬──────────┘
                                      │
┌─────────────────┐                   │
│  Your Computer  │  Backend (FastAPI)│
│   (Local)       │  └────────────────┘
│                 │
│  Bot (Python)   │
└─────────────────┘
```

## Environment Variables

### Frontend (Vercel)
- `VITE_API_URL`: Backend API URL (e.g., `https://abc123.ngrok.io`)
- `VITE_WS_URL`: WebSocket URL (e.g., `wss://abc123.ngrok.io/ws/events`)

### Backend (Local)
- `ROULETTE_WEB_CORS`: Comma-separated origins (e.g., `https://your-app.vercel.app,http://localhost:3000`)

## Important Notes

1. **ngrok Free Tier**: URLs change on restart. Update Vercel env vars after each restart.
2. **Keep ngrok Running**: Must stay running while backend is active.
3. **CORS Updates**: Backend must be restarted after updating CORS environment variable.
4. **Environment Variables**: Vercel requires redeploy after changing environment variables.

## Files Created/Modified

### New Files
- `web/vercel.json` - Vercel configuration
- `web/.gitignore` - Frontend gitignore
- `web/ENV_TEMPLATE.md` - Environment variable template
- `start_with_ngrok.py` - Helper script
- `VERCEL_DEPLOYMENT_GUIDE.md` - Full guide
- `QUICK_DEPLOY.md` - Quick reference
- `DEPLOYMENT_SUMMARY.md` - This file

### Modified Files
- `backend/server/app.py` - CORS configuration

## Next Steps

1. Follow `QUICK_DEPLOY.md` for deployment
2. Test the deployed frontend
3. Consider ngrok static domain for production (paid)
4. Set up monitoring for ngrok connection status

## Troubleshooting

See `VERCEL_DEPLOYMENT_GUIDE.md` for detailed troubleshooting section.

