#!/usr/bin/env python3
"""
Simple Betting Analytics API
============================

Serves aggregated data from the betting_transactions database.
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from new_flexible_analytics import FlexibleAnalytics

# Fix for Python 3.12+ SQLite datetime deprecation warning
def adapt_datetime(val):
    return val.isoformat()

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
DATABASE_PATH = "/app/betting_transactions.db"
def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(DATABASE_PATH)

@app.route("/api/stats", methods=['GET'])
def get_stats():
    """Get aggregated statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM betting_transactions")
        total_transactions = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(amount) FROM betting_transactions")
        total_volume = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(DISTINCT from_address) FROM betting_transactions")
        unique_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(amount) FROM betting_transactions")
        avg_bet = cursor.fetchone()[0] or 0
        
        # Get total cards picked
        cursor.execute("SELECT SUM(n_cards) FROM betting_transactions")
        total_cards = cursor.fetchone()[0] or 0
        
        # Get token breakdown
        cursor.execute("""
            SELECT token, COUNT(*), SUM(amount), AVG(amount)
            FROM betting_transactions 
            GROUP BY token
        """)
        token_stats = []
        for row in cursor.fetchall():
            token_stats.append({
                'token': row[0],
                'count': row[1],
                'total_volume': row[2] or 0,
                'average_bet': row[3] or 0,
                'percentage': (row[1] / total_transactions * 100) if total_transactions > 0 else 0
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'total_transactions': total_transactions,
                'total_volume': total_volume,
                'unique_users': unique_users,
                'average_bet': avg_bet,
                'total_cards': total_cards,
                'token_stats': token_stats
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/weekly", methods=['GET'])
def get_weekly_data():
    """Get weekly aggregated data."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Weekly aggregation query
        query = """
        WITH RECURSIVE weeks AS (
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
        ),
        weekly_counts AS (
            SELECT 
                w.week_start,
                w.week_end,
                w.week_number,
                COUNT(t.tx_hash) as transaction_count,
                COUNT(DISTINCT t.from_address) as unique_users,
                SUM(t.amount) as total_volume,
                AVG(t.amount) as avg_bet_amount,
                SUM(CASE WHEN t.token = 'MON' THEN 1 ELSE 0 END) as mon_transactions,
                SUM(CASE WHEN t.token = 'Jerry' THEN 1 ELSE 0 END) as jerry_transactions,
                SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) as mon_volume,
                SUM(CASE WHEN t.token = 'Jerry' THEN t.amount ELSE 0 END) as jerry_volume,
                SUM(t.n_cards) as total_cards,
                AVG(t.n_cards) as avg_cards
            FROM weeks w
            LEFT JOIN betting_transactions t ON 
                DATE(t.timestamp) >= w.week_start AND 
                DATE(t.timestamp) <= w.week_end
            GROUP BY w.week_start, w.week_end, w.week_number
        )
        SELECT 
            week_start,
            week_end,
            week_number,
            transaction_count,
            unique_users,
            total_volume,
            avg_bet_amount,
            mon_transactions,
            jerry_transactions,
            mon_volume,
            jerry_volume,
            total_cards,
            avg_cards
        FROM weekly_counts
        WHERE transaction_count > 0
        ORDER BY week_start
        """
        
        cursor.execute(query)
        
        weeks = []
        for row in cursor.fetchall():
            weeks.append({
                'week_start': row[0],
                'week_end': row[1],
                'week_number': row[2],
                'transaction_count': row[3],
                'unique_users': row[4],
                'total_volume': row[5] or 0,
                'avg_bet_amount': row[6] or 0,
                'mon_transactions': row[7],
                'jerry_transactions': row[8],
                'mon_volume': row[9] or 0,
                'jerry_volume': row[10] or 0,
                'total_cards': row[11] or 0,
                'avg_cards': row[12] or 0
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'weeks': weeks,
                'total_weeks': len(weeks),
                'total_transactions': sum(w['transaction_count'] for w in weeks),
                'total_volume': sum(w['total_volume'] for w in weeks),
                'total_users': max(w['unique_users'] for w in weeks) if weeks else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/daily", methods=['GET'])
def get_daily_data():
    """Get daily data for the last 30 days."""
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
        
        days = []
        for row in daily_data:
            date, txs, active_bettors, mon_vol, jerry_vol, cards, avg_bet, mon_txs, jerry_txs = row
            days.append({
                'date': date,
                'transaction_count': txs,
                'active_bettors': active_bettors,
                'mon_volume': mon_vol or 0,
                'jerry_volume': jerry_vol or 0,
                'total_cards': cards or 0,
                'avg_bet_amount': avg_bet or 0,
                'mon_transactions': mon_txs,
                'jerry_transactions': jerry_txs
            })
        
        # Calculate totals
        total_txs = sum(d['transaction_count'] for d in days)
        total_mon_vol = sum(d['mon_volume'] for d in days)
        total_jerry_vol = sum(d['jerry_volume'] for d in days)
        total_cards = sum(d['total_cards'] for d in days)
        total_mon_txs = sum(d['mon_transactions'] for d in days)
        total_jerry_txs = sum(d['jerry_transactions'] for d in days)
        
        # Get unique active bettors in the period
        cursor.execute("""
            SELECT COUNT(DISTINCT from_address) 
        FROM betting_transactions
            WHERE timestamp >= DATE('now', '-30 days')
        """)
        unique_active_bettors = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'days': days,
                'summary': {
                    'total_transactions': total_txs,
                    'unique_active_bettors': unique_active_bettors,
                    'total_mon_volume': total_mon_vol,
                    'total_jerry_volume': total_jerry_vol,
                    'total_cards': total_cards,
                    'mon_transactions': total_mon_txs,
                    'jerry_transactions': total_jerry_txs
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/periods", methods=['GET'])
def get_period_stats():
    """Get statistics for different time periods."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        periods = [
            ("Last 30 days", "datetime('now', '-30 days')", "datetime('now')"),
            ("Last 7 days", "datetime('now', '-7 days')", "datetime('now')"),
            ("Last 1 day", "datetime('now', '-1 day')", "datetime('now')")
        ]
        
        period_stats = []
        for period_name, start_date, end_date in periods:
            # Simplified query with better performance
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
            
            if row:
                period_stats.append({
                    'period': period_name,
                    'mon_volume': row[0] or 0,
                    'jerry_volume': row[1] or 0,
                    'transaction_count': row[2],
                    'active_bettors': row[3],
                    'total_cards': row[4] or 0
                })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': period_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/heatmap", methods=['GET'])
def get_heatmap_data():
    """Get heatmap data for day of week analysis."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Simplified query - only get last 12 weeks to improve performance
        query = """
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
            WHERE week_start <= DATE('now') AND week_number <= 12
        )
        SELECT 
            w.week_start,
            strftime('%w', t.timestamp) AS dow,
            COUNT(DISTINCT t.from_address) AS users,
            COUNT(DISTINCT t.tx_hash) AS bet_tx,
            SUM(t.amount) AS volume
        FROM weeks w
        LEFT JOIN betting_transactions t ON 
            DATE(t.timestamp) >= w.week_start AND DATE(t.timestamp) <= w.week_end
        GROUP BY w.week_start, strftime('%w', t.timestamp)
        HAVING COUNT(DISTINCT t.tx_hash) > 0
        ORDER BY w.week_start, dow
        LIMIT 100
        """
        
        cursor.execute(query)
        heatmap_data = cursor.fetchall()
        
        # Build weeks data structure
        weeks_data = {}
        for row in heatmap_data:
            week_start, dow, users, bet_tx, volume = row
            if week_start not in weeks_data:
                weeks_data[week_start] = {}
            weeks_data[week_start][int(dow)] = bet_tx
        
        # Convert to list format for frontend
        weeks_list = []
        for week_start in sorted(weeks_data.keys()):
            week_data = {
                'week_start': week_start,
                'days': {}
            }
            for i in range(7):
                week_data['days'][i] = weeks_data[week_start].get(i, 0)
            weeks_list.append(week_data)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': weeks_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/token-volumes", methods=['GET'])
def get_token_volume_heatmaps():
    """Get token volume heatmaps for MON and JERRY."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query for MON token volumes - use actual data range
        mon_query = """
        WITH RECURSIVE calendar(full_date) AS (
          SELECT '2025-02-04' -- Start from your actual data start date
          UNION ALL
          SELECT DATE(full_date, '+1 day')
          FROM calendar
          WHERE full_date < '2025-07-10' -- End at your actual data end date
        )
        SELECT
          DATE(c.full_date, '-6 days', 'weekday 1') as week_start,
          CASE CAST(strftime('%w', c.full_date) AS INTEGER)
            WHEN 0 THEN 7 
            ELSE CAST(strftime('%w', c.full_date) AS INTEGER)
          END as day_of_week,
          SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) as mon_volume
        FROM 
          calendar c
        LEFT JOIN 
          betting_transactions t ON DATE(t.timestamp) = c.full_date
        GROUP BY 
          week_start, day_of_week
        ORDER BY 
          week_start, day_of_week
        """
        
        jerry_query = """
        WITH RECURSIVE calendar(full_date) AS (
          SELECT '2025-02-04' -- Start from your actual data start date
          UNION ALL
          SELECT DATE(full_date, '+1 day')
          FROM calendar
          WHERE full_date < '2025-07-10' -- End at your actual data end date
        )
        SELECT
          DATE(c.full_date, '-6 days', 'weekday 1') as week_start,
          CASE CAST(strftime('%w', c.full_date) AS INTEGER)
            WHEN 0 THEN 7 
            ELSE CAST(strftime('%w', c.full_date) AS INTEGER)
          END as day_of_week,
          SUM(CASE WHEN t.token = 'Jerry' THEN t.amount ELSE 0 END) as jerry_volume
        FROM 
          calendar c
        LEFT JOIN 
          betting_transactions t ON DATE(t.timestamp) = c.full_date
        GROUP BY 
          week_start, day_of_week
        ORDER BY 
          week_start, day_of_week
        """
        
        # Execute queries
        cursor.execute(mon_query)
        mon_data = cursor.fetchall()
        
        cursor.execute(jerry_query)
        jerry_data = cursor.fetchall()
        
        # Process MON data
        mon_weeks = {}
        for row in mon_data:
            week_start, day_of_week, mon_volume = row
            if day_of_week is not None:
                day_names = ['', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_name = day_names[int(day_of_week)]
                
                if week_start not in mon_weeks:
                    mon_weeks[week_start] = {}
                mon_weeks[week_start][day_name] = mon_volume or 0
        
        # Process JERRY data
        jerry_weeks = {}
        for row in jerry_data:
            week_start, day_of_week, jerry_volume = row
            if day_of_week is not None:
                day_names = ['', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_name = day_names[int(day_of_week)]
                
                if week_start not in jerry_weeks:
                    jerry_weeks[week_start] = {}
                jerry_weeks[week_start][day_name] = jerry_volume or 0
        
        # Convert to frontend format
        sorted_weeks = sorted(set(list(mon_weeks.keys()) + list(jerry_weeks.keys())))
        weeks_list = []
        
        for week_start in sorted_weeks:
            week_data = {
                'week_start': week_start,
                'mon_volumes': {},
                'jerry_volumes': {}
            }
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                week_data['mon_volumes'][day] = mon_weeks.get(week_start, {}).get(day, 0)
                week_data['jerry_volumes'][day] = jerry_weeks.get(week_start, {}).get(day, 0)
            
            weeks_list.append(week_data)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': weeks_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/totals", methods=['GET'])
def get_total_stats():
    """Get total statistics including unique users."""
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
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'total_unique_users': total_unique_users,
                'total_transactions': total_transactions,
                'total_cards': total_cards,
                'total_mon_volume': total_mon_volume,
                'total_jerry_volume': total_jerry_volume,
                'total_mon_transactions': total_mon_transactions,
                'total_jerry_transactions': total_jerry_transactions
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/retention", methods=['GET'])
def get_user_retention():
    """Get user retention metrics week by week."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        WITH user_weeks AS (
            SELECT 
                from_address,
                DATE(timestamp, 'weekday 1', '-7 days') as week_start,
                MIN(DATE(timestamp, 'weekday 1', '-7 days')) OVER(PARTITION BY from_address) as first_week
            FROM betting_transactions
            WHERE DATE(timestamp) >= '2025-02-04'
            GROUP BY from_address, DATE(timestamp, 'weekday 1', '-7 days')
        ),
        new_users_by_week AS (
            SELECT 
                first_week as week_start,
                COUNT(DISTINCT from_address) as new_users
            FROM user_weeks
            GROUP BY first_week
        ),
        returning_users AS (
            SELECT 
                uw.first_week,
                uw.week_start,
                COUNT(DISTINCT uw.from_address) as returning_count
            FROM user_weeks uw
            WHERE uw.week_start > uw.first_week
            GROUP BY uw.first_week, uw.week_start
        )
        SELECT 
            nu.week_start as earliest_date,
            nu.new_users,
            NULL as one_week_later,
            NULL as two_week_later,
            NULL as three_week_later,
            NULL as four_week_later,
            NULL as five_week_later,
            NULL as six_week_later,
            NULL as seven_week_later,
            NULL as eight_week_later,
            NULL as nine_week_later,
            NULL as ten_week_later,
            NULL as over_ten_week_later
        FROM new_users_by_week nu
        ORDER BY nu.week_start
        LIMIT 20
        """
        
        cursor.execute(query)
        retention_data = cursor.fetchall()
        
        weeks = []
        for row in retention_data:
            earliest_date, users, w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11plus = row
            weeks.append({
                'earliest_date': earliest_date,
                'new_users': users,
                'one_week_later': w1,
                'two_week_later': w2,
                'three_week_later': w3,
                'four_week_later': w4,
                'five_week_later': w5,
                'six_week_later': w6,
                'seven_week_later': w7,
                'eight_week_later': w8,
                'nine_week_later': w9,
                'ten_week_later': w10,
                'over_ten_week_later': w11plus
            })
        
        # Calculate overall averages (simplified for now)
        total_weeks = len(weeks)
        if total_weeks > 0:
            avg_w1 = 0.15  # Placeholder values
            avg_w2 = 0.10
            avg_w3 = 0.08
            avg_w4 = 0.06
        else:
            avg_w1 = avg_w2 = avg_w3 = avg_w4 = 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'weeks': weeks,
                'averages': {
                    'one_week_retention': avg_w1,
                    'two_week_retention': avg_w2,
                    'three_week_retention': avg_w3,
                    'four_week_retention': avg_w4
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_full_analytics():
    """Get full analytics data for the dashboard using FlexibleAnalytics only."""
    try:
        db_path = DATABASE_PATH
        with FlexibleAnalytics(db_path) as analytics:
            analysis = analytics.analyze_timeframe('2025-02-03', 'week')
            top_bettors = analytics.get_top_bettors(20)
            return jsonify({
                'success': True,
                **analysis,
                'top_bettors': top_bettors
            })
    except Exception as e:
        print("API ERROR:", e)
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/health", methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'message': 'Backend is running',
        'database': DATABASE_PATH,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == "__main__":
    print(f"🚀 Starting betting analytics API...")
    print(f"📊 Database: {DATABASE_PATH}")
    print(f"🌐 API will be available at: http://localhost:5000")
    print(f"📈 Endpoints:")
    print(f"   - GET /api/stats - Basic statistics")
    print(f"   - GET /api/weekly - Weekly data")
    print(f"   - GET /api/daily - Daily data")
    print(f"   - GET /api/heatmap - Heatmap data")
    print(f"   - GET /api/periods - Period statistics")
    print(f"   - GET /api/health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000) 