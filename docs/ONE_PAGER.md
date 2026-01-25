# Coding Agent — Operator One-Pager

## Two core commands
### Run (live output only)
agent run "Your task here"

### Runlog (live output + saved log)
 /opt/coding-agent/run_with_log.sh run "Your task here"

## Monitor output in another window
tail -f /opt/coding-agent/logs/agent-live.log

## Difference: run vs runlog
- run: prints output to your terminal only
- runlog: prints output AND appends the full transcript to /opt/coding-agent/logs/agent-live.log

## Key paths
- Repo: /opt/coding-agent
- Workspace: /opt/coding-agent/workspace
- Logs: /opt/coding-agent/logs
- Log file: /opt/coding-agent/logs/agent-live.log
- API key env file (NOT in git): /etc/coding_agent.env

## Security notes
- Keep secrets in /etc/coding_agent.env (never commit keys)
- Tools restrict dangerous commands and limit file IO to workspace
