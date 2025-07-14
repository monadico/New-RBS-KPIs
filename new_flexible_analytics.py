#!/usr/bin/env python3
"""
New Flexible Analytics System
============================

Based on print_weekly_data.py structure with enhanced flexibility.
Provides comprehensive analytics with customizable timeframes and start dates.

Key Features:
- Total Metrics (All Time)
- Activity Over Time (by period)
- Volume Evolution (for stacked area charts)
- Flexible Timeframes (day/week/month)
- Custom start date support
- Player Activity Analysis (RareLink submissions)
"""

import sqlite3
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
        Get top bettors table with their statistics.
        Based on the provided query structure.
        """
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

    def get_activity_over_time(self, start_date: str, timeframe: str) -> List[Dict]:
        """
        Get activity over time data for the specified timeframe and start date.
        Based on print_weekly_data.py structure.
        """
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

    def get_volume_evolution(self, start_date: str, timeframe: str) -> List[Dict]:
        """
        Get volume evolution data structured for stacked area charts.
        This is essentially the same as activity_over_time but focused on volume metrics.
        """
        activity_data = self.get_activity_over_time(start_date, timeframe)
        
        # Transform for volume evolution (stacked area charts)
        volume_evolution = []
        for period in activity_data:
            volume_evolution.append({
                'period': period['period'],
                'start_date': period['start_date'],
                'end_date': period['end_date'],
                'mon_volume': period['mon_volume'],
                'jerry_volume': period['jerry_volume'],
                'total_volume': period['total_volume'],
                'mon_transactions': period['mon_transactions'],
                'jerry_transactions': period['jerry_transactions']
            })
        
        return volume_evolution

    def get_rbs_stats_by_periods(self) -> List[Dict]:
        """
        Get RBS statistics for different timeframes:
        - All time
        - Last 90 days
        - Last 30 days
        - Last 7 days
        - Last 1 day
        """
        periods = [
            ("All time", None, None),
            ("Last 90 days", "datetime('now', '-90 days')", "datetime('now')"),
            ("Last 30 days", "datetime('now', '-30 days')", "datetime('now')"),
            ("Last 7 days", "datetime('now', '-7 days')", "datetime('now')"),
            ("Last 1 day", "datetime('now', '-1 day')", "datetime('now')")
        ]
        
        rbs_stats = []
        
        for period_name, start_date, end_date in periods:
            if start_date is None and end_date is None:
                # All time query
                query = """
                SELECT 
                    SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as mon_volume,
                    SUM(CASE WHEN token = 'Jerry' THEN amount ELSE 0 END) as jerry_volume,
                    COUNT(DISTINCT tx_hash) as submissions,
                    COUNT(DISTINCT from_address) as active_bettors,
                    SUM(n_cards) as total_cards
                FROM betting_transactions
                """
                self.cursor.execute(query)
            else:
                # Time-bounded query
                query = f"""
                SELECT 
                    SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as mon_volume,
                    SUM(CASE WHEN token = 'Jerry' THEN amount ELSE 0 END) as jerry_volume,
                    COUNT(DISTINCT tx_hash) as submissions,
                    COUNT(DISTINCT from_address) as active_bettors,
                    SUM(n_cards) as total_cards
                FROM betting_transactions
                WHERE timestamp >= {start_date} AND timestamp <= {end_date}
                """
                self.cursor.execute(query)
            
            row = self.cursor.fetchone()
            
            if row:
                rbs_stats.append({
                    'period': period_name,
                    'mon_volume': row[0] or 0.0,
                    'jerry_volume': row[1] or 0.0,
                    'total_volume': (row[0] or 0.0) + (row[1] or 0.0),
                    'submissions': row[2] or 0,
                    'active_bettors': row[3] or 0,
                    'total_cards': row[4] or 0
                })
        
        return rbs_stats

    def get_cumulative_active_bettors(self, start_date: str, timeframe: str) -> List[Dict]:
        """
        Calculate cumulative active bettors over time.
        This builds up the total active bettors from the new bettors data.
        """
        activity_data = self.get_activity_over_time(start_date, timeframe)
        
        cumulative_data = []
        cumulative_active = 0
        
        for period in activity_data:
            cumulative_active += period['new_bettors']
            cumulative_data.append({
                'period': period['period'],
                'start_date': period['start_date'],
                'end_date': period['end_date'],
                'new_bettors': period['new_bettors'],
                'cumulative_active_bettors': cumulative_active,
                'active_addresses': period['active_addresses']
            })
        
        return cumulative_data

    def analyze_timeframe(self, start_date: str, timeframe: str) -> Dict:
        """Analyze data for a specific timeframe and start date."""
        total_metrics = self.get_total_metrics()
        activity_over_time = self.get_activity_over_time(start_date, timeframe)
        volume_evolution = self.get_volume_evolution(start_date, timeframe)
        player_activity = self.get_player_activity_analysis()
        average_metrics = self.get_average_metrics()
        rbs_stats_by_periods = self.get_rbs_stats_by_periods()
        cumulative_active_bettors = self.get_cumulative_active_bettors(start_date, timeframe)
        
        return {
            'timeframe': timeframe,
            'start_date': start_date,
            'total_periods': len(activity_over_time),
            'total_metrics': total_metrics,
            'activity_over_time': activity_over_time,
            'volume_evolution': volume_evolution,
            'player_activity': player_activity,
            'average_metrics': average_metrics,
            'rbs_stats_by_periods': rbs_stats_by_periods,
            'cumulative_active_bettors': cumulative_active_bettors
        }

    def print_analysis(self, analysis: Dict):
        """Print analysis results in a formatted way."""
        print("=" * 80)
        print(f"📊 {analysis['timeframe'].upper()} ANALYTICS")
        print(f"📅 Start Date: {analysis['start_date']}")
        print(f"📈 Total Periods: {analysis['total_periods']}")
        print("=" * 80)
        
        # Print Total Metrics
        totals = analysis['total_metrics']
        print("\n🎯 TOTAL METRICS (All Time):")
        print(f"   Total Rarelink Submissions: {format_number(totals['total_submissions'])}")
        print(f"   Total Active Addresses: {format_number(totals['total_active_addresses'])}")
        print(f"   Total MON Volume: {format_currency(totals['total_mon_volume'])}")
        print(f"   Total JERRY Volume: {format_currency(totals['total_jerry_volume'])}")
        print(f"   Total Cards: {format_number(totals['total_cards'])}")
        
        # Print Player Activity Analysis
        player_activity = analysis['player_activity']
        print(f"\n👥 PLAYER ACTIVITY ANALYSIS (Pizza Chart Data):")
        print(f"   Total Players: {format_number(player_activity['total_players'])}")
        print()
        
        for category in player_activity['categories']:
            print(f"   {category['category']}: {format_number(category['player_count'])} players ({category['percentage']:.1f}%)")
        
        # Print Average Metrics
        avg_metrics = analysis['average_metrics']
        print(f"\n📊 AVERAGE METRICS (3-Week Period):")
        print(f"   Average Submissions per Day: {avg_metrics['avg_submissions_per_day']:.2f}")
        print(f"   Average Players per Day: {avg_metrics['avg_users_per_day']:.2f}")
        print(f"   Average Cards per RareLink Slip: {avg_metrics['avg_cards_per_slip']:.2f}")
        print(f"   Total Days Analyzed: {avg_metrics['total_days']}")
        print(f"   Total Users in Period: {format_number(avg_metrics['total_users'])}")
        print(f"   Total Submissions in Period: {format_number(avg_metrics['total_bet_tx'])}")
        print(f"   Total Cards in Period: {format_number(avg_metrics['total_cards'])}")
        
        if not analysis['activity_over_time']:
            print("\n❌ No data found for the specified timeframe and start date!")
            return
        
        # Print Activity Over Time
        print(f"\n📈 ACTIVITY OVER TIME ({analysis['timeframe'].upper()}):")
        
        header_format = {
            'day':   f"{'Period':<8} {'Date':<12} {'Submissions':<12} {'Active Addr':<12} {'New Bettors':<12} {'MON Vol':<15} {'JERRY Vol':<15} {'Total Vol':<15}",
            'week':  f"{'Week':<6} {'Start Date':<12} {'End Date':<12} {'Submissions':<12} {'Active Addr':<12} {'New Bettors':<12} {'MON Vol':<15} {'JERRY Vol':<15} {'Total Vol':<15}",
            'month': f"{'Month':<8} {'Start Date':<12} {'End Date':<12} {'Submissions':<12} {'Active Addr':<12} {'New Bettors':<12} {'MON Vol':<15} {'JERRY Vol':<15} {'Total Vol':<15}"
        }
        print(header_format[analysis['timeframe']])
        print("-" * len(header_format[analysis['timeframe']]))
        
        for period in analysis['activity_over_time'][:3]:  # Show first 3 periods for testing
            mon_vol_str = format_currency(period['mon_volume'])
            jerry_vol_str = format_currency(period['jerry_volume'])
            total_vol_str = format_currency(period['total_volume'])
            
            if analysis['timeframe'] == 'day':
                print(f"{period['period']:<8} {period['start_date']:<12} {format_number(period['submissions']):<12} {format_number(period['active_addresses']):<12} {format_number(period['new_bettors']):<12} {mon_vol_str:<15} {jerry_vol_str:<15} {total_vol_str:<15}")
            else:
                print(f"{period['period']:<6} {period['start_date']:<12} {period['end_date']:<12} {format_number(period['submissions']):<12} {format_number(period['active_addresses']):<12} {format_number(period['new_bettors']):<12} {mon_vol_str:<15} {jerry_vol_str:<15} {total_vol_str:<15}")
        
        print("-" * len(header_format[analysis['timeframe']]))
        
        # Print summary
        total_submissions = sum(p['submissions'] for p in analysis['activity_over_time'])
        total_new_bettors = sum(p['new_bettors'] for p in analysis['activity_over_time'])
        total_mon_vol = sum(p['mon_volume'] for p in analysis['activity_over_time'])
        total_jerry_vol = sum(p['jerry_volume'] for p in analysis['activity_over_time'])
        total_vol = sum(p['total_volume'] for p in analysis['activity_over_time'])

        print(f"\n📊 PERIOD SUMMARY:")
        print(f"   Total Submissions in Periods: {format_number(total_submissions)}")
        print(f"   Total New Bettors in Periods: {format_number(total_new_bettors)}")
        print(f"   Total MON Volume in Periods: {format_currency(total_mon_vol)}")
        print(f"   Total JERRY Volume in Periods: {format_currency(total_jerry_vol)}")
        print(f"   Total Volume in Periods: {format_currency(total_vol)}")

def print_top_bettors(analytics, limit=20):
    """Print the top bettors table."""
    top_bettors = analytics.get_top_bettors(limit)
    if not top_bettors:
        print("\n❌ No top bettors data found!")
        return
    print("\n🏆 TOP BETTORS (by number of bets):")
    print(f"{'Rank':<5} {'Address':<44} {'MON':>12} {'JERRY':>12} {'Total':>12} {'Avg Cards':>10} {'Bets':>8} {'Days':>6}")
    print("-" * 110)
    for b in top_bettors:
        print(f"{b['rank']:<5} {b['user_address']:<44} {b['total_mon']:>12,.0f} {b['total_jerry']:>12,.0f} {b['total_bet']:>12,.0f} {b['avg_cards_per_slip']:>10.2f} {b['total_bets']:>8} {b['active_days']:>6}")
    print("-" * 110)

def main():
    """Main function to run the flexible analytics."""
    parser = argparse.ArgumentParser(description='New Flexible Betting Analytics')
    parser.add_argument('--timeframe', choices=['day', 'week', 'month'], default='week', help='Timeframe for analysis')
    parser.add_argument('--start-date', type=str, default='2025-02-03', help='Start date in YYYY-MM-DD format')
    parser.add_argument('--db-path', type=str, default='betting_transactions.db', help='Path to database file')
    parser.add_argument('--top-bettors', type=int, default=20, help='Number of top bettors to display')
    
    args = parser.parse_args()
    
    try:
        with FlexibleAnalytics(args.db_path) as analytics:
            print(f"🎯 Analyzing {args.timeframe} data starting from {args.start_date}")
            
            analysis = analytics.analyze_timeframe(args.start_date, args.timeframe)
            analytics.print_analysis(analysis)
            print_top_bettors(analytics, args.top_bettors)
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main() 