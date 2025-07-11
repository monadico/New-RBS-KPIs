import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import os


class BettingAnalyticsDB:
    """
    SQLite database manager for betting analytics data.
    Handles transactions, user engagement metrics, and checkpoints.
    """
    
    def __init__(self, db_path: str = "betting_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    tx_hash TEXT PRIMARY KEY,
                    origin_from_address TEXT NOT NULL,
                    bet_amt REAL NOT NULL,
                    betting_token TEXT NOT NULL,
                    cards_in_slip INTEGER NOT NULL,
                    bet_id_decoded INTEGER NOT NULL,
                    block_number INTEGER NOT NULL,
                    block_timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_timestamp 
                ON transactions(block_timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_address 
                ON transactions(origin_from_address)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_token 
                ON transactions(betting_token)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_block_number 
                ON transactions(block_number)
            """)
            
            # Create hourly metrics table for pre-computed aggregations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hourly_metrics (
                    hour_start DATETIME PRIMARY KEY,
                    active_users INTEGER NOT NULL,
                    new_users INTEGER NOT NULL,
                    cumulative_new_users INTEGER NOT NULL,
                    submission_txs INTEGER NOT NULL,
                    cumulative_txs INTEGER NOT NULL,
                    total_cards INTEGER NOT NULL,
                    cumulative_cards INTEGER NOT NULL,
                    avg_cards REAL NOT NULL,
                    mon_volume REAL NOT NULL,
                    cumulative_mon_volume REAL NOT NULL,
                    jerry_volume REAL NOT NULL,
                    cumulative_jerry_volume REAL NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
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
                cursor.execute("""
                    INSERT INTO checkpoints (last_processed_block) 
                    VALUES (0)
                """)
            
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
        """
        Insert multiple transactions into the database.
        Returns the number of transactions actually inserted (excluding duplicates).
        """
        if not transactions:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            inserted_count = 0
            
            for tx in transactions:
                try:
                    cursor.execute("""
                        INSERT INTO transactions 
                        (tx_hash, origin_from_address, bet_amt, betting_token, 
                         cards_in_slip, bet_id_decoded, block_number, block_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tx['tx_hash'],
                        tx['origin_from_address'],
                        tx['bet_amt'],
                        tx['betting_token'],
                        tx['cards_in_slip'],
                        tx['bet_id_decoded'],
                        tx.get('block_number', 0),
                        tx['block_timestamp']
                    ))
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    # Transaction already exists, skip it
                    continue
            
            conn.commit()
            print(f"Inserted {inserted_count} new transactions (skipped {len(transactions) - inserted_count} duplicates)")
            return inserted_count
    
    def get_transactions_since_block(self, block_number: int) -> List[Dict[str, Any]]:
        """Get all transactions since a specific block number."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tx_hash, origin_from_address, bet_amt, betting_token,
                       cards_in_slip, bet_id_decoded, block_number, block_timestamp
                FROM transactions 
                WHERE block_number > ?
                ORDER BY block_number, tx_hash
            """, (block_number,))
            
            columns = ['tx_hash', 'origin_from_address', 'bet_amt', 'betting_token',
                      'cards_in_slip', 'bet_id_decoded', 'block_number', 'block_timestamp']
            
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_all_transactions(self) -> pd.DataFrame:
        """Get all transactions as a pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query("""
                SELECT tx_hash, origin_from_address, bet_amt, betting_token,
                       cards_in_slip, bet_id_decoded, block_number, block_timestamp
                FROM transactions 
                ORDER BY block_timestamp
            """, conn, parse_dates=['block_timestamp'])
    
    def get_transactions_in_date_range(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get transactions within a specific date range."""
        with self.get_connection() as conn:
            return pd.read_sql_query("""
                SELECT tx_hash, origin_from_address, bet_amt, betting_token,
                       cards_in_slip, bet_id_decoded, block_number, block_timestamp
                FROM transactions 
                WHERE block_timestamp BETWEEN ? AND ?
                ORDER BY block_timestamp
            """, conn, params=[start_date, end_date], parse_dates=['block_timestamp'])
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Transaction counts
            cursor.execute("SELECT COUNT(*) FROM transactions")
            total_transactions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT origin_from_address) FROM transactions")
            unique_addresses = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(block_timestamp), MAX(block_timestamp) FROM transactions")
            date_range = cursor.fetchone()
            
            cursor.execute("SELECT betting_token, COUNT(*) FROM transactions GROUP BY betting_token")
            token_counts = dict(cursor.fetchall())
            
            cursor.execute("SELECT last_processed_block FROM checkpoints ORDER BY id DESC LIMIT 1")
            last_block = cursor.fetchone()[0]
            
            return {
                'total_transactions': total_transactions,
                'unique_addresses': unique_addresses,
                'date_range': {
                    'start': date_range[0],
                    'end': date_range[1]
                },
                'token_distribution': token_counts,
                'last_processed_block': last_block,
                'database_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
            }
    
    def upsert_hourly_metrics(self, metrics_df: pd.DataFrame):
        """Insert or update hourly metrics."""
        if metrics_df.empty:
            return
        
        with self.get_connection() as conn:
            # Use pandas to_sql with replace mode for simplicity
            metrics_df.to_sql('hourly_metrics', conn, if_exists='replace', index=True, index_label='hour_start')
            conn.commit()
            print(f"Updated hourly metrics for {len(metrics_df)} hours")
    
    def get_hourly_metrics(self) -> pd.DataFrame:
        """Get pre-computed hourly metrics."""
        with self.get_connection() as conn:
            return pd.read_sql_query("""
                SELECT * FROM hourly_metrics 
                ORDER BY hour_start DESC
            """, conn, parse_dates=['hour_start'], index_col='hour_start')
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """Remove transaction data older than specified days (keep aggregated metrics)."""
        cutoff_date = datetime.now() - pd.Timedelta(days=days_to_keep)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM transactions 
                WHERE block_timestamp < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            print(f"Cleaned up {deleted_count} old transactions (older than {days_to_keep} days)")
            return deleted_count


# Utility functions for easy database operations
def get_db_instance(db_path: str = "betting_analytics.db") -> BettingAnalyticsDB:
    """Get a database instance."""
    return BettingAnalyticsDB(db_path)


def print_database_stats(db_path: str = "betting_analytics.db"):
    """Print database statistics."""
    db = get_db_instance(db_path)
    stats = db.get_database_stats()
    
    print("\n=== DATABASE STATISTICS ===")
    print(f"Total Transactions: {stats['total_transactions']:,}")
    print(f"Unique Addresses: {stats['unique_addresses']:,}")
    print(f"Date Range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    print(f"Last Processed Block: {stats['last_processed_block']:,}")
    print(f"Database Size: {stats['database_size_mb']:.2f} MB")
    print(f"Token Distribution: {stats['token_distribution']}")
    print("=" * 30)


if __name__ == "__main__":
    # Test the database setup
    db = get_db_instance()
    print_database_stats() 