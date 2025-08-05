#!/usr/bin/env python3
"""
Top Claimers Query Script
=========================

Generates a list of top claimers based on claiming transactions.
Similar to top bettors but focused on claiming activity.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any

def get_top_claimers(limit: int = 20) -> List[Dict[str, Any]]:
    """Get top claimers based on claiming transactions."""
    
    conn_claiming = sqlite3.connect("data/comprehensive_claiming_transactions_fixed.db")
    conn_betting = sqlite3.connect("betting_transactions.db")
    cursor_claiming = conn_claiming.cursor()
    cursor_betting = conn_betting.cursor()
    
    try:
        # Debug: Check if database has any data
        cursor_claiming.execute("SELECT COUNT(*) FROM claiming_transactions")
        total_transactions = cursor_claiming.fetchone()[0]
        print(f"Total claiming transactions in database: {total_transactions}")
        
        cursor_betting.execute("SELECT COUNT(*) FROM betting_transactions")
        total_betting = cursor_betting.fetchone()[0]
        print(f"Total betting transactions in database: {total_betting}")
        
        if total_transactions == 0:
            print("❌ No claiming transactions found in database")
            return []
        
        # Debug: Check date range
        cursor_claiming.execute("SELECT MIN(timestamp), MAX(timestamp) FROM claiming_transactions")
        date_range = cursor_claiming.fetchone()
        print(f"Claiming date range in database: {date_range[0]} to {date_range[1]}")
        
        cursor_betting.execute("SELECT MIN(timestamp), MAX(timestamp) FROM betting_transactions")
        betting_date_range = cursor_betting.fetchone()
        print(f"Betting date range in database: {betting_date_range[0]} to {betting_date_range[1]}")
        
        # Debug: Check block timestamp range
        cursor_claiming.execute("SELECT MIN(block_number), MAX(block_number) FROM claiming_transactions")
        block_range = cursor_claiming.fetchone()
        print(f"Claiming block range in database: {block_range[0]} to {block_range[1]}")
        
        # Debug: Check sample data
        cursor_claiming.execute("SELECT * FROM claiming_transactions LIMIT 3")
        sample_data = cursor_claiming.fetchone()
        print(f"Sample claiming data: {sample_data}")
        
        # Query to get top claimers with betting volume and profit calculation
        query = """
        WITH claimer_stats AS (
            SELECT 
                from_address as usr,
                SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as mon_claimed,
                SUM(CASE WHEN token = 'JERRY' THEN amount ELSE 0 END) as jerry_claimed,
                COUNT(CASE WHEN token = 'MON' THEN 1 END) as mon_claims,
                COUNT(CASE WHEN token = 'JERRY' THEN 1 END) as jerry_claims,
                COUNT(*) as total_claims,
                AVG(amount) as avg_claim_amount
            FROM claiming_transactions
            GROUP BY from_address
        )
        
        SELECT 
            usr,
            mon_claimed,
            jerry_claimed,
            (mon_claimed + jerry_claimed) as total_claimed,
            mon_claims,
            jerry_claims,
            total_claims,
            avg_claim_amount
        FROM claimer_stats
        WHERE (mon_claimed + jerry_claimed) > 0
        ORDER BY (mon_claimed + jerry_claimed) DESC
        LIMIT ?
        """
        
        cursor_claiming.execute(query, (limit,))
        results = cursor_claiming.fetchall()
        
        print(f"Found {len(results)} claimers with data")
        
        # Convert to list of dictionaries and add betting data
        top_claimers = []
        for row in results:
            usr, mon_claimed, jerry_claimed, total_claimed, mon_claims, jerry_claims, total_claims, avg_claim_amount = row
            
            # Get betting data for this user
            cursor_betting.execute("""
                SELECT 
                    SUM(CASE WHEN token = 'MON' THEN amount ELSE 0 END) as mon_bet,
                    SUM(CASE WHEN token = 'JERRY' THEN amount ELSE 0 END) as jerry_bet,
                    SUM(amount) as total_bet,
                    COUNT(*) as total_submissions,
                    AVG(n_cards) as avg_slip_size
                FROM betting_transactions
                WHERE from_address = ?
            """, (usr,))
            
            betting_result = cursor_betting.fetchone()
            mon_bet = betting_result[0] if betting_result and betting_result[0] else 0
            jerry_bet = betting_result[1] if betting_result and betting_result[1] else 0
            total_bet = betting_result[2] if betting_result and betting_result[2] else 0
            total_submissions = betting_result[3] if betting_result and betting_result[3] else 0
            avg_slip_size = betting_result[4] if betting_result and betting_result[4] else 0
            
            # Calculate percentages
            mon_percentage = (mon_claimed / total_claimed * 100) if total_claimed > 0 else 0
            jerry_percentage = (jerry_claimed / total_claimed * 100) if total_claimed > 0 else 0
            
            # Calculate profit percentage
            profit_percentage = ((total_claimed - total_bet) / total_bet * 100) if total_bet > 0 else 0
            
            claimer_data = {
                'address': usr,
                'mon_claimed': mon_claimed,
                'jerry_claimed': jerry_claimed,
                'total_claimed': total_claimed,
                'mon_claims': mon_claims,
                'jerry_claims': jerry_claims,
                'total_claims': total_claims,
                'avg_claim_amount': avg_claim_amount,
                'mon_percentage': round(mon_percentage, 1),
                'jerry_percentage': round(jerry_percentage, 1),
                'mon_bet': mon_bet,
                'jerry_bet': jerry_bet,
                'total_bet': total_bet,
                'profit_percentage': round(profit_percentage, 1),
                'total_submissions': total_submissions,
                'avg_slip_size': round(avg_slip_size, 1)
            }
            
            top_claimers.append(claimer_data)
        
        return top_claimers
        
    finally:
        conn_claiming.close()
        conn_betting.close()

def format_claimer_data(claimers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format claimer data for display."""
    
    formatted_claimers = []
    
    for i, claimer in enumerate(claimers, 1):
        # Truncate address for display
        address = claimer['address']
        display_address = f"{address[:6]}...{address[-4:]}" if len(address) > 10 else address
        
        formatted_claimer = {
            'rank': i,
            'address': claimer['address'],
            'display_address': display_address,
            'total_claimed': claimer['total_claimed'],
            'mon_claimed': claimer['mon_claimed'],
            'jerry_claimed': claimer['jerry_claimed'],
            'total_claims': claimer['total_claims'],
            'avg_claim_amount': claimer['avg_claim_amount'],
            'mon_percentage': claimer['mon_percentage'],
            'jerry_percentage': claimer['jerry_percentage'],
            'mon_bet': claimer['mon_bet'],
            'jerry_bet': claimer['jerry_bet'],
            'total_bet': claimer['total_bet'],
            'profit_percentage': claimer['profit_percentage'],
            'total_submissions': claimer['total_submissions'],
            'avg_slip_size': claimer['avg_slip_size']
        }
        
        formatted_claimers.append(formatted_claimer)
    
    return formatted_claimers

def save_top_claimers_data(data: List[Dict[str, Any]], output_file: str = "new/public/top_claimers_dump.json"):
    """Save top claimers data to JSON file."""
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Top claimers data saved to {output_file}")

def main():
    """Main execution function."""
    print("=== TOP CLAIMERS QUERY ===")
    print("=" * 40)
    
    # Get top claimers
    print("📊 Fetching top claimers...")
    top_claimers = get_top_claimers(20)
    
    if not top_claimers:
        print("❌ No claimers found")
        return
    
    # Format data
    print("🎨 Formatting claimer data...")
    formatted_claimers = format_claimer_data(top_claimers)
    
    # Display results
    print(f"\n📈 TOP {len(formatted_claimers)} CLAIMERS:")
    print("=" * 60)
    
    for claimer in formatted_claimers[:10]:  # Show top 10
        print(f"#{claimer['rank']:2d} {claimer['display_address']}")
        print(f"   Total Claimed: ${claimer['total_claimed']:,.2f}")
        print(f"   MON: ${claimer['mon_claimed']:,.2f} ({claimer['mon_percentage']}%)")
        print(f"   JERRY: ${claimer['jerry_claimed']:,.2f} ({claimer['jerry_percentage']}%)")
        print(f"   Total Claims: {claimer['total_claims']}")
        print(f"   Avg Claim: ${claimer['avg_claim_amount']:,.2f}")
        print(f"   Total Bet: ${claimer['total_bet']:,.2f}")
        print(f"   Profit: {claimer['profit_percentage']:+.1f}%")
        print(f"   Total Submissions: {claimer['total_submissions']}")
        print(f"   Avg Slip Size: {claimer['avg_slip_size']:.1f} cards")
        print()
    
    # Save data
    save_top_claimers_data(formatted_claimers)
    
    # Summary statistics
    total_claimed = sum(c['total_claimed'] for c in formatted_claimers)
    total_claims = sum(c['total_claims'] for c in formatted_claimers)
    avg_claim = total_claimed / total_claims if total_claims > 0 else 0
    
    print(f"📊 SUMMARY STATISTICS:")
    print(f"  Total claimed by top {len(formatted_claimers)}: ${total_claimed:,.2f}")
    print(f"  Total claims: {total_claims:,}")
    print(f"  Average claim amount: ${avg_claim:,.2f}")
    
    print(f"\n✅ Top claimers query complete!")

if __name__ == "__main__":
    main() 