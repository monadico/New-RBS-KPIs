#!/bin/bash

# Database Update Script for Coolify Deployment
# Runs every 6 hours to keep data fresh

# Set the working directory
cd /app

# Create database directory if it doesn't exist
mkdir -p /app/data

# Log file for tracking updates
LOG_FILE="/app/database_update.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_message "=== Starting Database Update ==="

# Load environment variables (from .env file if it exists, otherwise use system env vars)
if [ -f ".env" ]; then
    source .env
    log_message "Loaded environment variables from .env file"
else
    log_message "Using system environment variables (from Coolify)"
fi

# Check if required environment variables are set
if [ -z "$MONAD_HYPERSYNC_URL" ] || [ -z "$HYPERSYNC_BEARER_TOKEN" ]; then
    log_message "ERROR: Missing required environment variables"
    log_message "Please check MONAD_HYPERSYNC_URL and HYPERSYNC_BEARER_TOKEN in .env file"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    log_message "Activated virtual environment"
fi

# Check if betting database file exists, create if not
if [ ! -f "/app/data/betting_transactions.db" ]; then
    log_message "Betting database file not found, creating empty database file first..."
    touch /app/data/betting_transactions.db
    chmod 666 /app/data/betting_transactions.db
    log_message "Empty betting database file created, running initial database creation..."
    python3 betting_database.py --db-path /app/data/betting_transactions.db --start-block 0
    if [ $? -eq 0 ]; then
        log_message "Initial betting database creation completed successfully"
    else
        log_message "ERROR: Initial betting database creation failed"
        exit 1
    fi
fi

# Check if claiming database file exists, create if not
if [ ! -f "/app/data/comprehensive_claiming_transactions_fixed.db" ]; then
    log_message "Claiming database file not found, creating empty database file first..."
    touch /app/data/comprehensive_claiming_transactions_fixed.db
    chmod 666 /app/data/comprehensive_claiming_transactions_fixed.db
    log_message "Empty claiming database file created, running initial database creation..."
    python3 claiming_database.py --start-block 0
    if [ $? -eq 0 ]; then
        log_message "Initial claiming database creation completed successfully"
    else
        log_message "ERROR: Initial claiming database creation failed"
        exit 1
    fi
fi

# Run the betting database update with incremental flag
log_message "Starting incremental betting database update..."
log_message "Current directory: $(pwd)"
log_message "Betting database file exists: $(ls -la /app/data/betting_transactions.db 2>/dev/null || echo 'No betting database file')"
python3 betting_database.py --db-path /app/data/betting_transactions.db --incremental

if [ $? -eq 0 ]; then
    log_message "Betting database update completed successfully"
else
    log_message "ERROR: Betting database update failed"
    exit 1
fi

# Run the bet ID retrieval and database update
log_message "Starting bet ID retrieval and database update..."
python3 fast_bet_id_query.py

if [ $? -eq 0 ]; then
    log_message "Bet ID retrieval and database update completed successfully"
else
    log_message "ERROR: Bet ID retrieval and database update failed"
    exit 1
fi

# Run the claiming database update with incremental flag
log_message "Starting incremental claiming database update..."
log_message "Claiming database file exists: $(ls -la /app/data/comprehensive_claiming_transactions_fixed.db 2>/dev/null || echo 'No claiming database file')"
python3 claiming_database.py --incremental

if [ $? -eq 0 ]; then
    log_message "Claiming database update completed successfully"
else
    log_message "ERROR: Claiming database update failed"
    exit 1
fi

# Generate updated betting analytics JSON
log_message "Generating betting analytics JSON..."
python3 json_query.py

if [ $? -eq 0 ]; then
    log_message "Betting analytics JSON generated successfully"
else
    log_message "ERROR: Betting analytics JSON generation failed"
    exit 1
fi

# Generate updated claiming analytics JSON
log_message "Generating claiming analytics JSON..."
python3 claiming_query.py

if [ $? -eq 0 ]; then
    log_message "Claiming analytics JSON generated successfully"
else
    log_message "ERROR: Claiming analytics JSON generation failed"
    exit 1
fi

# Generate winrate analytics JSON
log_message "Generating winrate analytics JSON..."
python3 winrate_query.py

if [ $? -eq 0 ]; then
    log_message "Winrate analytics JSON generated successfully"
else
    log_message "ERROR: Winrate analytics JSON generation failed"
    exit 1
fi

# Copy the updated JSON files to the frontend deployment directory
if [ -f "new/public/analytics_dump.json" ]; then
    cp new/public/analytics_dump.json frontend-deployment/public/analytics_dump.json
    log_message "Copied betting analytics JSON to frontend deployment"
fi

if [ -f "new/public/claiming_analytics_dump.json" ]; then
    cp new/public/claiming_analytics_dump.json frontend-deployment/public/claiming_analytics_dump.json
    log_message "Copied claiming analytics JSON to frontend deployment"
fi

if [ -f "new/public/winrate_analytics_dump.json" ]; then
    cp new/public/winrate_analytics_dump.json frontend-deployment/public/winrate_analytics_dump.json
    log_message "Copied winrate analytics JSON to frontend deployment"
fi

# Show database statistics
log_message "Betting Database Statistics:"
python3 betting_database.py --stats | tee -a "$LOG_FILE"

log_message "Claiming Database Statistics:"
python3 claiming_database.py --stats | tee -a "$LOG_FILE"

log_message "=== Database Update Complete ==="
log_message ""

# Keep only last 1000 lines of log file to prevent it from growing too large
tail -n 1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE" 