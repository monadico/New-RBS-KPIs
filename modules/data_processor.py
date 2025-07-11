#!/usr/bin/env python3
"""
Data processor for betting analytics.
Combines data fetching from Hypersync with database storage and hourly aggregation.
"""

import asyncio
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any

from hypersync import HypersyncClient, ClientConfig, TransactionSelection, LogSelection, FieldSelection, Query
from hypersync import LogField, TransactionField
from database import get_db_instance

# --- Configuration ---
load_dotenv()
MONAD_HYPERSYNC_URL = os.getenv("MONAD_HYPERSYNC_URL", "https://monad-testnet.hypersync.xyz")
HYPERSYNC_BEARER_TOKEN = os.getenv("HYPERSYNC_BEARER_TOKEN")

# --- Constants from newrbslogic.py ---
CONTRACT_ADDRESSES_1 = ['0x3ad50059d6008b711209a509fe58e68f0b672a42', '0x740990cb01e893a371a050736c62ae0b779109e7']
SIG_HASH_1 = '0x5029defb'

CONTRACT_ADDRESS_2_TX_TO = '0x740990cb01e893a371a050736c62ae0b779109e7'
CONTRACT_ADDRESS_2_LOG_A = '0xda054a96254776346386060c480b42a10c870cd2'
CONTRACT_ADDRESS_2_LOG_B = '0x740990cb01e893a371a050736c62ae0b779109e7'
SIG_HASH_2 = '0xb65c106f'
TOPIC_0_LOG_A = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
CARDS_LOG_TOPIC_0 = '0xefc52bf7792453af1461fa9a7097486359b41a048898b6d542c0f03389487187'

# --- Helper Functions (copied from newrbslogic.py) ---

def hex_to_int(hex_str: str) -> int:
    if not hex_str:
        return 0
    return int(hex_str, 16)


def calculate_cards_in_slip_from_tx(tx_input: str) -> int:
    """
    Calculates the number of cards in a slip from the transaction input data.
    For MON transactions (sighash 0x5029defb), the card count is the second
    parameter in the input data, which represents the length of the card array.
    """
    start_index = 74
    end_index = start_index + 64

    if not tx_input or len(tx_input) < end_index:
        return 0

    card_count_hex = tx_input[start_index:end_index]
    
    try:
        card_count = int(card_count_hex, 16)
        if card_count > 1_000_000:
            return 0
        return card_count
    except (ValueError, TypeError):
        return 0


def calculate_user_engagement_metrics(all_tx_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Calculates user engagement metrics including new users and active users per hour.
    
    Returns:
        DataFrame with columns: time, new_users, active_users, cumulative_new_users
    """
    if not all_tx_data:
        return pd.DataFrame()
    
    # Create DataFrame from transaction data
    df = pd.DataFrame(all_tx_data)
    
    # Create hourly time periods
    df['time'] = df['block_timestamp'].dt.floor('H')
    
    # Find first interaction date for each address
    first_interaction = df.groupby('origin_from_address')['block_timestamp'].min().reset_index()
    first_interaction['time'] = first_interaction['block_timestamp'].dt.floor('H')
    
    # Calculate active users per hour (distinct addresses)
    active_users_hourly = df.groupby('time')['origin_from_address'].nunique().reset_index()
    active_users_hourly.columns = ['time', 'active_users']
    
    # Calculate new users per hour (first-time addresses)
    new_users_hourly = first_interaction.groupby('time')['origin_from_address'].nunique().reset_index()
    new_users_hourly.columns = ['time', 'new_users']
    
    # Merge active and new users data
    user_metrics = pd.merge(active_users_hourly, new_users_hourly, on='time', how='outer').fillna(0)
    
    # Sort by time and calculate cumulative new users
    user_metrics = user_metrics.sort_values('time')
    user_metrics['cumulative_new_users'] = user_metrics['new_users'].cumsum()
    
    # Convert to int for cleaner display
    user_metrics['active_users'] = user_metrics['active_users'].astype(int)
    user_metrics['new_users'] = user_metrics['new_users'].astype(int)
    user_metrics['cumulative_new_users'] = user_metrics['cumulative_new_users'].astype(int)
    
    return user_metrics.set_index('time')


# --- Data Fetching Functions (adapted from newrbslogic.py) ---

async def fetch_data_part1(client: HypersyncClient, start_block: int, end_block: int) -> List[Dict[str, Any]]:
    """Fetches data based on the first SELECT statement, now with pagination."""
    print(f"Starting Part 1: Fetching transactions with MON bets from {start_block} to {end_block}.")
    
    all_tx_data = []
    current_block = start_block

    while current_block < end_block:
        print(f"Part 1: Querying from block {current_block}...")
        query = Query(
            from_block=current_block,
            to_block=end_block,
            transactions=[TransactionSelection(
                to=CONTRACT_ADDRESSES_1,
                sighash=[SIG_HASH_1]
            )],
            include_all_blocks=False,
            field_selection=FieldSelection(
                block=['timestamp', 'number'],
                transaction=['hash', 'from', 'value', 'input', 'status', 'block_number'],
                log=['topics', 'transaction_hash']
            )
        )

        response = await client.get(query)

        if response.data:
            block_timestamp_map = {
                b.number: hex_to_int(b.timestamp)
                for b in response.data.blocks if b.number and b.timestamp
            }

            for tx in response.data.transactions:
                if tx.status != 1:
                    continue

                timestamp = block_timestamp_map.get(tx.block_number)
                if not timestamp:
                    continue

                cards_in_slip = calculate_cards_in_slip_from_tx(tx.input)

                bet_id_decoded = 0
                if response.data.logs:
                    for log in response.data.logs:
                        if log.transaction_hash == tx.hash and len(log.topics) >= 3:
                            bet_id_decoded = hex_to_int(log.topics[2])
                            break
                
                all_tx_data.append({
                    "bet_amt": hex_to_int(tx.value) / 1e18,
                    "betting_token": "MON",
                    "cards_in_slip": cards_in_slip,
                    "bet_id_decoded": bet_id_decoded,
                    "tx_hash": tx.hash,
                    "origin_from_address": tx.from_,
                    "block_number": tx.block_number,
                    "block_timestamp": datetime.fromtimestamp(timestamp),
                })
        
        if response.next_block and response.next_block > current_block:
            current_block = response.next_block
        else:
            break

    print(f"Part 1 Complete: Found {len(all_tx_data)} total transactions.")
    return all_tx_data


async def fetch_data_part2(client: HypersyncClient, start_block: int, end_block: int) -> List[Dict[str, Any]]:
    """Fetches data based on the second SELECT statement, now with pagination."""
    print(f"Starting Part 2: Fetching transactions with Jerry bets from {start_block} to {end_block}.")
    
    all_tx_data = []
    current_block = start_block
    
    while current_block < end_block:
        print(f"Part 2: Querying from block {current_block}...")
        query = Query(
            from_block=current_block,
            to_block=end_block,
            transactions=[TransactionSelection(
                sighash=[SIG_HASH_2]
            )],
            logs=[
                LogSelection(
                    address=[CONTRACT_ADDRESS_2_LOG_A],
                    topics=[[TOPIC_0_LOG_A]]
                ),
                LogSelection(address=[CONTRACT_ADDRESS_2_LOG_B])
            ],
            include_all_blocks=False,
            field_selection=FieldSelection(
                block=['timestamp', 'number'],
                transaction=['hash', 'from', 'status', 'block_number', TransactionField.INPUT],
                log=[
                    LogField.ADDRESS, 
                    LogField.TOPIC0, 
                    LogField.TOPIC1, 
                    LogField.TOPIC2, 
                    LogField.TOPIC3, 
                    LogField.DATA, 
                    LogField.TRANSACTION_HASH
                ]
            )
        )

        response = await client.get(query)

        if response.data:
            block_timestamp_map = {
                b.number: hex_to_int(b.timestamp)
                for b in response.data.blocks if b.number and b.timestamp
            }

            logs_by_tx_hash = {}
            for log in response.data.logs:
                if log.transaction_hash not in logs_by_tx_hash:
                    logs_by_tx_hash[log.transaction_hash] = []
                logs_by_tx_hash[log.transaction_hash].append(log)

            for tx_hash, tx_logs in logs_by_tx_hash.items():
                has_jerry_log = any(log.address.lower() == CONTRACT_ADDRESS_2_LOG_A.lower() for log in tx_logs)
                has_rarebet_log = any(log.address.lower() == CONTRACT_ADDRESS_2_LOG_B.lower() for log in tx_logs)
                
                if has_jerry_log and has_rarebet_log:
                    tx = next((t for t in response.data.transactions if t.hash == tx_hash), None)
                    if not tx or tx.status != 1:
                        continue
                    
                    if not tx.input or not tx.input.startswith(SIG_HASH_2):
                        continue

                    timestamp = block_timestamp_map.get(tx.block_number)
                    if not timestamp:
                        continue
                    
                    jerry_log = next((log for log in tx_logs if log.address.lower() == CONTRACT_ADDRESS_2_LOG_A.lower()), None)
                    
                    card_event_log = next((
                        log for log in tx_logs
                        if log.address.lower() == CONTRACT_ADDRESS_2_LOG_B.lower()
                        and log.topics and log.topics[0] and log.topics[0].lower() == CARDS_LOG_TOPIC_0.lower()
                    ), None)

                    cards_in_slip = 0
                    bet_id_decoded = 0
                    if card_event_log and card_event_log.data:
                        data_hex = card_event_log.data[2:] if card_event_log.data.startswith('0x') else card_event_log.data
                        start_index = 192
                        end_index = start_index + 64
                        
                        if len(data_hex) >= end_index:
                            card_count_hex = data_hex[start_index:end_index]
                            cards_in_slip = hex_to_int(card_count_hex)
                        
                        if len(card_event_log.topics) >= 3:
                            bet_id_decoded = hex_to_int(card_event_log.topics[2])

                    all_tx_data.append({
                        "bet_amt": hex_to_int(jerry_log.data) / 1e18 if jerry_log and jerry_log.data else 0,
                        "betting_token": "Jerry",
                        "cards_in_slip": cards_in_slip,
                        "bet_id_decoded": bet_id_decoded,
                        "tx_hash": tx.hash,
                        "origin_from_address": tx.from_,
                        "block_number": tx.block_number,
                        "block_timestamp": datetime.fromtimestamp(timestamp),
                    })
        
        if response.next_block and response.next_block > current_block:
            current_block = response.next_block
        else:
            break

    print(f"Part 2 Complete: Found {len(all_tx_data)} total transactions.")
    return all_tx_data


# --- New ETL Functions ---

async def fetch_and_store_incremental_data(db, client: HypersyncClient, start_block: int = None) -> int:
    """
    Fetch new data incrementally and store in database.
    Returns the number of new transactions processed.
    """
    # Get last processed block if start_block not provided
    if start_block is None:
        start_block = db.get_last_processed_block()
        if start_block == 0:
            # If no checkpoint, use the original start block from newrbslogic.py
            start_block = 25358800
    
    # Get current blockchain height
    end_block = await client.get_height()
    print(f"Current blockchain height: {end_block}")
    
    if start_block >= end_block:
        print(f"No new blocks to process (last processed: {start_block}, current: {end_block})")
        return 0
    
    print(f"Processing blocks {start_block} to {end_block}")
    
    # Fetch new data
    part1_data, part2_data = await asyncio.gather(
        fetch_data_part1(client, start_block, end_block),
        fetch_data_part2(client, start_block, end_block)
    )
    
    all_tx_data = part1_data + part2_data
    
    if not all_tx_data:
        print("No new transactions found.")
        db.update_last_processed_block(end_block)
        return 0
    
    # Store transactions in database
    inserted_count = db.insert_transactions(all_tx_data)
    
    # Update checkpoint
    db.update_last_processed_block(end_block)
    
    print(f"Successfully processed {inserted_count} new transactions from {len(all_tx_data)} total found")
    return inserted_count


def calculate_and_store_hourly_metrics(db):
    """
    Calculate hourly metrics from stored transactions and save to database.
    """
    print("Calculating hourly metrics...")
    
    # Get all transactions from database
    df = db.get_all_transactions()
    
    if df.empty:
        print("No transactions found in database for metrics calculation.")
        return
    
    # Create hourly time periods
    df['time'] = df['block_timestamp'].dt.floor('H')
    
    # Calculate volume metrics
    df['mon_volume'] = df['bet_amt'].where(df['betting_token'] == 'MON', 0)
    df['jerry_volume'] = df['bet_amt'].where(df['betting_token'] == 'Jerry', 0)
    
    # Calculate user engagement metrics
    user_metrics = calculate_user_engagement_metrics(df.to_dict('records'))
    
    # Basic hourly aggregation
    hourly_agg = df.groupby('time').agg(
        users=('origin_from_address', lambda x: x.nunique()),
        submission_txs=('tx_hash', 'nunique'),
        total_cards=('cards_in_slip', 'sum'),
        avg_cards=('cards_in_slip', 'mean'),
        mon_volume=('mon_volume', 'sum'),
        jerry_volume=('jerry_volume', 'sum')
    ).fillna(0)
    
    # Merge with user engagement metrics
    if not user_metrics.empty:
        hourly_agg = pd.merge(hourly_agg, user_metrics, left_index=True, right_index=True, how='outer').fillna(0)
    else:
        # Add empty user metrics columns
        hourly_agg['active_users'] = 0
        hourly_agg['new_users'] = 0
        hourly_agg['cumulative_new_users'] = 0
    
    # Calculate cumulative metrics
    hourly_agg = hourly_agg.sort_index()
    hourly_agg['cumulative_txs'] = hourly_agg['submission_txs'].cumsum()
    hourly_agg['cumulative_cards'] = hourly_agg['total_cards'].cumsum()
    hourly_agg['cumulative_mon_volume'] = hourly_agg['mon_volume'].cumsum()
    hourly_agg['cumulative_jerry_volume'] = hourly_agg['jerry_volume'].cumsum()
    
    # Save to database
    db.upsert_hourly_metrics(hourly_agg)
    
    print(f"Calculated and stored hourly metrics for {len(hourly_agg)} hours")


def get_hourly_dashboard_data(db) -> pd.DataFrame:
    """
    Get formatted hourly dashboard data.
    """
    hourly_metrics = db.get_hourly_metrics()
    
    if hourly_metrics.empty:
        return pd.DataFrame()
    
    # Rename columns for display
    final_df = hourly_metrics.rename(columns={
        "submission_txs": "Submission txs",
        "cumulative_txs": "Cumulative txs",
        "avg_cards": "avg_cards",
        "total_cards": "total_cards",
        "cumulative_cards": "Cumulative cards",
        "mon_volume": "MON Volume",
        "jerry_volume": "JERRY Volume",
        "cumulative_mon_volume": "Cumulative MON Volume",
        "cumulative_jerry_volume": "Cumulative JERRY Volume",
        "active_users": "Active Users",
        "new_users": "New Users",
        "cumulative_new_users": "Cumulative New Users"
    })
    
    # Select columns for display
    display_columns = [
        'users', 'Active Users', 'New Users', 'Cumulative New Users',
        'Submission txs', 'Cumulative txs', 
        'avg_cards', 'total_cards', 'Cumulative cards',
        'MON Volume', 'Cumulative MON Volume', 
        'JERRY Volume', 'Cumulative JERRY Volume'
    ]
    
    return final_df[display_columns]


# --- Main Processing Functions ---

async def run_full_etl():
    """Run the complete ETL process: Extract, Transform, Load."""
    if not HYPERSYNC_BEARER_TOKEN:
        print("Error: HYPERSYNC_BEARER_TOKEN environment variable not set.")
        return
    
    # Initialize database and client
    db = get_db_instance()
    client_config = ClientConfig(url=MONAD_HYPERSYNC_URL, bearer_token=HYPERSYNC_BEARER_TOKEN)
    client = HypersyncClient(client_config)
    
    print("=== STARTING ETL PROCESS ===")
    
    # Step 1: Fetch and store new transaction data
    new_tx_count = await fetch_and_store_incremental_data(db, client)
    
    # Step 2: Calculate and store hourly metrics
    if new_tx_count > 0:
        calculate_and_store_hourly_metrics(db)
    
    # Step 3: Display results
    print("\n=== HOURLY DASHBOARD DATA ===")
    dashboard_df = get_hourly_dashboard_data(db)
    
    if not dashboard_df.empty:
        pd.set_option('display.max_columns', None)
        print(dashboard_df.head(24))  # Show last 24 hours
    else:
        print("No data available for dashboard.")
    
    print(f"\n=== ETL PROCESS COMPLETE ===")
    print(f"New transactions processed: {new_tx_count}")


async def run_incremental_update():
    """Run incremental update (for regular scheduled runs)."""
    if not HYPERSYNC_BEARER_TOKEN:
        print("Error: HYPERSYNC_BEARER_TOKEN environment variable not set.")
        return
    
    db = get_db_instance()
    client_config = ClientConfig(url=MONAD_HYPERSYNC_URL, bearer_token=HYPERSYNC_BEARER_TOKEN)
    client = HypersyncClient(client_config)
    
    print("=== INCREMENTAL UPDATE ===")
    
    # Fetch only new data
    new_tx_count = await fetch_and_store_incremental_data(db, client)
    
    if new_tx_count > 0:
        # Recalculate metrics
        calculate_and_store_hourly_metrics(db)
        print(f"Updated with {new_tx_count} new transactions")
    else:
        print("No new transactions to process")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "incremental":
        asyncio.run(run_incremental_update())
    else:
        asyncio.run(run_full_etl()) 