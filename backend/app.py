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
DATABASE_PATH = os.getenv("DATABASE_PATH", "../betting_transactions.db")

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
    """Get daily aggregated data for charts."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as transaction_count,
            COUNT(DISTINCT from_address) as unique_users,
            SUM(amount) as total_volume,
            SUM(n_cards) as total_cards,
            AVG(amount) as avg_bet_amount,
            SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as mon_volume,
            SUM(CASE WHEN token = 'Jerry' THEN amount ELSE 0 END) as jerry_volume
        FROM betting_transactions
        WHERE timestamp >= DATE('2024-02-03')
        GROUP BY DATE(timestamp)
        ORDER BY date
        """
        
        cursor.execute(query)
        
        daily_data = []
        for row in cursor.fetchall():
            daily_data.append({
                'date': row[0],
                'transaction_count': row[1],
                'unique_users': row[2],
                'total_volume': row[3] or 0,
                'total_cards': row[4] or 0,
                'avg_bet_amount': row[5] or 0,
                'mon_volume': row[6] or 0,
                'jerry_volume': row[7] or 0
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': daily_data
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
        
        # Get data by day of week
        query = """
        SELECT 
            strftime('%w', timestamp) as day_of_week,
            COUNT(*) as transaction_count,
            COUNT(DISTINCT from_address) as unique_users,
            SUM(amount) as total_volume,
            SUM(n_cards) as total_cards
        FROM betting_transactions
        WHERE timestamp >= DATE('2024-02-03')
        GROUP BY strftime('%w', timestamp)
        ORDER BY day_of_week
        """
        
        cursor.execute(query)
        
        heatmap_data = []
        for row in cursor.fetchall():
            heatmap_data.append({
                'day_of_week': int(row[0]),
                'day_name': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][int(row[0])],
                'transaction_count': row[1],
                'unique_users': row[2],
                'total_volume': row[3] or 0,
                'total_cards': row[4] or 0
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': heatmap_data
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
            ("All Time", "2024-02-03", "datetime('now')"),
            ("Last 90 days", "datetime('now', '-90 days')", "datetime('now')"),
            ("Last 30 days", "datetime('now', '-30 days')", "datetime('now')"),
            ("Last 7 days", "datetime('now', '-7 days')", "datetime('now')"),
            ("Last 1 day", "datetime('now', '-1 day')", "datetime('now')")
        ]
        
        period_stats = []
        for period_name, start_date, end_date in periods:
            query = f"""
            SELECT 
                COUNT(*) as transaction_count,
                COUNT(DISTINCT from_address) as unique_users,
                SUM(amount) as total_volume
            FROM betting_transactions
            WHERE timestamp >= {start_date} AND timestamp <= {end_date}
            """
            
            cursor.execute(query)
            row = cursor.fetchone()
            
            period_stats.append({
                'period': period_name,
                'transactions': row[0],
                'users': row[1],
                'volume': row[2] or 0
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