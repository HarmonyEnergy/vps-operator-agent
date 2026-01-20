#!/usr/bin/env python3
"""
Enhanced Interactive Coding Agent
Features:
- Upload files/documentation for context
- Review and edit prompts before submission
- Choose iteration count
- Review generated code before execution
- Demo/run final product
- Save successful outputs
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
CONTEXT_DIR = BASE_DIR / "context"  # NEW: For uploaded files
OUTPUT_DIR = BASE_DIR / "outputs"  # NEW: For successful results
LOG_FILE = Path("/var/log/coding_agent.log")

# Ensure directories exist
WORKSPACE_DIR.mkdir(exist_ok=True)
CONTEXT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

class InteractiveCodingAgent:
    """Enhanced interactive autonomous coding agent"""
    
    def __init__(self, interactive=True):
        self.interactive = interactive
        self.config = self.load_config()
        self.state = self.load_state()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.conversation_history = []
        self.context_files = []
        
        if not self.openai_api_key:
            self._log("ERROR: OPENAI_API_KEY not found in environment")
            raise ValueError("Missing OpenAI API key")
        
        # Load context files
        self.load_context_files()
    
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
    
    def load_context_files(self):
        """Load all files from context directory for AI reference"""
        if not CONTEXT_DIR.exists():
            return
        
        for file_path in CONTEXT_DIR.rglob("*"):
            if file_path.is_file():
                try:
                    # Read text files
                    if file_path.suffix in ['.py', '.txt', '.md', '.json', '.js', '.html', '.css', '.sh']:
                        content = file_path.read_text()
                        self.context_files.append({
                            "name": file_path.name,
                            "path": str(file_path.relative_to(CONTEXT_DIR)),
                            "content": content,
                            "size": len(content)
                        })
                        self._log(f"Loaded context file: {file_path.name} ({len(content)} chars)")
                except Exception as e:
                    self._log(f"Warning: Could not load {file_path.name}: {e}")
    
    def get_context_summary(self) -> str:
        """Generate summary of available context for AI"""
        if not self.context_files:
            return ""
        
        summary = "\n\n=== AVAILABLE CONTEXT FILES ===\n"
        summary += "The following files are available for reference:\n\n"
        
        for ctx in self.context_files:
            summary += f"File: {ctx['path']}\n"
            summary += f"Size: {ctx['size']} characters\n"
            summary += f"Content preview:\n{ctx['content'][:500]}\n"
            summary += "-" * 60 + "\n\n"
        
        summary += "You can reference these files when writing code.\n"
        summary += "=" * 60 + "\n"
        
        return summary
    
    def interactive_prompt_review(self) -> Tuple[str, int]:
        """Let user review and edit the prompt and set iteration count"""
        task = self.config.get("task_description", "")
        max_iter = self.config.get("max_iterations", 10)
        
        print("\n" + "="*60)
        print("📝 PROMPT REVIEW")
        print("="*60)
        print(f"\nCurrent task:\n{task}\n")
        
        if self.context_files:
            print(f"\n📁 Context files loaded: {len(self.context_files)}")
            for ctx in self.context_files:
                print(f"  - {ctx['path']} ({ctx['size']} chars)")
        
        print(f"\nCurrent max iterations: {max_iter}")
        print("\nOptions:")
        print("  1. Continue with this prompt")
        print("  2. Edit the prompt")
        print("  3. Change max iterations")
        print("  4. Both edit prompt and change iterations")
        print("  5. Cancel")
        
        choice = input("\nYour choice (1-5): ").strip()
        
        if choice == "5":
            print("Cancelled.")
            sys.exit(0)
        
        if choice in ["2", "4"]:
            print("\n" + "-"*60)
            print("Enter new task description (press Ctrl+D when done):")
            print("-"*60)
            try:
                lines = []
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                task = "\n".join(lines)
                print("\n✓ Updated task description")
        
        if choice in ["3", "4"]:
            new_iter = input(f"\nEnter max iterations (current: {max_iter}): ").strip()
            if new_iter.isdigit():
                max_iter = int(new_iter)
                print(f"✓ Set max iterations to {max_iter}")
        
        # Save updated config
        self.config["task_description"] = task
        self.config["max_iterations"] = max_iter
        self.save_config()
        
        return task, max_iter
    
    def review_code_before_execution(self, code: str, language: str, block_num: int) -> bool:
        """Let user review code before execution"""
        print("\n" + "="*60)
        print(f"🔍 CODE REVIEW - Block {block_num} ({language})")
        print("="*60)
        print("\nGenerated code:")
        print("-"*60)
        print(code)
        print("-"*60)
        
        print("\nOptions:")
        print("  1. Execute this code")
        print("  2. Skip this code block")
        print("  3. Edit code before execution")
        print("  4. Abort agent")
        
        choice = input("\nYour choice (1-4): ").strip()
        
        if choice == "4":
            print("Aborting agent.")
            sys.exit(0)
        elif choice == "2":
            print("Skipping this code block.")
            return False
        elif choice == "3":
            print("\nEnter edited code (press Ctrl+D when done):")
            print("-"*60)
            try:
                lines = []
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                edited_code = "\n".join(lines)
                # Save edited code to workspace
                temp_file = WORKSPACE_DIR / f"edited_block_{block_num}.{language}"
                temp_file.write_text(edited_code)
                print(f"\n✓ Saved edited code to {temp_file}")
        
        return True
    
    def demo_final_product(self):
        """Run demo of the final product"""
        print("\n" + "="*60)
        print("🎬 DEMO MODE")
        print("="*60)
        
        # List all files in workspace
        files = list(WORKSPACE_DIR.glob("*"))
        if not files:
            print("No files in workspace to demo.")
            return
        
        print("\nFiles available for demo:")
        for i, f in enumerate(files, 1):
            print(f"  {i}. {f.name}")
        
        print("\nOptions:")
        print("  - Enter file number to run it")
        print("  - 'all' to run all Python/bash scripts")
        print("  - 'save' to save outputs")
        print("  - 'quit' to exit demo")
        
        while True:
            choice = input("\nDemo choice: ").strip().lower()
            
            if choice == "quit":
                break
            elif choice == "save":
                self.save_outputs()
            elif choice == "all":
                self.run_all_scripts()
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    self.run_file(files[idx])
            else:
                print("Invalid choice.")
    
    def run_file(self, file_path: Path):
        """Run a single file"""
        print(f"\n🚀 Running {file_path.name}...")
        print("-"*60)
        
        if file_path.suffix == ".py":
            result = subprocess.run(["python3", str(file_path)], 
                                  capture_output=True, text=True, timeout=30)
        elif file_path.suffix == ".sh":
            result = subprocess.run(["bash", str(file_path)], 
                                  capture_output=True, text=True, timeout=30)
        else:
            print(f"Cannot execute {file_path.suffix} files")
            return
        
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
        print("-"*60)
    
    def run_all_scripts(self):
        """Run all executable scripts"""
        scripts = list(WORKSPACE_DIR.glob("*.py")) + list(WORKSPACE_DIR.glob("*.sh"))
        for script in scripts:
            self.run_file(script)
    
    def save_outputs(self):
        """Save successful outputs to outputs directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_subdir = OUTPUT_DIR / f"run_{timestamp}"
        output_subdir.mkdir(exist_ok=True)
        
        import shutil
        for file in WORKSPACE_DIR.glob("*"):
            if file.is_file():
                shutil.copy(file, output_subdir / file.name)
        
        print(f"\n✓ Saved outputs to: {output_subdir}")
        print(f"  Files: {len(list(output_subdir.glob('*')))}")
    
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "max_iterations": 10,
                "task_description": "",
                "model": "gpt-3.5-turbo"
            }
        except json.JSONDecodeError as e:
            self._log(f"ERROR: Invalid JSON in config: {e}")
            sys.exit(1)
    
    def save_config(self):
        """Save configuration"""
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)
    
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
        
        model = self.config.get("model", "gpt-3.5-turbo")
        
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
            time.sleep(2)
            return ""
    
    def extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code blocks from ChatGPT response"""
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
            system_prompt = """You are a code generator for an autonomous Linux system (Ubuntu 24.04).
You MUST provide working code to accomplish the user's task.

CRITICAL RULES:
1. ALWAYS provide code in markdown code blocks (```python or ```bash)
2. Make code complete and runnable (include all imports)
3. DO NOT ask questions - just write the code
4. When task is complete, add "TASK COMPLETE" to your response

You are running in an automated environment. Your code will be automatically executed."""

            # Add context files to the prompt
            context_summary = self.get_context_summary()
            
            user_message = f"""Write complete, working code for this task:

TASK: {task}

Requirements:
- Ubuntu 24.04 LTS environment
- Non-interactive (no user input)
- Include all necessary imports
- Handle errors gracefully
- Provide code in markdown code blocks

{context_summary}

Write the code NOW."""
            
        else:
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
            self._log("\n✓ ChatGPT indicates task is complete!")
            self.state["task_completed"] = True
            return True
        
        code_blocks = self.extract_code_blocks(response)
        
        if not code_blocks:
            self._log("WARNING: No code blocks found in response")
            self.state["last_feedback"] = f"ERROR: No code provided. Please provide code for: {task}"
            return False
        
        execution_results = []
        
        for idx, (language, code) in enumerate(code_blocks):
            self._log(f"\n--- Code Block {idx + 1} ({language}) ---")
            
            # Interactive code review
            if self.interactive:
                should_execute = self.review_code_before_execution(code, language, idx + 1)
                if not should_execute:
                    continue
            
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
                feedback_parts.append(f"✓ Code block {result['block_number']} executed successfully.")
                if result["stdout"]:
                    feedback_parts.append(f"Output:\n{result['stdout']}")
            else:
                feedback_parts.append(f"✗ Code block {result['block_number']} failed.")
                if result["stderr"]:
                    feedback_parts.append(f"Error:\n{result['stderr']}")
        
        feedback = "\n\n".join(feedback_parts)
        feedback += "\n\nAnalyze results and provide improved code, or indicate 'TASK COMPLETE' if done."
        
        self.state["last_feedback"] = feedback
        
        return False
    
    def run(self):
        """Main execution loop"""
        # Interactive prompt review before starting
        if self.interactive:
            task, max_iterations = self.interactive_prompt_review()
        else:
            task = self.config.get("task_description")
            max_iterations = self.config.get("max_iterations", 10)
        
        self._log("\n" + "="*60)
        self._log("ENHANCED INTERACTIVE CODING AGENT STARTED")
        self._log("="*60)
        self._log(f"Task: {task}")
        self._log(f"Max iterations: {max_iterations}")
        self._log(f"Context files: {len(self.context_files)}")
        
        while self.state["iteration"] < max_iterations:
            task_complete = self.run_iteration()
            
            self.state["iteration"] += 1
            self.state["last_run"] = datetime.now().isoformat()
            self.save_state()
            
            if task_complete:
                self._log("\n" + "="*60)
                self._log("TASK COMPLETED SUCCESSFULLY!")
                self._log("="*60)
                
                # Demo mode
                if self.interactive:
                    self.demo_final_product()
                
                return 0
            
            time.sleep(2)
        
        self._log("\n" + "="*60)
        self._log(f"Maximum iterations ({max_iterations}) reached")
        self._log("="*60)
        return 1


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Interactive Coding Agent")
    parser.add_argument("--non-interactive", action="store_true", 
                       help="Run in non-interactive mode (no prompts)")
    
    args = parser.parse_args()
    
    try:
        agent = InteractiveCodingAgent(interactive=not args.non_interactive)
        exit_code = agent.run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
