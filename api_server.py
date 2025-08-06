from fastapi import FastAPI, HTTPException, Query
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
from custom_range_query import get_custom_range_metrics
from claiming_custom_range_query import get_custom_range_metrics as get_claiming_custom_range_metrics
from top_claimers_query import get_top_claimers, format_claimer_data

# Load environment variables
load_dotenv('.env.local')  # Load local environment first
load_dotenv()  # Load any other .env files

# Environment-based configuration
IS_PRODUCTION = os.getenv('IS_PRODUCTION', 'false').lower() == 'true'

# No longer need to import analytics logic since we're serving pre-computed JSON

app = FastAPI(title="Betting Analytics API", version="1.0.0")

# Add CORS middleware to allow frontend requests
# Define allowed origins based on environment
if IS_PRODUCTION:
    ALLOWED_ORIGINS = [
        "https://rarebetsportsanalytics.io",
        "https://c4woc08wws0c44gk4sswgwg8.173.249.24.245.sslip.io",
        "http://localhost:3000",  # For local development
        "http://localhost:3001",  # For local development
    ]
else:
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment-based paths
if IS_PRODUCTION:
    DB_PATH = "/app/data/betting_transactions.db"
    JSON_FILE_PATH = "/app/new/public/analytics_dump.json"
    CLAIMING_JSON_FILE_PATH = "/app/new/public/claiming_analytics_dump.json"
    WINRATE_JSON_FILE_PATH = "/app/new/public/winrate_analytics_dump.json"
else:
    DB_PATH = os.getenv('DB_PATH', 'betting_transactions.db')
    JSON_FILE_PATH = "new/public/analytics_dump.json"
    CLAIMING_JSON_FILE_PATH = "new/public/claiming_analytics_dump.json"
    WINRATE_JSON_FILE_PATH = "new/public/winrate_analytics_dump.json"

@app.get("/")
async def root():
    return {
        "message": "Betting Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "/api/analytics": "Get complete analytics data",
            "/api/analytics/rbs-stats": "Get RBS statistics",
            "/api/analytics/volume-data": "Get volume data for charts",
            "/api/claiming/analytics": "Get complete claiming analytics data",
            "/api/claiming/stats": "Get claiming statistics",
            "/api/claiming/volume-data": "Get claiming volume data for charts",
            "/api/custom-range": "Get analytics for custom date range (start_date&end_date)",
            "/api/claiming/custom-range": "Get claiming analytics for custom date range (start_date&end_date)",
            "/api/top-claimers": "Get top claimers with betting data and profit calculations",
            "/api/winrate": "Get winrate analytics data",
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

@app.get("/api/claiming/analytics")
async def get_claiming_analytics():
    """Get all claiming analytics data from pre-computed JSON file"""
    try:
        json_file = Path(CLAIMING_JSON_FILE_PATH)
        if json_file.exists():
            print("📁 Serving pre-computed claiming analytics JSON...")
            with open(json_file, 'r') as f:
                data = json.load(f)
            print("✅ Claiming analytics JSON served successfully")
            return data
        else:
            print("❌ Claiming analytics JSON file not found")
            return {"error": "Claiming analytics data not found. Run claiming_query.py first."}
    except Exception as e:
        print(f"❌ Error reading claiming analytics JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/claiming/stats")
async def get_claiming_stats():
    """Get claiming stats from pre-computed JSON file"""
    try:
        json_file = Path(CLAIMING_JSON_FILE_PATH)
        if json_file.exists():
            with open(json_file, 'r') as f:
                data = json.load(f)
            return {"claiming_stats": data.get("claiming_stats_by_periods", [])}
        else:
            return {"error": "Claiming analytics data not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/claiming/volume-data")
async def get_claiming_volume_data():
    """Get claiming volume data from pre-computed JSON file"""
    try:
        json_file = Path(CLAIMING_JSON_FILE_PATH)
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
                    "claims": entry.get('claims', 0)
                })
            
            return {"volume_data": volume_data}
        else:
            return {"error": "Claiming analytics data not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/custom-range")
async def get_custom_range_analytics(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """Get analytics data for a custom date range by querying the database directly"""
    try:
        print(f"🔍 Custom range query: {start_date} to {end_date}")
        
        # Call the custom range query function
        result = get_custom_range_metrics(start_date, end_date)
        
        print(f"✅ Custom range query completed successfully")
        return result
        
    except Exception as e:
        print(f"❌ Error in custom range query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/claiming/custom-range")
async def get_claiming_custom_range_analytics(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """Get claiming analytics data for a custom date range by querying the database directly"""
    try:
        print(f"🔍 Claiming custom range query: {start_date} to {end_date}")

        # Call the claiming custom range query function
        result = get_claiming_custom_range_metrics(start_date, end_date)

        print(f"✅ Claiming custom range query completed successfully")
        return result

    except Exception as e:
        print(f"❌ Error in claiming custom range query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/top-claimers")
async def get_top_claimers_api(limit: int = Query(20, description="Number of top claimers to return")):
    """Get top claimers with betting data and profit calculations"""
    try:
        print(f"🔍 Fetching top {limit} claimers...")
        
        # Get top claimers data
        top_claimers = get_top_claimers(limit)
        
        if not top_claimers:
            return {"error": "No claimers found"}
        
        # Format the data for API response
        formatted_claimers = format_claimer_data(top_claimers)
        
        print(f"✅ Top claimers query completed successfully")
        return {
            "top_claimers": formatted_claimers,
            "total_count": len(formatted_claimers),
            "summary": {
                "total_claimed": sum(c['total_claimed'] for c in formatted_claimers),
                "total_claims": sum(c['total_claims'] for c in formatted_claimers),
                "total_bet": sum(c['total_bet'] for c in formatted_claimers),
                "total_submissions": sum(c['total_submissions'] for c in formatted_claimers)
            }
        }
        
    except Exception as e:
        print(f"❌ Error in top claimers query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/winrate")
async def get_winrate_analytics():
    """Get winrate analytics data from pre-computed JSON file"""
    try:
        json_file = Path(WINRATE_JSON_FILE_PATH)
        if json_file.exists():
            print("📁 Serving pre-computed winrate analytics JSON...")
            with open(json_file, 'r') as f:
                data = json.load(f)
            print("✅ Winrate analytics JSON served successfully")
            return data
        else:
            print("❌ Winrate analytics JSON file not found")
            return {"error": "Winrate data not found. Run winrate_query.py first."}
    except Exception as e:
        print(f"❌ Error reading winrate analytics JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/raffle/select-winner")
async def select_raffle_winner(request: dict):
    """Select a raffle winner based on RareLink submissions within a time range"""
    try:
        start_time = request.get("start_time")
        end_time = request.get("end_time")
        
        if not start_time or not end_time:
            raise HTTPException(status_code=400, detail="Start time and end time are required")
        
        print(f"🎰 Raffle selection: {start_time} to {end_time}")
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query RareLink submissions within the time range
        cursor.execute("""
            SELECT 
                bet_id,
                from_address,
                timestamp,
                n_cards
            FROM betting_transactions 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """, [start_time, end_time])
        
        submissions = cursor.fetchall()
        
        if not submissions:
            raise HTTPException(status_code=404, detail="No RareLink submissions found in the specified time range")
        
        # Process submissions to create entry pool
        entry_pool = []
        user_entries = {}
        total_submissions = len(submissions)
        
        for submission in submissions:
            bet_id, wallet_address, timestamp, n_cards = submission
            entry_count = n_cards or 0
            
            # Add user to entry pool based on number of player props
            for i in range(entry_count):
                entry_pool.append(wallet_address)
            
            # Track user entries for winner info
            if wallet_address not in user_entries:
                user_entries[wallet_address] = 0
            user_entries[wallet_address] += entry_count
        
        if not entry_pool:
            raise HTTPException(status_code=404, detail="No valid entries found in the specified time range")
        
        # Select random winner from entry pool
        import random
        winner_address = random.choice(entry_pool)
        winner_entries = user_entries[winner_address]
        
        # Find the bet_id for the winner
        winner_bet_id = None
        for submission in submissions:
            if submission[1] == winner_address:  # wallet_address
                winner_bet_id = submission[0]  # bet_id
                break
        
        # Get example transactions for the winner from the raffle time window
        cursor.execute("""
            SELECT 
                tx_hash,
                timestamp,
                token,
                amount,
                n_cards,
                bet_id,
                block_number
            FROM betting_transactions 
            WHERE from_address = ? 
            AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, [winner_address, start_time, end_time])
        
        winner_transactions = cursor.fetchall()
        
        # Format transactions for API response
        formatted_transactions = []
        for tx in winner_transactions:
            tx_hash, timestamp, token, amount, n_cards, bet_id, block_number = tx
            formatted_transactions.append({
                "tx_hash": tx_hash,
                "timestamp": timestamp,
                "token": token,
                "amount": amount,
                "n_cards": n_cards,
                "bet_id": bet_id,
                "block_number": block_number
            })
        
        result = {
            "winner": {
                "bet_id": winner_bet_id,
                "wallet_address": winner_address,
                "entries": winner_entries
            },
            "total_entries": len(entry_pool),
            "total_submissions": total_submissions,
            "unique_participants": len(user_entries),
            "selection_window": {
                "start_time": start_time,
                "end_time": end_time
            },
            "example_transactions": formatted_transactions
        }
        
        conn.close()
        print(f"✅ Raffle winner selected successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in raffle selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files (your Next.js build)
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve the frontend files"""
    if IS_PRODUCTION:
        frontend_path = Path("frontend-deployment/.next/server/app")
    else:
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