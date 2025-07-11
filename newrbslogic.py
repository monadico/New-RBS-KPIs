import asyncio
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any

from hypersync import HypersyncClient, ClientConfig, TransactionSelection, LogSelection, FieldSelection, Query
from hypersync import LogField, TransactionField

# --- Configuration ---
load_dotenv()
MONAD_HYPERSYNC_URL = os.getenv("MONAD_HYPERSYNC_URL", "https://monad-testnet.hypersync.xyz")
HYPERSYNC_BEARER_TOKEN = os.getenv("HYPERSYNC_BEARER_TOKEN")

# =================================================================================
# === BLOCK RANGE
# =================================================================================
START_BLOCK = 25358800
# END_BLOCK is determined dynamically.
# =================================================================================


# --- SQL Query Constants ---
CONTRACT_ADDRESSES_1 = ['0x3ad50059d6008b711209a509fe58e68f0b672a42', '0x740990cb01e893a371a050736c62ae0b779109e7']
SIG_HASH_1 = '0x5029defb'

CONTRACT_ADDRESS_2_TX_TO = '0x740990cb01e893a371a050736c62ae0b779109e7'
CONTRACT_ADDRESS_2_LOG_A = '0xda054a96254776346386060c480b42a10c870cd2'
CONTRACT_ADDRESS_2_LOG_B = '0x740990cb01e893a371a050736c62ae0b779109e7'
SIG_HASH_2 = '0xb65c106f'
TOPIC_0_LOG_A = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
CARDS_LOG_TOPIC_0 = '0xefc52bf7792453af1461fa9a7097486359b41a048898b6d542c0f03389487187'

# --- Helper Functions ---

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


def calculate_user_engagement_metrics(all_tx_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Calculates user engagement metrics including new users and active users per week.
    
    Returns:
        DataFrame with columns: time, new_users, active_users, cumulative_new_users
    """
    if not all_tx_data:
        return pd.DataFrame()
    
    # Create DataFrame from transaction data
    df = pd.DataFrame(all_tx_data)
    
    # Create weekly time periods
    df['time'] = df['block_timestamp'].dt.to_period('W').dt.to_timestamp()
    
    # Find first interaction date for each address
    first_interaction = df.groupby('origin_from_address')['block_timestamp'].min().reset_index()
    first_interaction['time'] = first_interaction['block_timestamp'].dt.to_period('W').dt.to_timestamp()
    
    # Calculate active users per week (distinct addresses)
    active_users_weekly = df.groupby('time')['origin_from_address'].nunique().reset_index()
    active_users_weekly.columns = ['time', 'active_users']
    
    # Calculate new users per week (first-time addresses)
    new_users_weekly = first_interaction.groupby('time')['origin_from_address'].nunique().reset_index()
    new_users_weekly.columns = ['time', 'new_users']
    
    # Merge active and new users data
    user_metrics = pd.merge(active_users_weekly, new_users_weekly, on='time', how='outer').fillna(0)
    
    # Sort by time and calculate cumulative new users
    user_metrics = user_metrics.sort_values('time')
    user_metrics['cumulative_new_users'] = user_metrics['new_users'].cumsum()
    
    # Convert to int for cleaner display
    user_metrics['active_users'] = user_metrics['active_users'].astype(int)
    user_metrics['new_users'] = user_metrics['new_users'].astype(int)
    user_metrics['cumulative_new_users'] = user_metrics['cumulative_new_users'].astype(int)
    
    return user_metrics.set_index('time')


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
                    "block_timestamp": datetime.fromtimestamp(timestamp),
                })
        
        if response.next_block and response.next_block > current_block:
            current_block = response.next_block
        else:
            # No more blocks to process in this query or reached the end
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
                    topics=[[TOPIC_0_LOG_A]]  # Transfer event signature
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

            # Process transactions that have logs from both addresses
            for tx_hash, tx_logs in logs_by_tx_hash.items():
                # Check if this transaction has logs from both addresses
                has_jerry_log = any(log.address.lower() == CONTRACT_ADDRESS_2_LOG_A.lower() for log in tx_logs)
                has_rarebet_log = any(log.address.lower() == CONTRACT_ADDRESS_2_LOG_B.lower() for log in tx_logs)
                
                if has_jerry_log and has_rarebet_log:
                    # Find the transaction object
                    tx = next((t for t in response.data.transactions if t.hash == tx_hash), None)
                    if not tx or tx.status != 1:
                        continue
                    
                    # Ensure we are only processing transactions with the correct function signature.
                    if not tx.input or not tx.input.startswith(SIG_HASH_2):
                        continue

                    timestamp = block_timestamp_map.get(tx.block_number)
                    if not timestamp:
                        continue
                    
                    # Get the Jerry token log for bet amount
                    jerry_log = next((log for log in tx_logs if log.address.lower() == CONTRACT_ADDRESS_2_LOG_A.lower()), None)
                    
                    print(f"  ✅ MATCH! Transaction {tx.hash} has both Jerry and Rarebet logs")
                    
                    # --- Card Counting Logic ---
                    # Find the specific log by its topic hash in topics[0].
                    card_event_log = next((
                        log for log in tx_logs
                        if log.address.lower() == CONTRACT_ADDRESS_2_LOG_B.lower()
                        and log.topics and log.topics[0] and log.topics[0].lower() == CARDS_LOG_TOPIC_0.lower()
                    ), None)

                    cards_in_slip = 0
                    bet_id_decoded = 0
                    if card_event_log and card_event_log.data:
                        # The number of cards is the fourth 32-byte word in the data field.
                        data_hex = card_event_log.data[2:] if card_event_log.data.startswith('0x') else card_event_log.data
                        
                        start_index = 192  # 3 * 64
                        end_index = start_index + 64
                        
                        if len(data_hex) >= end_index:
                            card_count_hex = data_hex[start_index:end_index]
                            cards_in_slip = hex_to_int(card_count_hex)
                        
                        # The bet ID is in the topics of this same log.
                        if len(card_event_log.topics) >= 3:
                            bet_id_decoded = hex_to_int(card_event_log.topics[2])

                    all_tx_data.append({
                        "bet_amt": hex_to_int(jerry_log.data) / 1e18 if jerry_log and jerry_log.data else 0,
                        "betting_token": "Jerry",
                        "cards_in_slip": cards_in_slip,
                        "bet_id_decoded": bet_id_decoded,
                        "tx_hash": tx.hash,
                        "origin_from_address": tx.from_,
                        "block_timestamp": datetime.fromtimestamp(timestamp),
                    })
        
        if response.next_block and response.next_block > current_block:
            current_block = response.next_block
        else:
            break

    print(f"Part 2 Complete: Found {len(all_tx_data)} total transactions.")
    return all_tx_data


async def main():
    """Main function to fetch, process, and aggregate data."""
    if not HYPERSYNC_BEARER_TOKEN:
        print("Error: HYPERSYNC_BEARER_TOKEN environment variable not set.")
        return

    client_config = ClientConfig(url=MONAD_HYPERSYNC_URL, bearer_token=HYPERSYNC_BEARER_TOKEN)
    client = HypersyncClient(client_config)

    end_block = await client.get_height()
    print(f"Latest block height found: {end_block}")

    start_block = START_BLOCK
    
    if start_block >= end_block:
        print(f"Start block ({start_block}) is ahead of the current chain height ({end_block}). Nothing to query.")
        return
        
    print(f"Querying from block {start_block} to {end_block}")

    part1_data, part2_data = await asyncio.gather(
        fetch_data_part1(client, start_block, end_block),
        fetch_data_part2(client, start_block, end_block)
    )

    all_tx = part1_data + part2_data
    if not all_tx:
        print("\nNo transactions found for the given criteria. The script will now exit.")
        return

    pd.set_option('display.max_columns', None)
    print("\nPerforming final aggregation...")
    df = pd.DataFrame(all_tx)
    df['time'] = df['block_timestamp'].dt.to_period('W').dt.to_timestamp()

    df['mon_volume'] = df['bet_amt'].where(df['betting_token'] == 'MON', 0)
    df['jerry_volume'] = df['bet_amt'].where(df['betting_token'] == 'Jerry', 0)

    # Calculate user engagement metrics
    print("Calculating user engagement metrics...")
    user_metrics = calculate_user_engagement_metrics(all_tx)

    agg_df = df.groupby('time').agg(
        users=('origin_from_address', lambda x: x.nunique()),
        submission_txs=('tx_hash', 'nunique'),
        total_cards=('cards_in_slip', 'sum'),
        avg_cards=('cards_in_slip', 'mean'),
        mon_volume=('mon_volume', 'sum'),
        jerry_volume=('jerry_volume', 'sum')
    ).sort_values(by='time', ascending=False)

    # Merge user engagement metrics with existing aggregation
    agg_df = pd.merge(agg_df, user_metrics, left_index=True, right_index=True, how='outer').fillna(0)

    agg_df['cumulative_txs'] = agg_df['submission_txs'].iloc[::-1].cumsum()[::-1]
    agg_df['cumulative_cards'] = agg_df['total_cards'].iloc[::-1].cumsum()[::-1]
    agg_df['cumulative_mon_volume'] = agg_df['mon_volume'].iloc[::-1].cumsum()[::-1]
    agg_df['cumulative_jerry_volume'] = agg_df['jerry_volume'].iloc[::-1].cumsum()[::-1]
    
    final_df = agg_df.rename(columns={
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

    final_df = final_df[[
        'users', 'Active Users', 'New Users', 'Cumulative New Users',
        'Submission txs', 'Cumulative txs', 
        'avg_cards', 'total_cards', 'Cumulative cards',
        'MON Volume', 'Cumulative MON Volume', 
        'JERRY Volume', 'Cumulative JERRY Volume'
    ]]

    print("\n--- KPI Dashboard Data ---")
    print(final_df)


if __name__ == "__main__":
    asyncio.run(main())