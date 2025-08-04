#!/usr/bin/env python3
"""
Optimized Betting Database System
================================

A high-performance system to fetch and store all betting transactions from all time
in a SQLite database with optimized batch processing and caching.
"""

import asyncio
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import argparse
import sys
from collections import defaultdict
from tqdm import tqdm

# Fix for Python 3.12+ SQLite datetime deprecation warning
def adapt_datetime(val):
    return val.isoformat()

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

from hypersync import HypersyncClient, ClientConfig, TransactionSelection, LogSelection, FieldSelection, Query
from hypersync import LogField, TransactionField, BlockField

# =============================================================================
# CONFIGURATION
# =============================================================================

# Load environment variables
load_dotenv('.env.local')  # Load local environment first
load_dotenv()  # Load any other .env files

# Environment-based configuration
IS_PRODUCTION = os.getenv('IS_PRODUCTION', 'false').lower() == 'true'

MONAD_HYPERSYNC_URL = os.getenv("MONAD_HYPERSYNC_URL", "https://monad-testnet.hypersync.xyz")
HYPERSYNC_BEARER_TOKEN = os.getenv("HYPERSYNC_BEARER_TOKEN")

# Contract addresses and signatures - matching original query exactly
CONTRACT_ADDRESSES_1 = ['0x3ad50059d6008b711209a509fe58e68f0b672a42', '0x740990cb01e893a371a050736c62ae0b779109e7']
SIG_HASH_1 = '0x5029defb'

CONTRACT_ADDRESS_2_TX_TO = '0x740990cb01e893a371a050736c62ae0b779109e7'
CONTRACT_ADDRESS_2_LOG_A = '0xda054a96254776346386060c480b42a10c870cd2'
CONTRACT_ADDRESS_2_LOG_B = '0x740990cb01e893a371a050736c62ae0b779109e7'
SIG_HASH_2 = '0xb65c106f'
TOPIC_0_LOG_A = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
CARDS_LOG_TOPIC_0 = '0xefc52bf7792453af1461fa9a7097486359b41a048898b6d542c0f03389487187'

# Event signatures for betting events
BETTING_EVENT_SIGNATURE = '0xefc52bf7792453af1461fa9a7097486359b41a048898b6d542c0f03389487187'  # Same as CARDS_LOG_TOPIC_0

# Performance settings
BATCH_SIZE = 50000  # Increased from 10000
MAX_CONCURRENT_REQUESTS = 3  # Limit concurrent requests
CACHE_SIZE = 1000  # Cache size for block timestamps

# =============================================================================
# OPTIMIZED DATABASE MANAGEMENT
# =============================================================================

class OptimizedBettingDatabase:
    """High-performance SQLite database manager for betting transactions."""
    
    def __init__(self, db_path: str = "betting_transactions.db"):
        self.db_path = db_path
        self.init_database()
        self.block_cache = {}  # Cache for block timestamps
    
    def init_database(self):
        """Initialize the database with optimized indexes."""
        # First, set up the database connection with optimizations
        conn = sqlite3.connect(self.db_path)
        
        # Set PRAGMA settings before any transactions
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA foreign_keys=OFF")
        
        cursor = conn.cursor()
        
        # Create betting_transactions table with optimized schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS betting_transactions (
                timestamp DATETIME NOT NULL,
                tx_hash TEXT PRIMARY KEY,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                token TEXT NOT NULL,
                amount REAL NOT NULL,
                n_cards INTEGER NOT NULL,
                bet_id INTEGER NOT NULL,
                block_number INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create optimized indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON betting_transactions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_from_address ON betting_transactions(from_address)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token ON betting_transactions(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_block_number ON betting_transactions(block_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bet_id ON betting_transactions(bet_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_block ON betting_transactions(token, block_number)")
        
        # Create checkpoint table to track processing progress
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY,
                last_processed_block INTEGER NOT NULL,
                last_update DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert initial checkpoint if none exists
        cursor.execute("SELECT COUNT(*) FROM checkpoints")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO checkpoints (last_processed_block) VALUES (0)")
        
        conn.commit()
        conn.close()
        print(f"Optimized database initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with optimizations."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys=OFF")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
        finally:
            conn.close()
    
    def get_last_processed_block(self) -> int:
        """Get the last processed block number."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_processed_block FROM checkpoints ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else 0
    
    def update_last_processed_block(self, block_number: int):
        """Update the last processed block number."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE checkpoints 
                SET last_processed_block = ?, last_update = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM checkpoints ORDER BY id DESC LIMIT 1)
            """, (block_number,))
            conn.commit()
            print(f"Updated last processed block to: {block_number}")
    
    def insert_transactions_batch(self, transactions: List[Dict[str, Any]]) -> int:
        """Insert multiple transactions using optimized batch processing."""
        if not transactions:
            return 0
        
        print(f"Inserting {len(transactions):,} transactions into database...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Use executemany for batch insertion
            batch_data = []
            with tqdm(total=len(transactions), desc="Database Insert", unit="tx", leave=False) as pbar:
                for tx in transactions:
                    batch_data.append((
                        tx['timestamp'],
                        tx['tx_hash'],
                        tx['from_address'],
                        tx['to_address'],
                        tx['token'],
                        tx['amount'],
                        tx['n_cards'],
                        tx['bet_id'],
                        tx['block_number']
                    ))
                    pbar.update(1)
            
            try:
                cursor.executemany("""
                    INSERT OR IGNORE INTO betting_transactions 
                    (timestamp, tx_hash, from_address, to_address, token, amount, n_cards, bet_id, block_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch_data)
                
                inserted_count = cursor.rowcount
                conn.commit()
                print(f"✅ Inserted {inserted_count:,} new transactions (skipped {len(transactions) - inserted_count:,} duplicates)")
                return inserted_count
                
            except sqlite3.Error as e:
                print(f"❌ Database error: {e}")
                return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics with optimized queries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total transactions
            cursor.execute("SELECT COUNT(*) FROM betting_transactions")
            total_txs = cursor.fetchone()[0]
            
            # Transactions by token
            cursor.execute("""
                SELECT token, COUNT(*), SUM(amount), AVG(amount)
                FROM betting_transactions 
                GROUP BY token
            """)
            token_stats = cursor.fetchall()
            
            # Unique users
            cursor.execute("SELECT COUNT(DISTINCT from_address) FROM betting_transactions")
            unique_users = cursor.fetchone()[0]
            
            # Date range
            cursor.execute("""
                SELECT MIN(timestamp), MAX(timestamp) 
                FROM betting_transactions
            """)
            date_range = cursor.fetchone()
            
            # Max block number
            cursor.execute("SELECT MAX(block_number) FROM betting_transactions")
            max_block = cursor.fetchone()[0]
            
            return {
                'total_transactions': total_txs,
                'unique_users': unique_users,
                'token_stats': token_stats,
                'date_range': date_range,
                'max_block': max_block
            }

# =============================================================================
# OPTIMIZED UTILITY FUNCTIONS
# =============================================================================

def hex_to_int(hex_str: str) -> int:
    """Convert hex string to integer with error handling."""
    if not hex_str or hex_str == '0x':
        return 0
    try:
        return int(hex_str, 16)
    except (ValueError, TypeError):
        return 0

def calculate_cards_in_slip_from_tx(tx_input: str) -> int:
    """Optimized card calculation with better error handling."""
    if not tx_input or len(tx_input) < 138:  # Minimum length check
        return 0
    
    try:
        # The input string starts with '0x' (2 chars) followed by the function
        # signature (8 chars). The first parameter (offset) is 64 characters.
        # The card count is the second parameter.
        start_index = 74
        end_index = start_index + 64

        if len(tx_input) < end_index:
            return 0

        card_count_hex = tx_input[start_index:end_index]
        card_count = int(card_count_hex, 16)
        
        # Sanity check
        if card_count > 1_000_000:
            return 0
            
        return card_count
    except (ValueError, TypeError, IndexError):
        return 0

# =============================================================================
# OPTIMIZED DATA FETCHING FUNCTIONS
# =============================================================================

async def fetch_mon_transactions_optimized(client: HypersyncClient, start_block: int, end_block: int, progress_bar: tqdm = None) -> List[Dict[str, Any]]:
    """Optimized MON transaction fetching with better caching and processing."""
    print(f"Fetching MON transactions from {start_block:,} to {end_block:,}...")
    
    all_tx_data = []
    current_block = start_block
    block_cache = {}

    while current_block < end_block:
        batch_end = min(current_block + BATCH_SIZE, end_block)
        
        # Update progress bar
        if progress_bar:
            progress_bar.set_description(f"MON: {current_block:,} → {batch_end:,}")
            progress_bar.update(batch_end - current_block)
        
        query = Query(
            from_block=current_block,
            to_block=batch_end,
            transactions=[TransactionSelection(
                to=CONTRACT_ADDRESSES_1,
                sighash=[SIG_HASH_1]
            )],
            logs=[
                LogSelection(address=CONTRACT_ADDRESSES_1)
            ],
            field_selection=FieldSelection(
                block=['timestamp', 'number'],
                transaction=['hash', 'from', 'to', 'value', 'input', 'status', 'block_number'],
                log=[LogField.ADDRESS, LogField.TOPIC0, LogField.TOPIC1, 
                     LogField.TOPIC2, LogField.TOPIC3, LogField.DATA, LogField.TRANSACTION_HASH]
            )
        )

        try:
            response = await client.get(query)
        except Exception as e:
            print(f"Error fetching MON data: {e}")
            current_block = batch_end
            continue

        if not response.data:
            current_block = batch_end
            continue

        # Build block timestamp cache
        for block in response.data.blocks:
            if block.number and block.timestamp:
                block_cache[block.number] = hex_to_int(block.timestamp)

        # Group logs by transaction hash for faster lookup
        logs_by_tx = defaultdict(list)
        for log in response.data.logs:
            logs_by_tx[log.transaction_hash].append(log)

        # Process transactions
        for tx in response.data.transactions:
            if tx.status != 1:  # Only successful transactions
                continue

            timestamp = block_cache.get(tx.block_number)
            if not timestamp:
                continue

            # Check if transaction has the correct MON signature
            if tx.input[:10] != SIG_HASH_1:
                print(f"      Skipping MON transaction with wrong signature: {tx.hash} (has {tx.input[:10]}, expected {SIG_HASH_1})")
                continue

            print(f"      MON transaction: {tx.hash}")
            print(f"        Input signature: {tx.input[:10]} (expected: {SIG_HASH_1})")
            print(f"        Has MON signature: {tx.input[:10] == SIG_HASH_1}")
            print(f"        Number of logs: {len([log for log in response.data.logs if log.transaction_hash == tx.hash])}")




            
            # Calculate cards in slip
            cards_in_slip = calculate_cards_in_slip_from_tx(tx.input)

            # Get bet_id_decoded from logs using separate query
            bet_id_decoded = 0
            try:
                # Query logs for this specific transaction
                log_query = Query(
                    from_block=tx.block_number,
                    to_block=tx.block_number + 1,
                    logs=[
                        LogSelection(
                            address=CONTRACT_ADDRESSES_1,
                            topics=[[CARDS_LOG_TOPIC_0]]
                        )
                    ],
                    field_selection=FieldSelection(
                        log=[LogField.ADDRESS, LogField.TOPIC0, LogField.TOPIC1, 
                             LogField.TOPIC2, LogField.TOPIC3, LogField.DATA, LogField.TRANSACTION_HASH]
                    )
                )
                log_response = await client.get(log_query)
                
                if log_response.data and log_response.data.logs:
                    print(f"        Checking logs for bet_id...")
                    for log in log_response.data.logs:
                        if log.transaction_hash == tx.hash and len(log.topics) >= 3:
                            print(f"          Log: address={log.address}, topics={log.topics}")
                            # Look for the card event log (topic 0 = CARDS_LOG_TOPIC_0)
                            if (log.topics and log.topics[0] and 
                                log.topics[0].lower() == '0xefc52bf7792453af1461fa9a7097486359b41a048898b6d542c0f03389487187'):
                                bet_id_decoded = hex_to_int(log.topics[2])
                                print(f"          Found bet_id: {bet_id_decoded}")
                                break
            except Exception as e:
                print(f"        Error querying logs: {e}")
            
            # Calculate bet amount
            bet_amt = hex_to_int(tx.value) / 1e18
            
            all_tx_data.append({
                "timestamp": datetime.fromtimestamp(timestamp),
                "tx_hash": tx.hash,
                "from_address": tx.from_,
                "to_address": tx.to,
                "token": "MON",
                "amount": bet_amt,
                "n_cards": cards_in_slip,
                "bet_id": bet_id_decoded,
                "block_number": tx.block_number,
            })
        
        if response.next_block and response.next_block > current_block:
            current_block = response.next_block
        else:
            current_block = batch_end

    print(f"Found {len(all_tx_data)} MON transactions")
    return all_tx_data

async def fetch_jerry_transactions_optimized(client: HypersyncClient, start_block: int, end_block: int, progress_bar: tqdm = None) -> List[Dict[str, Any]]:
    """Optimized Jerry transaction fetching."""
    print(f"Fetching Jerry transactions from {start_block:,} to {end_block:,}...")
    
    all_tx_data = []
    current_block = start_block
    block_cache = {}
    
    while current_block < end_block:
        batch_end = min(current_block + BATCH_SIZE, end_block)
        
        # Update progress bar
        if progress_bar:
            progress_bar.set_description(f"JERRY: {current_block:,} → {batch_end:,}")
            progress_bar.update(batch_end - current_block)
        
        query = Query(
            from_block=current_block,
            to_block=batch_end,
            transactions=[TransactionSelection(
                to=[CONTRACT_ADDRESS_2_TX_TO],
                sighash=[SIG_HASH_2]
            )],
            logs=[
                LogSelection(address=[CONTRACT_ADDRESS_2_LOG_A], topics=[[TOPIC_0_LOG_A]]),
                LogSelection(address=[CONTRACT_ADDRESS_2_LOG_B])
            ],
            field_selection=FieldSelection(
                block=['timestamp', 'number'],
                transaction=['hash', 'from', 'status', 'block_number', 'input'],
                log=[LogField.ADDRESS, LogField.TOPIC0, LogField.TOPIC1, 
                     LogField.TOPIC2, LogField.TOPIC3, LogField.DATA, LogField.TRANSACTION_HASH]
            )
        )

        try:
            response = await client.get(query)
        except Exception as e:
            print(f"Error fetching Jerry data: {e}")
            current_block = batch_end
            continue

        if not response.data:
            current_block = batch_end
            continue

        # Build block timestamp cache
        for block in response.data.blocks:
            if block.number and block.timestamp:
                block_cache[block.number] = hex_to_int(block.timestamp)

        # Group logs by transaction hash
        logs_by_tx = defaultdict(list)
        for log in response.data.logs:
            logs_by_tx[log.transaction_hash].append(log)

        # Process transactions
        for tx_hash, tx_logs in logs_by_tx.items():
            # Check if we have both required logs (JERRY token contract AND RBS contract)
            has_jerry_log = any(
                log.address.lower() == CONTRACT_ADDRESS_2_LOG_A.lower() 
                and log.topics and log.topics[0] and log.topics[0].lower() == TOPIC_0_LOG_A.lower()
                for log in tx_logs
            )
            has_rarebet_log = any(
                log.address.lower() == CONTRACT_ADDRESS_2_LOG_B.lower()
                for log in tx_logs
            )
            
            if not (has_jerry_log and has_rarebet_log):
                continue
            


            tx = next((t for t in response.data.transactions if t.hash == tx_hash), None)
            if not tx or tx.status != 1:
                continue

            # Check if transaction has the correct JERRY signature
            if tx.input[:10] != SIG_HASH_2:
                print(f"      Skipping JERRY transaction with wrong signature: {tx.hash} (has {tx.input[:10]}, expected {SIG_HASH_2})")
                continue




            
            timestamp = block_cache.get(tx.block_number)
            if not timestamp:
                continue
            
            # Get Jerry log for bet amount
            jerry_log = next((
                log for log in tx_logs 
                if log.address.lower() == CONTRACT_ADDRESS_2_LOG_A.lower()
                and log.topics and log.topics[0] and log.topics[0].lower() == TOPIC_0_LOG_A.lower()
            ), None)
            
            # Get card event log for cards in slip
            card_event_log = next((
                log for log in tx_logs
                if log.address.lower() == CONTRACT_ADDRESS_2_LOG_B.lower()
                and log.topics and log.topics[0] and log.topics[0].lower() == CARDS_LOG_TOPIC_0.lower()
            ), None)

            # Calculate cards in slip
            cards_in_slip = 0
            if card_event_log and card_event_log.data:
                try:
                    data_hex = card_event_log.data[2:] if card_event_log.data.startswith('0x') else card_event_log.data
                    start_index = 192
                    end_index = start_index + 64
                    
                    if len(data_hex) >= end_index:
                        card_count_hex = data_hex[start_index:end_index]
                        cards_in_slip = hex_to_int(card_count_hex)
                except (ValueError, TypeError, IndexError):
                    cards_in_slip = 0
            
            # Get bet_id using separate query (same approach as MON)
            bet_id_decoded = 0
            try:
                log_query = Query(
                    from_block=tx.block_number,
                    to_block=tx.block_number + 1,
                    logs=[
                        LogSelection(
                            address=CONTRACT_ADDRESSES_1,
                            topics=[[CARDS_LOG_TOPIC_0]]
                        )
                    ],
                    field_selection=FieldSelection(
                        log=[LogField.ADDRESS, LogField.TOPIC0, LogField.TOPIC1, 
                             LogField.TOPIC2, LogField.TOPIC3, LogField.DATA, LogField.TRANSACTION_HASH]
                    )
                )
                log_response = await client.get(log_query)
                
                if log_response.data and log_response.data.logs:
                    for log in log_response.data.logs:
                        if log.transaction_hash == tx.hash and len(log.topics) >= 3:
                            if (log.topics and log.topics[0] and 
                                log.topics[0].lower() == '0xefc52bf7792453af1461fa9a7097486359b41a048898b6d542c0f03389487187'):
                                bet_id_decoded = hex_to_int(log.topics[2])
                                break
            except Exception as e:
                print(f"        Error querying logs for JERRY: {e}")

            # Calculate bet amount from Jerry log
            bet_amt = 0
            if jerry_log and jerry_log.data:
                bet_amt = hex_to_int(jerry_log.data) / 1e18

            all_tx_data.append({
                "timestamp": datetime.fromtimestamp(timestamp),
                "tx_hash": tx.hash,
                "from_address": tx.from_,
                "to_address": CONTRACT_ADDRESS_2_TX_TO,
                "token": "Jerry",
                "amount": bet_amt,
                "n_cards": cards_in_slip,
                "bet_id": bet_id_decoded,
                "block_number": tx.block_number,
            })
        
        if response.next_block and response.next_block > current_block:
            current_block = response.next_block
        else:
            current_block = batch_end

    print(f"Found {len(all_tx_data)} Jerry transactions")
    return all_tx_data

# =============================================================================
# OPTIMIZED MAIN EXECUTION
# =============================================================================

async def process_all_transactions_optimized(db: OptimizedBettingDatabase, client: HypersyncClient, start_block: int = None, end_block: int = None):
    """Optimized processing of all transactions."""
    if start_block is None:
        start_block = db.get_last_processed_block()
        if start_block == 0:
            start_block = 0
    
    if end_block is None:
        end_block = await client.get_height()
        print(f"Current blockchain height: {end_block:,}")
    
    if start_block >= end_block:
        print(f"No new blocks to process (last processed: {start_block:,}, end: {end_block:,})")
        return 0
    
    total_blocks = end_block - start_block
    print(f"Processing {total_blocks:,} blocks from {start_block:,} to {end_block:,}")
    
    # Create separate progress bars for each token type
    with tqdm(total=total_blocks, desc="MON Processing", unit="blocks", position=0, leave=True) as mon_pbar, \
         tqdm(total=total_blocks, desc="JERRY Processing", unit="blocks", position=1, leave=True) as jerry_pbar:
        
        # Fetch data concurrently with semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        async def fetch_with_semaphore(fetch_func, client, start_block, end_block, progress_bar=None):
            async with semaphore:
                return await fetch_func(client, start_block, end_block, progress_bar)
        
        # Fetch new data concurrently
        mon_data, jerry_data = await asyncio.gather(
            fetch_with_semaphore(fetch_mon_transactions_optimized, client, start_block, end_block, mon_pbar),
            fetch_with_semaphore(fetch_jerry_transactions_optimized, client, start_block, end_block, jerry_pbar)
        )
    
    all_tx_data = mon_data + jerry_data
    
    if not all_tx_data:
        print("No new transactions found.")
        db.update_last_processed_block(end_block)
        return 0
    
    # Store transactions in database using optimized batch insertion
    inserted_count = db.insert_transactions_batch(all_tx_data)
    
    # Update checkpoint
    db.update_last_processed_block(end_block)
    
    return inserted_count

async def main():
    """Main execution function with optimizations."""
    global BATCH_SIZE
    
    parser = argparse.ArgumentParser(description="Optimized Betting Database System")
    parser.add_argument("--incremental", action="store_true", help="Only fetch new data")
    parser.add_argument("--start-block", type=int, help="Start from specific block")
    parser.add_argument("--end-block", type=int, help="End at specific block")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Batch size for processing")
    
    # Set default database path based on environment
    if IS_PRODUCTION:
        default_db_path = "/app/data/betting_transactions.db"
    else:
        default_db_path = os.getenv('DB_PATH', 'betting_transactions.db')
    
    parser.add_argument("--db-path", type=str, default=default_db_path, help="Path to database file")
    args = parser.parse_args()
    
    # Update batch size if specified
    if args.batch_size != BATCH_SIZE:
        BATCH_SIZE = args.batch_size
    
    # Initialize database
    db = OptimizedBettingDatabase(db_path=args.db_path)
    
    # Initialize Hypersync client
    config = ClientConfig(
        url=MONAD_HYPERSYNC_URL,
        bearer_token=HYPERSYNC_BEARER_TOKEN
    )
    client = HypersyncClient(config)
    
    try:
        if args.stats:
            # Show database statistics
            stats = db.get_database_stats()
            print(f"\n📊 OPTIMIZED DATABASE STATISTICS")
            print(f"=" * 50)
            print(f"Total Transactions: {stats['total_transactions']:,}")
            print(f"Unique Users: {stats['unique_users']:,}")
            print(f"Max Block Number: {stats['max_block']:,}")
            if stats['date_range'][0]:
                print(f"Date Range: {stats['date_range'][0]} to {stats['date_range'][1]}")
            print(f"\nToken Distribution:")
            for token, count, total_volume, avg_bet in stats['token_stats']:
                print(f"  {token}: {count:,} txs, {total_volume:,.2f} volume, {avg_bet:.4f} avg")
            return
        
        if args.start_block is not None:
            start_block = args.start_block
        elif args.incremental:
            start_block = db.get_last_processed_block()
        else:
            start_block = 0
        
        # Determine end block
        if args.end_block is not None:
            end_block = args.end_block
        else:
            end_block = await client.get_height()
        
        print(f"Starting optimized data processing from block {start_block:,} to {end_block:,}")
        print(f"Batch size: {BATCH_SIZE:,}, Max concurrent requests: {MAX_CONCURRENT_REQUESTS}")
        
        # Start timing
        start_time = datetime.now()
        
        # Process and store data
        inserted_count = await process_all_transactions_optimized(db, client, start_block, end_block)
        
        # Calculate timing
        end_time = datetime.now()
        duration = end_time - start_time
        blocks_processed = end_block - start_block
        blocks_per_second = blocks_processed / duration.total_seconds() if duration.total_seconds() > 0 else 0
        
        print(f"\n⏱️  Processing completed in {duration}")
        print(f"📊 Processed {blocks_processed:,} blocks at {blocks_per_second:.1f} blocks/second")
        
        if inserted_count > 0:
            print(f"\nProcessing complete! Inserted {inserted_count} new transactions.")
            
            # Show database stats
            stats = db.get_database_stats()
            print(f"\nDatabase Statistics:")
            print(f"Total Transactions: {stats['total_transactions']:,}")
            print(f"Unique Users: {stats['unique_users']:,}")
            print(f"Max Block Number: {stats['max_block']:,}")
            print(f"Token Distribution:")
            for token, count, total_volume, avg_bet in stats['token_stats']:
                print(f"  {token}: {count:,} txs, {total_volume:,.2f} volume, {avg_bet:.4f} avg")
        else:
            print("No new data to process.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 