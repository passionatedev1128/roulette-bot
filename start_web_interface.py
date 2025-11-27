"""
Quick start script for the web interface.
Starts both backend and frontend servers.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    # Check Python packages
    try:
        import fastapi
        import uvicorn
        print(" Backend dependencies OK")
    except ImportError:
        print(" Backend dependencies missing. Run: pip install -r requirements.txt")
        return False
    
    # Check Node.js and npm
    try:
        # Use shell=True on Windows to find node in PATH 
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f" Node.js installed: {result.stdout.strip()}")
        else:
            print(" Node.js not found. Install from: https://nodejs.org/")
            return False
    except FileNotFoundError:
        print(" Node.js not found. Install from: https://nodejs.org/")
        print("   After installation, restart your terminal and try again.")
        return False
    
    # Check if web/node_modules exists
    web_dir = Path("web")
    node_modules = web_dir / "node_modules"
    if not node_modules.exists():
        print("  Frontend dependencies not installed.")
        print("   Run: cd web && npm install")
        return False
    
    print(" Frontend dependencies OK")
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("\n" + "=" * 60)
    print("Starting Backend Server...")
    print("=" * 60)
    print("Backend will run on: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("Press CTRL+C to stop\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.server.app:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\nBackend server stopped.")

def start_frontend():
    """Start the Vite frontend server."""
    print("\n" + "=" * 60)
    print("Starting Frontend Server...")
    print("=" * 60)
    print("Frontend will run on: http://localhost:3000")
    print("Press CTRL+C to stop\n")
    
    web_dir = Path("web")
    if not web_dir.exists():
        print(f" Error: 'web' directory not found!")
        print(f"   Current directory: {os.getcwd()}")
        return
    
    # Check if node_modules exists
    node_modules = web_dir / "node_modules"
    if not node_modules.exists():
        print("  Warning: node_modules not found!")
        print("   Run 'cd web && npm install' first")
        response = input("   Install dependencies now? (y/n): ").strip().lower()
        if response == 'y':
            os.chdir(web_dir)
            try:
                subprocess.run(["npm", "install"], shell=True, check=True)
                print(" Dependencies installed!")
            except subprocess.CalledProcessError:
                print(" Failed to install dependencies")
                os.chdir("..")
                return
            except FileNotFoundError:
                print(" npm not found. Please install Node.js from https://nodejs.org/")
                os.chdir("..")
                return
            os.chdir("..")
        else:
            print(" Cannot start frontend without dependencies")
            return
    
    os.chdir(web_dir)
    
    try:
        # Use shell=True on Windows to find npm in PATH
        subprocess.run(["npm", "run", "dev"], shell=True)
    except FileNotFoundError:
        print("\n Error: npm not found!")
        print("   Please install Node.js from: https://nodejs.org/")
        print("   After installation, restart your terminal and try again.")
    except KeyboardInterrupt:
        print("\nFrontend server stopped.")
    finally:
        os.chdir("..")

def main():
    """Main entry point."""
    print("=" * 60)
    print("Roulette Bot - Web Interface Starter")
    print("=" * 60)
    
    if not check_dependencies():
        print("\n Please install missing dependencies first.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Choose an option:")
    print("=" * 60)
    print("1. Start Backend only (FastAPI server)")
    print("2. Start Frontend only (React/Vite server)")
    print("3. Start Both (requires 2 terminals)")
    print("4. Exit")
    print("=" * 60)
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        start_backend()
    elif choice == "2":
        start_frontend()
    elif choice == "3":
        print("\n  To run both servers, you need 2 terminals:")
        print("   Terminal 1: python start_web_interface.py (choose option 1)")
        print("   Terminal 2: python start_web_interface.py (choose option 2)")
        print("\n   Or manually:")
        print("   Terminal 1: uvicorn backend.server.app:app --reload --port 8000")
        print("   Terminal 2: cd web && npm run dev")
    elif choice == "4":
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Exiting...")
        sys.exit(1)

if __name__ == "__main__":
    main()

