#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

def test_environment():
    print("🔍 Testing Coding Agent Environment\n")
    
    tests_passed = 0
    tests_failed = 0
    
    print("Test 1: Workspace directory...")
    workspace = Path("./workspace")
    if workspace.exists() and workspace.is_dir():
        print("  ✓ Workspace directory exists\n")
        tests_passed += 1
    else:
        print("  ✗ Workspace directory not found\n")
        tests_failed += 1
    
    print("Test 2: Configuration file...")
    config_path = Path("./agent_config.json")
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            print(f"  ✓ Config loaded successfully")
            print(f"  Task: {config.get('task_description', 'Not set')[:50]}...")
            print()
            tests_passed += 1
        except Exception as e:
            print(f"  ✗ Config file invalid: {e}\n")
            tests_failed += 1
    else:
        print("  ✗ Config file not found\n")
        tests_failed += 1
    
    print("Test 3: Python code execution...")
    test_code = 'print("Hello from Python!")'
    test_file = workspace / "test_python.py"
    
    try:
        test_file.write_text(test_code)
        result = subprocess.run(
            ["python3", str(test_file)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "Hello" in result.stdout:
            print(f"  ✓ Python execution works")
            print(f"  Output: {result.stdout.strip()}\n")
            tests_passed += 1
        else:
            print(f"  ✗ Python execution failed\n")
            tests_failed += 1
        test_file.unlink()
    except Exception as e:
        print(f"  ✗ Python test error: {e}\n")
        tests_failed += 1
    
    print("="*50)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print("="*50)
    
    if tests_failed == 0:
        print("\n✅ Environment is ready! You can now run the agent.")
        print("\nNext steps:")
        print("1. Set OPENAI_API_KEY in /etc/coding_agent.env")
        print("2. Configure your task in agent_config.json")
        print("3. Run: ./run_agent.sh")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    return tests_failed == 0

if __name__ == "__main__":
    test_environment()
