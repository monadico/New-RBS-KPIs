#!/usr/bin/env python3
"""
Custom Range Query Script
Calculates analytics metrics for a specific date range by querying the database directly.
"""

import sqlite3
import json
import argparse
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import sys

# Database path
DB_PATH = "betting_transactions.db"

def get_connection():
    """Get database connection with proper datetime handling."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

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
    """Get analytics metrics for a custom date range."""
    
    if not validate_date_range(start_date, end_date):
        raise ValueError("Invalid date range")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Query transactions within the date range (filter out claiming transactions with 0 cards)
        query = """
        SELECT
            COUNT(*) as total_submissions,
            COUNT(DISTINCT from_address) as total_active_addresses,
            SUM(CASE WHEN token = 'MON' THEN CAST(amount AS REAL) ELSE 0 END) as total_mon_volume,
            SUM(CASE WHEN token = 'Jerry' THEN CAST(amount AS REAL) ELSE 0 END) as total_jerry_volume,
            SUM(CASE WHEN token = 'RBSD' THEN CAST(amount AS REAL) ELSE 0 END) as total_rbsd_volume,
            COUNT(DISTINCT CASE WHEN token = 'MON' THEN from_address END) as mon_users,
            COUNT(DISTINCT CASE WHEN token = 'Jerry' THEN from_address END) as jerry_users,
            COUNT(DISTINCT CASE WHEN token = 'RBSD' THEN from_address END) as rbsd_users,
            AVG(CAST(n_cards AS REAL)) as avg_cards_per_slip
        FROM betting_transactions
        WHERE DATE(timestamp, 'utc') >= ? AND DATE(timestamp, 'utc') <= ? AND n_cards >= 2
        """
        
        cursor.execute(query, (start_date, end_date))
        result = cursor.fetchone()
        
        if not result or result[0] == 0:
            return create_empty_response(start_date, end_date)
        
        # Calculate average submissions per day
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        days_in_range = (end_dt - start_dt).days + 1
        avg_submissions_per_day = result[0] / days_in_range if days_in_range > 0 else 0
        
        return {
            "total_metrics": {
                "total_submissions": result[0],
                "total_active_addresses": result[1],
                "total_mon_volume": result[2],
                "total_jerry_volume": result[3],
                "total_rbsd_volume": result[4],
                "mon_users": result[5],
                "jerry_users": result[6],
                "rbsd_users": result[7]
            },
            "average_metrics": {
                "avg_submissions_per_day": round(avg_submissions_per_day, 2),
                "avg_cards_per_slip": round(result[8], 2)
            },
            "date_range": {
                "start_date": start_date,
                "end_date": end_date,
                "days_in_range": days_in_range
            }
        }

def get_daily_activity(start_date: str, end_date: str) -> list:
    """Get daily activity breakdown for the date range."""
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
        SELECT
            DATE(timestamp, 'utc') as date,
            COUNT(*) as submissions,
            COUNT(DISTINCT from_address) as active_addresses,
            SUM(CASE WHEN token = 'MON' THEN CAST(amount AS REAL) ELSE 0 END) as mon_volume,
            SUM(CASE WHEN token = 'Jerry' THEN CAST(amount AS REAL) ELSE 0 END) as jerry_volume,
            AVG(CAST(n_cards AS REAL)) as avg_cards_per_slip
        FROM betting_transactions
        WHERE DATE(timestamp, 'utc') >= ? AND DATE(timestamp, 'utc') <= ? AND n_cards >= 2
        GROUP BY DATE(timestamp, 'utc')
        ORDER BY date
        """
        
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()
        
        daily_data = []
        for row in results:
            daily_data.append({
                "date": row[0],
                "submissions": row[1],
                "active_addresses": row[2],
                "mon_volume": row[3],
                "jerry_volume": row[4],
                "avg_cards_per_slip": round(row[5], 2)
            })
        
        return daily_data

def create_empty_response(start_date: str, end_date: str) -> Dict[str, Any]:
    """Create an empty response structure for date ranges with no data."""
    return {
        "total_metrics": {
            "total_submissions": 0,
            "total_active_addresses": 0,
            "total_mon_volume": 0.0,
            "total_jerry_volume": 0.0,
            "total_rbsd_volume": 0.0,
            "mon_users": 0,
            "jerry_users": 0,
            "rbsd_users": 0
        },
        "average_metrics": {
            "avg_submissions_per_day": 0.0,
            "avg_cards_per_slip": 0.0
        },
        "date_range": {
            "start_date": start_date,
            "end_date": end_date,
            "days_in_range": 0
        }
    }

def main():
    """Test the custom range query functionality."""
    # Test with June 2025
    start_date = "2025-06-01"
    end_date = "2025-06-30"
    
    print(f"Testing custom range query for {start_date} to {end_date}")
    
    try:
        result = get_custom_range_metrics(start_date, end_date)
        print("Results:")
        print(json.dumps(result, indent=2))
        
        # Also test daily breakdown
        daily_data = get_daily_activity(start_date, end_date)
        print(f"\nDaily breakdown (showing first 5 days):")
        for day in daily_data[:5]:
            print(f"  {day['date']}: {day['submissions']} submissions, {day['active_addresses']} active addresses")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 