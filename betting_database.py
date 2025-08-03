#!/usr/bin/env python3
"""
Betting Database System
=======================

A comprehensive system to fetch and store all betting transactions from all time
in a SQLite database with Snowflake-like structure.
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

# =============================================================================
# DATABASE MANAGEMENT
# =============================================================================

class BettingDatabase:
    """SQLite database manager for betting transactions."""
    
    def __init__(self, db_path: str = "betting_transactions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create betting_transactions table with specified schema
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
            
            # Create indexes for faster queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON betting_transactions(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_from_address ON betting_transactions(from_address)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_token ON betting_transactions(token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_block_number ON betting_transactions(block_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bet_id ON betting_transactions(bet_id)")
            
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
            print(f"Database initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
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
    
    def insert_transactions(self, transactions: List[Dict[str, Any]]) -> int:
        """Insert multiple transactions into the database."""
        if not transactions:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            inserted_count = 0
            
            for tx in transactions:
                try:
                    cursor.execute("""
                        INSERT INTO betting_transactions 
                        (timestamp, tx_hash, from_address, to_address, token, amount, n_cards, bet_id, block_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
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
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    continue  # Skip duplicates
            
            conn.commit()
            print(f"Inserted {inserted_count} new transactions (skipped {len(transactions) - inserted_count} duplicates)")
            return inserted_count
    
    def get_all_transactions(self) -> pd.DataFrame:
        """Get all transactions as a pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query("""
                SELECT timestamp, tx_hash, from_address, to_address, token, amount, n_cards, bet_id, block_number
                FROM betting_transactions 
                ORDER BY timestamp
            """, conn)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
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
            
            return {
                'total_transactions': total_txs,
                'unique_users': unique_users,
                'token_stats': token_stats,
                'date_range': date_range
            }

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def hex_to_int(hex_str: str) -> int:
    """Convert hex string to integer."""
    if not hex_str or hex_str == '0x':
        return 0
    return int(hex_str, 16)

def calculate_cards_in_slip_from_tx(tx_input: str) -> int:
    """
    Calculates the number of cards in a slip from the transaction input data.
    For MON transactions (sighash 0x5029defb), the card count is the second
    parameter in the input data, which represents the length of the card array.
    """
    # The input string starts with '0x' (2 chars) followed by the function
    # signature (8 chars). The first parameter (offset) is 64 characters.
    # The card count is the second parameter.
    # Start index: 2 (for '0x') + 8 (for signature) + 64 (for first param) = 74
    start_index = 74
    end_index = start_index + 64

    if not tx_input or len(tx_input) < end_index:
        return 0

    # Extract the 64-character hex string for the card count.
    card_count_hex = tx_input[start_index:end_index]
    
    try:
        card_count = int(card_count_hex, 16)
        
        # Sanity check: if the number is too large, it's likely an anomaly.
        if card_count > 1_000_000:
            return 0
            
        return card_count
    except (ValueError, TypeError):
        # If conversion fails, it's not the format we expect.
        return 0

def calculate_cards_in_slip_sql_style(data: str) -> int:
    """Calculate cards in slip using the exact same logic as the SQL query."""
    if not data or len(data) < 194:
        return 0
    
    try:
        # Remove the first 194 characters (RIGHT(data, LENGTH(data) - 194))
        remaining_data = data[194:]
        
        if len(remaining_data) < 64:
            return 0
        
        # Calculate cards: (length of remaining data / 64) - 1
        # This matches the SQL: ((LENGTH(RIGHT(data, LENGTH(data) - 194)) / 64) - 1)
        cards = (len(remaining_data) // 64) - 1
        return max(0, cards)
    except:
        return 0

# =============================================================================
# DATA FETCHING FUNCTIONS
# =============================================================================

async def fetch_mon_transactions(client: HypersyncClient, start_block: int, end_block: int) -> List[Dict[str, Any]]:
    """Fetch MON betting transactions - matching original query logic exactly."""
    print(f"Fetching MON transactions from {start_block} to {end_block}...")
    
    all_tx_data = []
    current_block = start_block

    while current_block < end_block:
        print(f"  Processing blocks {current_block} to {min(current_block + 10000, end_block)}...")
        
        query = Query(
            from_block=current_block,
            to_block=min(current_block + 10000, end_block),
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

        response = await client.get(query)

        if response.data:
            block_timestamp_map = {
                b.number: hex_to_int(b.timestamp)
                for b in response.data.blocks if b.number and b.timestamp
            }

            for tx in response.data.transactions:
                if tx.status != 1:  # Only successful transactions
                    continue

                timestamp = block_timestamp_map.get(tx.block_number)
                if not timestamp:
                    continue

                # Calculate cards in slip from transaction input
                cards_in_slip = calculate_cards_in_slip_from_tx(tx.input)

                # Get bet_id from RBS contract logs
                bet_id_decoded = 0
                if response.data.logs:
                    for log in response.data.logs:
                        if (log.transaction_hash == tx.hash and 
                            log.address and log.address.lower() in [addr.lower() for addr in CONTRACT_ADDRESSES_1] 
                            and log.topics and len(log.topics) >= 3):
                            bet_id_decoded = hex_to_int(log.topics[2])  # Convert hex to int
                            break  # Use the first valid bet_id found
                
                # Calculate bet amount (MON units)
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
            current_block += 10000

    print(f"Found {len(all_tx_data)} MON transactions")
    return all_tx_data

async def fetch_jerry_transactions(client: HypersyncClient, start_block: int, end_block: int) -> List[Dict[str, Any]]:
    """Fetch Jerry betting transactions - matching original query logic exactly."""
    print(f"Fetching Jerry transactions from {start_block} to {end_block}...")
    
    all_tx_data = []
    current_block = start_block
    
    while current_block < end_block:
        print(f"  Processing blocks {current_block} to {min(current_block + 10000, end_block)}...")
        
        # Query for Jerry transactions with both function signature and logs
        query = Query(
            from_block=current_block,
            to_block=min(current_block + 10000, end_block),
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
                transaction=['hash', 'from', 'status', 'block_number'],
                log=[LogField.ADDRESS, LogField.TOPIC0, LogField.TOPIC1, 
                     LogField.TOPIC2, LogField.TOPIC3, LogField.DATA, LogField.TRANSACTION_HASH]
            )
        )

        response = await client.get(query)

        if response.data:
            block_timestamp_map = {
                b.number: hex_to_int(b.timestamp)
                for b in response.data.blocks if b.number and b.timestamp
            }

            # Group logs by transaction hash
            logs_by_tx_hash = {}
            for log in response.data.logs:
                if log.transaction_hash not in logs_by_tx_hash:
                    logs_by_tx_hash[log.transaction_hash] = []
                logs_by_tx_hash[log.transaction_hash].append(log)

            # Process transactions that have both required logs
            for tx_hash, tx_logs in logs_by_tx_hash.items():
                has_jerry_log = any(
                    log.address.lower() == CONTRACT_ADDRESS_2_LOG_A.lower() 
                    and log.topics and log.topics[0] and log.topics[0].lower() == TOPIC_0_LOG_A.lower()
                    for log in tx_logs
                )
                has_rarebet_log = any(
                    log.address.lower() == CONTRACT_ADDRESS_2_LOG_B.lower()
                    for log in tx_logs
                )
                
                if has_jerry_log and has_rarebet_log:
                    tx = next((t for t in response.data.transactions if t.hash == tx_hash), None)
                    if not tx or tx.status != 1:
                        continue

                    timestamp = block_timestamp_map.get(tx.block_number)
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
                    bet_id_decoded = 0
                    
                    if card_event_log and card_event_log.data:
                        data_hex = card_event_log.data[2:] if card_event_log.data.startswith('0x') else card_event_log.data
                        start_index = 192
                        end_index = start_index + 64
                        
                        if len(data_hex) >= end_index:
                            card_count_hex = data_hex[start_index:end_index]
                            cards_in_slip = hex_to_int(card_count_hex)
                    
                    # Get bet_id from RBS contract logs (not just card event log)
                    for log in tx_logs:
                        if (log.address and log.address.lower() in [addr.lower() for addr in CONTRACT_ADDRESSES_1] 
                            and log.topics and len(log.topics) >= 3):
                            bet_id_decoded = hex_to_int(log.topics[2])  # Convert hex to int
                            break  # Use the first valid bet_id found

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
            current_block += 10000

    print(f"Found {len(all_tx_data)} Jerry transactions")
    return all_tx_data

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def process_all_transactions(db: BettingDatabase, client: HypersyncClient, start_block: int = None, end_block: int = None):
    """Process all transactions from start_block to end_block."""
    if start_block is None:
        start_block = db.get_last_processed_block()
        if start_block == 0:
            start_block = 0  # Start from block 0 for complete historical data
    
    if end_block is None:
        end_block = await client.get_height()
        print(f"Current blockchain height: {end_block}")
    
    if start_block >= end_block:
        print(f"No new blocks to process (last processed: {start_block}, end: {end_block})")
        return 0
    
    print(f"Processing blocks {start_block} to {end_block}")
    
    # Fetch new data using the same logic as block_check_fixed.py
    mon_data, jerry_data = await asyncio.gather(
        fetch_mon_transactions(client, start_block, end_block),
        fetch_jerry_transactions(client, start_block, end_block)
    )
    
    all_tx_data = mon_data + jerry_data
    
    if not all_tx_data:
        print("No new transactions found.")
        db.update_last_processed_block(end_block)
        return 0
    
    # Store transactions in database
    inserted_count = db.insert_transactions(all_tx_data)
    
    # Update checkpoint
    db.update_last_processed_block(end_block)
    
    return inserted_count

async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Betting Database System")
    parser.add_argument("--incremental", action="store_true", help="Only fetch new data")
    parser.add_argument("--start-block", type=int, help="Start from specific block")
    parser.add_argument("--end-block", type=int, help="End at specific block")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    # Set default database path based on environment
    if IS_PRODUCTION:
        default_db_path = "/app/data/betting_transactions.db"
    else:
        default_db_path = os.getenv('DB_PATH', 'betting_transactions.db')
    
    parser.add_argument("--db-path", type=str, default=default_db_path, help="Path to database file")
    args = parser.parse_args()
    
    # Initialize database
    db = BettingDatabase(db_path=args.db_path)
    
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
            print(f"\n📊 DATABASE STATISTICS")
            print(f"=" * 50)
            print(f"Total Transactions: {stats['total_transactions']:,}")
            print(f"Unique Users: {stats['unique_users']:,}")
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
            start_block = 0  # Start from beginning
        
        # Determine end block
        if args.end_block is not None:
            end_block = args.end_block
        else:
            end_block = await client.get_height()
        
        print(f"Starting data processing from block {start_block} to {end_block}")
        
        # Process and store data
        inserted_count = await process_all_transactions(db, client, start_block, end_block)
        
        if inserted_count > 0:
            print(f"\nProcessing complete! Inserted {inserted_count} new transactions.")
            
            # Show database stats
            stats = db.get_database_stats()
            print(f"\nDatabase Statistics:")
            print(f"Total Transactions: {stats['total_transactions']:,}")
            print(f"Unique Users: {stats['unique_users']:,}")
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