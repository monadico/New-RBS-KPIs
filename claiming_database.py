#!/usr/bin/env python3
"""
Fixed Comprehensive Claiming Database
====================================

Fixed version that properly categorizes tokens by checking which contracts
the transaction interacts with:
- JERRY: RBS contracts + JERRY contract (0xda054a96254776346386060c480b42a10c870cd2)
- RBSD: RBS contracts + RBSD contract (0x8a86d48c867b76FF74A36d3AF4d2F1E707B143eD)
- MON: RBS contracts but NOT JERRY or RBSD contracts
"""

import asyncio
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple
from contextlib import contextmanager

# Load environment variables
load_dotenv('.env.local')
load_dotenv()

from hypersync import HypersyncClient, ClientConfig, TransactionSelection, LogSelection, FieldSelection, Query
from hypersync import LogField, TransactionField, BlockField

# Configuration
MONAD_HYPERSYNC_URL = os.getenv("MONAD_HYPERSYNC_URL", "https://monad-testnet.hypersync.xyz")
HYPERSYNC_BEARER_TOKEN = os.getenv("HYPERSYNC_BEARER_TOKEN")

# Contract addresses and signatures
CLAIM_FUNCTION_SIGNATURE = '0xa11fd1e3'
CLAIM_EVENT_TOPIC = '0x9f930e45e5f186baa9054d3efb58f5f12c8894372119fb461d8abd2b9418cf2d'
TRANSFER_EVENT_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

# RBS Contract addresses
RBS_CONTRACT_ADDRESSES = [
    '0x3ad50059d6008b711209a509fe58e68f0b672a42',
    '0x740990cb01e893a371a050736c62ae0b779109e7'
]

# Token contract addresses
JERRY_CONTRACT_ADDRESS = '0xda054a96254776346386060c480b42a10c870cd2'
RBSD_CONTRACT_ADDRESS = '0x8a86d48c867b76FF74A36d3AF4d2F1E707B143eD'

def hex_to_int(hex_str: str) -> int:
    """Convert hex string to integer."""
    if not hex_str or hex_str == '0x':
        return 0
    return int(hex_str, 16)

class ComprehensiveClaimingDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize the database with the claiming transactions table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create claiming transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS claiming_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    tx_hash TEXT UNIQUE NOT NULL,
                    from_address TEXT NOT NULL,
                    to_address TEXT NOT NULL,
                    token TEXT NOT NULL,
                    amount REAL NOT NULL,
                    bet_id INTEGER NOT NULL,
                    block_number INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tx_hash ON claiming_transactions(tx_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON claiming_transactions(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_token ON claiming_transactions(token)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bet_id ON claiming_transactions(bet_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_block_number ON claiming_transactions(block_number)')
            
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
    
    def insert_transactions(self, transactions: List[Dict[str, Any]]) -> int:
        """Insert claiming transactions into the database."""
        if not transactions:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            inserted_count = 0
            
            for tx in transactions:
                try:
                    cursor.execute('''
                        INSERT INTO claiming_transactions 
                        (timestamp, tx_hash, from_address, to_address, token, amount, bet_id, block_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        tx['timestamp'],
                        tx['tx_hash'],
                        tx['from_address'],
                        tx['to_address'],
                        tx['token'],
                        tx['amount'],
                        tx['bet_id'],
                        tx['block_number']
                    ))
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    continue  # Skip duplicates
            
            conn.commit()
            print(f"Inserted {inserted_count} new transactions (skipped {len(transactions) - inserted_count} duplicates)")
            return inserted_count
    
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
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Basic stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_transactions,
                    COUNT(DISTINCT from_address) as unique_users,
                    COUNT(DISTINCT tx_hash) as unique_transactions
                FROM claiming_transactions
            ''')
            basic_stats = cursor.fetchone()
            
            # Token breakdown
            cursor.execute('''
                SELECT 
                    token,
                    COUNT(*) as count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    MIN(amount) as min_amount,
                    MAX(amount) as max_amount
                FROM claiming_transactions
                GROUP BY token
                ORDER BY total_amount DESC
            ''')
            token_stats = cursor.fetchall()
            
            return {
                'total_transactions': basic_stats[0],
                'unique_users': basic_stats[1],
                'unique_transactions': basic_stats[2],
                'token_stats': token_stats
            }

async def fetch_all_claiming_transactions_fixed(client: HypersyncClient, start_block: int, end_block: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Fetch all claiming transactions and properly categorize them based on contract interactions."""
    print(f"Fetching all claiming transactions from {start_block} to {end_block}...")
    
    mon_transactions = []
    jerry_transactions = []
    rbsd_transactions = []
    current_block = start_block
    
    while current_block < end_block:
        print(f"  Processing blocks {current_block} to {min(current_block + 500000, end_block)}...")
        
        # Comprehensive query for all claiming transactions
        query = Query(
            from_block=current_block,
            to_block=min(current_block + 500000, end_block),
            transactions=[
                TransactionSelection(
                    to=RBS_CONTRACT_ADDRESSES,
                    sighash=[CLAIM_FUNCTION_SIGNATURE]
                )
            ],
            logs=[
                # RBS claiming logs
                LogSelection(
                    address=RBS_CONTRACT_ADDRESSES,
                    topics=[[CLAIM_EVENT_TOPIC]]
                ),
                # JERRY transfer logs
                LogSelection(
                    address=[JERRY_CONTRACT_ADDRESS],
                    topics=[[TRANSFER_EVENT_TOPIC]]
                ),
                # RBSD transfer logs
                LogSelection(
                    address=[RBSD_CONTRACT_ADDRESS],
                    topics=[[TRANSFER_EVENT_TOPIC]]
                )
            ],
            field_selection=FieldSelection(
                block=['timestamp', 'number'],
                transaction=['hash', 'from', 'to', 'value', 'input', 'status', 'block_number'],
                log=[LogField.ADDRESS, LogField.TOPIC0, LogField.TOPIC1, 
                     LogField.TOPIC2, LogField.TOPIC3, LogField.DATA, LogField.TRANSACTION_HASH]
            )
        )

        response = await client.get(query)

        print(f"    Query returned: {len(response.data.transactions) if response.data else 0} transactions, {len(response.data.logs) if response.data else 0} logs")

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

            # print(f"    Grouped logs by {len(logs_by_tx_hash)} transaction hashes")

            for tx in response.data.transactions:
                if tx.status != 1:  # Only successful transactions
                    continue

                timestamp = block_timestamp_map.get(tx.block_number)
                if not timestamp:
                    continue

                # Get all logs for this transaction
                tx_logs = logs_by_tx_hash.get(tx.hash, [])
                
                # Check if transaction has RBS claiming logs
                has_rbs_claiming_log = any(
                    log.address and log.address.lower() in [addr.lower() for addr in RBS_CONTRACT_ADDRESSES] and
                    log.topics and log.topics[0] and log.topics[0].lower() == CLAIM_EVENT_TOPIC.lower()
                    for log in tx_logs
                )
                
                if not has_rbs_claiming_log:
                    continue
                
                # Check for token contract interactions
                has_jerry_transfer_log = any(
                    log.address and log.address.lower() == JERRY_CONTRACT_ADDRESS.lower() and
                    log.topics and log.topics[0] and log.topics[0].lower() == TRANSFER_EVENT_TOPIC.lower()
                    for log in tx_logs
                )
                
                has_rbsd_transfer_log = any(
                    log.address and log.address.lower() == RBSD_CONTRACT_ADDRESS.lower() and
                    log.topics and log.topics[0] and log.topics[0].lower() == TRANSFER_EVENT_TOPIC.lower()
                    for log in tx_logs
                )
                
                # Categorize based on contract interactions
                if has_jerry_transfer_log:
                    # This is a JERRY transaction
                    print(f"    Categorizing as JERRY: {tx.hash}")
                    
                    # Extract JERRY data
                    bet_id = 0
                    claim_amount = 0
                    
                    for log in tx_logs:
                        # Get claim amount from JERRY transfer log
                        if (log.address and log.address.lower() == JERRY_CONTRACT_ADDRESS.lower() and
                            log.topics and log.topics[0] and log.topics[0].lower() == TRANSFER_EVENT_TOPIC.lower()):
                            if log.data and len(log.data) >= 66:
                                data_hex = log.data[2:66]
                                try:
                                    claim_amount = hex_to_int(data_hex) / 1e18
                                    print(f"      Found claim amount: {claim_amount} Jerry from transfer log")
                                except (ValueError, TypeError):
                                    print(f"      Failed to parse claim amount from transfer log: {log.data}")
                        
                        # Get bet_id from RBS claiming log
                        elif (log.address and log.address.lower() in [addr.lower() for addr in RBS_CONTRACT_ADDRESSES] and
                              log.topics and log.topics[0] and log.topics[0].lower() == CLAIM_EVENT_TOPIC.lower()):
                            if len(log.topics) >= 3 and log.topics[2]:
                                bet_id = hex_to_int(log.topics[2])
                                print(f"      Found bet_id: {bet_id} from claiming log")
                    
                    if claim_amount > 0:
                        jerry_transactions.append({
                            "timestamp": datetime.fromtimestamp(timestamp),
                            "tx_hash": tx.hash,
                            "from_address": tx.from_,
                            "to_address": tx.to,
                            "token": "JERRY",
                            "amount": claim_amount,
                            "bet_id": bet_id,
                            "block_number": tx.block_number,
                        })
                
                elif has_rbsd_transfer_log:
                    # This is a RBSD transaction
                    print(f"    Categorizing as RBSD: {tx.hash}")
                    print(f"    🔍 RBSD TRANSACTION FOUND: {tx.hash}")
                    
                    # Extract RBSD data
                    bet_id = 0
                    claim_amount = 0
                    
                    for log in tx_logs:
                        # Get claim amount from RBSD transfer log
                        if (log.address and log.address.lower() == RBSD_CONTRACT_ADDRESS.lower() and
                            log.topics and log.topics[0] and log.topics[0].lower() == TRANSFER_EVENT_TOPIC.lower()):
                            if log.data and len(log.data) >= 66:
                                data_hex = log.data[2:66]
                                try:
                                    claim_amount = hex_to_int(data_hex) / 1e18
                                    print(f"      Found claim amount: {claim_amount} RBSD from transfer log")
                                except (ValueError, TypeError):
                                    print(f"      Failed to parse claim amount from transfer log: {log.data}")
                        
                        # Get bet_id from RBS claiming log
                        elif (log.address and log.address.lower() in [addr.lower() for addr in RBS_CONTRACT_ADDRESSES] and
                              log.topics and log.topics[0] and log.topics[0].lower() == CLAIM_EVENT_TOPIC.lower()):
                            if len(log.topics) >= 3 and log.topics[2]:
                                bet_id = hex_to_int(log.topics[2])
                                print(f"      Found bet_id: {bet_id} from claiming log")
                    
                    if claim_amount > 0:
                        rbsd_transactions.append({
                            "timestamp": datetime.fromtimestamp(timestamp),
                            "tx_hash": tx.hash,
                            "from_address": tx.from_,
                            "to_address": tx.to,
                            "token": "RBSD",
                            "amount": claim_amount,
                            "bet_id": bet_id,
                            "block_number": tx.block_number,
                        })
                        print(f"    ✅ RBSD transaction added: {tx.hash} | Amount: {claim_amount} RBSD")
                    else:
                        print(f"    ❌ RBSD transaction skipped (no valid amount): {tx.hash}")
                
                else:
                    # This is a MON transaction (no JERRY or RBSD transfer logs)
                    print(f"    Categorizing as MON: {tx.hash}")
                    
                    # Extract MON data
                    bet_id = 0
                    claim_amount = 0
                    
                    for log in tx_logs:
                        if (log.address and log.address.lower() in [addr.lower() for addr in RBS_CONTRACT_ADDRESSES] and
                            log.topics and log.topics[0] and log.topics[0].lower() == CLAIM_EVENT_TOPIC.lower()):
                            bet_id = hex_to_int(log.topics[2]) if len(log.topics) >= 3 and log.topics[2] else 0
                            
                            # Extract claim amount from log data (first 32 bytes)
                            if log.data and len(log.data) >= 66:
                                data_hex = log.data[2:66]
                                try:
                                    claim_amount = hex_to_int(data_hex) / 1e18
                                    print(f"      Found claim amount: {claim_amount} MON from log data")
                                except (ValueError, TypeError):
                                    print(f"      Failed to parse claim amount from log data: {log.data}")
                            break
                    
                    if claim_amount > 0:
                        mon_transactions.append({
                            "timestamp": datetime.fromtimestamp(timestamp),
                            "tx_hash": tx.hash,
                            "from_address": tx.from_,
                            "to_address": tx.to,
                            "token": "MON",
                            "amount": claim_amount,
                            "bet_id": bet_id,
                            "block_number": tx.block_number,
                        })
        
        if response.next_block and response.next_block > current_block:
            current_block = response.next_block
        else:
            current_block += 500000

    print(f"Found {len(mon_transactions)} MON claiming transactions")
    print(f"Found {len(jerry_transactions)} JERRY claiming transactions")
    print(f"Found {len(rbsd_transactions)} RBSD claiming transactions")
    
    # Print all RBSD transaction hashes
    if rbsd_transactions:
        print(f"\n🔍 ALL RBSD TRANSACTION HASHES:")
        for i, tx in enumerate(rbsd_transactions, 1):
            print(f"  {i}. {tx['tx_hash']} | Amount: {tx['amount']} RBSD | Bet ID: {tx['bet_id']}")
    else:
        print(f"\n❌ No RBSD transactions found in this block range")
    
    return mon_transactions, jerry_transactions, rbsd_transactions

async def process_all_claiming_transactions(db: ComprehensiveClaimingDatabase, client: HypersyncClient, start_block: int = None, end_block: int = None):
    """Process all claiming transactions from start_block to end_block."""
    if start_block is None:
        start_block = db.get_last_processed_block()
        if start_block == 0:
            start_block = 0  # Start from block 0 for complete historical data
    
    if end_block is None:
        end_block = await client.get_height()
        print(f"Current blockchain height: {end_block}")
    else:
        print(f"Using specified end block: {end_block}")
    
    if start_block >= end_block:
        print(f"No new blocks to process (last processed: {start_block}, current: {end_block})")
        return 0
    
    print(f"Processing blocks {start_block} to {end_block}")
    
    # Fetch new data
    mon_data, jerry_data, rbsd_data = await fetch_all_claiming_transactions_fixed(client, start_block, end_block)
    
    all_tx_data = mon_data + jerry_data + rbsd_data
    
    if not all_tx_data:
        print("No new transactions found.")
        db.update_last_processed_block(end_block)
        return 0
    
    # Store transactions in database
    inserted_count = db.insert_transactions(all_tx_data)
    
    # Update checkpoint
    db.update_last_processed_block(end_block)
    
    return inserted_count

def save_to_database(mon_data: List[Dict[str, Any]], jerry_data: List[Dict[str, Any]], rbsd_data: List[Dict[str, Any]], db_path: str = "data/comprehensive_claiming_transactions_fixed.db"):
    """Save the fetched data to the database."""
    print(f"\n💾 SAVING TO DATABASE: {db_path}")
    print("=" * 50)
    
    # Initialize database
    db = ComprehensiveClaimingDatabase(db_path)
    
    # Combine all transactions
    all_transactions = mon_data + jerry_data + rbsd_data
    
    if not all_transactions:
        print("No transactions to save.")
        return
    
    # Insert into database
    inserted_count = db.insert_transactions(all_transactions)
    
    if inserted_count > 0:
        print(f"✅ Successfully inserted {inserted_count} new claiming transactions!")
        
        # Get database statistics
        stats = db.get_database_stats()
        
        print(f"\n📊 DATABASE STATISTICS:")
        print(f"Total transactions in database: {stats['total_transactions']}")
        print(f"Unique users: {stats['unique_users']}")
        
        if stats['token_stats']:
            print(f"\n💰 TOKEN BREAKDOWN:")
            for token, count, total_amount, avg_amount, min_amount, max_amount in stats['token_stats']:
                print(f"  {token}: {count} transactions, {total_amount:,.2f} total volume")
                print(f"    Average: {avg_amount:,.2f}, Range: {min_amount:,.2f} - {max_amount:,.2f}")
    else:
        print("No new transactions to insert (all were duplicates).")
    
    print("=" * 50)

def print_summary(mon_data: List[Dict[str, Any]], jerry_data: List[Dict[str, Any]], rbsd_data: List[Dict[str, Any]]):
    """Print a comprehensive summary of the retrieved data."""
    print(f"\n📊 DATA RETRIEVAL SUMMARY")
    print("=" * 50)
    
    # Basic counts
    print(f"MON Claiming Transactions: {len(mon_data)}")
    print(f"JERRY Claiming Transactions: {len(jerry_data)}")
    print(f"RBSD Claiming Transactions: {len(rbsd_data)}")
    print(f"Total Transactions: {len(mon_data) + len(jerry_data) + len(rbsd_data)}")
    
    # Volume by token
    mon_volume = sum(tx['amount'] for tx in mon_data)
    jerry_volume = sum(tx['amount'] for tx in jerry_data)
    rbsd_volume = sum(tx['amount'] for tx in rbsd_data)
    total_volume = mon_volume + jerry_volume + rbsd_volume
    
    print(f"\n💰 VOLUME SUMMARY:")
    print(f"Total Claim Volume: {total_volume:,.2f}")
    print(f"MON Claim Volume: {mon_volume:,.2f}")
    print(f"JERRY Claim Volume: {jerry_volume:,.2f}")
    print(f"RBSD Claim Volume: {rbsd_volume:,.2f}")
    
    # Transaction details
    if mon_data:
        print(f"\n🎯 MON CLAIMING DETAILS:")
        avg_mon_amount = mon_volume / len(mon_data) if mon_data else 0
        min_mon_amount = min(tx['amount'] for tx in mon_data)
        max_mon_amount = max(tx['amount'] for tx in mon_data)
        print(f"  Average Claim: {avg_mon_amount:,.2f} MON")
        print(f"  Min Claim: {min_mon_amount:,.2f} MON")
        print(f"  Max Claim: {max_mon_amount:,.2f} MON")
    
    if jerry_data:
        print(f"\n🎯 JERRY CLAIMING DETAILS:")
        avg_jerry_amount = jerry_volume / len(jerry_data) if jerry_data else 0
        min_jerry_amount = min(tx['amount'] for tx in jerry_data)
        max_jerry_amount = max(tx['amount'] for tx in jerry_data)
        print(f"  Average Claim: {avg_jerry_amount:,.2f} JERRY")
        print(f"  Min Claim: {min_jerry_amount:,.2f} JERRY")
        print(f"  Max Claim: {max_jerry_amount:,.2f} JERRY")
    
    if rbsd_data:
        print(f"\n🎯 RBSD CLAIMING DETAILS:")
        avg_rbsd_amount = rbsd_volume / len(rbsd_data) if rbsd_data else 0
        min_rbsd_amount = min(tx['amount'] for tx in rbsd_data)
        max_rbsd_amount = max(tx['amount'] for tx in rbsd_data)
        print(f"  Average Claim: {avg_rbsd_amount:,.2f} RBSD")
        print(f"  Min Claim: {min_rbsd_amount:,.2f} RBSD")
        print(f"  Max Claim: {max_rbsd_amount:,.2f} RBSD")
    
    # User activity
    all_transactions = mon_data + jerry_data + rbsd_data
    unique_users = len(set(tx['from_address'] for tx in all_transactions))
    print(f"\n👥 USER ACTIVITY:")
    print(f"Unique Claimers: {unique_users}")
    
    # Recent transactions (last 10)
    print(f"\n🕒 RECENT TRANSACTIONS:")
    recent_txs = sorted(all_transactions, key=lambda x: x['timestamp'], reverse=True)[:10]
    for i, tx in enumerate(recent_txs, 1):
        print(f"  {i}. {tx['tx_hash'][:10]}... | {tx['amount']:,.2f} {tx['token']} | Bet ID: {tx['bet_id']}")
    
    print("=" * 50)

async def main():
    """Main function for claiming database system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claiming Database System")
    parser.add_argument("--incremental", action="store_true", help="Only fetch new data")
    parser.add_argument("--start-block", type=int, help="Start from specific block")
    parser.add_argument("--end-block", type=int, help="End at specific block (defaults to current height)")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    args = parser.parse_args()
    
    # Initialize database
    db = ComprehensiveClaimingDatabase(db_path="data/comprehensive_claiming_transactions_fixed.db")
    
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
            for token, count, total_volume, avg_amount, min_amount, max_amount in stats['token_stats']:
                print(f"  {token}: {count:,} txs, {total_volume:,.2f} volume, {avg_amount:.4f} avg")
            return
        
        if args.start_block is not None:
            start_block = args.start_block
        elif args.incremental:
            start_block = db.get_last_processed_block()
        else:
            start_block = 0  # Start from beginning
        
        print(f"Starting data processing from block {start_block}")
        
        # Process and store data
        inserted_count = await process_all_claiming_transactions(db, client, start_block, args.end_block)
        
        if inserted_count > 0:
            print(f"\nProcessing complete! Inserted {inserted_count} new transactions.")
            
            # Show database stats
            stats = db.get_database_stats()
            print(f"\nDatabase Statistics:")
            print(f"Total Transactions: {stats['total_transactions']:,}")
            print(f"Unique Users: {stats['unique_users']:,}")
            print(f"Token Distribution:")
            for token, count, total_volume, avg_amount, min_amount, max_amount in stats['token_stats']:
                print(f"  {token}: {count:,} txs, {total_volume:,.2f} volume, {avg_amount:.4f} avg")
        else:
            print("No new data to process.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 