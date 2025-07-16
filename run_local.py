#!/usr/bin/env python3
"""
Local Development Runner
Runs the complete analytics pipeline locally for testing.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_database():
    """Check if database exists and has data"""
    db_path = Path("betting_transactions.db")
    if not db_path.exists():
        print("❌ Database file not found. Run betting_database.py first.")
        return False
    
    # Check if database has data
    import sqlite3
    try:
        conn = sqlite3.connect('betting_transactions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM betting_transactions")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            print("❌ Database is empty. Run betting_database.py first.")
            return False
        
        print(f"✅ Database has {count} transactions")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    print("🚀 Local Analytics Pipeline")
    print("=" * 40)
    
    # Check if database exists and has data
    if not check_database():
        print("\nTo create the database, run:")
        print("python betting_database.py")
        return
    
    # Step 1: Generate analytics JSON (optional, for fallback)
    print("\n📊 Generating analytics JSON (fallback)...")
    if run_command("python json_query.py", "Generating analytics JSON"):
        print("✅ Analytics JSON generated")
    else:
        print("⚠️  Analytics JSON generation failed, but API will still work")
    
    # Step 2: Start API server
    print("\n🌐 Starting API server...")
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Frontend will be available at: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Start the API server
        subprocess.run([sys.executable, "api_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main() 