# Environment Variables Template

This file contains the template for environment variables needed for Vercel deployment.

## Local Development

Create a `.env` file in the `web` directory (this file is git-ignored):

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/events
```

## Production (Vercel)

Set these in Vercel Dashboard:
1. Go to your project in Vercel
2. Navigate to **Settings** > **Environment Variables**
3. Add the following variables for **Production** environment:

```
VITE_API_URL = https://your-ngrok-url.ngrok.io
VITE_WS_URL = wss://your-ngrok-url.ngrok.io/ws/events
```

**Important**: 
- Replace `your-ngrok-url.ngrok.io` with your actual ngrok URL
- Use `https://` for API URL and `wss://` (secure WebSocket) for WS URL
- After setting variables, you need to redeploy for changes to take effect

## Getting ngrok URL

After starting ngrok with `ngrok http 8000`, you'll get a URL like:
- `https://abc123.ngrok.io`

Use this URL (with `https://`) for `VITE_API_URL` and convert to `wss://` for `VITE_WS_URL`.

## Notes

- `.env` files are git-ignored for security
- Vercel environment variables are required for production builds
- Changes to environment variables require a redeploy

