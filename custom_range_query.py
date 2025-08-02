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
    """Get database connection with proper error handling."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def validate_date_range(start_date: str, end_date: str) -> tuple[date, date]:
    """Validate and parse date range."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        if start > end:
            raise ValueError("Start date must be before end date")
            
        return start, end
    except ValueError as e:
        print(f"Invalid date format: {e}")
        print("Expected format: YYYY-MM-DD")
        sys.exit(1)

def get_custom_range_metrics(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Calculate metrics for a custom date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Dictionary containing calculated metrics
    """
    start, end = validate_date_range(start_date, end_date)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Convert dates to datetime strings for database query
        start_datetime = datetime.combine(start, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.combine(end, datetime.max.time()).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Querying database for date range: {start_date} to {end_date}")
        print(f"Datetime range: {start_datetime} to {end_datetime}")
        
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
        WHERE timestamp >= ? AND timestamp <= ? AND n_cards >= 2
        """
        
        cursor.execute(query, (start_datetime, end_datetime))
        result = cursor.fetchone()
        
        if not result:
            print("No data found for the specified date range")
            return create_empty_response(start_date, end_date)
        
        # Calculate additional metrics
        total_days = (end - start).days + 1
        total_volume = result['total_mon_volume'] + result['total_jerry_volume'] + result['total_rbsd_volume']
        
        # Calculate averages
        avg_submissions_per_day = result['total_submissions'] / total_days if total_days > 0 else 0
        avg_active_addresses_per_day = result['total_active_addresses'] / total_days if total_days > 0 else 0
        avg_volume_per_day = total_volume / total_days if total_days > 0 else 0
        avg_cards_per_slip = result['avg_cards_per_slip'] or 0
        
        # Get activity over time (daily breakdown)
        daily_activity = get_daily_activity(cursor, start_datetime, end_datetime)
        
        # Create response structure
        response = {
            "success": True,
            "metadata": {
                "generated_at": datetime.now().isoformat() + "Z",
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_days": total_days
                },
                "query_type": "custom_range"
            },
            "total_metrics": {
                "total_submissions": result['total_submissions'],
                "total_active_addresses": result['total_active_addresses'],
                "total_mon_volume": result['total_mon_volume'],
                "total_jerry_volume": result['total_jerry_volume'],
                "total_rbsd_volume": result['total_rbsd_volume'],
                "total_volume": total_volume
            },
            "average_metrics": {
                "avg_submissions_per_day": round(avg_submissions_per_day, 2),
                "avg_active_addresses_per_day": round(avg_active_addresses_per_day, 2),
                "avg_volume_per_day": round(avg_volume_per_day, 2),
                "avg_cards_per_slip": round(avg_cards_per_slip, 2),
                "total_days": total_days
            },
            "activity_over_time": daily_activity,
            "user_breakdown": {
                "mon_users": result['mon_users'],
                "jerry_users": result['jerry_users'],
                "rbsd_users": result['rbsd_users']
            }
        }
        
        print(f"✅ Calculated metrics for {total_days} days:")
        print(f"   - Total submissions: {result['total_submissions']:,}")
        print(f"   - Active addresses: {result['total_active_addresses']:,}")
        print(f"   - MON volume: ${result['total_mon_volume']:,.2f}")
        print(f"   - JERRY volume: ${result['total_jerry_volume']:,.2f}")
        
        return response

def get_daily_activity(cursor, start_datetime: str, end_datetime: str) -> List[Dict[str, Any]]:
    """Get daily activity breakdown for the date range."""
    query = """
    SELECT 
        DATE(timestamp) as date,
        COUNT(*) as submissions,
        COUNT(DISTINCT from_address) as active_addresses,
        SUM(CASE WHEN token = 'MON' THEN CAST(amount AS REAL) ELSE 0 END) as mon_volume,
        SUM(CASE WHEN token = 'Jerry' THEN CAST(amount AS REAL) ELSE 0 END) as jerry_volume,
        SUM(CASE WHEN token = 'RBSD' THEN CAST(amount AS REAL) ELSE 0 END) as rbsd_volume
    FROM betting_transactions 
    WHERE timestamp >= ? AND timestamp <= ? AND n_cards >= 2
    GROUP BY DATE(timestamp)
    ORDER BY date
    """
    
    cursor.execute(query, (start_datetime, end_datetime))
    results = cursor.fetchall()
    
    daily_activity = []
    for row in results:
        daily_activity.append({
            "date": row['date'],
            "submissions": row['submissions'],
            "active_addresses": row['active_addresses'],
            "mon_volume": row['mon_volume'],
            "jerry_volume": row['jerry_volume'],
            "rbsd_volume": row['rbsd_volume'],
            "total_volume": row['mon_volume'] + row['jerry_volume'] + row['rbsd_volume']
        })
    
    return daily_activity

def create_empty_response(start_date: str, end_date: str) -> Dict[str, Any]:
    """Create an empty response when no data is found."""
    return {
        "success": True,
        "metadata": {
            "generated_at": datetime.now().isoformat() + "Z",
            "date_range": {
                "start_date": start_date,
                "end_date": end_date,
                "total_days": 0
            },
            "query_type": "custom_range"
        },
        "total_metrics": {
            "total_submissions": 0,
            "total_active_addresses": 0,
            "total_mon_volume": 0,
            "total_jerry_volume": 0,
            "total_rbsd_volume": 0,
            "total_volume": 0
        },
        "average_metrics": {
            "avg_submissions_per_day": 0,
            "avg_active_addresses_per_day": 0,
            "avg_volume_per_day": 0,
            "avg_cards_per_slip": 0,
            "total_days": 0
        },
        "activity_over_time": [],
        "user_breakdown": {
            "mon_users": 0,
            "jerry_users": 0,
            "rbsd_users": 0
        }
    }

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description="Calculate analytics for a custom date range")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    try:
        # Calculate metrics
        result = get_custom_range_metrics(args.start_date, args.end_date)
        
        # Output result
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Results saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 