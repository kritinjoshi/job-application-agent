#!/bin/bash

echo "Installing Antigravity Automater into MacOS Crontab..."

# The exact absolute path arrays organically mapping to your physical Python Virtual Environment
WORKSPACE_DIR="/Users/mrunalshirude/.gemini/antigravity/scratch/job_application_agent"
PYTHON_BIN="$WORKSPACE_DIR/venv/bin/python"
LOG_FILE="$WORKSPACE_DIR/agent_execution.log"

# Validate natively
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Could not locate virtual environment python at $PYTHON_BIN"
    exit 1
fi

# The CRON Command dynamically executes strictly locally natively precisely at 7:00 AM server local time!
CRON_JOB="0 7 * * * cd $WORKSPACE_DIR && export PYTHONPATH=$WORKSPACE_DIR:\$PYTHONPATH && /usr/bin/caffeinate -i $PYTHON_BIN -m src.main >> $LOG_FILE 2>&1"

# Check if the natively mapped job physically exists organically
crontab -l 2>/dev/null | grep -F "$PYTHON_BIN -m src.main" > /dev/null
if [ $? -eq 0 ]; then
    # Replace existing with new timing
    (crontab -l 2>/dev/null | grep -v "$PYTHON_BIN -m src.main"; echo "$CRON_JOB") | crontab -
    echo "The Cron Agent has been successfully updated to run at 7:00 AM PST daily!"
    exit 0
fi

# Write carefully logically out into standard crontab organically!
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "\nSuccess! Your machine will autonomously execute the Job Application Agent securely every morning at exactly 7:00 AM PST."
echo "You can view execution outputs explicitly tracking natively inside: $LOG_FILE"
echo "To structurally uninstall natively later, literally cleanly run: crontab -e"
