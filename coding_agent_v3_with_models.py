#!/usr/bin/env python3
"""
Enhanced Interactive Coding Agent v2.0
Features:
- Fetches available models from OpenAI API in real-time
- Interactive model selection with live pricing
- Cost tracking per session
- All previous interactive features
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
CONTEXT_DIR = BASE_DIR / "context"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_FILE = Path("/var/log/coding_agent.log")

WORKSPACE_DIR.mkdir(exist_ok=True)
CONTEXT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Model pricing database (fallback if API doesn't provide pricing)
MODEL_PRICING = {
    "o4-mini": {"input": 5.0, "output": 5.0, "tier": "reasoning", "speed": "medium", "recommended": True},
    "gpt-4o": {"input": 2.50, "output": 10.0, "tier": "premium", "speed": "fast", "recommended": False},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "tier": "fast", "speed": "very-fast", "recommended": False},
    "o1-mini": {"input": 3.0, "output": 12.0, "tier": "reasoning", "speed": "slow", "recommended": False},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50, "tier": "basic", "speed": "fast", "recommended": False},
}


class InteractiveCodingAgent:
    """Enhanced interactive coding agent with live model selection"""
    
    def __init__(self, interactive=True):
        self.interactive = interactive
        self.config = self.load_config()
        self.state = self.load_state()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.conversation_history = []
        self.context_files = []
        self.session_cost = 0.0
        self.tokens_used = {"input": 0, "output": 0}
        self.available_models = []
        
        if not self.openai_api_key:
            self._log("ERROR: OPENAI_API_KEY not found in environment")
            raise ValueError("Missing OpenAI API key")
        
        # Fetch available models from OpenAI
        if interactive:
            self.fetch_available_models()
        
        self.load_context_files()
    
    def _log(self, msg: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        
        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_msg + "\n")
        except:
            pass
    
    def fetch_available_models(self):
        """Fetch available models from OpenAI API"""
        print("\n🔍 Fetching available models from OpenAI API...")
        
        try:
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            all_models = data.get("data", [])
            
            # Filter for chat/completion models only
            chat_models = []
            for model in all_models:
                model_id = model.get("id", "")
                # Include GPT models and reasoning models (o-series)
                if any(prefix in model_id for prefix in ["gpt-", "o1-", "o4-", "o3-"]):
                    if "vision" not in model_id and "instruct" not in model_id:
                        chat_models.append(model_id)
            
            # Sort by relevance (reasoning models first, then GPT-4, then GPT-3.5)
            def model_priority(m):
                if m.startswith("o4"): return 0
                if m.startswith("o1"): return 1
                if "gpt-4o" in m and "mini" not in m: return 2
                if "gpt-4o-mini" in m: return 3
                if "gpt-4" in m: return 4
                if "gpt-3.5" in m: return 5
                return 10
            
            chat_models.sort(key=model_priority)
            self.available_models = chat_models[:10]  # Top 10 most relevant
            
            print(f"✓ Found {len(self.available_models)} available models")
            
        except Exception as e:
            print(f"⚠️  Could not fetch models from API: {e}")
            print("Using fallback model list...")
            self.available_models = list(MODEL_PRICING.keys())
    
    def get_model_info(self, model_id: str) -> dict:
        """Get pricing and info for a model"""
        # Check if we have pricing data
        for key in MODEL_PRICING:
            if key in model_id:
                info = MODEL_PRICING[key].copy()
                info["id"] = model_id
                return info
        
        # Default fallback
        return {
            "id": model_id,
            "input": 1.0,
            "output": 3.0,
            "tier": "unknown",
            "speed": "unknown",
            "recommended": False
        }
    
    def display_model_selection(self):
        """Display interactive model selection UI"""
        print("\n" + "="*75)
        print("🤖 MODEL SELECTION - Choose your AI model")
        print("="*75)
        
        for idx, model_id in enumerate(self.available_models, 1):
            info = self.get_model_info(model_id)
            
            # Format display
            recommended = " ⭐ RECOMMENDED" if info.get("recommended") else ""
            tier_emoji = {"reasoning": "🧠", "premium": "💎", "fast": "⚡", "basic": "📝"}.get(info["tier"], "🤖")
            
            print(f"\n{idx}. {tier_emoji} {model_id}{recommended}")
            print(f"   Pricing: ${info['input']}/1M input, ${info['output']}/1M output tokens")
            print(f"   Speed: {info['speed'].upper()} | Tier: {info['tier'].upper()}")
            
            # Add descriptions
            descriptions = {
                "o4-mini": "Best for coding agents - reasoning optimized for iteration",
                "gpt-4o": "Fast, intelligent multimodal - great all-rounder",
                "gpt-4o-mini": "Fastest and cheapest - good for simple tasks",
                "o1-mini": "Advanced reasoning - for complex debugging",
                "gpt-3.5-turbo": "Cheapest option - basic tasks only"
            }
            
            for key, desc in descriptions.items():
                if key in model_id:
                    print(f"   {desc}")
                    break
        
        print("\n" + "-"*75)
        
        while True:
            choice = input(f"\nSelect model (1-{len(self.available_models)}) or Enter for recommended: ").strip()
            
            if choice == "":
                # Return recommended
                for model_id in self.available_models:
                    info = self.get_model_info(model_id)
                    if info.get("recommended"):
                        print(f"✓ Using recommended: {model_id}")
                        return model_id
                # If no recommended, use first
                print(f"✓ Using: {self.available_models[0]}")
                return self.available_models[0]
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.available_models):
                    selected = self.available_models[idx]
                    print(f"✓ Selected: {selected}")
                    return selected
            
            print("Invalid choice. Try again.")
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for tokens"""
        info = self.get_model_info(model)
        input_cost = (input_tokens / 1_000_000) * info["input"]
        output_cost = (output_tokens / 1_000_000) * info["output"]
        return input_cost + output_cost
    
    def display_session_stats(self):
        """Display session statistics"""
        print("\n" + "="*75)
        print("📊 SESSION STATISTICS")
        print("="*75)
        print(f"Iterations completed: {self.state['iteration']}")
        print(f"Tokens used: {self.tokens_used['input']:,} input / {self.tokens_used['output']:,} output")
        print(f"Estimated cost: ${self.session_cost:.4f}")
        print("="*75)
    
    def load_context_files(self):
        """Load context files"""
        if not CONTEXT_DIR.exists():
            return
        
        for file_path in CONTEXT_DIR.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.txt', '.md', '.json', '.js', '.sh']:
                try:
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
        """Generate context summary"""
        if not self.context_files:
            return ""
        
        summary = "\n\n=== AVAILABLE CONTEXT FILES ===\n"
        for ctx in self.context_files:
            summary += f"File: {ctx['path']} ({ctx['size']} chars)\n"
            summary += f"{ctx['content'][:300]}...\n\n"
        return summary
    
    def interactive_prompt_review(self) -> Tuple[str, int, str]:
        """Review prompt, iterations, and select model"""
        task = self.config.get("task_description", "")
        max_iter = self.config.get("max_iterations", 10)
        
        # Model selection
        if self.interactive:
            model = self.display_model_selection()
        else:
            model = self.config.get("model", "o4-mini")
        
        print("\n" + "="*75)
        print("📝 PROMPT REVIEW")
        print("="*75)
        print(f"\nTask: {task}\n")
        print(f"📁 Context files: {len(self.context_files)}")
        print(f"🔢 Max iterations: {max_iter}")
        print(f"🤖 Model: {model}")
        
        print("\nOptions:")
        print("  1. Continue")
        print("  2. Edit task")
        print("  3. Change iterations")
        print("  4. Edit task & iterations")
        print("  5. Cancel")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "5":
            sys.exit(0)
        
        if choice in ["2", "4"]:
            print("\nEnter new task (Ctrl+D when done):")
            lines = []
            try:
                while True:
                    lines.append(input())
            except EOFError:
                task = "\n".join(lines)
        
        if choice in ["3", "4"]:
            new_iter = input(f"\nMax iterations (current: {max_iter}): ").strip()
            if new_iter.isdigit():
                max_iter = int(new_iter)
        
        self.config["task_description"] = task
        self.config["max_iterations"] = max_iter
        self.config["model"] = model
        self.save_config()
        
        return task, max_iter, model
    
    def load_config(self) -> dict:
        """Load config"""
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except:
            return {"max_iterations": 10, "task_description": "", "model": "o4-mini"}
    
    def save_config(self):
        """Save config"""
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def load_state(self) -> dict:
        """Load state"""
        try:
            with open(STATE_PATH) as f:
                return json.load(f)
        except:
            return {"iteration": 0, "task_completed": False}
    
    def save_state(self):
        """Save state"""
        with open(STATE_PATH, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def call_chatgpt(self, user_message: str, system_prompt: Optional[str], model: str) -> str:
        """Call OpenAI API"""
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
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        try:
            self._log(f"Calling OpenAI API with {model}...")
            response = requests.post(url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Track costs
            if "usage" in result:
                usage = result["usage"]
                self.tokens_used["input"] += usage.get("prompt_tokens", 0)
                self.tokens_used["output"] += usage.get("completion_tokens", 0)
                cost = self.estimate_cost(usage.get("prompt_tokens", 0), 
                                        usage.get("completion_tokens", 0), model)
                self.session_cost += cost
            
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return assistant_message
            
        except Exception as e:
            self._log(f"ERROR: API call failed: {e}")
            return ""
    
    def extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code blocks"""
        import re
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return [(lang or "text", code.strip()) for lang, code in matches]
    
    def execute_code(self, code: str, language: str) -> Tuple[int, str, str]:
        """Execute code"""
        if language.lower() in ["python", "python3", "py"]:
            temp_file = WORKSPACE_DIR / f"temp_{int(time.time())}.py"
            temp_file.write_text(code)
            cmd = ["python3", str(temp_file)]
        elif language.lower() in ["bash", "sh", "shell"]:
            temp_file = WORKSPACE_DIR / f"temp_{int(time.time())}.sh"
            temp_file.write_text(code)
            temp_file.chmod(0o755)
            cmd = ["bash", str(temp_file)]
        else:
            return -1, "", f"Unsupported: {language}"
        
        try:
            result = subprocess.run(cmd, cwd=WORKSPACE_DIR, capture_output=True, 
                                  text=True, timeout=30)
            if temp_file.exists():
                temp_file.unlink()
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            return -1, "", str(e)
    
    def run_iteration(self, model: str) -> bool:
        """Run one iteration"""
        iteration = self.state["iteration"]
        task = self.config.get("task_description", "")
        
        self._log(f"\n{'='*75}")
        self._log(f"ITERATION {iteration + 1}")
        self._log(f"{'='*75}")
        
        if iteration == 0:
            system_prompt = f"""You are a code generator on Ubuntu 24.04. Model: {model}
ALWAYS provide code in markdown blocks. When complete, include 'TASK COMPLETE'."""
            
            context = self.get_context_summary()
            user_message = f"{task}\n\n{context}\n\nProvide complete runnable code."
        else:
            system_prompt = "Debug and improve code based on execution results."
            user_message = self.state.get("last_feedback", "Continue.")
        
        response = self.call_chatgpt(user_message, system_prompt, model)
        
        if not response:
            return False
        
        self._log(f"\nResponse:\n{response[:500]}...\n")
        
        if "TASK COMPLETE" in response.upper():
            self._log("✓ Task complete!")
            self.state["task_completed"] = True
            return True
        
        code_blocks = self.extract_code_blocks(response)
        
        if not code_blocks:
            self._log("WARNING: No code blocks")
            self.state["last_feedback"] = "Please provide code blocks."
            return False
        
        results = []
        for idx, (lang, code) in enumerate(code_blocks):
            self._log(f"\nExecuting {lang} code block {idx+1}...")
            rc, stdout, stderr = self.execute_code(code, lang)
            
            self._log(f"Return code: {rc}")
            if stdout: self._log(f"Output: {stdout[:300]}")
            if stderr: self._log(f"Error: {stderr[:300]}")
            
            results.append({
                "block": idx+1,
                "lang": lang,
                "rc": rc,
                "stdout": stdout[:500],
                "stderr": stderr[:500]
            })
        
        feedback = []
        for r in results:
            if r["rc"] == 0:
                feedback.append(f"✓ Block {r['block']} succeeded. Output: {r['stdout']}")
            else:
                feedback.append(f"✗ Block {r['block']} failed. Error: {r['stderr']}")
        
        self.state["last_feedback"] = "\n".join(feedback) + "\n\nAnalyze and improve."
        
        return False
    
    def run(self):
        """Main execution"""
        if self.interactive:
            task, max_iter, model = self.interactive_prompt_review()
        else:
            task = self.config.get("task_description")
            max_iter = self.config.get("max_iterations", 10)
            model = self.config.get("model", "o4-mini")
        
        self._log(f"\n{'='*75}")
        self._log("CODING AGENT STARTED")
        self._log(f"Model: {model}")
        self._log(f"Task: {task[:100]}...")
        self._log(f"Max iterations: {max_iter}")
        self._log(f"{'='*75}")
        
        while self.state["iteration"] < max_iter:
            complete = self.run_iteration(model)
            
            self.state["iteration"] += 1
            self.save_state()
            
            if complete:
                self.display_session_stats()
                return 0
            
            time.sleep(1)
        
        self.display_session_stats()
        return 1


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--non-interactive", action="store_true")
    args = parser.parse_args()
    
    try:
        agent = InteractiveCodingAgent(interactive=not args.non_interactive)
        sys.exit(agent.run())
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
