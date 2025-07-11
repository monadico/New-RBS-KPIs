#!/usr/bin/env python3
"""
Multi-timeframe analytics for betting data.
Handles hourly, daily, weekly, and monthly aggregations without double-counting users.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from database import get_db_instance


class MultiTimeframeAnalytics:
    """
    Analytics engine that properly handles multiple timeframes without double-counting.
    """
    
    def __init__(self, db_path: str = "betting_analytics.db"):
        self.db = get_db_instance(db_path)
    
    def get_user_metrics_for_timeframe(self, timeframe: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Calculate user metrics (active_users, new_users) for any timeframe.
        Always uses raw transaction data to avoid double-counting.
        
        New users are only calculated for D, W, M timeframes (not hourly).
        
        Args:
            timeframe: 'H', 'D', 'W', 'M' for hourly, daily, weekly, monthly
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        # Get raw transaction data
        if start_date and end_date:
            df = self.db.get_transactions_in_date_range(start_date, end_date)
        else:
            df = self.db.get_all_transactions()
        
        if df.empty:
            return pd.DataFrame()
        
        # Create time periods based on timeframe
        if timeframe == 'H':
            df['period'] = df['block_timestamp'].dt.floor('h')
        elif timeframe == 'D':
            df['period'] = df['block_timestamp'].dt.date
        elif timeframe == 'W':
            df['period'] = df['block_timestamp'].dt.to_period('W').dt.to_timestamp()
        elif timeframe == 'M':
            df['period'] = df['block_timestamp'].dt.to_period('M').dt.to_timestamp()
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        # Calculate active users per period (distinct users) - for all timeframes
        active_users = df.groupby('period')['origin_from_address'].nunique().reset_index()
        active_users.columns = ['period', 'active_users']
        
        # Calculate new users only for D, W, M timeframes (not hourly)
        if timeframe in ['D', 'W', 'M']:
            # Calculate new users per period (users with first transaction in that period)
            first_interaction = df.groupby('origin_from_address')['block_timestamp'].min().reset_index()
            first_interaction.columns = ['origin_from_address', 'first_tx_time']
            
            # Apply same period logic to first transactions
            if timeframe == 'D':
                first_interaction['period'] = first_interaction['first_tx_time'].dt.date
            elif timeframe == 'W':
                first_interaction['period'] = first_interaction['first_tx_time'].dt.to_period('W').dt.to_timestamp()
            elif timeframe == 'M':
                first_interaction['period'] = first_interaction['first_tx_time'].dt.to_period('M').dt.to_timestamp()
            
            new_users = first_interaction.groupby('period')['origin_from_address'].nunique().reset_index()
            new_users.columns = ['period', 'new_users']
            
            # Merge active and new users
            user_metrics = pd.merge(active_users, new_users, on='period', how='outer').fillna(0)
            
            # Calculate cumulative new users
            user_metrics = user_metrics.sort_values('period')
            user_metrics['cumulative_new_users'] = user_metrics['new_users'].cumsum()
            
            # Convert to int for cleaner display
            user_metrics['new_users'] = user_metrics['new_users'].astype(int)
            user_metrics['cumulative_new_users'] = user_metrics['cumulative_new_users'].astype(int)
            
        else:
            # For hourly timeframe, only include active users (no new users)
            user_metrics = active_users
        
        # Convert active_users to int for cleaner display
        user_metrics['active_users'] = user_metrics['active_users'].astype(int)
        
        return user_metrics.set_index('period')
    
    def get_additive_metrics_for_timeframe(self, timeframe: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Calculate additive metrics (transactions, volume, cards) for any timeframe.
        Can be safely aggregated from hourly data when available.
        
        Args:
            timeframe: 'H', 'D', 'W', 'M' for hourly, daily, weekly, monthly
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        # For hourly, try to use pre-computed metrics first
        if timeframe == 'H':
            try:
                hourly_metrics = self.db.get_hourly_metrics()
                if not hourly_metrics.empty:
                    if start_date or end_date:
                        # Filter by date range
                        mask = pd.Series(True, index=hourly_metrics.index)
                        if start_date:
                            mask &= hourly_metrics.index >= start_date
                        if end_date:
                            mask &= hourly_metrics.index <= end_date
                        hourly_metrics = hourly_metrics[mask]
                    
                    # Return only additive metrics
                    return hourly_metrics[['submission_txs', 'total_cards', 'avg_cards', 'mon_volume', 'jerry_volume']]
            except:
                pass  # Fall back to raw data calculation
        
        # Fall back to raw transaction data
        if start_date and end_date:
            df = self.db.get_transactions_in_date_range(start_date, end_date)
        else:
            df = self.db.get_all_transactions()
        
        if df.empty:
            return pd.DataFrame()
        
        # Create time periods
        if timeframe == 'H':
            df['period'] = df['block_timestamp'].dt.floor('h')
        elif timeframe == 'D':
            df['period'] = df['block_timestamp'].dt.date
        elif timeframe == 'W':
            df['period'] = df['block_timestamp'].dt.to_period('W').dt.to_timestamp()
        elif timeframe == 'M':
            df['period'] = df['block_timestamp'].dt.to_period('M').dt.to_timestamp()
        
        # Calculate volume metrics
        df['mon_volume'] = df['bet_amt'].where(df['betting_token'] == 'MON', 0)
        df['jerry_volume'] = df['bet_amt'].where(df['betting_token'] == 'Jerry', 0)
        
        # Aggregate additive metrics
        additive_metrics = df.groupby('period').agg(
            submission_txs=('tx_hash', 'nunique'),
            total_cards=('cards_in_slip', 'sum'),
            avg_cards=('cards_in_slip', 'mean'),
            mon_volume=('mon_volume', 'sum'),
            jerry_volume=('jerry_volume', 'sum')
        ).fillna(0)
        
        return additive_metrics
    
    def get_combined_metrics_for_timeframe(self, timeframe: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Get complete metrics for a timeframe, properly handling user vs additive metrics.
        
        Args:
            timeframe: 'H', 'D', 'W', 'M' for hourly, daily, weekly, monthly
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        # Get user metrics (always from raw data)
        user_metrics = self.get_user_metrics_for_timeframe(timeframe, start_date, end_date)
        
        # Get additive metrics (from pre-computed or raw data)
        additive_metrics = self.get_additive_metrics_for_timeframe(timeframe, start_date, end_date)
        
        if user_metrics.empty and additive_metrics.empty:
            return pd.DataFrame()
        
        # Merge the two types of metrics
        combined_metrics = pd.merge(user_metrics, additive_metrics, left_index=True, right_index=True, how='outer').fillna(0)
        
        # Add cumulative metrics for additive measures
        combined_metrics = combined_metrics.sort_index()
        
        # Only add cumulative columns if the base columns exist
        if 'submission_txs' in combined_metrics.columns:
            combined_metrics['cumulative_txs'] = combined_metrics['submission_txs'].cumsum()
        if 'total_cards' in combined_metrics.columns:
            combined_metrics['cumulative_cards'] = combined_metrics['total_cards'].cumsum()
        if 'mon_volume' in combined_metrics.columns:
            combined_metrics['cumulative_mon_volume'] = combined_metrics['mon_volume'].cumsum()
        if 'jerry_volume' in combined_metrics.columns:
            combined_metrics['cumulative_jerry_volume'] = combined_metrics['jerry_volume'].cumsum()
        
        return combined_metrics
    
    def get_hourly_metrics(self, hours: int = 24) -> pd.DataFrame:
        """Get hourly metrics for the last N hours."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        return self.get_combined_metrics_for_timeframe('H', start_time, end_time)
    
    def get_daily_metrics(self, days: int = 7) -> pd.DataFrame:
        """Get daily metrics for the last N days."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        return self.get_combined_metrics_for_timeframe('D', start_time, end_time)
    
    def get_weekly_metrics(self, weeks: int = 4) -> pd.DataFrame:
        """Get weekly metrics for the last N weeks."""
        end_time = datetime.now()
        start_time = end_time - timedelta(weeks=weeks)
        return self.get_combined_metrics_for_timeframe('W', start_time, end_time)
    
    def get_monthly_metrics(self, months: int = 3) -> pd.DataFrame:
        """Get monthly metrics for the last N months."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=months * 30)  # Approximate
        return self.get_combined_metrics_for_timeframe('M', start_time, end_time)
    
    def format_metrics_for_display(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Format metrics DataFrame for display with proper column names."""
        if df.empty:
            return df
        
        # Rename columns for display
        display_df = df.rename(columns={
            "submission_txs": "Transactions",
            "cumulative_txs": "Cumulative Txs",
            "active_users": "Active Users",
            "new_users": "New Users",
            "cumulative_new_users": "Cumulative New Users",
            "avg_cards": "Avg Cards",
            "total_cards": "Total Cards",
            "cumulative_cards": "Cumulative Cards",
            "mon_volume": "MON Volume",
            "jerry_volume": "JERRY Volume",
            "cumulative_mon_volume": "Cumulative MON Volume",
            "cumulative_jerry_volume": "Cumulative JERRY Volume"
        })
        
        # Select columns for display based on timeframe
        if timeframe == 'H':
            # For hourly: no new user metrics
            display_columns = [
                'Active Users',
                'Transactions', 'Cumulative Txs', 
                'Avg Cards', 'Total Cards', 'Cumulative Cards',
                'MON Volume', 'Cumulative MON Volume', 
                'JERRY Volume', 'Cumulative JERRY Volume'
            ]
        else:
            # For daily, weekly, monthly: include new user metrics
            display_columns = [
                'Active Users', 'New Users', 'Cumulative New Users',
                'Transactions', 'Cumulative Txs', 
                'Avg Cards', 'Total Cards', 'Cumulative Cards',
                'MON Volume', 'Cumulative MON Volume', 
                'JERRY Volume', 'Cumulative JERRY Volume'
            ]
        
        # Only include columns that exist
        existing_columns = [col for col in display_columns if col in display_df.columns]
        
        return display_df[existing_columns]
    
    def print_timeframe_summary(self, timeframe: str, periods: int = None):
        """Print a summary for a specific timeframe."""
        timeframe_names = {
            'H': 'Hourly',
            'D': 'Daily', 
            'W': 'Weekly',
            'M': 'Monthly'
        }
        
        # Set default periods if not provided
        if periods is None:
            default_periods = {'H': 24, 'D': 7, 'W': 4, 'M': 3}
            periods = default_periods.get(timeframe, 10)
        
        print(f"\n=== {timeframe_names[timeframe].upper()} ANALYTICS (LAST {periods} PERIODS) ===")
        
        # Get metrics using the appropriate method
        if timeframe == 'H':
            metrics_df = self.get_hourly_metrics(periods)
        elif timeframe == 'D':
            metrics_df = self.get_daily_metrics(periods)
        elif timeframe == 'W':
            metrics_df = self.get_weekly_metrics(periods)
        elif timeframe == 'M':
            metrics_df = self.get_monthly_metrics(periods)
        
        if metrics_df.empty:
            print(f"No data available for {timeframe_names[timeframe].lower()} analysis.")
            return
        
        # Format for display
        display_df = self.format_metrics_for_display(metrics_df, timeframe)
        
        # Show the data
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(display_df.to_string())
        
        # Show summary statistics
        print(f"\n{timeframe_names[timeframe]} Summary:")
        print(f"Total Periods: {len(metrics_df)}")
        if 'Active Users' in display_df.columns:
            print(f"Peak Active Users: {display_df['Active Users'].max()}")
            # Only show new user metrics for non-hourly timeframes
            if timeframe != 'H' and 'New Users' in display_df.columns:
                print(f"Total New Users: {display_df['New Users'].sum()}")
        if 'Transactions' in display_df.columns:
            print(f"Total Transactions: {display_df['Transactions'].sum()}")
            print(f"Total MON Volume: {display_df['MON Volume'].sum():.2f}")
            print(f"Total JERRY Volume: {display_df['JERRY Volume'].sum():.2f}")


def main():
    """Main function to demonstrate multi-timeframe analytics."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-timeframe betting analytics')
    parser.add_argument('--db', default='betting_analytics.db', help='Database file path')
    parser.add_argument('--timeframe', choices=['H', 'D', 'W', 'M'], default='H', help='Timeframe (H=hourly, D=daily, W=weekly, M=monthly)')
    parser.add_argument('--periods', type=int, help='Number of periods to analyze')
    parser.add_argument('--all', action='store_true', help='Show all timeframes')
    
    args = parser.parse_args()
    
    analytics = MultiTimeframeAnalytics(args.db)
    
    if args.all:
        # Show all timeframes
        analytics.print_timeframe_summary('H', 24)
        analytics.print_timeframe_summary('D', 7)
        analytics.print_timeframe_summary('W', 4)
        analytics.print_timeframe_summary('M', 3)
    else:
        # Show specific timeframe
        analytics.print_timeframe_summary(args.timeframe, args.periods)


if __name__ == "__main__":
    main() 