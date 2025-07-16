#!/usr/bin/env python3
"""
Debug Token Volumes
==================

Count MON token volumes from all days in the database to understand data availability.
"""

import sqlite3
import os
from datetime import datetime

# Fix for Python 3.12+ SQLite datetime deprecation warning
def adapt_datetime(val):
    return val.isoformat()

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect("betting_transactions.db")

def format_currency(num):
    """Format currency values."""
    return f"${num:,.0f}"

def debug_mon_volumes():
    """Debug MON token volumes from all days."""
    print("=" * 80)
    print("🔍 DEBUGGING MON TOKEN VOLUMES")
    print("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, let's see the date range and total MON volume
        print("📊 DATABASE OVERVIEW:")
        cursor.execute("SELECT MIN(DATE(timestamp)), MAX(DATE(timestamp)), COUNT(*) FROM betting_transactions")
        min_date, max_date, total_txs = cursor.fetchone()
        print(f"   Date Range: {min_date} to {max_date}")
        print(f"   Total Transactions: {total_txs:,}")
        
        # Get total MON volume
        cursor.execute("SELECT SUM(amount) FROM betting_transactions WHERE token = 'MON'")
        total_mon_volume = cursor.fetchone()[0] or 0
        print(f"   Total MON Volume: {format_currency(total_mon_volume)}")
        
        # Get MON transactions count
        cursor.execute("SELECT COUNT(*) FROM betting_transactions WHERE token = 'MON'")
        total_mon_txs = cursor.fetchone()[0]
        print(f"   MON Transactions: {total_mon_txs:,}")
        
        print()
        
        # Now let's get daily MON volumes
        print("📅 DAILY MON VOLUMES:")
        query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as transaction_count,
            SUM(amount) as total_volume,
            AVG(amount) as avg_amount
        FROM betting_transactions 
        WHERE token = 'MON'
        GROUP BY DATE(timestamp)
        ORDER BY date
        """
        
        cursor.execute(query)
        daily_data = cursor.fetchall()
        
        if not daily_data:
            print("❌ No MON transaction data found!")
            return
        
        print(f"📈 Found {len(daily_data)} days with MON transactions")
        print()
        
        # Print header
        print(f"{'Date':<12} {'Txs':<8} {'Total Volume':<15} {'Avg Amount':<12}")
        print("-" * 50)
        
        # Print each day
        total_volume = 0
        total_txs = 0
        
        for day in daily_data:
            date, txs, volume, avg_amount = day
            total_volume += volume or 0
            total_txs += txs
            
            print(f"{date:<12} {txs:<8,} {format_currency(volume or 0):<15} {format_currency(avg_amount or 0):<12}")
        
        print("-" * 50)
        print(f"TOTAL: {total_txs:,} transactions, {format_currency(total_volume)} volume")
        
        # Let's also check for any days with zero volume
        print()
        print("🔍 CHECKING FOR DAYS WITH ZERO MON VOLUME:")
        
        # Get all unique dates in the database
        cursor.execute("SELECT DISTINCT DATE(timestamp) FROM betting_transactions ORDER BY DATE(timestamp)")
        all_dates = [row[0] for row in cursor.fetchall()]
        
        # Get dates with MON transactions
        cursor.execute("SELECT DISTINCT DATE(timestamp) FROM betting_transactions WHERE token = 'MON' ORDER BY DATE(timestamp)")
        mon_dates = [row[0] for row in cursor.fetchall()]
        
        zero_dates = [date for date in all_dates if date not in mon_dates]
        
        print(f"   Total unique dates in database: {len(all_dates)}")
        print(f"   Dates with MON transactions: {len(mon_dates)}")
        print(f"   Dates with zero MON volume: {len(zero_dates)}")
        
        if zero_dates:
            print(f"   Sample zero-volume dates: {zero_dates[:10]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_mon_volumes() 