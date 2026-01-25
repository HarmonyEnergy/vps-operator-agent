# VPS Operator Agent

An AI-powered agent for executing tasks on a VPS with built-in safety constraints.

## Features

- **Safe Shell Execution**: Automatically handles pipes, redirects, and compound commands with security validation
- **Workspace Isolation**: All operations confined to `/opt/coding-agent/workspace`
- **Automatic Deliverables**: Surfaces created files at task completion
- **Tool Transcript**: Full visibility into command execution and results
- **Comprehensive Security**: Blocks dangerous commands, validates paths, enforces timeouts

## Usage
```bash
# Via wrapper (sources environment automatically)
agent run "analyze the logs and create a summary report"

# Direct Python
cd /opt/coding-agent
source .venv/bin/activate
python3 cli.py run "your task here"

# With options
agent run --model gpt-4o --max-turns 30 "complex task"
agent run --no-transcript "simple task"

# Run tests
agent test
```

## Architecture

- `vps_agent.py`: Main agent loop using OpenAI Responses API
- `tools.py`: Sandboxed tool implementations (shell, Python, file I/O)
- `cli.py`: Command-line interface
- `test_suite.py`: Comprehensive test coverage

## Safety Features

### Blocked Operations
- System modification (rm -rf /, mkfs, etc.)
- User management (useradd, passwd, etc.)
- Network attacks (direct nc, telnet, etc.)
- Privilege escalation (sudo, su, chmod 777, etc.)
- Fork bombs and resource exhaustion

### Allowed Operations
- File I/O within workspace
- Shell commands with pipes and redirects
- Python script execution
- Standard CLI tools (grep, awk, sed, find, etc.)

## Configuration

Environment variables (in `/etc/coding_agent.env`):
- `OPENAI_API_KEY`: Required for agent operation

## Development
```bash
# Run tests
python3 test_suite.py

# Manual tool testing
python3 -c "import tools; print(tools.run_shell('ls -la'))"
```

## Logs

Agent runs are logged to `logs/agent-live.log` when using the wrapper script.
