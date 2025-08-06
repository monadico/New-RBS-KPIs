#!/usr/bin/env python3
"""
Prize Selector - RareLink Prize Winner Selection

This script implements the raffle logic for selecting prize winners based on RareLink submissions.
Each player prop in a RareLink = 1 entry. Winners are randomly selected based on weighted entries.

Usage:
    python prize_selector.py --start-date 2025-07-01 --end-date 2024-07-07
    python prize_selector.py --start-date 2025-07-01 --end-date 2025-07-07 --verbose
"""

import sqlite3
import argparse
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json
import sys
from pathlib import Path

class PrizeSelector:
    def __init__(self, db_path: str = "betting_transactions.db"):
        """Initialize the prize selector with database path."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect_db(self) -> bool:
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✅ Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
    
    def disconnect_db(self):
        """Disconnect from the database."""
        if self.conn:
            self.conn.close()
            print("🔌 Disconnected from database")
    
    def get_submissions_in_period(self, start_date: str, end_date: str) -> List[Tuple]:
        """
        Get all RareLink submissions within the specified time period.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of tuples containing (bet_id, wallet_address, timestamp, n_cards)
        """
        try:
            # Convert dates to datetime for proper comparison
            start_dt = datetime.fromisoformat(f"{start_date}T00:00:00")
            end_dt = datetime.fromisoformat(f"{end_date}T23:59:59")
            
            query = """
                SELECT 
                    bet_id,
                    from_address,
                    timestamp,
                    n_cards
                FROM betting_transactions 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """
            
            self.cursor.execute(query, [start_dt.isoformat(), end_dt.isoformat()])
            submissions = self.cursor.fetchall()
            
            print(f"📊 Found {len(submissions)} submissions between {start_date} and {end_date}")
            return submissions
            
        except Exception as e:
            print(f"❌ Error querying submissions: {e}")
            return []
    
    def create_entry_pool(self, submissions: List[Tuple]) -> Tuple[List[str], Dict[str, int]]:
        """
        Create the entry pool based on submissions.
        Each player prop (n_cards) = 1 entry.
        
        Args:
            submissions: List of submission tuples
            
        Returns:
            Tuple of (entry_pool, user_entries_dict)
        """
        entry_pool = []
        user_entries = {}
        
        for submission in submissions:
            bet_id, wallet_address, timestamp, n_cards = submission
            entry_count = n_cards or 0
            
            # Add user to entry pool based on number of player props
            for i in range(entry_count):
                entry_pool.append(wallet_address)
            
            # Track user entries for winner info
            if wallet_address not in user_entries:
                user_entries[wallet_address] = 0
            user_entries[wallet_address] += entry_count
        
        print(f"🎰 Created entry pool with {len(entry_pool)} total entries")
        print(f"👥 {len(user_entries)} unique participants")
        
        return entry_pool, user_entries
    
    def get_wallet_transactions(self, wallet_address: str, limit: int = 10) -> List[Tuple]:
        """
        Get recent transactions for a specific wallet address.
        
        Args:
            wallet_address: The wallet address to query
            limit: Number of transactions to return
            
        Returns:
            List of transaction tuples
        """
        try:
            query = """
                SELECT 
                    tx_hash,
                    timestamp,
                    token,
                    amount,
                    n_cards,
                    bet_id,
                    block_number
                FROM betting_transactions 
                WHERE from_address = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            
            self.cursor.execute(query, [wallet_address, limit])
            transactions = self.cursor.fetchall()
            
            return transactions
            
        except Exception as e:
            print(f"❌ Error querying wallet transactions: {e}")
            return []
    
    def select_winner(self, entry_pool: List[str], user_entries: Dict[str, int], 
                     submissions: List[Tuple]) -> Optional[Dict]:
        """
        Select a random winner from the entry pool.
        
        Args:
            entry_pool: List of wallet addresses (weighted by entries)
            user_entries: Dictionary mapping wallet addresses to their total entries
            submissions: Original submissions for additional context
            
        Returns:
            Dictionary with winner information or None if no valid entries
        """
        if not entry_pool:
            print("❌ No valid entries found")
            return None
        
        # Select random winner from entry pool
        winner_address = random.choice(entry_pool)
        winner_entries = user_entries[winner_address]
        
        # Find the bet_id for the winner
        winner_bet_id = None
        for submission in submissions:
            if submission[1] == winner_address:  # wallet_address
                winner_bet_id = submission[0]  # bet_id
                break
        
        # Get example transactions for the winner
        winner_transactions = self.get_wallet_transactions(winner_address, 10)
        
        winner_info = {
            "bet_id": winner_bet_id,
            "wallet_address": winner_address,
            "entries": winner_entries,
            "total_entries": len(entry_pool),
            "total_submissions": len(submissions),
            "unique_participants": len(user_entries),
            "example_transactions": winner_transactions
        }
        
        return winner_info
    
    def run_raffle(self, start_date: str, end_date: str, verbose: bool = False) -> Optional[Dict]:
        """
        Run the complete raffle process for the specified time period.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            verbose: Whether to print detailed information
            
        Returns:
            Dictionary with raffle results or None if failed
        """
        print(f"\n🎰 Starting raffle for period: {start_date} to {end_date}")
        print("=" * 50)
        
        # Connect to database
        if not self.connect_db():
            return None
        
        try:
            # Get submissions in the period
            submissions = self.get_submissions_in_period(start_date, end_date)
            
            if not submissions:
                print("❌ No submissions found in the specified period")
                return None
            
            # Create entry pool
            entry_pool, user_entries = self.create_entry_pool(submissions)
            
            if not entry_pool:
                print("❌ No valid entries found")
                return None
            
            # Select winner
            winner_info = self.select_winner(entry_pool, user_entries, submissions)
            
            if not winner_info:
                return None
            
            # Print results
            print("\n🏆 WINNER SELECTED!")
            print("=" * 30)
            print(f"Wallet Address: {winner_info['wallet_address']}")
            print(f"Bet ID: {winner_info['bet_id']}")
            print(f"Winner Entries: {winner_info['entries']}")
            print(f"Total Entries: {winner_info['total_entries']}")
            print(f"Total Submissions: {winner_info['total_submissions']}")
            print(f"Unique Participants: {winner_info['unique_participants']}")
            
            # Show example transactions for the winner
            if winner_info['example_transactions']:
                print(f"\n📋 Example Transactions for Winner:")
                print("-" * 100)
                print(f"{'Tx Hash':<66} {'Date':<19} {'Token':<8} {'Amount':<12} {'Cards':<6} {'Bet ID':<8}")
                print("-" * 120)
                for tx in winner_info['example_transactions']:
                    tx_hash, timestamp, token, amount, n_cards, bet_id, block_number = tx
                    # Format timestamp
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = timestamp[:19]
                    # Show full tx_hash
                    print(f"{tx_hash:<66} {date_str:<19} {token:<8} {amount:<12.2f} {n_cards:<6} {bet_id:<8}")
            
            if verbose:
                print("\n📊 Detailed Statistics:")
                print("-" * 20)
                # Show top participants by entries
                sorted_users = sorted(user_entries.items(), key=lambda x: x[1], reverse=True)
                print("Top 10 participants by entries:")
                for i, (wallet, entries) in enumerate(sorted_users[:10], 1):
                    print(f"{i:2d}. {wallet[:8]}...{wallet[-6:]} - {entries} entries")
            
            return winner_info
            
        finally:
            self.disconnect_db()

def main():
    """Main function to run the prize selector."""
    parser = argparse.ArgumentParser(
        description="Select prize winners based on RareLink submissions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python prize_selector.py --start-date 2024-08-01 --end-date 2024-08-02
  python prize_selector.py --start-date 2024-08-01 --end-date 2024-08-02 --verbose
  python prize_selector.py --start-date 2024-08-01 --end-date 2024-08-02 --db-path custom.db
        """
    )
    
    parser.add_argument(
        "--start-date",
        required=True,
        help="Start date in YYYY-MM-DD format"
    )
    
    parser.add_argument(
        "--end-date", 
        required=True,
        help="End date in YYYY-MM-DD format"
    )
    
    parser.add_argument(
        "--db-path",
        default="betting_transactions.db",
        help="Path to the SQLite database (default: betting_transactions.db)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed statistics"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file for results (JSON format)"
    )
    
    args = parser.parse_args()
    
    # Validate dates
    try:
        datetime.fromisoformat(args.start_date)
        datetime.fromisoformat(args.end_date)
    except ValueError as e:
        print(f"❌ Invalid date format: {e}")
        print("Please use YYYY-MM-DD format (e.g., 2024-08-01)")
        sys.exit(1)
    
    # Check if database exists
    if not Path(args.db_path).exists():
        print(f"❌ Database not found: {args.db_path}")
        sys.exit(1)
    
    # Run raffle
    selector = PrizeSelector(args.db_path)
    result = selector.run_raffle(args.start_date, args.end_date, args.verbose)
    
    if result and args.output:
        # Save results to file
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Results saved to: {args.output}")
    
    if result:
        print(f"\n✅ Raffle completed successfully!")
        return 0
    else:
        print(f"\n❌ Raffle failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 