#!/usr/bin/env python3
"""
Test script to demonstrate incremental analytics functionality.
"""

import json
import os
from datetime import datetime, timedelta
from json_query import FlexibleAnalytics, merge_analytics_data, load_existing_analytics

def create_test_data():
    """Create sample analytics data for testing."""
    return {
        "success": True,
        "metadata": {
            "generated_at": "2025-07-22T01:00:00.000000Z",
            "timeframes_available": ["daily", "weekly", "monthly"],
            "default_timeframe": "weekly",
            "last_incremental_update": "2025-07-22T01:30:00.000000"
        },
        "total_metrics": {
            "total_submissions": 100,
            "total_active_addresses": 50,
            "total_mon_volume": 1000.0,
            "total_jerry_volume": 500.0,
            "total_cards": 300
        },
        "average_metrics": {
            "avg_submissions_per_day": 10.0,
            "avg_cards_per_slip": 3.0,
            "avg_players_per_day": 8.0
        },
        "timeframes": {
            "daily": {
                "activity_over_time": [
                    {
                        "period": 1,
                        "start_date": "2025-07-21",
                        "end_date": "2025-07-21",
                        "submissions": 10,
                        "active_addresses": 8,
                        "total_cards": 30,
                        "mon_volume": 100.0,
                        "jerry_volume": 50.0,
                        "total_volume": 150.0,
                        "avg_cards_per_submission": 3.0,
                        "avg_bet_amount": 15.0,
                        "mon_transactions": 8,
                        "jerry_transactions": 2
                    }
                ]
            }
        }
    }

def create_test_transactions():
    """Create sample new transactions."""
    return [
        {
            "tx_hash": "0x1234567890abcdef",
            "from_address": "0xabcdef1234567890",
            "token": "MON",
            "amount": 25.0,
            "n_cards": 2,
            "timestamp": "2025-07-22T02:00:00.000000"
        },
        {
            "tx_hash": "0x0987654321fedcba",
            "from_address": "0xfedcba0987654321",
            "token": "Jerry",
            "amount": 15.0,
            "n_cards": 1,
            "timestamp": "2025-07-22T03:00:00.000000"
        }
    ]

def test_incremental_update():
    """Test the incremental update functionality."""
    print("🧪 Testing Incremental Analytics System")
    print("=" * 50)
    
    # Create test data
    existing_data = create_test_data()
    new_transactions = create_test_transactions()
    since_timestamp = "2025-07-22T01:30:00.000000"
    
    print(f"📊 Original total submissions: {existing_data['total_metrics']['total_submissions']}")
    print(f"📊 Original total cards: {existing_data['total_metrics']['total_cards']}")
    print(f"📊 Original MON volume: {existing_data['total_metrics']['total_mon_volume']}")
    print(f"📊 Original Jerry volume: {existing_data['total_metrics']['total_jerry_volume']}")
    
    print(f"\n🔄 New transactions to process: {len(new_transactions)}")
    for tx in new_transactions:
        print(f"  - {tx['token']}: {tx['amount']} ({tx['n_cards']} cards)")
    
    # Perform incremental update
    print(f"\n🔄 Performing incremental update...")
    updated_data = merge_analytics_data(existing_data, new_transactions, since_timestamp)
    
    if updated_data:
        print(f"\n✅ Incremental update successful!")
        print(f"📊 Updated total submissions: {updated_data['total_metrics']['total_submissions']}")
        print(f"📊 Updated total cards: {updated_data['total_metrics']['total_cards']}")
        print(f"📊 Updated MON volume: {updated_data['total_metrics']['total_mon_volume']}")
        print(f"📊 Updated Jerry volume: {updated_data['total_metrics']['total_jerry_volume']}")
        
        # Check if periods were updated
        daily_data = updated_data['timeframes']['daily']['activity_over_time']
        for period in daily_data:
            if period['start_date'] == "2025-07-21":
                print(f"📅 Period {period['start_date']} updated:")
                print(f"  - Submissions: {period['submissions']}")
                print(f"  - Total cards: {period['total_cards']}")
                print(f"  - Total volume: {period['total_volume']}")
                break
    else:
        print("❌ Incremental update failed!")

if __name__ == "__main__":
    test_incremental_update() 