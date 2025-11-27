#!/usr/bin/env python3
"""
Helper script to start the backend server with ngrok tunnel.
This script helps expose your local backend to the internet for Vercel deployment.
"""

import os
import subprocess
import sys
import time
import json
from pathlib import Path

def check_ngrok_installed():
    """Check if ngrok is installed."""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False

def get_ngrok_url():
    """Get the ngrok tunnel URL from ngrok API."""
    try:
        import urllib.request
        import json
        response = urllib.request.urlopen('http://localhost:4040/api/tunnels', timeout=2)
        if response.status == 200:
            data = json.loads(response.read().decode())
            tunnels = data.get('tunnels', [])
            if tunnels:
                # Prefer HTTPS tunnel
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        return tunnel.get('public_url')
                # Fallback to HTTP
                return tunnels[0].get('public_url')
    except Exception:
        pass
    return None

def main():
    """Main entry point."""
    print("=" * 60)
    print("Roulette Bot - Backend with ngrok Tunnel")
    print("=" * 60)
    print()
    
    # Check ngrok installation
    if not check_ngrok_installed():
        print(" Error: ngrok is not installed!")
        print()
        print("Please install ngrok:")
        print("  1. Visit https://ngrok.com/download")
        print("  2. Or install via npm: npm install -g ngrok")
        print("  3. Or install via pip: pip install pyngrok")
        print()
        print("After installation, set your authtoken:")
        print("  ngrok config add-authtoken YOUR_AUTHTOKEN")
        sys.exit(1)
    
    print(" ngrok is installed")
    print()
    
    # Ask for Vercel domain (optional, for CORS)
    vercel_domain = input("Enter your Vercel domain (e.g., your-app.vercel.app) [optional]: ").strip()
    
    # Build CORS origins
    cors_origins = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    if vercel_domain:
        cors_origins = f"https://{vercel_domain},{cors_origins}"
    
    print()
    print("Starting ngrok tunnel...")
    print("(This will expose your local backend on port 8000)")
    print()
    
    # Start ngrok in background
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', '8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a bit for ngrok to start
    print("Waiting for ngrok to initialize...")
    time.sleep(3)
    
    # Try to get ngrok URL
    ngrok_url = None
    max_attempts = 10
    for i in range(max_attempts):
        ngrok_url = get_ngrok_url()
        if ngrok_url:
            break
        time.sleep(1)
    
    if not ngrok_url:
        print("  Warning: Could not automatically detect ngrok URL")
        print("   Please check ngrok web interface at: http://localhost:4040")
        print("   Copy the HTTPS URL and update Vercel environment variables")
    else:
        print(" ngrok tunnel established!")
        print()
        print("=" * 60)
        print("BACKEND URL (for Vercel environment variables):")
        print("=" * 60)
        print(f"  API URL:  {ngrok_url}")
        print(f"  WS URL:   {ngrok_url.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/events")
        print()
        print("Update these in Vercel dashboard:")
        print("  Settings > Environment Variables")
        print("    VITE_API_URL =", ngrok_url)
        print("    VITE_WS_URL =", f"{ngrok_url.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/events")
        print()
        print("Ngrok web interface: http://localhost:4040")
        print("=" * 60)
        print()
    
    # Set CORS environment variable
    os.environ['ROULETTE_WEB_CORS'] = cors_origins
    
    print("Starting backend server...")
    print("Backend will be accessible at:")
    print(f"  Local:  http://localhost:8000")
    if ngrok_url:
        print(f"  Public: {ngrok_url}")
    print()
    print("Press CTRL+C to stop both ngrok and backend")
    print()
    
    try:
        # Start backend server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.server.app:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\nStopping...")
        ngrok_process.terminate()
        ngrok_process.wait()
        print(" Stopped ngrok and backend")

if __name__ == "__main__":
    main()

