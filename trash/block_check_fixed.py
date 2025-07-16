#!/usr/bin/env python3
"""
Fixed Block Check - Separate queries for MON and Jerry transactions
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from hypersync import HypersyncClient, ClientConfig, Query, FieldSelection, BlockField, TransactionField, TransactionSelection, LogSelection, LogField

load_dotenv()
MONAD_HYPERSYNC_URL = os.getenv("MONAD_HYPERSYNC_URL", "https://monad-testnet.hypersync.xyz")
HYPERSYNC_BEARER_TOKEN = os.getenv("HYPERSYNC_BEARER_TOKEN")

tx_hash = '0x460c4057e98c2f6185cf7945022b8ad8d6b75eb59ebc32c443c7f0aa78f9a611'

def hex_to_int(hex_str: str) -> int:
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
    """
    Calculate cards in slip using the exact same logic as the SQL query.
    SQL: ((LENGTH(RIGHT(data, LENGTH(data) - 194)) / 64) - 1)
    """
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

def analyze_target_transaction(tx, block_timestamp=None, logs=None, token_type="Unknown"):
    """Analyze the target transaction and extract all relevant data."""
    print(f"\n=== DETAILED ANALYSIS OF TARGET TRANSACTION ===")
    print(f"Transaction Hash: {tx.hash}")
    print(f"Block Number: {tx.block_number}")
    print(f"From Address: {tx.from_}")
    print(f"To Address: {tx.to}")
    print(f"Transaction Status: {tx.status}")
    print(f"Token Type: {token_type}")
    
    if block_timestamp:
        print(f"Block Timestamp: {datetime.fromtimestamp(block_timestamp)}")
    
    # Calculate bet amount based on token type
    bet_amt = 0
    cards_in_slip = 0
    bet_id_decoded = 0
    
    # Analyze input data
    print(f"Input Data Length: {len(tx.input)} characters")
    print(f"Input Data: {tx.input}")
    
    if token_type == "MON":
        # MON: Use transaction value for bet amount
        bet_amt = hex_to_int(tx.value) / 1e18 if tx.value else 0
        print(f"Bet Amount (MON): {bet_amt}")
        # MON: Use original MON calculation method
        cards_in_slip = calculate_cards_in_slip_from_tx(tx.input)
        print(f"Cards in Slip (MON): {cards_in_slip}")
        
        # Get bet_id_decoded from logs
        if logs:
            for log in logs:
                if log.transaction_hash == tx.hash and len(log.topics) >= 3:
                    bet_id_decoded = hex_to_int(log.topics[2])
                    break
        print(f"Bet ID Decoded: {bet_id_decoded}")
        
    elif token_type == "Jerry":
        # Jerry: Use log data calculation
        if logs:
            # Get the Jerry token log for bet amount
            jerry_log = next((log for log in logs if log.address.lower() == '0xda054a96254776346386060c480b42a10c870cd2'), None)
            if jerry_log and jerry_log.data:
                bet_amt = hex_to_int(jerry_log.data) / 1e18
                print(f"Bet Amount (Jerry): {bet_amt}")
                print(f"Jerry Log Data: {jerry_log.data}")
            
            # Find the card event log
            card_event_log = next((
                log for log in logs
                if log.address.lower() == '0x740990cb01e893a371a050736c62ae0b779109e7'
                and log.topics and log.topics[0] and log.topics[0].lower() == '0xefc52bf7792453af1461fa9a7097486359b41a048898b6d542c0f03389487187'
            ), None)
            
            if card_event_log and card_event_log.data:
                print(f"Card Event Log Data: {card_event_log.data}")
                # Calculate cards in slip using SQL-style logic
                cards_in_slip = calculate_cards_in_slip_sql_style(card_event_log.data)
                print(f"Cards in Slip (Jerry): {cards_in_slip}")
                
                # Get bet_id_decoded from the same log
                if len(card_event_log.topics) >= 3:
                    bet_id_decoded = hex_to_int(card_event_log.topics[2])
                    print(f"Bet ID Decoded: {bet_id_decoded}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Transaction: {tx.hash}")
    print(f"From Address: {tx.from_}")
    print(f"To Address: {tx.to}")
    print(f"Block Timestamp: {datetime.fromtimestamp(block_timestamp) if block_timestamp else 'Unknown'}")
    print(f"Token: {token_type}")
    print(f"Amount: {bet_amt}")
    print(f"Cards: {cards_in_slip}")
    print(f"Bet ID: {bet_id_decoded}")
    print(f"Status: {'Success' if tx.status == 1 else 'Failed' if tx.status == 0 else 'Unknown'}")

async def query_mon_transactions(client):
    """Query specifically for MON transactions."""
    print(f"\n=== QUERYING MON TRANSACTIONS ===")
    
    query = Query(
        from_block=25634134,
        to_block=await client.get_height(),
        transactions=[TransactionSelection(
            sighash=['0x5029defb'],  # MON function signature
            to=['0x3ad50059d6008b711209a509fe58e68f0b672a42', '0x740990cb01e893a371a050736c62ae0b779109e7']  # RBS contract addresses
        )],
        field_selection=FieldSelection(
            block=[BlockField.NUMBER, BlockField.TIMESTAMP],
            transaction=[
                TransactionField.HASH,
                TransactionField.FROM,
                TransactionField.TO,
                TransactionField.VALUE,
                TransactionField.INPUT,
                TransactionField.STATUS,
                TransactionField.BLOCK_NUMBER,
            ],
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
    return response

async def query_jerry_transactions(client):
    """Query specifically for Jerry transactions with proper AND logic."""
    print(f"\n=== QUERYING JERRY TRANSACTIONS ===")
    
    # Step 1: Query for transactions with Jerry function signature
    print("Step 1: Querying transactions with Jerry function signature...")
    query1 = Query(
        from_block=25634134,
        to_block=await client.get_height(),
        transactions=[TransactionSelection(
            sighash=['0xb65c106f'],  # Jerry function signature
            to=['0x740990cb01e893a371a050736c62ae0b779109e7']  # Jerry contract address
        )],
        field_selection=FieldSelection(
            block=[BlockField.NUMBER, BlockField.TIMESTAMP],
            transaction=[
                TransactionField.HASH,
                TransactionField.FROM,
                TransactionField.TO,
                TransactionField.VALUE,
                TransactionField.INPUT,
                TransactionField.STATUS,
                TransactionField.BLOCK_NUMBER,
            ],
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
    
    response1 = await client.get(query1)
    
    if not response1.data or not response1.data.transactions:
        print("No transactions with Jerry function signature found")
        return response1
    
    print(f"Found {len(response1.data.transactions)} transactions with Jerry function signature")
    
    # Step 2: Query for transactions with Jerry logs
    print("Step 2: Querying transactions with Jerry logs...")
    query2 = Query(
        from_block=25634134,
        to_block=await client.get_height(),
        logs=[
            LogSelection(
                address=['0xda054a96254776346386060c480b42a10c870cd2'],  # Jerry token address
                topics=[['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']]  # Transfer event
            ),
            LogSelection(
                address=['0x740990cb01e893a371a050736c62ae0b779109e7'],  # Rarebet logs
                topics=[['0xefc52bf7792453af1461fa9a7097486359b41a048898b6d542c0f03389487187']]  # Card event
            )
        ],
        field_selection=FieldSelection(
            block=[BlockField.NUMBER, BlockField.TIMESTAMP],
            transaction=[
                TransactionField.HASH,
                TransactionField.FROM,
                TransactionField.TO,
                TransactionField.VALUE,
                TransactionField.INPUT,
                TransactionField.STATUS,
                TransactionField.BLOCK_NUMBER,
            ],
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
    
    response2 = await client.get(query2)
    
    if not response2.data or not response2.data.transactions:
        print("No transactions with Jerry logs found")
        return response1  # Return empty result
    
    print(f"Found {len(response2.data.transactions)} transactions with Jerry logs")
    
    # Step 3: Client-side filtering - find intersection
    print("Step 3: Finding intersection (transactions with BOTH Jerry function AND Jerry logs)...")
    
    # Get transaction hashes from both queries
    jerry_function_txs = {tx.hash for tx in response1.data.transactions}
    jerry_logs_txs = {tx.hash for tx in response2.data.transactions}
    
    # Find intersection
    intersection_txs = jerry_function_txs.intersection(jerry_logs_txs)
    
    print(f"Intersection: {len(intersection_txs)} transactions have both Jerry function AND Jerry logs")
    
    # Filter transactions and logs to only include intersection
    filtered_transactions = [tx for tx in response1.data.transactions if tx.hash in intersection_txs]
    filtered_logs = [log for log in response2.data.logs if log.transaction_hash in intersection_txs]
    
    # Create a simple response-like object with filtered data
    # Since we can't create proper Response objects, we'll return the filtered data directly
    class FilteredResponse:
        def __init__(self, data):
            self.data = data
    
    class FilteredResponseData:
        def __init__(self, blocks, transactions, logs):
            self.blocks = blocks
            self.transactions = transactions
            self.logs = logs
    
    # Combine block data (use response1 blocks)
    combined_blocks = response1.data.blocks if response1.data.blocks else []
    
    # Create filtered response
    filtered_response_data = FilteredResponseData(
        blocks=combined_blocks,
        transactions=filtered_transactions,
        logs=filtered_logs
    )
    
    filtered_response = FilteredResponse(data=filtered_response_data)
    
    return filtered_response

async def main():
    print(f"=== FIXED BLOCK CHECK ===")
    
    config = ClientConfig(
        url=MONAD_HYPERSYNC_URL,
        bearer_token=HYPERSYNC_BEARER_TOKEN
    )
    client = HypersyncClient(config)
    
    current_block = await client.get_height()
    print(f"Block Range: 25634134 to {current_block}")
    print(f"Looking for Transaction: {tx_hash}")
    print("=" * 50)

    # Query both MON and Jerry transactions separately
    mon_response = await query_mon_transactions(client)
    jerry_response = await query_jerry_transactions(client)
    
    # Combine results
    all_transactions = []
    all_logs = []
    block_timestamp_map = {}
    
    # Process MON transactions
    if mon_response.data:
        if mon_response.data.blocks:
            for block in mon_response.data.blocks:
                timestamp = hex_to_int(block.timestamp) if block.timestamp else 0
                block_timestamp_map[block.number] = timestamp
        
        if mon_response.data.transactions:
            print(f"\nFound {len(mon_response.data.transactions)} MON transactions")
            for tx in mon_response.data.transactions:
                all_transactions.append(('MON', tx))
        
        if mon_response.data.logs:
            all_logs.extend(mon_response.data.logs)
    
    # Process Jerry transactions
    if jerry_response.data:
        if jerry_response.data.blocks:
            for block in jerry_response.data.blocks:
                timestamp = hex_to_int(block.timestamp) if block.timestamp else 0
                block_timestamp_map[block.number] = timestamp
        
        if jerry_response.data.transactions:
            print(f"Found {len(jerry_response.data.transactions)} Jerry transactions")
            for tx in jerry_response.data.transactions:
                all_transactions.append(('Jerry', tx))
        
        if jerry_response.data.logs:
            all_logs.extend(jerry_response.data.logs)
    
    print(f"\nTotal transactions found: {len(all_transactions)}")
    
    # Count transactions by type
    mon_count = sum(1 for token_type, _ in all_transactions if token_type == 'MON')
    jerry_count = sum(1 for token_type, _ in all_transactions if token_type == 'Jerry')
    print(f"MON transactions: {mon_count}")
    print(f"Jerry transactions: {jerry_count}")
    
    # Look for our target transaction and print all transactions
    target_found = False
    for i, (token_type, tx) in enumerate(all_transactions):
        block_timestamp = block_timestamp_map.get(tx.block_number)
        tx_logs = [log for log in all_logs if log.transaction_hash == tx.hash]
        
        if tx.hash == tx_hash:
            target_found = True
            print(f"\n{'='*60}")
            print(f"🎯 TARGET TRANSACTION FOUND (Transaction #{i+1})")
            print(f"{'='*60}")
            analyze_target_transaction(tx, block_timestamp, tx_logs, token_type)
        else:
            print(f"\n{'='*40}")
            print(f"📋 Transaction #{i+1} ({token_type})")
            print(f"{'='*40}")
            analyze_target_transaction(tx, block_timestamp, tx_logs, token_type)
    
    if not target_found:
        print(f"\n✗ Target transaction NOT found in block range")
        print(f"Target hash: {tx_hash}")
        print(f"Actual hashes found:")
        for token_type, tx in all_transactions:
            print(f"  {token_type}: {tx.hash}")
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Block Range: 25634134 to {current_block}")
    print(f"Total transactions analyzed: {len(all_transactions)}")
    print(f"MON transactions: {mon_count}")
    print(f"Jerry transactions: {jerry_count}")
    print(f"Unique transaction hashes: {len(set(tx.hash for _, tx in all_transactions))}")
    print(f"Target transaction found: {'Yes' if target_found else 'No'}")
    
    # Comparison with total contract transactions
    print(f"\n📈 COMPARISON WITH TOTAL CONTRACT TRANSACTIONS:")
    print(f"Filtered betting transactions: {len(all_transactions)}")
    print(f"Total contract transactions: ~5242 (from contract_transaction_counter.py)")
    print(f"Coverage: {(len(all_transactions) / 5242 * 100):.1f}% of all contract transactions")

if __name__ == "__main__":
    asyncio.run(main()) 