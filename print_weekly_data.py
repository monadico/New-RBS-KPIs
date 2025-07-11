#!/usr/bin/env python3
"""
Weekly Data Printer
==================

Prints all weekly metrics in a readable format to verify data calculations.
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

def format_number(num):
    """Format large numbers with K/M suffixes."""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def format_currency(num):
    """Format currency values."""
    return f"${num:,.0f}"

def print_daily_data():
    """Print daily data for the last 30 days."""
    print("=" * 80)
    print("📅 DAILY BETTING ANALYTICS DATA")
    print("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as transaction_count,
            COUNT(DISTINCT from_address) as active_bettors,
            SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as mon_volume,
            SUM(CASE WHEN token = 'Jerry' THEN amount ELSE 0 END) as jerry_volume,
            SUM(n_cards) as total_cards,
            AVG(amount) as avg_bet_amount,
            SUM(CASE WHEN token = 'MON' THEN 1 ELSE 0 END) as mon_transactions,
            SUM(CASE WHEN token = 'Jerry' THEN 1 ELSE 0 END) as jerry_transactions
        FROM betting_transactions
        WHERE timestamp >= DATE('now', '-30 days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        LIMIT 30
        """
        
        cursor.execute(query)
        daily_data = cursor.fetchall()
        
        if not daily_data:
            print("❌ No daily data found!")
            return
        
        print(f"📈 Found {len(daily_data)} days of data")
        print()
        
        # Print header
        print(f"{'Date':<12} {'Txs':<8} {'Active Bettors':<15} {'MON Vol':<12} {'JERRY Vol':<12} {'Cards':<8} {'Avg Bet':<10} {'MON Txs':<10} {'JERRY Txs':<12}")
        print("-" * 115)
        
        # Print each day
        for day in daily_data:
            date, txs, active_bettors, mon_vol, jerry_vol, cards, avg_bet, mon_txs, jerry_txs = day
            
            print(f"{date:<12} {format_number(txs):<8} {format_number(active_bettors):<15} {format_currency(mon_vol or 0):<12} {format_currency(jerry_vol or 0):<12} {format_number(cards or 0):<8} {format_currency(avg_bet or 0):<10} {format_number(mon_txs):<10} {format_number(jerry_txs):<12}")
        
        print("-" * 115)
        
        # Calculate totals
        total_txs = sum(d[1] for d in daily_data)
        total_active_bettors = sum(d[2] for d in daily_data)  # This is daily active, not unique
        total_mon_vol = sum(d[3] or 0 for d in daily_data)
        total_jerry_vol = sum(d[4] or 0 for d in daily_data)
        total_cards = sum(d[5] or 0 for d in daily_data)
        total_mon_txs = sum(d[7] for d in daily_data)
        total_jerry_txs = sum(d[8] for d in daily_data)
        
        # Get unique active bettors in the period
        cursor.execute("""
            SELECT COUNT(DISTINCT from_address) 
            FROM betting_transactions 
            WHERE timestamp >= DATE('now', '-30 days')
        """)
        unique_active_bettors = cursor.fetchone()[0]
        
        print()
        print("📊 DAILY SUMMARY (Last 30 days):")
        print(f"   Total Transactions: {format_number(total_txs)}")
        print(f"   Unique Active Bettors: {format_number(unique_active_bettors)}")
        print(f"   Total MON Volume: {format_currency(total_mon_vol)}")
        print(f"   Total JERRY Volume: {format_currency(total_jerry_vol)}")
        print(f"   Total Cards Picked: {format_number(total_cards)}")
        print(f"   MON Transactions: {format_number(total_mon_txs)}")
        print(f"   JERRY Transactions: {format_number(total_jerry_txs)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def print_weekly_data():
    """Print weekly data aggregated from daily data."""
    print()
    print("=" * 80)
    print("📊 WEEKLY BETTING ANALYTICS DATA (Aggregated from Daily)")
    print("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Weekly aggregation from daily data
        query = """
        WITH daily_data AS (
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as transaction_count,
                COUNT(DISTINCT from_address) as active_bettors,
                SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as mon_volume,
                SUM(CASE WHEN token = 'Jerry' THEN amount ELSE 0 END) as jerry_volume,
                SUM(n_cards) as total_cards,
                AVG(amount) as avg_bet_amount,
                SUM(CASE WHEN token = 'MON' THEN 1 ELSE 0 END) as mon_transactions,
                SUM(CASE WHEN token = 'Jerry' THEN 1 ELSE 0 END) as jerry_transactions
            FROM betting_transactions
            WHERE timestamp >= DATE('2024-02-03')
            GROUP BY DATE(timestamp)
        ),
        weeks AS (
            SELECT 
                DATE('2024-02-03', 'weekday 0', '-6 days') as week_start,
                DATE('2024-02-03', 'weekday 0', '+0 days') as week_end,
                1 as week_number
            
            UNION ALL
            
            SELECT 
                DATE(week_start, '+7 days') as week_start,
                DATE(week_end, '+7 days') as week_end,
                week_number + 1 as week_number
            FROM weeks
            WHERE week_start <= DATE('now')
        )
        SELECT 
            w.week_start,
            w.week_end,
            w.week_number,
            SUM(d.transaction_count) as transaction_count,
            SUM(d.active_bettors) as active_bettors,
            SUM(d.mon_volume) as mon_volume,
            SUM(d.jerry_volume) as jerry_volume,
            SUM(d.total_cards) as total_cards,
            AVG(d.avg_bet_amount) as avg_bet_amount,
            SUM(d.mon_transactions) as mon_transactions,
            SUM(d.jerry_transactions) as jerry_transactions
        FROM weeks w
        LEFT JOIN daily_data d ON 
            d.date >= w.week_start AND d.date <= w.week_end
        GROUP BY w.week_start, w.week_end, w.week_number
        HAVING SUM(d.transaction_count) > 0
        ORDER BY w.week_start
        """
        
        cursor.execute(query)
        weeks = cursor.fetchall()
        
        if not weeks:
            print("❌ No weekly data found!")
            return
        
        print(f"📈 Found {len(weeks)} weeks of data")
        print()
        
        # Print header
        print(f"{'Week':<4} {'Start Date':<12} {'End Date':<12} {'Txs':<8} {'Active Bettors':<15} {'MON Vol':<12} {'JERRY Vol':<12} {'Total Cards':<12} {'Avg Cards/Tx':<12} {'MON Txs':<10} {'JERRY Txs':<12}")
        print("-" * 135)
        
        # Print each week
        for week in weeks:
            week_start, week_end, week_num, txs, active_bettors, mon_vol, jerry_vol, cards, avg_bet, mon_txs, jerry_txs = week
            
            # Calculate average cards per transaction
            avg_cards_per_tx = cards / txs if txs > 0 else 0
            
            print(f"{week_num:<4} {week_start:<12} {week_end:<12} {format_number(txs):<8} {format_number(active_bettors):<15} {format_currency(mon_vol or 0):<12} {format_currency(jerry_vol or 0):<12} {format_number(cards or 0):<12} {avg_cards_per_tx:<12.1f} {format_number(mon_txs):<10} {format_number(jerry_txs):<12}")
        
        print("-" * 135)
        
        # Calculate totals
        total_txs = sum(w[3] for w in weeks)
        total_active_bettors = sum(w[4] for w in weeks)  # This is weekly active, not unique
        total_mon_vol = sum(w[5] or 0 for w in weeks)
        total_jerry_vol = sum(w[6] or 0 for w in weeks)
        total_cards = sum(w[7] or 0 for w in weeks)
        total_mon_txs = sum(w[9] for w in weeks)
        total_jerry_txs = sum(w[10] for w in weeks)
        
        # Calculate overall average cards per transaction
        overall_avg_cards_per_tx = total_cards / total_txs if total_txs > 0 else 0
        
        # Get unique active bettors across all weeks
        cursor.execute("""
            SELECT COUNT(DISTINCT from_address) 
            FROM betting_transactions 
            WHERE timestamp >= DATE('2024-02-03')
        """)
        unique_active_bettors = cursor.fetchone()[0]
        
        print()
        print("📊 WEEKLY SUMMARY:")
        print(f"   Total Transactions: {format_number(total_txs)}")
        print(f"   Unique Active Bettors: {format_number(unique_active_bettors)}")
        print(f"   Total MON Volume: {format_currency(total_mon_vol)}")
        print(f"   Total JERRY Volume: {format_currency(total_jerry_vol)}")
        print(f"   Total Cards Picked: {format_number(total_cards)}")
        print(f"   Average Cards per Transaction: {overall_avg_cards_per_tx:.1f}")
        print(f"   MON Transactions: {format_number(total_mon_txs)}")
        print(f"   JERRY Transactions: {format_number(total_jerry_txs)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def print_total_stats():
    """Print total statistics including unique users."""
    print()
    print("=" * 80)
    print("📊 TOTAL STATISTICS (All Time)")
    print("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total unique users (all time)
        cursor.execute("SELECT COUNT(DISTINCT from_address) FROM betting_transactions")
        total_unique_users = cursor.fetchone()[0]
        
        # Get total transactions
        cursor.execute("SELECT COUNT(*) FROM betting_transactions")
        total_transactions = cursor.fetchone()[0]
        
        # Get total cards
        cursor.execute("SELECT SUM(n_cards) FROM betting_transactions")
        total_cards = cursor.fetchone()[0] or 0
        
        # Get token volumes
        cursor.execute("SELECT SUM(amount) FROM betting_transactions WHERE token = 'MON'")
        total_mon_volume = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(amount) FROM betting_transactions WHERE token = 'Jerry'")
        total_jerry_volume = cursor.fetchone()[0] or 0
        
        # Get token transaction counts
        cursor.execute("SELECT COUNT(*) FROM betting_transactions WHERE token = 'MON'")
        total_mon_transactions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM betting_transactions WHERE token = 'Jerry'")
        total_jerry_transactions = cursor.fetchone()[0]
        
        print("📈 ALL-TIME STATISTICS:")
        print(f"   Total Unique Users: {format_number(total_unique_users)}")
        print(f"   Total Transactions: {format_number(total_transactions)}")
        print(f"   Total Cards Picked: {format_number(total_cards)}")
        print(f"   Total MON Volume: {format_currency(total_mon_volume)}")
        print(f"   Total JERRY Volume: {format_currency(total_jerry_volume)}")
        print(f"   MON Transactions: {format_number(total_mon_transactions)}")
        print(f"   JERRY Transactions: {format_number(total_jerry_transactions)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print_total_stats()
    print_daily_data()
    print_weekly_data() 