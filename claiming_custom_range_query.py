#!/usr/bin/env python3
import sqlite3
import json
from datetime import datetime, date
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')  # Load local environment first
load_dotenv()  # Load any other .env files

# Environment-based configuration
IS_PRODUCTION = os.getenv('IS_PRODUCTION', 'false').lower() == 'true'

if IS_PRODUCTION:
    DB_PATH = "/app/data/comprehensive_claiming_transactions_fixed.db"
else:
    DB_PATH = "data/comprehensive_claiming_transactions_fixed.db"

def get_connection():
    """Get database connection with proper datetime handling."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def validate_date_range(start_date: str, end_date: str) -> bool:
    """Validate that the date range is reasonable."""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start > end:
            return False
            
        # Check if range is not too large (e.g., max 1 year)
        delta = end - start
        if delta.days > 365:
            return False
            
        return True
    except ValueError:
        return False

def get_custom_range_metrics(start_date: str, end_date: str) -> Dict[str, Any]:
    """Get claiming analytics metrics for a custom date range."""
    
    if not validate_date_range(start_date, end_date):
        raise ValueError("Invalid date range")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Query claiming transactions within the date range
        query = """
        SELECT
            COUNT(*) as total_claims,
            COUNT(DISTINCT from_address) as total_unique_claimers,
            SUM(CASE WHEN token = 'MON' THEN CAST(amount AS REAL) ELSE 0 END) as total_mon_claimed,
            SUM(CASE WHEN token = 'JERRY' THEN CAST(amount AS REAL) ELSE 0 END) as total_jerry_claimed
        FROM claiming_transactions
        WHERE DATE(timestamp, 'utc') >= ? AND DATE(timestamp, 'utc') <= ?
        """
        
        cursor.execute(query, (start_date, end_date))
        result = cursor.fetchone()
        
        if not result or result[0] == 0:
            return create_empty_response(start_date, end_date)
        
        # Calculate average claims per day
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        days_in_range = (end_dt - start_dt).days + 1
        avg_claims_per_day = result[0] / days_in_range if days_in_range > 0 else 0
        
        return {
            "total_metrics": {
                "total_claims": result[0],
                "total_unique_claimers": result[1],
                "total_mon_claimed": result[2],
                "total_jerry_claimed": result[3]
            },
            "average_metrics": {
                "avg_claims_per_day": round(avg_claims_per_day, 2)
            },
            "date_range": {
                "start_date": start_date,
                "end_date": end_date,
                "days_in_range": days_in_range
            }
        }

def get_daily_activity(start_date: str, end_date: str) -> list:
    """Get daily claiming activity breakdown for the date range."""
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
        SELECT
            DATE(timestamp, 'utc') as date,
            COUNT(*) as claims,
            COUNT(DISTINCT from_address) as unique_claimers,
            SUM(CASE WHEN token = 'MON' THEN CAST(amount AS REAL) ELSE 0 END) as mon_claimed,
            SUM(CASE WHEN token = 'JERRY' THEN CAST(amount AS REAL) ELSE 0 END) as jerry_claimed
        FROM claiming_transactions
        WHERE DATE(timestamp, 'utc') >= ? AND DATE(timestamp, 'utc') <= ?
        GROUP BY DATE(timestamp, 'utc')
        ORDER BY date
        """
        
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()
        
        daily_data = []
        for row in results:
            daily_data.append({
                "date": row[0],
                "claims": row[1],
                "unique_claimers": row[2],
                "mon_claimed": row[3],
                "jerry_claimed": row[4]
            })
        
        return daily_data

def create_empty_response(start_date: str, end_date: str) -> Dict[str, Any]:
    """Create an empty response structure for date ranges with no data."""
    return {
        "total_metrics": {
            "total_claims": 0,
            "total_unique_claimers": 0,
            "total_mon_claimed": 0.0,
            "total_jerry_claimed": 0.0
        },
        "average_metrics": {
            "avg_claims_per_day": 0.0
        },
        "date_range": {
            "start_date": start_date,
            "end_date": end_date,
            "days_in_range": 0
        }
    }

def main():
    """Test the claiming custom range query functionality."""
    # Test with June 2025
    start_date = "2025-06-01"
    end_date = "2025-06-30"
    
    print(f"Testing claiming custom range query for {start_date} to {end_date}")
    
    try:
        result = get_custom_range_metrics(start_date, end_date)
        print("Results:")
        print(json.dumps(result, indent=2))
        
        # Also test daily breakdown
        daily_data = get_daily_activity(start_date, end_date)
        print(f"\nDaily breakdown (showing first 5 days):")
        for day in daily_data[:5]:
            print(f"  {day['date']}: {day['claims']} claims, {day['unique_claimers']} unique claimers")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 