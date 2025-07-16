#!/usr/bin/env python3
"""
Consolidated Analytics System
============================

Single file that handles all analytics processing and JSON export.
Combines database queries, analytics logic, and JSON saving functionality.

Key Features:
- Total Metrics (All Time)
- Activity Over Time (by period)
- Volume Evolution (for stacked area charts)
- Flexible Timeframes (day/week/month)
- Custom start date support
- Player Activity Analysis (RareLink submissions)
- JSON export to frontend
"""

import sqlite3
import json
import shutil
import gzip
import os
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Fix for Python 3.12+ SQLite datetime deprecation warning
def adapt_datetime(val):
    return val.isoformat()

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

# Configuration
DB_PATH = "/root/hypersync-client-python/betting_transactions.db"
OUTPUT_FILE = "analytics_dump.json"
FRONTEND_PUBLIC = "new/public/analytics_dump.json"
COMPRESSED_FILE = "new/public/analytics_dump.json.gz"

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect("betting_transactions.db")

def format_number(num):
    """Format large numbers with K/M suffixes."""
    if num is None:
        return "0"
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def format_currency(num):
    """Format currency values."""
    if num is None:
        return "$0"
    return f"${num:,.0f}"

class ConsolidatedAnalytics:
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
        """
        Get player activity analysis based on RareLink submissions.
        Creates categories for player distribution.
        """
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

    def get_average_metrics(self) -> Dict:
        """
        Get average metrics for all time:
        - Average submissions per day
        - Average players per day  
        - Average cards per RareLink slip
        """
        query = """
        SELECT 
            COUNT(DISTINCT from_address) as total_users,
            COUNT(DISTINCT tx_hash) as total_bet_tx,
            ROUND(AVG(n_cards), 2) as avg_cards_per_slip,
            SUM(n_cards) as total_cards,
            COUNT(DISTINCT DATE(timestamp)) as total_days,
            ROUND(CAST(COUNT(DISTINCT from_address) AS FLOAT) / COUNT(DISTINCT DATE(timestamp)), 2) as avg_users_per_day,
            ROUND(CAST(COUNT(DISTINCT tx_hash) AS FLOAT) / COUNT(DISTINCT DATE(timestamp)), 2) as avg_submissions_per_day
        FROM betting_transactions
        """
        
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        return {
            'total_users': result[0] or 0,
            'total_bet_tx': result[1] or 0,
            'avg_cards_per_slip': result[2] or 0.0,
            'total_cards': result[3] or 0,
            'total_days': result[4] or 0,
            'avg_users_per_day': result[5] or 0.0,
            'avg_submissions_per_day': result[6] or 0.0
        }

    def get_top_bettors(self, limit: int = 1000) -> list:
        """
        Get top bettors by total submissions.
        Returns list of dicts with address and submission count.
        """
        query = """
        SELECT 
            from_address,
            COUNT(DISTINCT tx_hash) as submission_count,
            SUM(n_cards) as total_cards,
            SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as mon_volume,
            SUM(CASE WHEN token = 'Jerry' THEN amount ELSE 0 END) as jerry_volume
        FROM betting_transactions
        GROUP BY from_address
        ORDER BY submission_count DESC
        LIMIT ?
        """
        
        self.cursor.execute(query, (limit,))
        results = self.cursor.fetchall()
        
        top_bettors = []
        for row in results:
            address, submissions, cards, mon_vol, jerry_vol = row
            top_bettors.append({
                'address': address,
                'submissions': submissions,
                'total_cards': cards,
                'mon_volume': mon_vol or 0.0,
                'jerry_volume': jerry_vol or 0.0
            })
        
        return top_bettors

    def get_activity_over_time(self, start_date: str, timeframe: str) -> List[Dict]:
        """
        Get activity over time for a specific timeframe.
        Returns data for submissions, active addresses, and volume.
        """
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
        
        query = f"""
        {period_generator}
        SELECT 
            p.period_number,
            p.period_start,
            p.period_end,
            COUNT(DISTINCT t.tx_hash) as submissions,
            COUNT(DISTINCT t.from_address) as active_addresses,
            SUM(CASE WHEN t.token = 'MON' THEN t.amount ELSE 0 END) as mon_volume,
            SUM(CASE WHEN t.token = 'Jerry' THEN t.amount ELSE 0 END) as jerry_volume,
            SUM(t.n_cards) as total_cards,
            ROUND(AVG(t.n_cards), 2) as avg_cards_per_submission
        FROM periods p
        LEFT JOIN betting_transactions t ON 
            DATE(t.timestamp) >= p.period_start AND 
            DATE(t.timestamp) <= p.period_end
        GROUP BY p.period_number, p.period_start, p.period_end
        ORDER BY p.period_number
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        activity_data = []
        for row in results:
            period_num, start_date, end_date, submissions, active_addr, mon_vol, jerry_vol, total_cards, avg_cards = row
            activity_data.append({
                'period_number': period_num,
                'start_date': start_date,
                'end_date': end_date,
                'submissions': submissions or 0,
                'active_addresses': active_addr or 0,
                'mon_volume': mon_vol or 0.0,
                'jerry_volume': jerry_vol or 0.0,
                'total_cards': total_cards or 0,
                'avg_cards_per_submission': avg_cards or 0.0
            })
        
        return activity_data

    def get_volume_evolution(self, start_date: str, timeframe: str) -> List[Dict]:
        """
        Get volume evolution over time for stacked area charts.
        Returns MON and JERRY volume data by period.
        """
        activity_data = self.get_activity_over_time(start_date, timeframe)
        
        volume_data = []
        for period in activity_data:
            volume_data.append({
                'start_date': period['start_date'],
                'mon_volume': period['mon_volume'],
                'jerry_volume': period['jerry_volume']
            })
        
        return volume_data

    def get_rbs_stats_by_periods(self) -> List[Dict]:
        """
        Get RBS statistics by periods for the stats table.
        Returns comprehensive period-by-period analysis.
        """
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
            DATE(t.timestamp) >= p.week_start AND 
            DATE(t.timestamp) <= p.week_end
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

    def get_cumulative_active_bettors(self, start_date: str, timeframe: str) -> List[Dict]:
        """
        Get cumulative active bettors over time.
        Shows growth of unique users over time.
        """
        activity_data = self.get_activity_over_time(start_date, timeframe)
        
        cumulative_data = []
        cumulative_users = set()
        
        for period in activity_data:
            # Get unique users for this period
            query = """
            SELECT DISTINCT from_address
            FROM betting_transactions
            WHERE DATE(timestamp) >= ? AND DATE(timestamp) <= ?
            """
            self.cursor.execute(query, (period['start_date'], period['end_date']))
            period_users = {row[0] for row in self.cursor.fetchall()}
            
            # Add to cumulative set
            cumulative_users.update(period_users)
            
            cumulative_data.append({
                'start_date': period['start_date'],
                'cumulative_active_bettors': len(cumulative_users)
            })
        
        return cumulative_data

    def analyze_timeframe(self, start_date: str, timeframe: str) -> Dict:
        """
        Complete analysis for a specific timeframe.
        Returns all metrics for the given timeframe.
        """
        total_metrics = self.get_total_metrics()
        player_activity = self.get_player_activity_analysis()
        activity_over_time = self.get_activity_over_time(start_date, timeframe)
        volume_evolution = self.get_volume_evolution(start_date, timeframe)
        rbs_stats = self.get_rbs_stats_by_periods()
        
        return {
            'total_metrics': total_metrics,
            'player_activity': player_activity,
            'activity_over_time': activity_over_time,
            'volume_evolution': volume_evolution,
            'rbs_stats_by_periods': rbs_stats
        }

    def print_analysis(self, analysis: Dict):
        """Print formatted analysis results."""
        print("\n" + "="*60)
        print("RBS ANALYTICS REPORT")
        print("="*60)
        
        # Total Metrics
        print("\n📊 TOTAL METRICS (All Time):")
        print("-" * 40)
        tm = analysis['total_metrics']
        print(f"Total Submissions: {format_number(tm['total_submissions'])}")
        print(f"Total Active Addresses: {format_number(tm['total_active_addresses'])}")
        print(f"Total $MON Volume: {format_currency(tm['total_mon_volume'])}")
        print(f"Total $JERRY Volume: {format_currency(tm['total_jerry_volume'])}")
        print(f"Total Cards: {format_number(tm['total_cards'])}")
        
        # Player Activity
        print("\n👥 PLAYER ACTIVITY:")
        print("-" * 40)
        pa = analysis['player_activity']
        print(f"Total Players: {format_number(pa['total_players'])}")
        for category in pa['categories']:
            print(f"{category['category']}: {format_number(category['player_count'])} ({category['percentage']}%)")
        
        # Recent Activity
        print("\n📈 RECENT ACTIVITY:")
        print("-" * 40)
        ao = analysis['activity_over_time']
        if ao:
            latest = ao[-1]
            print(f"Latest Period: {latest['start_date']} to {latest['end_date']}")
            print(f"Submissions: {format_number(latest['submissions'])}")
            print(f"Active Addresses: {format_number(latest['active_addresses'])}")
            print(f"$MON Volume: {format_currency(latest['mon_volume'])}")
            print(f"$JERRY Volume: {format_currency(latest['jerry_volume'])}")
        
        print("\n" + "="*60)

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

def get_timeframe_slips_by_card_count(analytics, timeframe, start_date='2025-02-03', min_cards=2, max_cards=7):
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

def print_top_bettors(analytics, limit=20):
    """Print top bettors table."""
    top_bettors = analytics.get_top_bettors(limit)
    
    print(f"\n🏆 TOP {limit} BETTORS:")
    print("-" * 80)
    print(f"{'Rank':<4} {'Address':<42} {'Submissions':<12} {'Cards':<8} {'$MON':<12} {'$JERRY':<12}")
    print("-" * 80)
    
    for i, bettor in enumerate(top_bettors[:limit], 1):
        address = bettor['address'][:40] + "..." if len(bettor['address']) > 40 else bettor['address']
        submissions = format_number(bettor['submissions'])
        cards = format_number(bettor['total_cards'])
        mon_vol = format_currency(bettor['mon_volume'])
        jerry_vol = format_currency(bettor['jerry_volume'])
        
        print(f"{i:<4} {address:<42} {submissions:<12} {cards:<8} {mon_vol:<12} {jerry_vol:<12}")

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='RBS Analytics System')
    parser.add_argument('--db-path', type=str, default='betting_transactions.db', help='Path to database file')
    parser.add_argument('--start-date', type=str, default='2025-02-03', help='Start date for analysis')
    parser.add_argument('--timeframe', type=str, default='week', choices=['day', 'week', 'month'], help='Timeframe for analysis')
    parser.add_argument('--top-bettors', type=int, default=20, help='Number of top bettors to show')
    parser.add_argument('--output-json', action='store_true', help='Output JSON instead of text')
    
    args = parser.parse_args()
    
    with ConsolidatedAnalytics(args.db_path) as analytics:
        if args.output_json:
            # Generate JSON output
            generate_and_save_json(analytics)
        else:
            # Generate text output
            analysis = analytics.analyze_timeframe(args.start_date, args.timeframe)
            analytics.print_analysis(analysis)
            print_top_bettors(analytics, args.top_bettors)

def generate_and_save_json(analytics):
    """Generate analytics and save to JSON files."""
    print("🔄 Generating analytics for all timeframes...")
    
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
            "generated_at": "2025-01-27T00:00:00Z",
            "timeframes_available": ["daily", "weekly", "monthly"],
            "default_timeframe": "weekly"
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
    
    # Print file sizes
    uncompressed_size = os.path.getsize(FRONTEND_PUBLIC)
    compressed_size = os.path.getsize(COMPRESSED_FILE)
    compression_ratio = (1 - compressed_size / uncompressed_size) * 100
    
    print(f"📊 File sizes:")
    print(f"   Uncompressed: {uncompressed_size / 1024:.1f} KB")
    print(f"   Compressed: {compressed_size / 1024:.1f} KB")
    print(f"   Compression: {compression_ratio:.1f}%")

if __name__ == "__main__":
    # Check if we should generate JSON or run in text mode
    import sys
    if len(sys.argv) > 1 and any(arg in sys.argv for arg in ['--output-json', '-j']):
        # Generate JSON output
        with ConsolidatedAnalytics(DB_PATH) as analytics:
            generate_and_save_json(analytics)
    else:
        # Run in text mode
        main() 