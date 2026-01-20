#!/bin/bash

# Live Coding Agent Monitor
AGENT_DIR="/opt/coding-agent"
LOG_FILE="/var/log/coding_agent.log"
STATE_FILE="$AGENT_DIR/agent_state.json"
CONFIG_FILE="$AGENT_DIR/agent_config.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'
BOLD='\033[1m'

clear
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║          AUTONOMOUS CODING AGENT - LIVE MONITOR           ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

show_status() {
    echo -e "${BOLD}${BLUE}📊 CURRENT STATUS${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if pgrep -f "coding_agent.py" > /dev/null; then
        echo -e "Status: ${GREEN}●${NC} ${BOLD}RUNNING${NC}"
    else
        echo -e "Status: ${RED}●${NC} ${BOLD}STOPPED${NC}"
    fi
    
    if [ -f "$CONFIG_FILE" ]; then
        TASK=$(jq -r '.task_description' "$CONFIG_FILE" 2>/dev/null)
        echo -e "Task: ${CYAN}${TASK:0:60}...${NC}"
    fi
    
    if [ -f "$STATE_FILE" ]; then
        ITERATION=$(jq -r '.iteration' "$STATE_FILE" 2>/dev/null)
        COMPLETED=$(jq -r '.task_completed' "$STATE_FILE" 2>/dev/null)
        echo -e "Iteration: ${YELLOW}$ITERATION${NC}/10"
        
        if [ "$COMPLETED" = "true" ]; then
            echo -e "Completion: ${GREEN}✓ COMPLETE${NC}"
        else
            echo -e "Completion: ${YELLOW}⏳ IN PROGRESS${NC}"
        fi
    fi
    echo ""
}

show_workspace() {
    echo -e "${BOLD}${BLUE}📁 WORKSPACE FILES${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ -d "$AGENT_DIR/workspace" ]; then
        FILE_COUNT=$(ls -1 "$AGENT_DIR/workspace" 2>/dev/null | wc -l)
        if [ $FILE_COUNT -gt 0 ]; then
            echo -e "${GREEN}Files created: $FILE_COUNT${NC}"
            ls -lh "$AGENT_DIR/workspace" | tail -n +2
        else
            echo -e "${YELLOW}No files created yet${NC}"
        fi
    fi
    echo ""
}

show_status
show_workspace

echo -e "${BOLD}${BLUE}📋 LIVE LOGS (Press Ctrl+C to exit)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

tail -f "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
    if [[ $line == *"ERROR"* ]]; then
        echo -e "${RED}$line${NC}"
    elif [[ $line == *"WARNING"* ]]; then
        echo -e "${YELLOW}$line${NC}"
    elif [[ $line == *"ITERATION"* ]]; then
        echo -e "${BOLD}${MAGENTA}$line${NC}"
    elif [[ $line == *"TASK COMPLETED"* ]]; then
        echo -e "${BOLD}${GREEN}$line${NC}"
    elif [[ $line == *"Return code: 0"* ]]; then
        echo -e "${GREEN}$line${NC}"
    else
        echo "$line"
    fi
done
