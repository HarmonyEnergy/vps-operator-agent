# Autonomous Coding Agent - Project Context

## What This Is
An autonomous coding agent that calls ChatGPT to write code, executes it on a VPS, feeds back results/errors, and iterates until complete.

## Key Innovation
Instead of manually copying code from ChatGPT → testing → copying errors back → repeating, this system automates the entire loop.

## Current Implementation

### Files in Context
- coding_agent.py - Original simple agent (auto-runs everything)
- coding_agent_interactive.py - Enhanced with prompt review, code review, demo mode
- coding_agent_v1_backup.py - Backup of original
- run_interactive.sh - Launcher that loads API key and runs agent
- agent_config.json - Task configuration
- agent_state.json - Current iteration state

### How It Works
1. Load task from agent_config.json
2. Load context files from context/ directory (this directory!)
3. Send task + context to ChatGPT
4. ChatGPT writes code
5. Execute code on VPS
6. Feed results/errors back to ChatGPT
7. Iterate until task complete

### Interactive Features
- **Prompt Review**: Edit task and set iterations before running
- **Code Review**: Approve/skip/edit each code block before execution
- **Context Loading**: AI automatically references files in context/
- **Demo Mode**: Test final product after completion
- **Output Saving**: Save successful runs to outputs/

### Directory Structure
```
/opt/coding-agent/
├── coding_agent_interactive.py   # Main agent
├── context/                       # Context files (YOU ARE HERE)
│   ├── All the agent code files
│   └── PROJECT_CONTEXT.md (this file)
├── workspace/                     # Execution directory
└── outputs/                       # Saved results
```

## Usage Patterns

### Extend Existing Code
Upload code to context/, then task: "Add feature X to [filename]"

### Refactor Code  
Task: "Refactor coding_agent_interactive.py to add pause/resume feature"

### Debug Code
Upload broken code, task: "Fix all bugs in [filename]"

## Key Concepts

**This is a CODING ITERATOR, not a web scraper.**

The goal: Autonomous code generation → testing → debugging → iteration until success.

The AI can see all files in this context/ directory and reference them when generating new code.
