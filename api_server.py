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

# Add the current directory to Python path to import json_query
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing analytics logic
from json_query import FlexibleAnalytics, get_overall_slips_by_card_count, get_average_metrics

app = FastAPI(title="Betting Analytics API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    return sqlite3.connect('betting_transactions.db')

@app.get("/")
async def root():
    return {"message": "Betting Analytics API"}

@app.get("/api/analytics")
async def get_analytics():
    """Get all analytics data using existing json_query logic"""
    try:
        # Use your existing FlexibleAnalytics class
        with FlexibleAnalytics() as analytics:
            # Get all the data using your existing methods
            total_metrics = analytics.get_total_metrics()
            average_metrics = get_average_metrics(analytics)
            player_activity = analytics.get_player_activity_analysis()
            top_bettors = analytics.get_top_bettors()
            overall_slips_by_card_count = get_overall_slips_by_card_count(analytics)
            
            # Get timeframe data (daily, weekly, monthly)
            timeframes = {}
            for timeframe in ['daily', 'weekly', 'monthly']:
                timeframes[timeframe] = analytics.analyze_timeframe('2025-02-03', timeframe)
            
            # Get RBS stats
            rbs_stats_by_periods = analytics.get_rbs_stats_by_periods()
            
            # Combine all data
            analytics_data = {
                "success": True,
                "total_metrics": total_metrics,
                "average_metrics": average_metrics,
                "player_activity": player_activity,
                "top_bettors": top_bettors,
                "overall_slips_by_card_count": overall_slips_by_card_count,
                "timeframes": timeframes,
                "rbs_stats_by_periods": rbs_stats_by_periods
            }
            
            return analytics_data
            
    except Exception as e:
        print(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/rbs-stats")
async def get_rbs_stats():
    """Get RBS stats specifically"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query for RBS stats (similar to your json_query.py)
        query = """
        SELECT 
            strftime('%Y-%W', timestamp, 'weekday 0') as period,
            COUNT(DISTINCT player_address) as active_bettors,
            COUNT(*) as total_bets,
            SUM(amount) as total_volume,
            AVG(amount) as avg_bet_size
        FROM betting_transactions 
        WHERE timestamp >= date('now', '-30 days')
        GROUP BY period
        ORDER BY period DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        data = []
        for row in results:
            data.append({
                "period": row[0],
                "active_bettors": row[1],
                "total_bets": row[2],
                "total_volume": float(row[3]) if row[3] else 0,
                "avg_bet_size": float(row[4]) if row[4] else 0
            })
        
        conn.close()
        return {"rbs_stats": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/volume-data")
async def get_volume_data():
    """Get volume data for charts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query for volume data
        query = """
        SELECT 
            strftime('%Y-%m-%d', timestamp) as date,
            SUM(amount) as daily_volume,
            COUNT(*) as daily_bets
        FROM betting_transactions 
        WHERE timestamp >= date('now', '-7 days')
        GROUP BY date
        ORDER BY date
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        data = []
        for row in results:
            data.append({
                "date": row[0],
                "volume": float(row[1]) if row[1] else 0,
                "bets": row[2]
            })
        
        conn.close()
        return {"volume_data": data}
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