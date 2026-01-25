from __future__ import annotations

import json
from typing import Any, Dict, List

from openai import OpenAI
import tools_enhanced as tools

client = OpenAI()

TOOLS = [
    {
        "type": "function",
        "name": "run_shell",
        "description": "Run a shell command inside the workspace. Supports pipes, redirects with safety checks. cwd is workspace-relative.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "cwd": {"type": ["string", "null"]},
                "timeout": {"type": "integer", "minimum": 1, "maximum": 600},
            },
            "required": ["command"],
        },
    },
    {
        "type": "function",
        "name": "run_python",
        "description": "Write python code to a file in workspace and run it.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string"},
                "filename": {"type": "string"},
                "timeout": {"type": "integer", "minimum": 1, "maximum": 600},
            },
            "required": ["code"],
        },
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Read a text file from workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "max_bytes": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Write a text file into workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
]

TOOL_IMPL = {
    "run_shell": lambda **kw: tools.run_shell(**kw),
    "run_python": lambda **kw: tools.run_python(**kw),
    "read_file": lambda **kw: tools.read_file(**kw),
    "write_file": lambda **kw: tools.write_file(**kw),
}

SYSTEM = """You are a remote VPS operator agent.

Rules:
- Use tools for ALL actions (shell, file IO, python runs).
- Keep all work inside /opt/coding-agent/workspace.
- When you run commands, you MUST present their stdout/stderr inline in the final response.
- Shell commands now support pipes, redirects, and other shell features (e.g., df -h | head, echo "test" > file.txt).
- End your final response with a DELIVERABLES section listing any files the user should review.

Be concise, verify results, and avoid "it worked" without evidence.
"""

def _fmt_block(label: str, text: str) -> str:
    text = (text or "").rstrip()
    if not text:
        return ""
    return f"\n--- {label} ---\n{text}\n"

def _summarize_tool_result(name: str, result: Dict[str, Any]) -> str:
    parts: List[str] = []
    parts.append(f"\n=== TOOL: {name} ===")
    
    # Common fields
    if "command" in result:
        parts.append(f"command: {result.get('command')}")
    if "shell_mode" in result:
        mode = "shell=True" if result.get('shell_mode') else "shell=False"
        parts.append(f"mode: {mode}")
    if "cwd" in result:
        parts.append(f"cwd: {result.get('cwd')}")
    if "returncode" in result:
        parts.append(f"returncode: {result.get('returncode')}")
    if "file" in result:
        parts.append(f"file: {result.get('file')}")
    if "path" in result:
        parts.append(f"path: {result.get('path')}")
    if "bytes" in result:
        parts.append(f"bytes: {result.get('bytes')}")
    if "error" in result:
        parts.append(f"error: {result.get('error')}")
    if "success" in result:
        parts.append(f"success: {result.get('success')}")
    
    # Payloads
    parts.append(_fmt_block("stdout", result.get("stdout", "")))
    parts.append(_fmt_block("stderr", result.get("stderr", "")))
    
    if "content" in result:
        parts.append(_fmt_block("content", result.get("content", "")))
    
    return "\n".join([p for p in parts if p is not None and p != ""])

def _format_deliverables() -> str:
    """Generate deliverables section showing created files."""
    deliverables = tools.list_deliverables()
    
    if not deliverables:
        return "\n## DELIVERABLES\nNo output files created in workspace."
    
    output = ["\n## DELIVERABLES"]
    output.append(f"Found {len(deliverables)} file(s) in workspace:\n")
    
    for path in deliverables[:20]:  # Limit to 20 files
        output.append(f"  • {path}")
    
    if len(deliverables) > 20:
        output.append(f"\n  ... and {len(deliverables) - 20} more files")
    
    return "\n".join(output)

def run_task(
    task: str,
    model: str = "gpt-4.1-mini",
    max_turns: int = 25,
    include_transcript: bool = True,
) -> str:
    """
    Runs a tool-using loop. Always captures tool IO to a transcript so results
    are visible even if the model summarises too aggressively.
    """
    items: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": task},
    ]
    
    transcript: List[str] = []
    
    for turn_num in range(max_turns):
        resp = client.responses.create(
            model=model,
            tools=TOOLS,
            input=items,
        )
        
        # Register the model output items for this turn
        items.extend(resp.output)
        
        tool_calls = [o for o in resp.output if getattr(o, "type", None) == "function_call"]
        
        if not tool_calls:
            final_text = (resp.output_text or "").strip() or "(no text output)"
            deliverables_section = _format_deliverables()
            
            if include_transcript and transcript:
                return (
                    "TOOL TRANSCRIPT\n" + 
                    "\n".join(transcript) + 
                    "\n\nFINAL\n" + 
                    final_text +
                    deliverables_section
                )
            return final_text + deliverables_section
        
        # Execute each tool call
        for call in tool_calls:
            name = call.name
            args = json.loads(call.arguments or "{}")
            
            result = TOOL_IMPL[name](**args)
            
            if include_transcript:
                transcript.append(_summarize_tool_result(name, result))
            
            items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result),
                }
            )
    
    # Max turns reached
    tail = f"Max turns ({max_turns}) reached without the model finalizing."
    deliverables_section = _format_deliverables()
    
    if include_transcript and transcript:
        return (
            "TOOL TRANSCRIPT\n" + 
            "\n".join(transcript) + 
            "\n\nFINAL\n" + 
            tail +
            deliverables_section
        )
    return tail + deliverables_section

if __name__ == "__main__":
    import sys
    
    task = " ".join(sys.argv[1:]).strip()
    if not task:
        print("Usage: python3 vps_agent_enhanced.py <task>")
        raise SystemExit(2)
    print(run_task(task))
