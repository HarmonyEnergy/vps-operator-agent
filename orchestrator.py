#!/usr/bin/env python3
"""
VPS Orchestrator Agent - Self-Iterating System with Full Logging
Runs on your VPS, executes multi-step tasks autonomously with complete audit trail
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from openai import OpenAI
import shutil

# Configuration
WORKSPACE = Path("/opt/coding-agent/workspace")
LOGS_DIR = Path("/opt/coding-agent/logs/orchestrator")
MAX_ITERATIONS = 10
DEFAULT_MODEL = "gpt-4o-mini"

class Orchestrator:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.iteration = 0
        
        # Session setup
        self.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir = LOGS_DIR / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.session_dir / "iterations").mkdir(exist_ok=True)
        (self.session_dir / "deliverables").mkdir(exist_ok=True)
        
        # Get git version
        self.code_version = self._get_git_version()
        
        # Session metadata
        self.metadata = {
            "session_id": self.session_id,
            "model": self.model,
            "start_time": datetime.now().isoformat(),
            "code_version": self.code_version,
            "max_iterations": MAX_ITERATIONS,
        }
        
        # Transcript for markdown report
        self.transcript_lines = []
        
        # Monitoring metrics
        self.total_tokens = 0
        self.total_cost = 0.0
        self.api_call_count = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

        
    def _get_git_version(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd="/opt/coding-agent",
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "unknown"
        
    def _log_iteration(self, iteration_num: int, reasoning: str, commands: List[str], results: List[Dict]):
        """Log details of a single iteration"""
        iter_prefix = self.session_dir / "iterations" / f"{iteration_num:03d}"
        
        # Save reasoning
        (iter_prefix.parent / f"{iteration_num:03d}_reasoning.txt").write_text(reasoning)
        
        # Save commands
        (iter_prefix.parent / f"{iteration_num:03d}_commands.sh").write_text("\n".join(commands) if commands else "(no commands)")
        
        # Save outputs
        output_lines = []
        for i, result in enumerate(results, 1):
            output_lines.append(f"=== Command {i}: {result['command']} ===")
            output_lines.append(f"Exit Code: {result['returncode']}")
            if result['stdout']:
                output_lines.append(f"\n--- STDOUT ---\n{result['stdout']}")
            if result['stderr']:
                output_lines.append(f"\n--- STDERR ---\n{result['stderr']}")
            output_lines.append("")
        
        (iter_prefix.parent / f"{iteration_num:03d}_output.txt").write_text("\n".join(output_lines) if output_lines else "(no output)")
    
    def execute_command(self, command: str, cwd: Path = WORKSPACE) -> Dict[str, Any]:
        """Execute a shell command and return structured results"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300,
                env={'PATH': '/usr/bin:/bin:/usr/local/bin'}
            )
            return {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "returncode": 124,
                "stdout": "",
                "stderr": "Command timed out after 300s",
                "success": False
            }
        except Exception as e:
            return {
                "command": command,
                "returncode": 1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    def _copy_deliverables(self):
        """Copy workspace files to deliverables directory"""
        deliverables = []
        try:
            for item in WORKSPACE.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(WORKSPACE)
                    dest = self.session_dir / "deliverables" / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)
                    deliverables.append(str(rel_path))
        except Exception as e:
            self.transcript_lines.append(f"\nWARNING: Error copying deliverables: {e}")
        return deliverables
    
    def _generate_markdown_report(self):
        """Generate comprehensive markdown report"""
        report_lines = [
            f"# Orchestrator Session Report",
            f"",
            f"## Session Information",
            f"- **Session ID**: `{self.session_id}`",
            f"- **Task**: {self.metadata.get('task', 'N/A')}",
            f"- **Model**: {self.model}",
            f"- **Code Version**: `{self.code_version}`",
            f"- **Start Time**: {self.metadata['start_time']}",
            f"- **End Time**: {self.metadata.get('end_time', 'N/A')}",
            f"- **Duration**: {self.metadata.get('duration_seconds', 0):.1f}s",
            f"- **Status**: {self.metadata.get('status', 'unknown')}",
            f"- **Iterations**: {self.iteration}/{MAX_ITERATIONS}",
            f"",
            f"## Execution Transcript",
            f"",
        ]
        
        report_lines.extend(self.transcript_lines)
        
        # Add deliverables section
        deliverables = self.metadata.get('deliverables', [])
        report_lines.extend([
            f"",
            f"## Deliverables",
            f"",
        ])
        
        if deliverables:
            report_lines.append(f"Created {len(deliverables)} file(s):")
            report_lines.append("")
            for d in deliverables:
                report_lines.append(f"- `{d}`")
        else:
            report_lines.append("No files created in workspace.")
        
        report_lines.extend([
            f"",
            f"## Session Statistics",
            f"",
            f"- Total Commands: {self.metadata.get('total_commands', 0)}",
            f"- Failed Commands: {self.metadata.get('failed_commands', 0)}",
            f"",
            f"---",
            f"",
            f"*Session log directory: `/opt/coding-agent/logs/orchestrator/{self.session_id}/`*",
        ])
        
        return "\n".join(report_lines)
    

    def _calculate_cost(self, prompt_tokens, completion_tokens):
        """Calculate cost for GPT-4o-mini"""
        prompt_cost = (prompt_tokens / 1_000_000) * 0.15
        completion_cost = (completion_tokens / 1_000_000) * 0.60
        return prompt_cost + completion_cost

    def get_complete_response(self, messages, max_continuation_attempts=5):
        """Get complete LLM response, handling truncation automatically"""
        accumulated_response = ""
        attempts = 0
        
        while attempts < max_continuation_attempts:
            try:
                self.api_call_count += 1
                if attempts == 0:
                    print(f"  → API call...")
                else:
                    print(f"  → API call (continuation chunk {attempts + 1})...")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=8000
                )
                
                content = response.choices[0].message.content
                finish_reason = response.choices[0].finish_reason
                accumulated_response += content
                
                # Track tokens
                usage = response.usage
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens
                
                self.total_prompt_tokens += prompt_tokens
                self.total_completion_tokens += completion_tokens
                self.total_tokens += total_tokens
                
                call_cost = self._calculate_cost(prompt_tokens, completion_tokens)
                self.total_cost += call_cost
                
                status_symbol = "✓" if finish_reason == "stop" else "↻"
                print(f"  {status_symbol} {finish_reason.capitalize()} | Tokens: {total_tokens:,} (↑{prompt_tokens} ↓{completion_tokens}) | ${call_cost:.5f}")
                
                if finish_reason == "stop":
                    return accumulated_response, "complete"
                elif finish_reason == "length":
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": "Continue."})
                    attempts += 1
                else:
                    return accumulated_response, finish_reason
                    
            except Exception as e:
                print(f"ERROR in get_complete_response: {e}")
                return accumulated_response if accumulated_response else None, "error"
        
        print(f"  ⚠ Reached max continuation attempts ({max_continuation_attempts})")
        return accumulated_response, "max_continuations"

    def run_task(self, task: str) -> str:
        """
        Main orchestration loop - iterates until task complete or max iterations
        """
        start_time = datetime.now()
        
        # Save input task
        (self.session_dir / "input.txt").write_text(task)
        self.metadata["task"] = task
        
        self.transcript_lines.append(f"```")
        self.transcript_lines.append(f"ORCHESTRATOR STARTING")
        self.transcript_lines.append(f"Task: {task}")
        self.transcript_lines.append(f"Max Iterations: {MAX_ITERATIONS}")
        self.transcript_lines.append(f"```")
        self.transcript_lines.append("")
        
        print(f"\n{'='*60}")
        print(f"ORCHESTRATOR STARTING")
        print(f"Session ID: {self.session_id}")
        print(f"Task: {task}")
        print(f"Max Iterations: {MAX_ITERATIONS}")
        print(f"{'='*60}\n")
        
        # Load system prompt from external file
        system_prompt_path = Path("/opt/coding-agent/system_prompts/orchestrator_prompt.txt")
        try:
            system_prompt = system_prompt_path.read_text()
        except FileNotFoundError:
            print(f"ERROR: System prompt not found at {system_prompt_path}")
            sys.exit(1)

        
        # Build conversation
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {task}"}
        ]
        
        total_commands = 0
        failed_commands = 0
        
        for self.iteration in range(1, MAX_ITERATIONS + 1):
            self.transcript_lines.append(f"### Iteration {self.iteration}")
            self.transcript_lines.append("")
            
            print(f"\n--- ITERATION {self.iteration} ---")
            
            # Get agent response using complete response method
            try:
                content, completion_status = self.get_complete_response(messages)
                
                if completion_status not in ["complete", "max_continuations"]:
                    print(f"⚠ Unusual completion: {completion_status}")
                    self.transcript_lines.append(f"**WARNING**: Unusual completion status: {completion_status}")
                    self.transcript_lines.append("")
                    if completion_status == "error":
                        break
                
                print(f"Agent Response:\n{content}\n")
                
                # Parse JSON response
                try:
                    # Strip markdown code fences if present
                    clean_content = content.strip()
                    if clean_content.startswith('```'):
                        lines = clean_content.split('\n')
                        lines = lines[1:] if lines[0].startswith('```') else lines
                        lines = lines[:-1] if lines and lines[-1].startswith('```') else lines
                        clean_content = '\n'.join(lines)
                    
                    action = json.loads(clean_content)
                except json.JSONDecodeError:
                    print("ERROR: Agent didn't return valid JSON")
                    self.transcript_lines.append("**ERROR**: Agent didn't return valid JSON")
                    self.transcript_lines.append("")
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": "ERROR: You must respond with valid JSON only. No other text."})
                    continue
                
                # Check status
                status = action.get("status", "continue")
                reasoning = action.get("reasoning", "No reasoning provided")
                commands = action.get("commands", [])
                
                self.transcript_lines.append(f"**Reasoning**: {reasoning}")
                self.transcript_lines.append(f"**Status**: `{status}`")
                self.transcript_lines.append("")
                
                print(f"Reasoning: {reasoning}")
                print(f"Status: {status}")
                
                if status == "complete":
                    self.metadata["status"] = "complete"
                    print(f"\n{'='*60}")
                    print("TASK COMPLETE")
                    print(f"{'='*60}\n")
                    break
                
                if status == "blocked":
                    self.metadata["status"] = "blocked"
                    self.metadata["block_reason"] = reasoning
                    print(f"\n{'='*60}")
                    print("TASK BLOCKED")
                    print(f"Reason: {reasoning}")
                    print(f"{'='*60}\n")
                    break
                
                # Execute commands
                results = []
                if commands:
                    self.transcript_lines.append("**Commands**:")
                    self.transcript_lines.append("```bash")
                    for cmd in commands:
                        self.transcript_lines.append(cmd)
                    self.transcript_lines.append("```")
                    self.transcript_lines.append("")
                    
                for cmd in commands:
                    total_commands += 1
                    print(f"\nExecuting: {cmd}")
                    result = self.execute_command(cmd)
                    results.append(result)
                    
                    if not result['success']:
                        failed_commands += 1
                    
                    print(f"Exit Code: {result['returncode']}")
                    if result['stdout']:
                        stdout_preview = result['stdout'][:500]
                        print(f"Output:\n{stdout_preview}")
                        self.transcript_lines.append(f"Output: `{stdout_preview}`")
                    if result['stderr']:
                        stderr_preview = result['stderr'][:500]
                        print(f"Error:\n{stderr_preview}")
                        self.transcript_lines.append(f"Error: `{stderr_preview}`")
                
                self.transcript_lines.append("")
                
                # Log this iteration
                self._log_iteration(self.iteration, reasoning, commands, results)
                
                # Show iteration summary
                print(f"\n  💰 Session total: {self.total_tokens:,} tokens | ${self.total_cost:.4f}")
                
                # Add to conversation
                messages.append({"role": "assistant", "content": content})
                
                # Provide feedback
                feedback = {
                    "iteration": self.iteration,
                    "results": results
                }
                messages.append({
                    "role": "user",
                    "content": f"Command results:\n{json.dumps(feedback, indent=2)}"
                })
                
            except Exception as e:
                print(f"ERROR: {e}")
                self.transcript_lines.append(f"**SYSTEM ERROR**: {e}")
                self.transcript_lines.append("")
                messages.append({
                    "role": "user",
                    "content": f"System error: {str(e)}. Please continue or mark as blocked."
                })
        
        # Handle max iterations
        if self.iteration >= MAX_ITERATIONS and self.metadata.get("status") != "complete":
            self.metadata["status"] = "max_iterations"
            print(f"\n{'='*60}")
            print("MAX ITERATIONS REACHED")
            print(f"{'='*60}\n")
        
        # Finalize metadata
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.metadata["end_time"] = end_time.isoformat()
        self.metadata["duration_seconds"] = duration
        self.metadata["total_commands"] = total_commands
        self.metadata["failed_commands"] = failed_commands
        
        # Copy deliverables
        deliverables = self._copy_deliverables()
        self.metadata["deliverables"] = deliverables
        
        # Save metadata
        (self.session_dir / "session.json").write_text(
            json.dumps(self.metadata, indent=2)
        )
        
        # Generate markdown report
        report = self._generate_markdown_report()
        (self.session_dir / "REPORT.md").write_text(report)
        
        # Monitoring summary
        print(f"\n{'='*60}")
        print("MONITORING SUMMARY")
        print(f"{'='*60}")
        print(f"API Calls: {self.api_call_count}")
        print(f"Total Tokens: {self.total_tokens:,} (↑{self.total_prompt_tokens:,} ↓{self.total_completion_tokens:,})")
        print(f"Total Cost: ${self.total_cost:.4f}")
        if self.iteration > 0:
            print(f"Avg Tokens/Iteration: {self.total_tokens // self.iteration:,}")
        print(f"{'='*60}")
        
        # Print summary
        summary = [
            f"\n{'='*60}",
            f"SESSION COMPLETE",
            f"{'='*60}",
            f"Session ID: {self.session_id}",
            f"Status: {self.metadata['status']}",
            f"Duration: {duration:.1f}s",
            f"Iterations: {self.iteration}/{MAX_ITERATIONS}",
            f"",
            f"Deliverables: {len(deliverables)} file(s)",
        ]
        
        for d in deliverables:
            summary.append(f"  - {d}")
        
        summary.extend([
            f"",
            f"Full report: /opt/coding-agent/logs/orchestrator/{self.session_id}/REPORT.md",
            f"{'='*60}",
        ])
        
        return "\n".join(summary)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 orchestrator.py '<task description>'")
        sys.exit(1)
    
    # Get API key
    try:
        with open("/etc/coding_agent.env") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
            else:
                print("ERROR: OPENAI_API_KEY not found in /etc/coding_agent.env")
                sys.exit(1)
    except FileNotFoundError:
        print("ERROR: /etc/coding_agent.env not found")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    
    orchestrator = Orchestrator(api_key=api_key)
    result = orchestrator.run_task(task)
    print(result)


if __name__ == "__main__":
    main()
