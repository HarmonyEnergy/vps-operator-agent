#!/bin/bash
set -e
SCRIPT_DIR="/opt/coding-agent"
LOG_FILE="/var/log/coding_agent.log"

cd "$SCRIPT_DIR"

# Load environment variables
if [ -f /etc/coding_agent.env ]; then
    set -o allexport
    source /etc/coding_agent.env
    set +o allexport
fi

# Run the interactive agent
python3 "${SCRIPT_DIR}/coding_agent_interactive.py" "$@" 2>&1 | tee -a "$LOG_FILE"
