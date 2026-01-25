from __future__ import annotations
import shlex
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List

WORKSPACE = Path("/opt/coding-agent/workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

# Comprehensive binary blocklist
BLOCKED_BINARIES = {
    'rm', 'rmdir', 'dd', 'mkfs', 'fdisk', 'parted',
    'shutdown', 'reboot', 'poweroff', 'halt',
    'iptables', 'ip6tables', 'ufw', 'firewall-cmd',
    'passwd', 'useradd', 'userdel', 'usermod', 'groupadd',
    'chmod', 'chown', 'chgrp', 'chattr',
    'mount', 'umount', 'systemctl', 'service',
    'crontab', 'at', 'batch',
    'sudo', 'su', 'doas',
    'nc', 'netcat', 'socat', 'telnet',
}

# Shell metacharacters that require shell=True
SHELL_METACHARACTERS = {'|', '>', '<', '>>', '<<', '&', '&&', '||', ';', '$(', '`'}

def _has_shell_syntax(command: str) -> bool:
    """Detect if command contains shell-specific syntax."""
    return any(meta in command for meta in SHELL_METACHARACTERS)

def _extract_binary(command: str) -> str:
    """Extract the primary binary from a command string."""
    # Handle common patterns
    cmd = command.strip()
    # Remove leading env vars (KEY=val cmd)
    cmd = re.sub(r'^(\w+=\S+\s+)+', '', cmd)
    # Get first word
    parts = shlex.split(cmd) if not _has_shell_syntax(cmd) else cmd.split()
    if not parts:
        return ""
    binary = parts[0]
    # Strip path
    return Path(binary).name

def _validate_command_safety(command: str) -> None:
    """
    Validate command doesn't contain dangerous patterns.
    Raises ValueError if unsafe.
    """
    cmd_lower = command.lower()
    
    # Check for dangerous patterns
    dangerous_patterns = [
        (r'/dev/(sd|hd|nvme|vd)[a-z]', 'Direct disk device access'),
        (r'rm\s+(-[rf]*\s+)*/', 'Recursive delete from root'),
        (r':\(\)\s*\{', 'Fork bomb'),
        (r'mkfs', 'Filesystem creation'),
        (r'>\s*/dev/', 'Writing to device files'),
        (r'/etc/(passwd|shadow|sudoers)', 'Modifying critical system files'),
    ]
    
    for pattern, reason in dangerous_patterns:
        if re.search(pattern, cmd_lower):
            raise ValueError(f"Blocked: {reason}")
    
    # Check for blocked binaries
    binary = _extract_binary(command)
    if binary in BLOCKED_BINARIES:
        raise ValueError(f"Blocked binary: {binary}")
    
    # Check for absolute paths outside workspace (only for file operations)
    # Allow /usr/bin, /bin etc for executables
    file_patterns = [
        r'(?:^|\s)(/(?!usr/|bin/|lib/|opt/coding-agent/workspace)[^\s]+)',
    ]
    for pattern in file_patterns:
        matches = re.findall(pattern, command)
        for match in matches:
            if not match.startswith(str(WORKSPACE)):
                # Allow if it's clearly an executable path
                if not any(match.startswith(p) for p in ['/usr/', '/bin/', '/lib/']):
                    raise ValueError(f"Absolute path outside workspace: {match}")

def _safe_cwd(cwd: str | None) -> Path:
    if not cwd:
        return WORKSPACE
    p = (WORKSPACE / cwd).resolve()
    if WORKSPACE not in p.parents and p != WORKSPACE:
        raise ValueError("cwd must be inside workspace")
    return p

def run_shell(command: str, cwd: str | None = None, timeout: int = 60) -> Dict[str, Any]:
    """
    Execute shell command with safety checks.
    
    Automatically chooses shell=False or shell=True based on command complexity.
    """
    # Validate inputs
    if not command or not command.strip():
        return {"returncode": 1, "stdout": "", "stderr": "Empty command", "command": command}
    
    if not (1 <= timeout <= 600):
        timeout = min(max(timeout, 1), 600)
    
    # Safety validation
    try:
        _validate_command_safety(command)
    except ValueError as e:
        return {
            "returncode": 126,  # Command cannot execute
            "stdout": "",
            "stderr": f"BLOCKED: {str(e)}",
            "command": command,
            "cwd": str(WORKSPACE),
        }
    
    safe_cwd_path = _safe_cwd(cwd)
    
    # Decide execution strategy
    use_shell = _has_shell_syntax(command)
    
    try:
        if use_shell:
            # shell=True with restricted PATH
            env = {
                'PATH': '/usr/bin:/bin:/usr/local/bin',
                'HOME': str(WORKSPACE),
                'PWD': str(safe_cwd_path),
            }
            proc = subprocess.run(
                command,
                cwd=str(safe_cwd_path),
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True,
                env=env,
                executable='/bin/bash',
            )
        else:
            # shell=False (safer)
            args = shlex.split(command)
            proc = subprocess.run(
                args,
                cwd=str(safe_cwd_path),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout[-8000:] if proc.stdout else "",
            "stderr": proc.stderr[-8000:] if proc.stderr else "",
            "cwd": str(safe_cwd_path),
            "command": command,
            "shell_mode": use_shell,
        }
    
    except subprocess.TimeoutExpired:
        return {
            "returncode": 124,  # timeout exit code
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "command": command,
            "cwd": str(safe_cwd_path),
        }
    except Exception as e:
        return {
            "returncode": 127,
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "command": command,
            "cwd": str(safe_cwd_path),
        }

def run_python(code: str, filename: str = "snippet.py", timeout: int = 60) -> Dict[str, Any]:
    if not (1 <= timeout <= 600):
        timeout = min(max(timeout, 1), 600)
    
    try:
        p = (WORKSPACE / filename).resolve()
        if WORKSPACE not in p.parents:
            raise ValueError("filename must be inside workspace")
        
        p.write_text(code, encoding="utf-8")
        
        proc = subprocess.run(
            ["python3", str(p)],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout[-8000:] if proc.stdout else "",
            "stderr": proc.stderr[-8000:] if proc.stderr else "",
            "file": str(p),
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": 124,
            "stdout": "",
            "stderr": f"Python execution timed out after {timeout}s",
            "file": str(p) if 'p' in locals() else filename,
        }
    except Exception as e:
        return {
            "returncode": 127,
            "stdout": "",
            "stderr": f"Error: {str(e)}",
            "file": str(p) if 'p' in locals() else filename,
        }

def read_file(path: str, max_bytes: int = 200_000) -> Dict[str, Any]:
    try:
        p = (WORKSPACE / path).resolve()
        if WORKSPACE not in p.parents and p != WORKSPACE:
            raise ValueError("path must be inside workspace")
        
        if not p.exists():
            return {"path": str(p), "error": "not_found"}
        
        if not p.is_file():
            return {"path": str(p), "error": "not_a_file"}
        
        data = p.read_bytes()[:max_bytes]
        return {"path": str(p), "content": data.decode("utf-8", errors="replace")}
    except Exception as e:
        return {"path": path, "error": str(e)}

def write_file(path: str, content: str) -> Dict[str, Any]:
    try:
        p = (WORKSPACE / path).resolve()
        if WORKSPACE not in p.parents and p != WORKSPACE:
            raise ValueError("path must be inside workspace")
        
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        
        return {
            "path": str(p),
            "bytes": len(content.encode("utf-8")),
            "success": True,
        }
    except Exception as e:
        return {
            "path": path,
            "error": str(e),
            "success": False,
        }

def list_deliverables() -> List[str]:
    """
    Scan workspace for likely deliverable files.
    Returns list of paths relative to workspace.
    """
    deliverables = []
    
    # Common output patterns
    extensions = {'.txt', '.json', '.csv', '.html', '.md', '.py', '.sh', '.log'}
    exclude_names = {'snippet.py', '.gitkeep'}
    
    for item in WORKSPACE.rglob('*'):
        if item.is_file():
            # Skip common noise
            if item.name in exclude_names:
                continue
            if item.suffix in extensions:
                rel_path = item.relative_to(WORKSPACE)
                deliverables.append(str(rel_path))
    
    return sorted(deliverables)
