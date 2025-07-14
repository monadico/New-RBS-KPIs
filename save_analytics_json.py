#!/usr/bin/env python3
import json
import shutil
import gzip
from new_flexible_analytics import FlexibleAnalytics

DB_PATH = "/root/hypersync-client-python/betting_transactions.db"
OUTPUT_FILE = "analytics_dump.json"
FRONTEND_PUBLIC = "frontend2/public/analytics_dump.json"
COMPRESSED_FILE = "frontend2/public/analytics_dump.json.gz"


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


if __name__ == "__main__":
    with FlexibleAnalytics(DB_PATH) as analytics:
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
        import os
        uncompressed_size = os.path.getsize(FRONTEND_PUBLIC)
        compressed_size = os.path.getsize(COMPRESSED_FILE)
        compression_ratio = (1 - compressed_size / uncompressed_size) * 100
        
        print(f"📊 File sizes:")
        print(f"   Uncompressed: {uncompressed_size / 1024:.1f} KB")
        print(f"   Compressed: {compressed_size / 1024:.1f} KB")
        print(f"   Compression: {compression_ratio:.1f}%") 