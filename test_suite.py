#!/usr/bin/env python3
"""Comprehensive test suite for VPS operator agent."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import tools_enhanced as tools

def test_shell_safety():
    """Test that dangerous commands are blocked."""
    print("Testing shell safety...")
    
    dangerous_commands = [
        "rm -rf /",
        "dd if=/dev/zero of=/dev/sda",
        "mkfs.ext4 /dev/sda1",
        ":(){:|:&};:",
        "chmod 777 /etc/passwd",
    ]
    
    for cmd in dangerous_commands:
        result = tools.run_shell(cmd)
        assert result['returncode'] == 126, f"Failed to block: {cmd}"
        assert 'BLOCKED' in result['stderr'], f"No block message for: {cmd}"
    
    print("✓ All dangerous commands blocked")

def test_shell_pipes():
    """Test that pipes and redirects work."""
    print("Testing shell syntax support...")
    
    # Test pipe
    result = tools.run_shell("echo 'test' | wc -l")
    assert result['returncode'] == 0, "Pipe command failed"
    assert '1' in result['stdout'], "Pipe didn't work"
    
    # Test redirect
    result = tools.run_shell("echo 'hello' > test_output.txt")
    assert result['returncode'] == 0, "Redirect failed"
    
    # Verify file was created
    read_result = tools.read_file("test_output.txt")
    assert 'hello' in read_result.get('content', ''), "Redirect didn't write file"
    
    print("✓ Shell syntax working (pipes, redirects)")

def test_workspace_isolation():
    """Test that operations are confined to workspace."""
    print("Testing workspace isolation...")
    
    # Try to write outside workspace (should fail)
    result = tools.write_file("../escape.txt", "malicious")
    assert not result.get('success', False), "Escaped workspace!"
    
    # Try to read outside workspace
    result = tools.read_file("../../../etc/passwd")
    assert 'error' in result, "Read outside workspace!"
    
    print("✓ Workspace isolation enforced")

def test_file_operations():
    """Test file read/write."""
    print("Testing file operations...")
    
    content = "Test content\nLine 2\nLine 3"
    
    # Write
    result = tools.write_file("test_file.txt", content)
    assert result.get('success'), "Write failed"
    
    # Read
    result = tools.read_file("test_file.txt")
    assert result.get('content') == content, "Read didn't match write"
    
    print("✓ File operations working")

def test_python_execution():
    """Test Python code execution."""
    print("Testing Python execution...")
    
    code = """
print("Hello from Python")
with open("python_output.txt", "w") as f:
    f.write("Python was here")
"""
    
    result = tools.run_python(code, "test_script.py")
    assert result['returncode'] == 0, "Python execution failed"
    assert "Hello from Python" in result['stdout'], "Python output missing"
    
    # Verify file was created
    read_result = tools.read_file("python_output.txt")
    assert "Python was here" in read_result.get('content', ''), "Python didn't write file"
    
    print("✓ Python execution working")

def test_deliverables_detection():
    """Test that deliverables are detected."""
    print("Testing deliverables detection...")
    
    # Create some files
    tools.write_file("report.txt", "Report content")
    tools.write_file("data.json", '{"key": "value"}')
    tools.write_file("output/results.csv", "a,b,c\n1,2,3")
    
    deliverables = tools.list_deliverables()
    
    assert len(deliverables) >= 3, f"Expected >= 3 deliverables, got {len(deliverables)}"
    assert any('report.txt' in d for d in deliverables), "Missing report.txt"
    assert any('data.json' in d for d in deliverables), "Missing data.json"
    assert any('results.csv' in d for d in deliverables), "Missing results.csv"
    
    print(f"✓ Deliverables detection working ({len(deliverables)} files found)")

def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("VPS OPERATOR AGENT - TEST SUITE")
    print("=" * 60)
    
    try:
        test_shell_safety()
        test_shell_pipes()
        test_workspace_isolation()
        test_file_operations()
        test_python_execution()
        test_deliverables_detection()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(run_all_tests())
