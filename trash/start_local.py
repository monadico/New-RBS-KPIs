#!/usr/bin/env python3
"""
Local Development Startup Script
===============================

Starts both backend and frontend for local development.
"""

import subprocess
import sys
import os
import time
import signal
import threading

def start_backend():
    """Start the Flask backend."""
    print("🚀 Starting backend...")
    backend_dir = os.path.join(os.getcwd(), "backend")
    subprocess.run([sys.executable, "app.py"], cwd=backend_dir)

def start_frontend():
    """Start the React frontend."""
    print("🎨 Starting frontend...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    subprocess.run(["npm", "start"], cwd=frontend_dir)

def main():
    """Start both services."""
    print("🏁 Starting local development environment...")
    print("📊 Backend: http://localhost:5000")
    print("🎨 Frontend: http://localhost:3000")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main() 