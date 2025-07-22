from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any
import uvicorn
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')  # Load local environment first
load_dotenv()  # Load any other .env files

# Environment-based configuration
IS_PRODUCTION = os.getenv('IS_PRODUCTION', 'false').lower() == 'true'

# No longer need to import analytics logic since we're serving pre-computed JSON

app = FastAPI(title="Betting Analytics API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment-based paths
if IS_PRODUCTION:
    DB_PATH = "/app/data/betting_transactions.db"
    JSON_FILE_PATH = "new/public/analytics_dump.json"
else:
    DB_PATH = os.getenv('DB_PATH', 'betting_transactions.db')
    JSON_FILE_PATH = "new/public/analytics_dump.json"

@app.get("/")
async def root():
    return {
        "message": "Betting Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "/api/analytics": "Get complete analytics data",
            "/api/analytics/rbs-stats": "Get RBS statistics",
            "/api/analytics/volume-data": "Get volume data for charts",
            "/docs": "API documentation"
        }
    }

@app.get("/api/analytics")
async def get_analytics():
    """Get all analytics data from pre-computed JSON file (fast!)"""
    try:
        # Read from the pre-computed JSON file (instant!)
        json_file = Path(JSON_FILE_PATH)
        if json_file.exists():
            print("📁 Serving pre-computed analytics JSON...")
            with open(json_file, 'r') as f:
                data = json.load(f)
            print("✅ Analytics JSON served successfully")
            return data
        else:
            print("❌ Analytics JSON file not found")
            return {"error": "Analytics data not found. Run json_query.py first."}
    except Exception as e:
        print(f"❌ Error reading analytics JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/rbs-stats")
async def get_rbs_stats():
    """Get RBS stats from pre-computed JSON file"""
    try:
        json_file = Path(JSON_FILE_PATH)
        if json_file.exists():
            with open(json_file, 'r') as f:
                data = json.load(f)
            return {"rbs_stats": data.get("rbs_stats_by_periods", [])}
        else:
            return {"error": "Analytics data not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/volume-data")
async def get_volume_data():
    """Get volume data from pre-computed JSON file"""
    try:
        json_file = Path(JSON_FILE_PATH)
        if json_file.exists():
            with open(json_file, 'r') as f:
                data = json.load(f)
            # Extract volume data from the JSON
            activity_over_time = data.get("timeframes", {}).get("daily", {}).get("activity_over_time", [])
            
            # Format for volume charts
            volume_data = []
            for entry in activity_over_time[-7:]:  # Last 7 days
                volume_data.append({
                    "date": entry.get('period', ''),
                    "volume": entry.get('total_volume', 0),
                    "bets": entry.get('total_submissions', 0)
                })
            
            return {"volume_data": volume_data}
        else:
            return {"error": "Analytics data not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files (your Next.js build)
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve the frontend files"""
    frontend_path = Path("new/.next/server/app")
    file_path = frontend_path / path
    
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Fallback to index.html for SPA routing
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    print("Starting Betting Analytics API Server...")
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000) 