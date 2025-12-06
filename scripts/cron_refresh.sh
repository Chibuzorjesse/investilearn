#!/bin/bash
# Cron job example for refreshing InvestiLearn data cache
#
# Add to crontab with: crontab -e
# Then add one of these lines:

# Run daily at 2 AM (after market close)
# 0 2 * * * /path/to/investilearn/scripts/cron_refresh.sh

# Run weekly on Sunday at 3 AM
# 0 3 * * 0 /path/to/investilearn/scripts/cron_refresh.sh

# Navigate to project directory
cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment if needed
# source venv/bin/activate

# Run the data refresh script
echo "$(date): Starting data refresh..."
uv run python scripts/refresh_data.py --all --delay 1.5

# Check exit code
if [ $? -eq 0 ]; then
    echo "$(date): Data refresh completed successfully"
else
    echo "$(date): Data refresh failed with exit code $?"
    exit 1
fi
