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
        
        # Weekly aggregation with correct active bettors and new users calculation
        query = """
        WITH weeks AS (
            SELECT 
                DATE('2025-02-03', 'weekday 0', '-6 days') as week_start,
                DATE('2025-02-03', 'weekday 0', '+0 days') as week_end,
                1 as week_number
            
            UNION ALL
            
            SELECT 
                DATE(week_start, '+7 days') as week_start,
                DATE(week_end, '+7 days') as week_end,
                week_number + 1 as week_number
            FROM weeks
            WHERE week_start <= DATE('now')
        ),
        first_time_users AS (
            SELECT 
                from_address,
                MIN(timestamp) as first_bet_date
            FROM betting_transactions
            GROUP BY from_address
        )
        SELECT 
            w.week_start,
            w.week_end,
            w.week_number,
            COUNT(t.tx_hash) as transaction_count,
            COUNT(DISTINCT t.from_address) as active_bettors,
            COUNT(DISTINCT CASE WHEN DATE(ftu.first_bet_date) >= w.week_start AND DATE(ftu.first_bet_date) <= w.week_end THEN t.from_address END) as new_users,
            SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) as mon_volume,
            SUM(CASE WHEN t.token = 'Jerry' THEN t.amount ELSE 0 END) as jerry_volume,
            SUM(t.n_cards) as total_cards,
            AVG(t.amount) as avg_bet_amount,
            SUM(CASE WHEN t.token = 'MON' THEN 1 ELSE 0 END) as mon_transactions,
            SUM(CASE WHEN t.token = 'Jerry' THEN 1 ELSE 0 END) as jerry_transactions
        FROM weeks w
        LEFT JOIN betting_transactions t ON 
            DATE(t.timestamp) >= w.week_start AND DATE(t.timestamp) <= w.week_end
        LEFT JOIN first_time_users ftu ON t.from_address = ftu.from_address
        GROUP BY w.week_start, w.week_end, w.week_number
        HAVING COUNT(t.tx_hash) > 0
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
        print(f"{'Week':<4} {'Start Date':<12} {'End Date':<12} {'Txs':<8} {'Active Bettors':<15} {'New Users':<12} {'MON Vol':<12} {'JERRY Vol':<12} {'Total Cards':<12} {'Avg Cards/Tx':<12} {'MON Txs':<10} {'JERRY Txs':<12}")
        print("-" * 150)
        
        # Print each week
        for week in weeks:
            week_start, week_end, week_num, txs, active_bettors, new_users, mon_vol, jerry_vol, cards, avg_bet, mon_txs, jerry_txs = week
            
            # Calculate average cards per transaction
            avg_cards_per_tx = cards / txs if txs > 0 else 0
            
            print(f"{week_num:<4} {week_start:<12} {week_end:<12} {format_number(txs):<8} {format_number(active_bettors):<15} {format_number(new_users):<12} {format_currency(mon_vol or 0):<12} {format_currency(jerry_vol or 0):<12} {format_number(cards or 0):<12} {avg_cards_per_tx:<12.1f} {format_number(mon_txs):<10} {format_number(jerry_txs):<12}")
        
        print("-" * 135)
        
        # Calculate totals
        total_txs = sum(w[3] for w in weeks)
        total_active_bettors = sum(w[4] for w in weeks)  # This is weekly active, not unique
        total_new_users = sum(w[5] for w in weeks)  # Total new users across all weeks
        total_mon_vol = sum(w[6] or 0 for w in weeks)
        total_jerry_vol = sum(w[7] or 0 for w in weeks)
        total_cards = sum(w[8] or 0 for w in weeks)
        total_mon_txs = sum(w[10] for w in weeks)
        total_jerry_txs = sum(w[11] for w in weeks)
        
        # Calculate overall average cards per transaction
        overall_avg_cards_per_tx = total_cards / total_txs if total_txs > 0 else 0
        
        # Get unique active bettors across all weeks
        cursor.execute("""
            SELECT COUNT(DISTINCT from_address) 
            FROM betting_transactions 
            WHERE timestamp >= DATE('2025-02-03')
        """)
        unique_active_bettors = cursor.fetchone()[0]
        
        print()
        print("📊 WEEKLY SUMMARY:")
        print(f"   Total Transactions: {format_number(total_txs)}")
        print(f"   Unique Active Bettors: {format_number(unique_active_bettors)}")
        print(f"   Total New Users: {format_number(total_new_users)}")
        print(f"   Total MON Volume: {format_currency(total_mon_vol)}")
        print(f"   Total JERRY Volume: {format_currency(total_jerry_vol)}")
        print(f"   Total Cards Picked: {format_number(total_cards)}")
        print(f"   Average Cards per Transaction: {overall_avg_cards_per_tx:.1f}")
        print(f"   MON Transactions: {format_number(total_mon_txs)}")
        print(f"   JERRY Transactions: {format_number(total_jerry_txs)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def print_period_stats():
    """Print statistics for different time periods."""
    print()
    print("=" * 80)
    print("📊 STATISTICS BY DIFFERENT PERIODS")
    print("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        periods = [
            ("All Time", "2024-02-03", "datetime('now')"),
            ("Last 90 days", "datetime('now', '-90 days')", "datetime('now')"),
            ("Last 30 days", "datetime('now', '-30 days')", "datetime('now')"),
            ("Last 7 days", "datetime('now', '-7 days')", "datetime('now')"),
            ("Last 1 day", "datetime('now', '-1 day')", "datetime('now')")
        ]
        
        print(f"{'Period':<20} {'MON Volume':<15} {'JERRY Volume':<15} {'Txs':<10} {'Active Bettors':<15} {'Total Cards':<12}")
        print("-" * 90)
        
        for period_name, start_date, end_date in periods:
            query = f"""
            SELECT 
                SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as mon_volume,
                SUM(CASE WHEN token = 'Jerry' THEN amount ELSE 0 END) as jerry_volume,
                COUNT(DISTINCT tx_hash) as transaction_count,
                COUNT(DISTINCT from_address) as active_bettors,
                SUM(n_cards) as total_cards
            FROM betting_transactions
            WHERE timestamp >= {start_date} AND timestamp <= {end_date}
            """
            
            cursor.execute(query)
            row = cursor.fetchone()
            
            mon_vol = row[0] or 0
            jerry_vol = row[1] or 0
            txs = row[2]
            active_bettors = row[3]
            total_cards = row[4] or 0
            
            print(f"{period_name:<20} {format_currency(mon_vol):<15} {format_currency(jerry_vol):<15} {format_number(txs):<10} {format_number(active_bettors):<15} {format_number(total_cards):<12}")
        
        print("-" * 90)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def print_heatmap_data():
    """Print heatmap data for day of week analysis, matching Snowflake logic."""
    print()
    print("=" * 80)
    print("🔥 HEATMAP DATA - TRANSACTIONS BY DAY OF WEEK (Snowflake logic)")
    print("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get data by week (Monday start) and day of week
        query = """
        SELECT
          DATE(timestamp, 'weekday 1', '-7 days', 'start of day') AS week_start,
          strftime('%w', timestamp) AS dow,
          COUNT(DISTINCT from_address) AS users,
          COUNT(DISTINCT tx_hash) AS bet_tx,
          SUM(amount) AS volume
        FROM betting_transactions
        WHERE timestamp >= DATE('2025-02-03')
        GROUP BY week_start, dow
        ORDER BY week_start, dow
        """
        
        cursor.execute(query)
        heatmap_data = cursor.fetchall()
        
        if not heatmap_data:
            print("❌ No heatmap data found!")
            return
        
        # Build a dict: {week_start: {dow: bet_tx}}
        weeks_data = {}
        for row in heatmap_data:
            week_start, dow, users, bet_tx, volume = row
            if week_start not in weeks_data:
                weeks_data[week_start] = {}
            weeks_data[week_start][int(dow)] = bet_tx
        
        # Day names, 0=Sunday, 1=Monday, ...
        day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        
        # Print header
        print(f"{'Week Starting':<15} " + " ".join([f"{d:<8}" for d in day_names]))
        print("-" * 90)
        
        sorted_weeks = sorted(weeks_data.keys())
        for week_start in sorted_weeks:
            print(f"{week_start:<15}", end="")
            for i in range(7):
                tx_count = weeks_data[week_start].get(i, 0)
                print(f"{tx_count:<8}", end="")
            print()
        print("-" * 90)
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

def print_token_volume_heatmaps():
    """Print heatmap data for MON and JERRY token volumes by day of week."""
    print()
    print("=" * 80)
    print("💰 TOKEN VOLUME HEATMAPS - MON & JERRY BY DAY OF WEEK")
    print("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query for MON token volume heatmap
        mon_query = """
        WITH RECURSIVE weeks AS (
            SELECT 
                DATE('2025-02-03', 'weekday 0', '-6 days') as week_start,
                DATE('2025-02-03', 'weekday 0', '+0 days') as week_end,
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
            strftime('%w', t.timestamp) as day_of_week,
            w.week_number,
            w.week_start,
            SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) as mon_volume
        FROM weeks w
        LEFT JOIN betting_transactions t ON 
            DATE(t.timestamp) >= w.week_start AND DATE(t.timestamp) <= w.week_end
        GROUP BY strftime('%w', t.timestamp), w.week_number, w.week_start
        HAVING SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) > 0
        ORDER BY w.week_start, day_of_week
        """
        
        # Query for JERRY token volume heatmap
        jerry_query = """
        WITH RECURSIVE weeks AS (
            SELECT 
                DATE('2025-02-03', 'weekday 0', '-6 days') as week_start,
                DATE('2025-02-03', 'weekday 0', '+0 days') as week_end,
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
            strftime('%w', t.timestamp) as day_of_week,
            w.week_number,
            w.week_start,
            SUM(CASE WHEN t.token = 'Jerry' THEN t.amount ELSE 0 END) as jerry_volume
        FROM weeks w
        LEFT JOIN betting_transactions t ON 
            DATE(t.timestamp) >= w.week_start AND DATE(t.timestamp) <= w.week_end
        GROUP BY strftime('%w', t.timestamp), w.week_number, w.week_start
        HAVING SUM(CASE WHEN t.token = 'Jerry' THEN t.amount ELSE 0 END) > 0
        ORDER BY w.week_start, day_of_week
        """
        
        # Execute MON query
        cursor.execute(mon_query)
        mon_data = cursor.fetchall()
        
        # Execute JERRY query
        cursor.execute(jerry_query)
        jerry_data = cursor.fetchall()
        
        if not mon_data and not jerry_data:
            print("❌ No token volume data found!")
            return
        
        # Process MON data
        mon_weeks = {}
        for row in mon_data:
            day_of_week, week_num, week_start, mon_volume = row
            day_name = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][int(day_of_week)]
            
            if week_start not in mon_weeks:
                mon_weeks[week_start] = {}
            mon_weeks[week_start][day_name] = mon_volume or 0
        
        # Process JERRY data
        jerry_weeks = {}
        for row in jerry_data:
            day_of_week, week_num, week_start, jerry_volume = row
            day_name = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][int(day_of_week)]
            
            if week_start not in jerry_weeks:
                jerry_weeks[week_start] = {}
            jerry_weeks[week_start][day_name] = jerry_volume or 0
        
        # Print MON Volume Heatmap
        print("\n🟢 MON TOKEN VOLUME HEATMAP:")
        print(f"{'Week Starting':<15} {'Mon':<12} {'Tue':<12} {'Wed':<12} {'Thu':<12} {'Fri':<12} {'Sat':<12} {'Sun':<12}")
        print("-" * 100)
        
        sorted_weeks = sorted(set(list(mon_weeks.keys()) + list(jerry_weeks.keys())))
        for week_start in sorted_weeks[-12:]:  # Show last 12 weeks
            print(f"{week_start:<15}", end="")
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                volume = mon_weeks.get(week_start, {}).get(day, 0)
                
                # Color intensity based on MON volume
                if volume > 10000:
                    intensity = "🔴"  # High
                elif volume > 5000:
                    intensity = "🟡"  # Medium
                elif volume > 1000:
                    intensity = "🟢"  # Low
                else:
                    intensity = "⚪"  # Very low
                
                print(f"{intensity} {format_currency(volume):<10}", end="")
            print()
        
        print("-" * 100)
        
        # Print JERRY Volume Heatmap
        print("\n🟣 JERRY TOKEN VOLUME HEATMAP:")
        print(f"{'Week Starting':<15} {'Mon':<12} {'Tue':<12} {'Wed':<12} {'Thu':<12} {'Fri':<12} {'Sat':<12} {'Sun':<12}")
        print("-" * 100)
        
        for week_start in sorted_weeks[-12:]:  # Show last 12 weeks
            print(f"{week_start:<15}", end="")
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                volume = jerry_weeks.get(week_start, {}).get(day, 0)
                
                # Color intensity based on JERRY volume
                if volume > 5000:
                    intensity = "🔴"  # High
                elif volume > 2000:
                    intensity = "🟡"  # Medium
                elif volume > 500:
                    intensity = "🟢"  # Low
                else:
                    intensity = "⚪"  # Very low
                
                print(f"{intensity} {format_currency(volume):<10}", end="")
            print()
        
        print("-" * 100)
        
        # Print summary statistics by day of week
        print("\n📊 AVERAGE TOKEN VOLUMES BY DAY OF WEEK:")
        print(f"{'Day':<12} {'Avg MON':<15} {'Avg JERRY':<15}")
        print("-" * 45)
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in day_names:
            mon_volumes = []
            jerry_volumes = []
            
            for week_data in mon_weeks.values():
                if day in week_data:
                    mon_volumes.append(week_data[day])
            
            for week_data in jerry_weeks.values():
                if day in week_data:
                    jerry_volumes.append(week_data[day])
            
            if mon_volumes or jerry_volumes:
                avg_mon = sum(mon_volumes) / len(mon_volumes) if mon_volumes else 0
                avg_jerry = sum(jerry_volumes) / len(jerry_volumes) if jerry_volumes else 0
                
                print(f"{day:<12} {format_currency(avg_mon):<15} {format_currency(avg_jerry):<15}")
        
        print("-" * 45)
        
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
    print_period_stats()
    print_heatmap_data()
    print_token_volume_heatmaps() 