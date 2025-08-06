#!/usr/bin/env python3
"""
Winrate Query Script
===================

Calculates overall winrate by comparing bet_ids between betting and claiming databases.
Generates data for a pie chart showing Won vs Lost/Undecided bets.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONAD_HYPERSYNC_URL = os.getenv("MONAD_HYPERSYNC_URL", "https://monad-testnet.hypersync.xyz")
HYPERSYNC_BEARER_TOKEN = os.getenv("HYPERSYNC_BEARER_TOKEN")

# Database path configuration
if os.getenv("IS_PRODUCTION"):
    BETTING_DB_PATH = "/app/data/betting_transactions.db"
    CLAIMING_DB_PATH = "/app/data/comprehensive_claiming_transactions_fixed.db"
else:
    BETTING_DB_PATH = "betting_transactions.db"
    CLAIMING_DB_PATH = "data/comprehensive_claiming_transactions_fixed.db"

def get_winrate_stats() -> Dict[str, Any]:
    """Calculate overall winrate statistics."""
    
    # Connect to betting database
    betting_conn = sqlite3.connect(BETTING_DB_PATH)
    betting_cursor = betting_conn.cursor()
    
    # Connect to claiming database
    claiming_conn = sqlite3.connect(CLAIMING_DB_PATH)
    claiming_cursor = claiming_conn.cursor()
    
    try:
        # Get total bets with bet_id (all time)
        betting_cursor.execute("""
            SELECT COUNT(DISTINCT bet_id) as total_bets
            FROM betting_transactions 
            WHERE bet_id > 0
        """)
        total_bets = betting_cursor.fetchone()[0]
        
        # Get won bets (bet_id exists in both tables)
        # First, get all bet_ids from claiming database (all time)
        claiming_cursor.execute("SELECT DISTINCT bet_id FROM claiming_transactions WHERE bet_id > 0")
        claimed_bet_ids = set(row[0] for row in claiming_cursor.fetchall())
        
        # Then count how many of these exist in betting database (all time)
        betting_cursor.execute("SELECT DISTINCT bet_id FROM betting_transactions WHERE bet_id > 0")
        betting_bet_ids = set(row[0] for row in betting_cursor.fetchall())
        
        # Find intersection (won bets)
        won_bet_ids = claimed_bet_ids.intersection(betting_bet_ids)
        won_bets = len(won_bet_ids)
        
        # Calculate lost/undecided bets
        lost_bets = total_bets - won_bets
        
        # Calculate winrate percentage
        winrate_percentage = (won_bets / total_bets * 100) if total_bets > 0 else 0
        
        # Get additional statistics (all time)
        betting_cursor.execute("""
            SELECT COUNT(*) as total_transactions,
                   COUNT(CASE WHEN token = 'MON' THEN 1 END) as mon_transactions,
                   COUNT(CASE WHEN token = 'JERRY' THEN 1 END) as jerry_transactions
            FROM betting_transactions
        """)
        total_transactions, mon_transactions, jerry_transactions = betting_cursor.fetchone()
        
        # Get claiming statistics (all time)
        claiming_cursor.execute("SELECT COUNT(*) as total_claims FROM claiming_transactions")
        total_claims = claiming_cursor.fetchone()[0]
        
        return {
            'total_bets': total_bets,
            'won_bets': won_bets,
            'lost_bets': lost_bets,
            'winrate_percentage': round(winrate_percentage, 2),
            'total_transactions': total_transactions,
            'mon_transactions': mon_transactions,
            'jerry_transactions': jerry_transactions,
            'total_claims': total_claims,
            'calculated_at': datetime.now().isoformat()
        }
        
    finally:
        betting_conn.close()
        claiming_conn.close()

def generate_pie_chart_data(stats: Dict[str, Any]) -> Dict[str, Any]:
    """Generate data structure for pie chart."""
    
    return {
        'labels': ['Won', 'Lost/Undecided'],
        'datasets': [{
            'data': [stats['won_bets'], stats['lost_bets']],
            'backgroundColor': ['#4CAF50', '#FF5722'],  # Green for won, Red for lost
            'borderColor': ['#45a049', '#e53935'],
            'borderWidth': 2
        }],
        'winrate_percentage': stats['winrate_percentage'],
        'total_bets': stats['total_bets']
    }

def save_winrate_data(data: Dict[str, Any], output_file: str = "new/public/winrate_analytics_dump.json"):
def save_winrate_data(data: Dict[str, Any], output_file: str = "data/winrate_analytics_dump.json"):
    """Save winrate data to JSON file."""
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Winrate data saved to {output_file}")

def main():
    """Main execution function."""
    print("=== WINRATE CALCULATION ===")
    print("=" * 40)
    
    # Calculate winrate statistics
    print("📊 Calculating winrate statistics...")
    stats = get_winrate_stats()
    
    # Display statistics
    print(f"\n📈 WINRATE STATISTICS:")
    print(f"  Total bets with bet_id: {stats['total_bets']:,}")
    print(f"  Won bets: {stats['won_bets']:,}")
    print(f"  Lost/Undecided bets: {stats['lost_bets']:,}")
    print(f"  Overall winrate: {stats['winrate_percentage']}%")
    print()
    print(f"📊 ADDITIONAL STATISTICS:")
    print(f"  Total transactions: {stats['total_transactions']:,}")
    print(f"  MON transactions: {stats['mon_transactions']:,}")
    print(f"  JERRY transactions: {stats['jerry_transactions']:,}")
    print(f"  Total claims: {stats['total_claims']:,}")
    print()
    
    # Generate pie chart data
    print("🎨 Generating pie chart data...")
    pie_chart_data = generate_pie_chart_data(stats)
    
    # Save data
    save_winrate_data(pie_chart_data)
    
    # Display pie chart data structure
    print(f"\n📋 PIE CHART DATA:")
    print(f"  Labels: {pie_chart_data['labels']}")
    print(f"  Data: {pie_chart_data['datasets'][0]['data']}")
    print(f"  Winrate: {pie_chart_data['winrate_percentage']}%")
    print(f"  Total bets: {pie_chart_data['total_bets']:,}")
    
    print(f"\n✅ Winrate calculation complete!")

if __name__ == "__main__":
    main() 