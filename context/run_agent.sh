#!/bin/bash
set -e
SCRIPT_DIR="/opt/coding-agent"
VENV_PATH="${SCRIPT_DIR}/.venv"
LOG_FILE="/var/log/coding_agent.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "========================================" >> "$LOG_FILE"
echo "Coding Agent run started: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

cd "$SCRIPT_DIR"
source "${VENV_PATH}/bin/activate"

if [ -f /etc/coding_agent.env ]; then
    set -o allexport
    source /etc/coding_agent.env
    set +o allexport
fi

python3 "${SCRIPT_DIR}/coding_agent.py" 2>&1 | tee -a "$LOG_FILE"

echo "----------------------------------------" >> "$LOG_FILE"
echo "Coding Agent run completed: $(date)" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
