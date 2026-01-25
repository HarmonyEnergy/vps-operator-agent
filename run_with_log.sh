#!/usr/bin/env bash
set -euo pipefail

ROOT="/opt/coding-agent"
LOGDIR="$ROOT/logs"
LOGFILE="$LOGDIR/agent-live.log"

mkdir -p "$LOGDIR"

ts() { date '+%Y-%m-%d %H:%M:%S %Z'; }

{
  echo
  echo "================================================================================"
  echo "RUN START: $(ts)"
  echo "HOST: $(hostname)"
  echo "USER: $(whoami)"
  echo "CMD: agent $*"
  echo "--------------------------------------------------------------------------------"
} >> "$LOGFILE"

# Run agent, tee output to log
# Also preserve exit code correctly
set +e
agent "$@" 2>&1 | tee -a "$LOGFILE"
rc=${PIPESTATUS[0]}
set -e

{
  echo "--------------------------------------------------------------------------------"
  echo "RUN END: $(ts) (exit=$rc)"
  echo "================================================================================"
} >> "$LOGFILE"

exit "$rc"
