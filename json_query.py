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
    DB_PATH = "/app/data/betting_transactions.db"
    OUTPUT_FILE = "/app/analytics_dump.json"
    FRONTEND_PUBLIC = "/app/new/public/analytics_dump.json"
    COMPRESSED_FILE = "/app/new/public/analytics_dump.json.gz"
    ANALYTICS_CHECKPOINT_FILE = "/app/data/analytics_checkpoint.json"
else:
    DB_PATH = os.getenv('DB_PATH', 'betting_transactions.db')
    OUTPUT_FILE = "analytics_dump.json"
    FRONTEND_PUBLIC = "new/public/analytics_dump.json"
    COMPRESSED_FILE = "new/public/analytics_dump.json.gz"
    ANALYTICS_CHECKPOINT_FILE = "data/analytics_checkpoint.json"

class FlexibleAnalytics:
    """Main analytics class for flexible timeframe analysis."""
    
    def __init__(self, db_path: str = "betting_transactions.db"):
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

    def get_last_analytics_checkpoint(self) -> Optional[str]:
        """Get the last timestamp when analytics were generated."""
        try:
            if os.path.exists(ANALYTICS_CHECKPOINT_FILE):
                with open(ANALYTICS_CHECKPOINT_FILE, 'r') as f:
                    checkpoint = json.load(f)
                    return checkpoint.get('last_generated')
            return None
        except Exception as e:
            print(f"Warning: Could not read analytics checkpoint: {e}")
            return None

    def update_analytics_checkpoint(self, timestamp: str):
        """Update the analytics checkpoint timestamp."""
        try:
            os.makedirs(os.path.dirname(ANALYTICS_CHECKPOINT_FILE), exist_ok=True)
            checkpoint = {
                'last_generated': timestamp,
                'updated_at': datetime.now().isoformat()
            }
            with open(ANALYTICS_CHECKPOINT_FILE, 'w') as f:
                json.dump(checkpoint, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not update analytics checkpoint: {e}")

    def get_new_transactions_since(self, since_timestamp: str) -> List[Dict]:
        """Get new transactions since the last analytics generation."""
        query = """
        SELECT 
            tx_hash, from_address, token, amount, n_cards, timestamp
        FROM betting_transactions 
        WHERE timestamp > ?
        ORDER BY timestamp
        """
        self.cursor.execute(query, (since_timestamp,))
        results = self.cursor.fetchall()
        
        transactions = []
        for row in results:
            tx_hash, from_address, token, amount, n_cards, timestamp = row
            transactions.append({
                'tx_hash': tx_hash,
                'from_address': from_address,
                'token': token,
                'amount': amount,
                'n_cards': n_cards,
                'timestamp': timestamp
            })
        return transactions

    def get_total_metrics(self) -> Dict:
        """Get total metrics for all time."""
        query = """
        SELECT
            COUNT(DISTINCT tx_hash) as total_submissions,
            COUNT(DISTINCT from_address) as total_active_addresses,
            SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as total_mon_volume,
            SUM(CASE WHEN token = 'Jerry' THEN amount ELSE 0 END) as total_jerry_volume,
            SUM(n_cards) as total_cards
        FROM betting_transactions
        """
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return {
            'total_submissions': result[0] or 0,
            'total_active_addresses': result[1] or 0,
            'total_mon_volume': result[2] or 0.0,
            'total_jerry_volume': result[3] or 0.0,
            'total_cards': result[4] or 0
        }

    def get_player_activity_analysis(self) -> Dict:
        """Get player activity analysis based on RareLink submissions."""
        query = """
        WITH user_submissions AS (
            SELECT 
                from_address,
                COUNT(DISTINCT tx_hash) as bet_tx_count
            FROM betting_transactions
            GROUP BY from_address
        ),
        categorized_users AS (
            SELECT 
                CASE
                    WHEN bet_tx_count = 1 THEN '1 RareLink'
                    WHEN bet_tx_count >= 2 AND bet_tx_count < 10 THEN '2~9 RareLinks'
                    WHEN bet_tx_count >= 10 AND bet_tx_count < 100 THEN '10~99 RareLinks'
                    WHEN bet_tx_count >= 100 THEN '100+ RareLinks'
                END as submission_category,
                COUNT(DISTINCT from_address) as player_count
            FROM user_submissions
            GROUP BY 
                CASE
                    WHEN bet_tx_count = 1 THEN '1 RareLink'
                    WHEN bet_tx_count >= 2 AND bet_tx_count < 10 THEN '2~9 RareLinks'
                    WHEN bet_tx_count >= 10 AND bet_tx_count < 100 THEN '10~99 RareLinks'
                    WHEN bet_tx_count >= 100 THEN '100+ RareLinks'
                END
        )
        SELECT 
            submission_category,
            player_count,
            ROUND(CAST(player_count AS FLOAT) / (SELECT SUM(player_count) FROM categorized_users) * 100, 2) as percentage
        FROM categorized_users
        ORDER BY 
            CASE submission_category
                WHEN '1 RareLink' THEN 1
                WHEN '2~9 RareLinks' THEN 2
                WHEN '10~99 RareLinks' THEN 3
                WHEN '100+ RareLinks' THEN 4
            END
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        player_activity = {
            'categories': [],
            'total_players': 0,
            'summary': {}
        }
        
        total_players = 0
        for row in results:
            category, player_count, percentage = row
            total_players += player_count
            
            player_activity['categories'].append({
                'category': category,
                'player_count': player_count,
                'percentage': percentage
            })
        
        player_activity['total_players'] = total_players
        
        # Create summary
        for cat in player_activity['categories']:
            player_activity['summary'][cat['category']] = {
                'count': cat['player_count'],
                'percentage': cat['percentage']
            }
        
        return player_activity

    def get_top_bettors(self, limit: int = 1000) -> list:
        """Get top bettors table with their statistics."""
        query = """
        SELECT 
            from_address as user_address,
            SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as total_mon,
            SUM(CASE WHEN token = 'Jerry' THEN amount ELSE 0 END) as total_jerry,
            SUM(amount) as total_bet,
            ROUND(AVG(n_cards), 2) as avg_cards_per_slip,
            COUNT(DISTINCT tx_hash) as total_bets,
            COUNT(DISTINCT DATE(timestamp)) as active_days
        FROM betting_transactions
        GROUP BY from_address
        ORDER BY total_bets DESC
        LIMIT ?
        """
        self.cursor.execute(query, (limit,))
        results = self.cursor.fetchall()
        top_bettors = []
        for i, row in enumerate(results):
            user_address, total_mon, total_jerry, total_bet, avg_cards, total_bets, active_days = row
            top_bettors.append({
                'rank': i + 1,
                'user_address': user_address,
                'total_mon': total_mon or 0.0,
                'total_jerry': total_jerry or 0.0,
                'total_bet': total_bet or 0.0,
                'avg_cards_per_slip': avg_cards or 0.0,
                'total_bets': total_bets or 0,
                'active_days': active_days or 0
            })
        return top_bettors

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
        first_time_users AS (
            SELECT 
                from_address,
                MIN(timestamp) as first_bet_date
            FROM betting_transactions
            GROUP BY from_address
        )
        SELECT 
            p.period_start,
            p.period_end,
            p.period_number,
            COUNT(t.tx_hash) as submissions,
            COUNT(DISTINCT t.from_address) as active_addresses,
            COUNT(DISTINCT CASE WHEN DATE(ftu.first_bet_date) >= p.period_start AND DATE(ftu.first_bet_date) <= p.period_end THEN t.from_address END) as new_bettors,
            SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) as mon_volume,
            SUM(CASE WHEN t.token = 'Jerry' THEN t.amount ELSE 0 END) as jerry_volume,
            SUM(t.n_cards) as total_cards,
            ROUND(AVG(t.n_cards), 2) as avg_cards_per_submission,
            AVG(t.amount) as avg_bet_amount,
            SUM(CASE WHEN t.token = 'MON' THEN 1 ELSE 0 END) as mon_transactions,
            SUM(CASE WHEN t.token = 'Jerry' THEN 1 ELSE 0 END) as jerry_transactions
        FROM periods p
        LEFT JOIN betting_transactions t ON 
            DATE(t.timestamp) >= p.period_start AND DATE(t.timestamp) <= p.period_end
            {timestamp_filter}
        LEFT JOIN first_time_users ftu ON t.from_address = ftu.from_address
        GROUP BY p.period_start, p.period_end, p.period_number
        HAVING COUNT(t.tx_hash) > 0
        ORDER BY p.period_start
        """

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        activity_data = []
        for row in results:
            period_start, period_end, period_num, submissions, active_addresses, new_bettors, mon_vol, jerry_vol, cards, avg_cards, avg_bet, mon_txs, jerry_txs = row
            
            activity_data.append({
                'period': period_num,
                'start_date': period_start,
                'end_date': period_end,
                'submissions': submissions or 0,
                'active_addresses': active_addresses or 0,
                'new_bettors': new_bettors or 0,
                'mon_volume': mon_vol or 0.0,
                'jerry_volume': jerry_vol or 0.0,
                'total_volume': (mon_vol or 0.0) + (jerry_vol or 0.0),
                'total_cards': cards or 0,
                'avg_cards_per_submission': avg_cards or 0.0,
                'avg_bet_amount': avg_bet or 0.0,
                'mon_transactions': mon_txs or 0,
                'jerry_transactions': jerry_txs or 0
            })

        return activity_data

    def get_rbs_stats_by_periods(self) -> List[Dict]:
        """Get RBS statistics by periods for the stats table."""
        query = """
        WITH periods AS (
            SELECT 
                DATE('2025-02-03', 'weekday 0', '-6 days') as week_start,
                DATE('2025-02-03', 'weekday 0', '+0 days') as week_end,
                1 as week_number
            
            UNION ALL
            
            SELECT 
                DATE(week_start, '+7 days') as week_start,
                DATE(week_end, '+7 days') as week_end,
                week_number + 1 as week_number
            FROM periods
            WHERE week_start <= DATE('now')
        )
        SELECT 
            p.week_number,
            p.week_start,
            p.week_end,
            COUNT(DISTINCT t.tx_hash) as total_submissions,
            COUNT(DISTINCT t.from_address) as unique_players,
            SUM(t.n_cards) as total_cards,
            ROUND(AVG(t.n_cards), 2) as avg_cards_per_slip,
            SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) as mon_volume,
            SUM(CASE WHEN t.token = 'Jerry' THEN t.amount ELSE 0 END) as jerry_volume,
            ROUND(CAST(COUNT(DISTINCT t.from_address) AS FLOAT) / COUNT(DISTINCT t.tx_hash), 2) as avg_submissions_per_player
        FROM periods p
        LEFT JOIN betting_transactions t ON 
            DATE(t.timestamp) >= p.week_start AND DATE(t.timestamp) <= p.week_end
        GROUP BY p.week_number, p.week_start, p.week_end
        ORDER BY p.week_number
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        stats_data = []
        for row in results:
            week_num, start_date, end_date, submissions, players, cards, avg_cards, mon_vol, jerry_vol, avg_sub_per_player = row
            stats_data.append({
                'period': f"Week {week_num}",
                'mon_volume': mon_vol or 0.0,
                'jerry_volume': jerry_vol or 0.0,
                'total_volume': (mon_vol or 0.0) + (jerry_vol or 0.0),
                'submissions': submissions or 0,
                'active_bettors': players or 0,
                'total_cards': cards or 0
            })
        
        return stats_data

    def analyze_timeframe(self, start_date: str, timeframe: str, since_timestamp: Optional[str] = None) -> Dict:
        """Analyze data for a specific timeframe and start date."""
        total_metrics = self.get_total_metrics()
        activity_over_time = self.get_activity_over_time(start_date, timeframe, since_timestamp)
        player_activity = self.get_player_activity_analysis()
        rbs_stats_by_periods = self.get_rbs_stats_by_periods()
        
        return {
            'timeframe': timeframe,
            'start_date': start_date,
            'total_periods': len(activity_over_time),
            'total_metrics': total_metrics,
            'activity_over_time': activity_over_time,
            'player_activity': player_activity,
            'rbs_stats_by_periods': rbs_stats_by_periods
        }

def get_overall_slips_by_card_count(analytics, min_cards=2, max_cards=7):
    query = f"""
        SELECT n_cards, COUNT(DISTINCT tx_hash) as bet_count
        FROM betting_transactions
        WHERE n_cards BETWEEN ? AND ?
        GROUP BY n_cards
        ORDER BY n_cards
    """
    analytics.cursor.execute(query, (min_cards, max_cards))
    results = analytics.cursor.fetchall()
    total_bets = sum(row[1] for row in results)
    summary = []
    for n_cards, bet_count in results:
        percent = (bet_count / total_bets * 100) if total_bets > 0 else 0
        summary.append({
            "cards_in_slip": n_cards,
            "bets": bet_count,
            "percentage": round(percent, 2)
        })
    return summary

def get_weekly_slips_by_card_count(analytics, min_cards=2, max_cards=7):
    """Get weekly breakdown of slips by card count for the stacked bar chart."""
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
    )
    SELECT 
        w.week_number,
        w.week_start,
        w.week_end,
        t.n_cards,
        COUNT(DISTINCT t.tx_hash) as bets
    FROM weeks w
    LEFT JOIN betting_transactions t ON 
        DATE(t.timestamp) >= w.week_start AND 
        DATE(t.timestamp) <= w.week_end AND
        t.n_cards BETWEEN ? AND ?
    GROUP BY w.week_number, w.week_start, w.week_end, t.n_cards
    HAVING COUNT(DISTINCT t.tx_hash) > 0
    ORDER BY w.week_number, t.n_cards
    """
    
    analytics.cursor.execute(query, (min_cards, max_cards))
    results = analytics.cursor.fetchall()
    
    # Group by week and card count
    weekly_data = {}
    for week_num, week_start, week_end, n_cards, bets in results:
        if week_num not in weekly_data:
            weekly_data[week_num] = {
                'week_number': week_num,
                'week_start': week_start,
                'week_end': week_end,
                'card_counts': {}
            }
        weekly_data[week_num]['card_counts'][n_cards] = bets
    
    # Convert to array format for frontend
    weekly_array = []
    for week_num in sorted(weekly_data.keys()):
        week_data = weekly_data[week_num]
        week_data['card_counts'] = [week_data['card_counts'].get(i, 0) for i in range(min_cards, max_cards + 1)]
        weekly_array.append(week_data)
    
    return weekly_array

def get_timeframe_slips_by_card_count(analytics, timeframe, start_date='2025-02-03', min_cards=2, max_cards=7, since_timestamp: Optional[str] = None):
    """Get card count data for different timeframes (daily, weekly, monthly)."""
    if timeframe == 'day':
        period_generator = f"""
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
        """
    elif timeframe == 'week':
        period_generator = f"""
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
        """
    elif timeframe == 'month':
        period_generator = f"""
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
        """
    else:
        return []
    
    # Add timestamp filter if since_timestamp is provided
    timestamp_filter = ""
    if since_timestamp:
        timestamp_filter = f"AND t.timestamp > '{since_timestamp}'"
    
    query = f"""
    {period_generator}
    SELECT 
        p.period_number,
        p.period_start,
        p.period_end,
        t.n_cards,
        COUNT(DISTINCT t.tx_hash) as bets
    FROM periods p
    LEFT JOIN betting_transactions t ON 
        DATE(t.timestamp) >= p.period_start AND 
        DATE(t.timestamp) <= p.period_end AND
        t.n_cards BETWEEN ? AND ?
        {timestamp_filter}
    GROUP BY p.period_number, p.period_start, p.period_end, t.n_cards
    HAVING COUNT(DISTINCT t.tx_hash) > 0
    ORDER BY p.period_number, t.n_cards
    """
    
    analytics.cursor.execute(query, (min_cards, max_cards))
    results = analytics.cursor.fetchall()
    
    # Group by period and card count
    period_data = {}
    for period_num, period_start, period_end, n_cards, bets in results:
        if period_num not in period_data:
            period_data[period_num] = {
                'period_number': period_num,
                'period_start': period_start,
                'period_end': period_end,
                'card_counts': {}
            }
        period_data[period_num]['card_counts'][n_cards] = bets
    
    # Convert to array format for frontend
    period_array = []
    for period_num in sorted(period_data.keys()):
        period_info = period_data[period_num]
        period_info['card_counts'] = [period_info['card_counts'].get(i, 0) for i in range(min_cards, max_cards + 1)]
        period_array.append(period_info)
    
    return period_array

def get_average_metrics(analytics):
    """Calculate average metrics using the user's SQL logic."""
    query = """
    SELECT 
        COUNT(DISTINCT from_address) as users,
        COUNT(DISTINCT tx_hash) as bet_tx,
        ROUND(AVG(n_cards)) as avg_cards,
        SUM(n_cards) as tot_cards,
        COUNT(DISTINCT DATE(timestamp)) as total_days
    FROM betting_transactions
    """
    
    analytics.cursor.execute(query)
    result = analytics.cursor.fetchone()
    
    if result:
        users, bet_tx, avg_cards, tot_cards, total_days = result
        total_days = total_days or 1  # Avoid division by zero
        
        return {
            "avg_submissions_per_day": round(bet_tx / total_days, 2),
            "avg_users_per_day": round(users / total_days, 2),
            "avg_players_per_day": round(users / total_days, 2),
            "avg_cards_per_slip": avg_cards or 0,
            "total_users": users,
            "total_bet_tx": bet_tx,
            "total_cards": tot_cards,
            "total_days": total_days
        }
    else:
        return {
            "avg_submissions_per_day": 0,
            "avg_users_per_day": 0,
            "avg_players_per_day": 0,
            "avg_cards_per_slip": 0,
            "total_users": 0,
            "total_bet_tx": 0,
            "total_cards": 0,
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
    # In a more sophisticated implementation, we could merge specific timeframes
    print(f"🔄 Merging analytics data since {since_timestamp}...")
    
    # Update metadata
    new_data['metadata']['generated_at'] = datetime.now().isoformat() + "Z"
    new_data['metadata']['last_incremental_update'] = since_timestamp
    
    return new_data

if __name__ == "__main__":
    with FlexibleAnalytics(DB_PATH) as analytics:
        print("🔄 Starting analytics generation...")
        
        # Check for incremental update
        last_checkpoint = analytics.get_last_analytics_checkpoint()
        current_timestamp = datetime.now().isoformat()
        
        if last_checkpoint:
            print(f"📅 Last analytics generated: {last_checkpoint}")
            print("🔄 Running incremental update...")
            
            # Check if there are new transactions
            new_transactions = analytics.get_new_transactions_since(last_checkpoint)
            if not new_transactions:
                print("✅ No new transactions found. Analytics are up to date.")
                analytics.update_analytics_checkpoint(current_timestamp)
                exit(0)
            
            print(f"📊 Found {len(new_transactions)} new transactions since {last_checkpoint}")
            
            # Load existing analytics
            existing_analytics = load_existing_analytics()
            
            # Generate new analytics (full regeneration for now)
            print("🔄 Generating analytics for all timeframes...")
            timeframes = ['day', 'week', 'month']
            all_analytics = {}
            
            for timeframe in timeframes:
                print(f"📊 Processing {timeframe} data...")
                analysis = analytics.analyze_timeframe('2025-02-03', timeframe)
                all_analytics[timeframe] = analysis
            
            # Get additional data
            print("📈 Getting additional metrics...")
            top_bettors = analytics.get_top_bettors(20)
            overall_slips_by_card_count = get_overall_slips_by_card_count(analytics, 2, 7)
            weekly_slips_by_card_count = get_weekly_slips_by_card_count(analytics, 2, 7)
            average_metrics = get_average_metrics(analytics)
            
            # Get timeframe-specific card count data
            print("🎯 Getting card count data for all timeframes...")
            daily_slips_by_card_count = get_timeframe_slips_by_card_count(analytics, 'day', '2025-02-03', 2, 7)
            weekly_slips_by_card_count = get_timeframe_slips_by_card_count(analytics, 'week', '2025-02-03', 2, 7)
            monthly_slips_by_card_count = get_timeframe_slips_by_card_count(analytics, 'month', '2025-02-03', 2, 7)
            
            # Use weekly data as the main data (for backward compatibility)
            main_data = all_analytics['week']
            
            # Create optimized structure
            data = {
                "success": True,
                "metadata": {
                    "generated_at": current_timestamp + "Z",
                    "timeframes_available": ["daily", "weekly", "monthly"],
                    "default_timeframe": "weekly",
                    "last_incremental_update": last_checkpoint,
                    "new_transactions_processed": len(new_transactions)
                },
                # Main metrics (all time)
                "total_metrics": main_data['total_metrics'],
                "average_metrics": average_metrics,
                "player_activity": main_data['player_activity'],
                "rbs_stats_by_periods": main_data['rbs_stats_by_periods'],
                
                # Timeframe-specific data
                "timeframes": {
                    "daily": {
                        "activity_over_time": all_analytics['day']['activity_over_time'],
                        "slips_by_card_count": daily_slips_by_card_count
                    },
                    "weekly": {
                        "activity_over_time": all_analytics['week']['activity_over_time'],
                        "slips_by_card_count": weekly_slips_by_card_count
                    },
                    "monthly": {
                        "activity_over_time": all_analytics['month']['activity_over_time'],
                        "slips_by_card_count": monthly_slips_by_card_count
                    }
                },
                
                # Legacy data (for backward compatibility)
                "activity_over_time": main_data['activity_over_time'],
                "overall_slips_by_card_count": overall_slips_by_card_count,
                "weekly_slips_by_card_count": weekly_slips_by_card_count,
                "top_bettors": top_bettors
            }
            
        else:
            print("🔄 No previous analytics found. Running full generation...")
            
            # Generate analytics for multiple timeframes
            timeframes = ['day', 'week', 'month']
            all_analytics = {}
            
            for timeframe in timeframes:
                print(f"📊 Processing {timeframe} data...")
                analysis = analytics.analyze_timeframe('2025-02-03', timeframe)
                all_analytics[timeframe] = analysis
            
            # Get additional data
            print("📈 Getting additional metrics...")
            top_bettors = analytics.get_top_bettors(20)
            overall_slips_by_card_count = get_overall_slips_by_card_count(analytics, 2, 7)
            weekly_slips_by_card_count = get_weekly_slips_by_card_count(analytics, 2, 7)
            average_metrics = get_average_metrics(analytics)
            
            # Get timeframe-specific card count data
            print("🎯 Getting card count data for all timeframes...")
            daily_slips_by_card_count = get_timeframe_slips_by_card_count(analytics, 'day', '2025-02-03', 2, 7)
            weekly_slips_by_card_count = get_timeframe_slips_by_card_count(analytics, 'week', '2025-02-03', 2, 7)
            monthly_slips_by_card_count = get_timeframe_slips_by_card_count(analytics, 'month', '2025-02-03', 2, 7)
            
            # Use weekly data as the main data (for backward compatibility)
            main_data = all_analytics['week']
            
            # Create optimized structure
            data = {
                "success": True,
                "metadata": {
                    "generated_at": current_timestamp + "Z",
                    "timeframes_available": ["daily", "weekly", "monthly"],
                    "default_timeframe": "weekly",
                    "initial_generation": True
                },
                # Main metrics (all time)
                "total_metrics": main_data['total_metrics'],
                "average_metrics": average_metrics,
                "player_activity": main_data['player_activity'],
                "rbs_stats_by_periods": main_data['rbs_stats_by_periods'],
                
                # Timeframe-specific data
                "timeframes": {
                    "daily": {
                        "activity_over_time": all_analytics['day']['activity_over_time'],
                        "slips_by_card_count": daily_slips_by_card_count
                    },
                    "weekly": {
                        "activity_over_time": all_analytics['week']['activity_over_time'],
                        "slips_by_card_count": weekly_slips_by_card_count
                    },
                    "monthly": {
                        "activity_over_time": all_analytics['month']['activity_over_time'],
                        "slips_by_card_count": monthly_slips_by_card_count
                    }
                },
                
                # Legacy data (for backward compatibility)
                "activity_over_time": main_data['activity_over_time'],
                "overall_slips_by_card_count": overall_slips_by_card_count,
                "weekly_slips_by_card_count": weekly_slips_by_card_count,
                "top_bettors": top_bettors
            }
        
        # Save uncompressed JSON
        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Analytics data saved to {OUTPUT_FILE}")
        
        # Copy to frontend public dir
        shutil.copyfile(OUTPUT_FILE, FRONTEND_PUBLIC)
        print(f"✅ Analytics data copied to {FRONTEND_PUBLIC}")
        
        # Create compressed version for faster loading
        with open(FRONTEND_PUBLIC, 'rb') as f_in:
            with gzip.open(COMPRESSED_FILE, 'wb') as f_out:
                f_out.writelines(f_in)
        print(f"✅ Compressed version saved to {COMPRESSED_FILE}")
        
        # Update checkpoint
        analytics.update_analytics_checkpoint(current_timestamp)
        print(f"✅ Analytics checkpoint updated: {current_timestamp}")
        
        # Print file sizes
        import os
        uncompressed_size = os.path.getsize(FRONTEND_PUBLIC)
        compressed_size = os.path.getsize(COMPRESSED_FILE)
        compression_ratio = (1 - compressed_size / uncompressed_size) * 100
        
        print(f"📊 File sizes:")
        print(f"   Uncompressed: {uncompressed_size / 1024:.1f} KB")
        print(f"   Compressed: {compressed_size / 1024:.1f} KB")
        print(f"   Compression: {compression_ratio:.1f}%") 