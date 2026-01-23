#!/usr/bin/env python3
"""
Autonomous Coding Agent - IMPROVED VERSION
Uses gpt-3.5-turbo (more reliable) and clearer prompting
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import requests

# Configuration
BASE_DIR = Path(__file__).parent.absolute()
CONFIG_PATH = BASE_DIR / "agent_config.json"
STATE_PATH = BASE_DIR / "agent_state.json"
WORKSPACE_DIR = BASE_DIR / "workspace"
LOG_FILE = Path("/var/log/coding_agent.log")

# Ensure workspace exists
WORKSPACE_DIR.mkdir(exist_ok=True)

class CodingAgent:
    """Autonomous coding agent that interacts with ChatGPT"""
    
    def __init__(self):
        self.config = self.load_config()
        self.state = self.load_state()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.conversation_history = []
        
        if not self.openai_api_key:
            self._log("ERROR: OPENAI_API_KEY not found in environment")
            raise ValueError("Missing OpenAI API key")
    
    def _log(self, msg: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        
        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_msg + "\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")
    
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            self._log(f"Config file not found at {CONFIG_PATH}, using defaults")
            return {
                "max_iterations": 10,
                "task_description": "",
                "allowed_commands": ["python3", "bash", "node", "npm", "pip"],
                "timeout_seconds": 30
            }
        except json.JSONDecodeError as e:
            self._log(f"ERROR: Invalid JSON in config: {e}")
            sys.exit(1)
    
    def load_state(self) -> dict:
        """Load agent state from JSON file"""
        try:
            with open(STATE_PATH, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "iteration": 0,
                "task_completed": False,
                "last_run": None
            }
    
    def save_state(self):
        """Save agent state to JSON file"""
        try:
            with open(STATE_PATH, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self._log(f"ERROR: Failed to save state: {e}")
    
    def call_chatgpt(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """Call ChatGPT API and get response"""
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # Use gpt-3.5-turbo instead of gpt-4 for more reliability
        model = self.config.get("model", "gpt-3.5-turbo")
        if model == "gpt-4":
            self._log("WARNING: gpt-4 model may not be available, trying gpt-3.5-turbo instead")
            model = "gpt-3.5-turbo"
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            self._log(f"Calling ChatGPT API with model: {model}")
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            self._log(f"ERROR: ChatGPT API call failed: {e}")
            # Wait a bit and return empty on error
            time.sleep(2)
            return ""
        except (KeyError, IndexError) as e:
            self._log(f"ERROR: Failed to parse ChatGPT response: {e}")
            return ""
    
    def extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code blocks from ChatGPT response with language identifiers"""
        import re
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for lang, code in matches:
            if not lang:
                lang = "text"
            code_blocks.append((lang, code.strip()))
        
        return code_blocks
    
    def execute_code(self, code: str, language: str) -> Tuple[int, str, str]:
        """Execute code in the workspace directory"""
        if language.lower() in ["python", "python3", "py"]:
            temp_file = WORKSPACE_DIR / f"temp_script_{int(time.time())}.py"
            temp_file.write_text(code)
            cmd = ["python3", str(temp_file)]
            
        elif language.lower() in ["bash", "sh", "shell"]:
            temp_file = WORKSPACE_DIR / f"temp_script_{int(time.time())}.sh"
            temp_file.write_text(code)
            temp_file.chmod(0o755)
            cmd = ["bash", str(temp_file)]
            
        elif language.lower() in ["javascript", "js", "node"]:
            temp_file = WORKSPACE_DIR / f"temp_script_{int(time.time())}.js"
            temp_file.write_text(code)
            cmd = ["node", str(temp_file)]
            
        else:
            return -1, "", f"Unsupported language: {language}"
        
        try:
            self._log(f"Executing {language} code...")
            result = subprocess.run(
                cmd,
                cwd=WORKSPACE_DIR,
                capture_output=True,
                text=True,
                timeout=self.config.get("timeout_seconds", 30)
            )
            
            if temp_file.exists():
                temp_file.unlink()
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            self._log("ERROR: Code execution timed out")
            if temp_file.exists():
                temp_file.unlink()
            return -1, "", "Execution timed out"
        except Exception as e:
            self._log(f"ERROR: Failed to execute code: {e}")
            if temp_file.exists():
                temp_file.unlink()
            return -1, "", str(e)
    
    def run_iteration(self) -> bool:
        """Run one iteration of the coding agent"""
        iteration = self.state["iteration"]
        task = self.config.get("task_description", "")
        
        if not task:
            self._log("ERROR: No task description provided in config")
            return True
        
        self._log(f"\n{'='*60}")
        self._log(f"ITERATION {iteration + 1}")
        self._log(f"{'='*60}")
        
        if iteration == 0:
            # IMPROVED: Much clearer first iteration prompt
            system_prompt = """You are a code generator for an autonomous Linux system (Ubuntu 24.04).
You MUST provide working code to accomplish the user's task.

CRITICAL RULES:
1. ALWAYS provide code in markdown code blocks (```python or ```bash)
2. Make code complete and runnable (include all imports)
3. DO NOT ask questions - just write the code
4. DO NOT say "I cannot execute code" - your code WILL be executed
5. When task is complete, add "TASK COMPLETE" to your response

You are running in an automated environment. Your code will be automatically executed."""

            user_message = f"""Write complete, working code for this task:

TASK: {task}

Requirements:
- Ubuntu 24.04 LTS environment
- Non-interactive (no user input)
- Include all necessary imports
- Handle errors gracefully
- Provide code in markdown code blocks

Write the code NOW."""
            
        else:
            # Subsequent iterations
            system_prompt = """You are debugging code in an automated environment.
Analyze the execution results and provide improved code.

When task succeeds, include "TASK COMPLETE" in your response."""
            
            user_message = self.state.get("last_feedback", "Continue with the task.")
        
        response = self.call_chatgpt(user_message, system_prompt)
        
        if not response:
            self._log("ERROR: Empty response from ChatGPT")
            return False
        
        self._log(f"\nChatGPT Response:\n{'-'*60}\n{response}\n{'-'*60}")
        
        if "TASK COMPLETE" in response.upper():
            self._log("\nTask indicated complete!")
            self.state["task_completed"] = True
            return True
        
        code_blocks = self.extract_code_blocks(response)
        
        if not code_blocks:
            self._log("WARNING: No code blocks found in response")
            self.state["last_feedback"] = f"""ERROR: You did not provide any code blocks.

You MUST provide code in this format:
```python
# your code here
```

Please provide the complete working code for the task: {task}"""
            return False
        
        execution_results = []
        
        for idx, (language, code) in enumerate(code_blocks):
            self._log(f"\n--- Code Block {idx + 1} ({language}) ---")
            self._log(f"Code:\n{code[:200]}{'...' if len(code) > 200 else ''}")
            
            return_code, stdout, stderr = self.execute_code(code, language)
            
            result_summary = {
                "block_number": idx + 1,
                "language": language,
                "return_code": return_code,
                "stdout": stdout[:500],
                "stderr": stderr[:500]
            }
            
            execution_results.append(result_summary)
            
            self._log(f"\nReturn code: {return_code}")
            if stdout:
                self._log(f"STDOUT:\n{stdout[:500]}")
            if stderr:
                self._log(f"STDERR:\n{stderr[:500]}")
        
        feedback_parts = []
        
        for result in execution_results:
            if result["return_code"] == 0:
                feedback_parts.append(f"Code block {result['block_number']} ({result['language']}) executed successfully.")
                if result["stdout"]:
                    feedback_parts.append(f"Output:\n{result['stdout']}")
            else:
                feedback_parts.append(f"Code block {result['block_number']} ({result['language']}) failed with return code {result['return_code']}.")
                if result["stderr"]:
                    feedback_parts.append(f"Error:\n{result['stderr']}")
                if result["stdout"]:
                    feedback_parts.append(f"Output:\n{result['stdout']}")
        
        feedback = "\n\n".join(feedback_parts)
        
        # Check if task seems complete even without explicit marker
        all_successful = all(r["return_code"] == 0 for r in execution_results)
        if all_successful and iteration > 0:
            feedback += "\n\nCode executed successfully! If the task is complete, respond with 'TASK COMPLETE'."
        else:
            feedback += "\n\nAnalyze the results and provide improved code, or indicate 'TASK COMPLETE' if done."
        
        self.state["last_feedback"] = feedback
        
        return False
    
    def run(self):
        """Main execution loop"""
        self._log("\n" + "="*60)
        self._log("CODING AGENT STARTED")
        self._log("="*60)
        self._log(f"Task: {self.config.get('task_description', 'Not specified')}")
        self._log(f"Max iterations: {self.config.get('max_iterations', 10)}")
        
        max_iterations = self.config.get("max_iterations", 10)
        
        while self.state["iteration"] < max_iterations:
            task_complete = self.run_iteration()
            
            self.state["iteration"] += 1
            self.state["last_run"] = datetime.now().isoformat()
            self.save_state()
            
            if task_complete:
                self._log("\n" + "="*60)
                self._log("TASK COMPLETED SUCCESSFULLY!")
                self._log("="*60)
                return 0
            
            time.sleep(2)
        
        self._log("\n" + "="*60)
        self._log(f"Maximum iterations ({max_iterations}) reached without completion")
        self._log("="*60)
        return 1


def main():
    """Entry point"""
    try:
        agent = CodingAgent()
        exit_code = agent.run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
