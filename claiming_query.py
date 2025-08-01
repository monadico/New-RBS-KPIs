#!/usr/bin/env python3
import json
import shutil
import gzip
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

# Fix for Python 3.12+ SQLite datetime deprecation warning
def adapt_datetime(val):
    return val.isoformat()

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')  # Load local environment first
load_dotenv()  # Load any other .env files

# Environment-based configuration
IS_PRODUCTION = os.getenv('IS_PRODUCTION', 'false').lower() == 'true'

if IS_PRODUCTION:
    DB_PATH = "/app/data/comprehensive_claiming_transactions.db"
    OUTPUT_FILE = "/app/claiming_analytics_dump.json"
    FRONTEND_PUBLIC = "/app/new/public/claiming_analytics_dump.json"
    FRONTEND_DEPLOYMENT_PUBLIC = "/app/frontend-deployment/public/claiming_analytics_dump.json"
    COMPRESSED_FILE = "/app/new/public/claiming_analytics_dump.json.gz"
else:
    DB_PATH = os.getenv('CLAIMING_DB_PATH', 'comprehensive_claiming_transactions_fixed.db')
    OUTPUT_FILE = "claiming_analytics_dump.json"
    FRONTEND_PUBLIC = "new/public/claiming_analytics_dump.json"
    FRONTEND_DEPLOYMENT_PUBLIC = "frontend-deployment/public/claiming_analytics_dump.json"
    COMPRESSED_FILE = "new/public/claiming_analytics_dump.json.gz"

class ClaimingAnalytics:
    """Main analytics class for claiming transaction analysis."""
    
    def __init__(self, db_path: str = "comprehensive_claiming_transactions.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Enter context manager, connect to DB."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager, close connection."""
        if self.conn:
            self.conn.close()

    def get_total_metrics(self) -> Dict:
        """Get total metrics for all time."""
        query = """
        SELECT
            COUNT(DISTINCT tx_hash) as total_claims,
            COUNT(DISTINCT from_address) as total_unique_claimers,
            SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as total_mon_volume,
            SUM(CASE WHEN token = 'JERRY' THEN amount ELSE 0 END) as total_jerry_volume,
            SUM(CASE WHEN token = 'RBSD' THEN amount ELSE 0 END) as total_rbsd_volume
        FROM claiming_transactions
        """
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return {
            'total_claims': result[0] or 0,
            'total_unique_claimers': result[1] or 0,
            'total_mon_volume': result[2] or 0.0,
            'total_jerry_volume': result[3] or 0.0,
            'total_rbsd_volume': result[4] or 0.0
        }

    def get_activity_over_time(self, start_date: str, timeframe: str, since_timestamp: Optional[str] = None) -> List[Dict]:
        """Get activity over time data for the specified timeframe and start date."""
        timeframe_map = {
            'day': {
                'period_generator': f"""
                    WITH RECURSIVE periods AS (
                        SELECT 
                            DATE('{start_date}') as period_start,
                            DATE('{start_date}') as period_end,
                            1 as period_number
                        
                        UNION ALL
                        
                        SELECT 
                            DATE(period_start, '+1 day') as period_start,
                            DATE(period_start, '+1 day') as period_end,
                            period_number + 1 as period_number
                        FROM periods
                        WHERE period_start <= DATE('now')
                    )
                """,
                'period_columns': 'period_start, period_end, period_number',
                'date_format': '%Y-%m-%d'
            },
            'week': {
                'period_generator': f"""
                    WITH RECURSIVE periods AS (
                        SELECT 
                            DATE('{start_date}', 'weekday 0', '-6 days') as period_start,
                            DATE('{start_date}', 'weekday 0', '+0 days') as period_end,
                            1 as period_number
                        
                        UNION ALL
                        
                        SELECT 
                            DATE(period_start, '+7 days') as period_start,
                            DATE(period_end, '+7 days') as period_end,
                            period_number + 1 as period_number
                        FROM periods
                        WHERE period_start <= DATE('now')
                    )
                """,
                'period_columns': 'period_start, period_end, period_number',
                'date_format': '%Y-%m-%d'
            },
            'month': {
                'period_generator': f"""
                    WITH RECURSIVE periods AS (
                        SELECT 
                            DATE('{start_date}', 'start of month') as period_start,
                            DATE('{start_date}', 'start of month', '+1 month', '-1 day') as period_end,
                            1 as period_number
                        
                        UNION ALL
                        
                        SELECT 
                            DATE(period_start, '+1 month') as period_start,
                            DATE(period_start, '+2 months', '-1 day') as period_end,
                            period_number + 1 as period_number
                        FROM periods
                        WHERE period_start <= DATE('now')
                    )
                """,
                'period_columns': 'period_start, period_end, period_number',
                'date_format': '%Y-%m'
            }
        }

        if timeframe not in timeframe_map:
            raise ValueError(f"Invalid timeframe: {timeframe}")

        config = timeframe_map[timeframe]
        
        # Add timestamp filter if since_timestamp is provided
        timestamp_filter = ""
        if since_timestamp:
            timestamp_filter = f"AND t.timestamp > '{since_timestamp}'"
        
        query = f"""
        {config['period_generator']},
        first_time_claimers AS (
            SELECT 
                from_address,
                MIN(timestamp) as first_claim_date
            FROM claiming_transactions
            GROUP BY from_address
        )
        SELECT 
            p.period_start,
            p.period_end,
            p.period_number,
            COUNT(t.tx_hash) as claims,
            COUNT(DISTINCT t.from_address) as active_claimers,
            COUNT(DISTINCT CASE WHEN DATE(ftc.first_claim_date) >= p.period_start AND DATE(ftc.first_claim_date) <= p.period_end THEN t.from_address END) as new_claimers,
            SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) as mon_volume,
            SUM(CASE WHEN t.token = 'JERRY' THEN t.amount ELSE 0 END) as jerry_volume,
            SUM(CASE WHEN t.token = 'RBSD' THEN t.amount ELSE 0 END) as rbsd_volume,
            SUM(t.amount) as total_volume,
            AVG(t.amount) as avg_claim_amount,
            SUM(CASE WHEN t.token = 'MON' THEN 1 ELSE 0 END) as mon_transactions,
            SUM(CASE WHEN t.token = 'JERRY' THEN 1 ELSE 0 END) as jerry_transactions,
            SUM(CASE WHEN t.token = 'RBSD' THEN 1 ELSE 0 END) as rbsd_transactions
        FROM periods p
        LEFT JOIN claiming_transactions t ON 
            DATE(t.timestamp, 'utc') >= p.period_start AND DATE(t.timestamp, 'utc') <= p.period_end
            {timestamp_filter}
        LEFT JOIN first_time_claimers ftc ON t.from_address = ftc.from_address
        GROUP BY p.period_start, p.period_end, p.period_number
        HAVING COUNT(t.tx_hash) > 0
        ORDER BY p.period_start
        """

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        activity_data = []
        for row in results:
            period_start, period_end, period_num, claims, active_claimers, new_claimers, mon_vol, jerry_vol, rbsd_vol, total_vol, avg_claim, mon_txs, jerry_txs, rbsd_txs = row
            
            activity_data.append({
                'period': period_num,
                'start_date': period_start,
                'end_date': period_end,
                'claims': claims or 0,
                'active_claimers': active_claimers or 0,
                'new_claimers': new_claimers or 0,
                'mon_volume': mon_vol or 0.0,
                'jerry_volume': jerry_vol or 0.0,
                'rbsd_volume': rbsd_vol or 0.0,
                'total_volume': total_vol or 0.0,
                'avg_claim_amount': avg_claim or 0.0,
                'mon_transactions': mon_txs or 0,
                'jerry_transactions': jerry_txs or 0,
                'rbsd_transactions': rbsd_txs or 0
            })

        return activity_data

    def get_claiming_stats_by_periods(self) -> List[Dict]:
        """Get claiming statistics for specific time periods (All Time, Last 90/30/7/1 days)."""
        query = """
        WITH timeframes AS (
            SELECT 'All Time' as period_name, 
                   DATE('2025-02-03') as start_date, 
                   DATE('now') as end_date
            
            UNION ALL
            
            SELECT 'Last 90 Days' as period_name,
                   DATE('now', '-90 days') as start_date,
                   DATE('now') as end_date
            
            UNION ALL
            
            SELECT 'Last 30 Days' as period_name,
                   DATE('now', '-30 days') as start_date,
                   DATE('now') as end_date
            
            UNION ALL
            
            SELECT 'Last 7 Days' as period_name,
                   DATE('now', '-7 days') as start_date,
                   DATE('now') as end_date
            
            UNION ALL
            
            SELECT 'Last Day' as period_name,
                   DATE('now', '-1 day') as start_date,
                   DATE('now', '-1 day') as end_date
        )
        SELECT 
            tf.period_name,
            tf.start_date,
            tf.end_date,
            COUNT(DISTINCT t.tx_hash) as total_claims,
            COUNT(DISTINCT t.from_address) as unique_claimers,
            SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) as mon_volume,
            SUM(CASE WHEN t.token = 'JERRY' THEN t.amount ELSE 0 END) as jerry_volume,
            SUM(CASE WHEN t.token = 'RBSD' THEN t.amount ELSE 0 END) as rbsd_volume,
            SUM(t.amount) as total_volume,
            ROUND(AVG(t.amount), 2) as avg_claim_amount,
            ROUND(CAST(COUNT(DISTINCT t.from_address) AS FLOAT) / COUNT(DISTINCT t.tx_hash), 2) as avg_claims_per_claimer
        FROM timeframes tf
        LEFT JOIN claiming_transactions t ON 
            DATE(t.timestamp, 'utc') >= tf.start_date AND DATE(t.timestamp, 'utc') <= tf.end_date
        GROUP BY tf.period_name, tf.start_date, tf.end_date
        ORDER BY 
            CASE tf.period_name
                WHEN 'All Time' THEN 1
                WHEN 'Last 90 Days' THEN 2
                WHEN 'Last 30 Days' THEN 3
                WHEN 'Last 7 Days' THEN 4
                WHEN 'Last Day' THEN 5
            END
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        stats_data = []
        for row in results:
            period_name, start_date, end_date, claims, claimers, mon_vol, jerry_vol, rbsd_vol, total_vol, avg_claim, avg_claims_per_claimer = row
            stats_data.append({
                'period': period_name,
                'mon_volume': mon_vol or 0.0,
                'jerry_volume': jerry_vol or 0.0,
                'rbsd_volume': rbsd_vol or 0.0,
                'total_volume': total_vol or 0.0,
                'claims': claims or 0,
                'unique_claimers': claimers or 0,
                'avg_claim_amount': avg_claim or 0.0,
                'avg_claims_per_claimer': avg_claims_per_claimer or 0.0
            })
        
        return stats_data

    def get_top_claimers(self, limit: int = 1000) -> list:
        """Get top claimers table with their statistics."""
        query = """
        SELECT 
            from_address as user_address,
            SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as total_mon,
            SUM(CASE WHEN token = 'JERRY' THEN amount ELSE 0 END) as total_jerry,
            SUM(CASE WHEN token = 'RBSD' THEN amount ELSE 0 END) as total_rbsd,
            SUM(amount) as total_claimed,
            COUNT(DISTINCT tx_hash) as total_claims,
            COUNT(DISTINCT DATE(timestamp)) as active_days
        FROM claiming_transactions
        GROUP BY from_address
        ORDER BY total_claimed DESC
        LIMIT ?
        """
        self.cursor.execute(query, (limit,))
        results = self.cursor.fetchall()
        top_claimers = []
        for i, row in enumerate(results):
            user_address, total_mon, total_jerry, total_rbsd, total_claimed, total_claims, active_days = row
            top_claimers.append({
                'rank': i + 1,
                'user_address': user_address,
                'total_mon': total_mon or 0.0,
                'total_jerry': total_jerry or 0.0,
                'total_rbsd': total_rbsd or 0.0,
                'total_claimed': total_claimed or 0.0,
                'total_claims': total_claims or 0,
                'active_days': active_days or 0
            })
        return top_claimers

    def analyze_timeframe(self, start_date: str, timeframe: str, since_timestamp: Optional[str] = None) -> Dict:
        """Analyze data for a specific timeframe and start date."""
        total_metrics = self.get_total_metrics()
        activity_over_time = self.get_activity_over_time(start_date, timeframe, since_timestamp)
        claiming_stats_by_periods = self.get_claiming_stats_by_periods()
        
        return {
            'timeframe': timeframe,
            'start_date': start_date,
            'total_periods': len(activity_over_time),
            'total_metrics': total_metrics,
            'activity_over_time': activity_over_time,
            'claiming_stats_by_periods': claiming_stats_by_periods
        }

def get_average_metrics(analytics):
    """Calculate average metrics for claiming data."""
    query = """
    SELECT 
        COUNT(DISTINCT from_address) as users,
        COUNT(DISTINCT tx_hash) as claim_tx,
        ROUND(AVG(amount), 2) as avg_claim_amount,
        SUM(amount) as tot_claimed,
        COUNT(DISTINCT DATE(timestamp, 'utc')) as total_days
    FROM claiming_transactions
    """
    
    analytics.cursor.execute(query)
    result = analytics.cursor.fetchone()
    
    if result:
        users, claim_tx, avg_claim_amount, tot_claimed, total_days = result
        total_days = total_days or 1  # Avoid division by zero
        
        return {
            "avg_claims_per_day": round(claim_tx / total_days, 2),
            "avg_claimers_per_day": round(users / total_days, 2),
            "avg_claim_amount": avg_claim_amount or 0.0,
            "total_users": users,
            "total_claim_tx": claim_tx,
            "total_claimed": tot_claimed,
            "total_days": total_days
        }
    else:
        return {
            "avg_claims_per_day": 0,
            "avg_claimers_per_day": 0,
            "avg_claim_amount": 0.0,
            "total_users": 0,
            "total_claim_tx": 0,
            "total_claimed": 0,
            "total_days": 0
        }

def load_existing_analytics() -> Optional[Dict]:
    """Load existing analytics data if available."""
    try:
        if os.path.exists(FRONTEND_PUBLIC):
            with open(FRONTEND_PUBLIC, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Warning: Could not load existing analytics: {e}")
        return None

def merge_analytics_data(existing_data: Dict, new_data: Dict, since_timestamp: str) -> Dict:
    """Merge new analytics data with existing data."""
    if not existing_data:
        return new_data
    
    # For incremental updates, we need to be careful about merging
    # For now, we'll regenerate everything to ensure consistency
    print(f"🔄 Merging analytics data since {since_timestamp}...")
    
    # Update metadata
    new_data['metadata']['generated_at'] = datetime.now().isoformat() + "Z"
    new_data['metadata']['last_incremental_update'] = since_timestamp
    
    return new_data

if __name__ == "__main__":
    with ClaimingAnalytics(DB_PATH) as analytics:
        print("🔄 Starting claiming analytics generation...")
        current_timestamp = datetime.now().isoformat()
        
        print("🔄 Running full analytics generation...")
        
        # Generate analytics for multiple timeframes
        timeframes = ['day', 'week', 'month']
        all_analytics = {}
        
        for timeframe in timeframes:
            print(f"📊 Processing {timeframe} data...")
            analysis = analytics.analyze_timeframe('2025-02-03', timeframe)
            all_analytics[timeframe] = analysis
        
        # Get additional data
        print("📈 Getting additional metrics...")
        top_claimers = analytics.get_top_claimers(20)
        average_metrics = get_average_metrics(analytics)
        
        # Use weekly data as the main data (for backward compatibility)
        main_data = all_analytics['week']
        
        # Create optimized structure
        data = {
            "success": True,
            "metadata": {
                "generated_at": current_timestamp + "Z",
                "timeframes_available": ["daily", "weekly", "monthly"],
                "default_timeframe": "weekly",
                "full_generation": True
            },
            # Main metrics (all time)
            "total_metrics": main_data['total_metrics'],
            "average_metrics": average_metrics,
            "claiming_stats_by_periods": main_data['claiming_stats_by_periods'],
            
            # Timeframe-specific data
            "timeframes": {
                "daily": {
                    "activity_over_time": all_analytics['day']['activity_over_time']
                },
                "weekly": {
                    "activity_over_time": all_analytics['week']['activity_over_time']
                },
                "monthly": {
                    "activity_over_time": all_analytics['month']['activity_over_time']
                }
            },
            
            # Legacy data (for backward compatibility)
            "activity_over_time": main_data['activity_over_time'],
            "top_claimers": top_claimers
        }
        
        # Save uncompressed JSON
        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Claiming analytics data saved to {OUTPUT_FILE}")
        
        # Copy to frontend public dirs
        os.makedirs(os.path.dirname(FRONTEND_PUBLIC), exist_ok=True)
        shutil.copyfile(OUTPUT_FILE, FRONTEND_PUBLIC)
        print(f"✅ Claiming analytics data copied to {FRONTEND_PUBLIC}")
        
        # Also copy to frontend-deployment public dir
        os.makedirs(os.path.dirname(FRONTEND_DEPLOYMENT_PUBLIC), exist_ok=True)
        shutil.copyfile(OUTPUT_FILE, FRONTEND_DEPLOYMENT_PUBLIC)
        print(f"✅ Claiming analytics data copied to {FRONTEND_DEPLOYMENT_PUBLIC}")
        
        # Create compressed version for faster loading
        os.makedirs(os.path.dirname(COMPRESSED_FILE), exist_ok=True)
        with open(FRONTEND_PUBLIC, 'rb') as f_in:
            with gzip.open(COMPRESSED_FILE, 'wb') as f_out:
                f_out.writelines(f_in)
        print(f"✅ Compressed version saved to {COMPRESSED_FILE}")
        
        # Print file sizes
        import os
        uncompressed_size = os.path.getsize(FRONTEND_PUBLIC)
        compressed_size = os.path.getsize(COMPRESSED_FILE)
        compression_ratio = (1 - compressed_size / uncompressed_size) * 100
        
        print(f"📊 File sizes:")
        print(f"   Uncompressed: {uncompressed_size / 1024:.1f} KB")
        print(f"   Compressed: {compressed_size / 1024:.1f} KB")
        print(f"   Compression: {compression_ratio:.1f}%")
        
        # Print summary statistics
        print(f"📈 Summary:")
        print(f"   Total claims: {data['total_metrics']['total_claims']:,}")
        print(f"   Unique claimers: {data['total_metrics']['total_unique_claimers']:,}")
        print(f"   Total MON volume: {data['total_metrics']['total_mon_volume']:,.2f}")
        print(f"   Total Jerry volume: {data['total_metrics']['total_jerry_volume']:,.2f}")
        print(f"   Total RBSD volume: {data['total_metrics']['total_rbsd_volume']:,.2f}") 