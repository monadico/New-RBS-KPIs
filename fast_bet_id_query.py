#!/usr/bin/env python3
"""
Optimized Stream Query for Bet ID Retrieval
==========================================

This demonstrates the fastest way to retrieve bet IDs using Hypersync's stream function.
Key optimizations:
1. Uses stream() for concurrent processing
2. Minimal field selection
3. Specific contract and topic filtering
4. Progress tracking with tqdm
5. Memory efficient processing
"""

import asyncio
import os
import time
import logging
import datetime
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any

from hypersync import HypersyncClient, ClientConfig, Query, LogSelection, FieldSelection, LogField, StreamConfig
from tqdm import tqdm

# Load environment variables
load_dotenv('.env.local')
load_dotenv()

MONAD_HYPERSYNC_URL = os.getenv("MONAD_HYPERSYNC_URL", "https://monad-testnet.hypersync.xyz")
HYPERSYNC_BEARER_TOKEN = os.getenv("HYPERSYNC_BEARER_TOKEN")

# Contract addresses and event signatures
CONTRACT_ADDRESSES = ['0x3ad50059d6008b711209a509fe58e68f0b672a42', '0x740990cb01e893a371a050736c62ae0b779109e7']
CARDS_LOG_TOPIC_0 = '0xefc52bf7792453af1461fa9a7097486359b41a048898b6d542c0f03389487187'

# Set up logging
logger = logging.getLogger(__name__)
fmt = "%(filename)-20s:%(lineno)-4d %(asctime)s %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt,
                    handlers=[logging.StreamHandler()])

# Configure logging
logging.basicConfig(level=logging.INFO, format=fmt,
                    handlers=[logging.StreamHandler()])

def hex_to_int(hex_str: str) -> int:
    """Convert hex string to integer."""
    if not hex_str or hex_str == '0x':
        return 0
    return int(hex_str, 16)

def get_database_block_range(db_path: str = "betting_transactions.db") -> tuple[int, int]:
    """Get the min and max block numbers from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT MIN(block_number) as min_block, MAX(block_number) as max_block 
            FROM betting_transactions
        """)
        result = cursor.fetchone()
        min_block, max_block = result
        return min_block, max_block
    finally:
        conn.close()

def update_bet_ids_batch(bet_id_map: Dict[str, int], db_path: str = "betting_transactions.db", batch_size: int = 1000):
    """Update bet IDs in the database using batch processing."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Convert dict to list of tuples for batch processing
        items = list(bet_id_map.items())
        total_items = len(items)
        updated_count = 0
        
        print(f"🔄 Updating {total_items:,} bet IDs in batches of {batch_size}...")
        
        for i in range(0, total_items, batch_size):
            batch = items[i:i + batch_size]
            
            with conn:  # This creates a transaction
                for tx_hash, bet_id in batch:
                    cursor.execute("""
                        UPDATE betting_transactions 
                        SET bet_id = ? 
                        WHERE tx_hash = ?
                    """, (bet_id, tx_hash))
                    updated_count += cursor.rowcount
            
            # Progress update
            if (i + batch_size) % (batch_size * 10) == 0 or i + batch_size >= total_items:
                print(f"  ✅ Updated {min(i + batch_size, total_items):,}/{total_items:,} bet IDs")
        
        print(f"✅ Database update complete! Updated {updated_count:,} bet IDs")
        return updated_count
        
    finally:
        conn.close()

def get_database_stats(db_path: str = "betting_transactions.db") -> Dict[str, int]:
    """Get database statistics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Total transactions
        cursor.execute("SELECT COUNT(*) FROM betting_transactions")
        total_transactions = cursor.fetchone()[0]
        
        # MON transactions
        cursor.execute("SELECT COUNT(*) FROM betting_transactions WHERE token = 'MON'")
        mon_transactions = cursor.fetchone()[0]
        
        # Transactions with bet_id
        cursor.execute("SELECT COUNT(*) FROM betting_transactions WHERE bet_id > 0")
        with_bet_id = cursor.fetchone()[0]
        
        # MON transactions with bet_id
        cursor.execute("SELECT COUNT(*) FROM betting_transactions WHERE token = 'MON' AND bet_id > 0")
        mon_with_bet_id = cursor.fetchone()[0]
        
        return {
            'total_transactions': total_transactions,
            'mon_transactions': mon_transactions,
            'with_bet_id': with_bet_id,
            'mon_with_bet_id': mon_with_bet_id
        }
    finally:
        conn.close()

async def stream_bet_ids_ultra_fast(client: HypersyncClient, start_block: int, end_block: int) -> List[Dict[str, Any]]:
    """
    Ultra-fast bet ID retrieval using Hypersync stream function.
    
    Key optimizations:
    1. Uses stream() for concurrent processing
    2. Only fetches logs (not transactions/blocks) - we only need bet IDs
    3. Minimal field selection - only topic0, topic2, and transaction_hash
    4. Specific contract addresses and topic filtering
    5. Progress tracking with tqdm
    """
    print(f"🚀 Starting ultra-fast bet ID stream from {start_block:,} to {end_block:,}...")
    
    # OPTIMIZED QUERY - Only what we need for bet IDs
    query = Query(
        from_block=start_block,
        to_block=end_block,
        # Only fetch logs - we don't need transactions or blocks for bet IDs
        logs=[
            LogSelection(
                address=CONTRACT_ADDRESSES,
                topics=[[CARDS_LOG_TOPIC_0]]  # Only the specific event we need
            )
        ],
        # MINIMAL FIELD SELECTION - Only essential fields
        field_selection=FieldSelection(
            log=[
                LogField.TOPIC0,      # Event signature (for verification)
                LogField.TOPIC2,      # Bet ID (this is what we want)
                LogField.TRANSACTION_HASH  # To link back to transaction
            ]
        ),
        # Set limits to prevent overwhelming responses
        max_num_logs=10000
    )
    
    # Configure stream for optimal performance
    config = StreamConfig(
        concurrency=4  # Number of parallel queries
    )
    
    # Start the stream
    receiver = await client.stream(query, config)
    
    bet_ids = []
    total_logs_processed = 0
    start_time = time.time()
    
    print(f"📡 Stream started with {config.concurrency} concurrent queries...")
    
    try:
        with tqdm(desc="Processing bet IDs", unit="logs") as pbar:
            while True:
                res = await receiver.recv()
                # Exit if the stream finished
                if res is None:
                    break
                
                logs_in_batch = len(res.data.logs) if res.data and res.data.logs else 0
                total_logs_processed += logs_in_batch
                
                # Process logs to extract bet IDs
                if res.data and res.data.logs:
                    for log in res.data.logs:
                        if (log.topics and len(log.topics) >= 3 and 
                            log.topics[0] == CARDS_LOG_TOPIC_0):
                            
                            bet_id = hex_to_int(log.topics[2])
                            if bet_id > 0:
                                bet_ids.append({
                                    'tx_hash': log.transaction_hash,
                                    'bet_id': bet_id
                                })
                
                # Update progress bar
                pbar.update(logs_in_batch)
                pbar.set_postfix({
                    "Bet IDs found": len(bet_ids),
                    "Current block": res.next_block,
                    "Logs processed": total_logs_processed
                })
    
    finally:
        # Always close the receiver
        await receiver.close()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n✅ Stream completed!")
    print(f"⏱️  Total time: {duration:.2f} seconds")
    print(f"📊 Total logs processed: {total_logs_processed:,}")
    print(f"🎯 Bet IDs found: {len(bet_ids):,}")
    print(f"⚡ Processing rate: {total_logs_processed/duration:.0f} logs/second")
    
    return bet_ids

async def main():
    """Main execution function - optimized for bet ID retrieval and database update."""
    # Initialize Hypersync client
    config = ClientConfig(
        url=MONAD_HYPERSYNC_URL,
        bearer_token=HYPERSYNC_BEARER_TOKEN
    )
    client = HypersyncClient(config)
    
    print("=== BET ID RETRIEVAL & DATABASE UPDATE ===")
    print("=" * 50)
    
    # Get database statistics before update
    print("📊 DATABASE STATISTICS (BEFORE UPDATE):")
    stats_before = get_database_stats()
    print(f"  Total transactions: {stats_before['total_transactions']:,}")
    print(f"  MON transactions: {stats_before['mon_transactions']:,}")
    print(f"  Transactions with bet_id: {stats_before['with_bet_id']:,}")
    print(f"  MON transactions with bet_id: {stats_before['mon_with_bet_id']:,}")
    print()
    
    # Get block range from database
    min_block, max_block = get_database_block_range()
    print(f"🎯 DATABASE BLOCK RANGE:")
    print(f"  Min block: {min_block:,}")
    print(f"  Max block: {max_block:,}")
    print(f"  Total blocks: {max_block - min_block:,}")
    print()
    
    # Get current chain height
    height = await client.get_height()
    print(f"📊 Current chain height: {height:,}")
    
    # Use entire database block range for full run
    start_block = min_block
    end_block = max_block
    
    print(f"🚀 PRODUCTION RUN: Starting bet ID retrieval from {start_block:,} to {end_block:,}")
    print(f"   This will process {(end_block - start_block):,} blocks")
    print(f"   Estimated time: {(end_block - start_block) / 10000:.1f} minutes (based on 10k blocks/min)")
    print()
    
    # Get bet IDs using ultra-fast method
    bet_ids = await stream_bet_ids_ultra_fast(client, start_block, end_block)
    
    # Create bet ID mapping for database update
    bet_id_map = {item['tx_hash']: item['bet_id'] for item in bet_ids}
    
    print(f"\n📋 BET ID RETRIEVAL RESULTS:")
    print("=" * 40)
    print(f"Total bet IDs found: {len(bet_ids):,}")
    print()
    
    if bet_ids:
        print("tx hash - bet id")
        print("-" * 40)
        for bet_id_data in bet_ids[:10]:  # Show first 10 for preview
            print(f"{bet_id_data['tx_hash']} - {bet_id_data['bet_id']}")
        if len(bet_ids) > 10:
            print(f"... and {len(bet_ids) - 10:,} more")
        print()
        
        # Update database with bet IDs
        print("🔄 UPDATING DATABASE...")
        updated_count = update_bet_ids_batch(bet_id_map)
        
        # Get database statistics after update
        print("\n📊 DATABASE STATISTICS (AFTER UPDATE):")
        stats_after = get_database_stats()
        print(f"  Total transactions: {stats_after['total_transactions']:,}")
        print(f"  MON transactions: {stats_after['mon_transactions']:,}")
        print(f"  Transactions with bet_id: {stats_after['with_bet_id']:,}")
        print(f"  MON transactions with bet_id: {stats_after['mon_with_bet_id']:,}")
        
        # Show improvement
        improvement = stats_after['with_bet_id'] - stats_before['with_bet_id']
        print(f"\n📈 IMPROVEMENT:")
        print(f"  New bet IDs added: {improvement:,}")
        print(f"  Database updates: {updated_count:,}")
        
    else:
        print("No bet IDs found in the specified block range.")
    
    print(f"\n✅ Process complete!")

if __name__ == "__main__":
    asyncio.run(main())
