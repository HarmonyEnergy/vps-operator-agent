#!/bin/bash

# Quick Install Script for Interactive Coding Agent
# Just run: bash install_interactive.sh

set -e

echo "=========================================="
echo "  Installing Interactive Coding Agent"
echo "=========================================="
echo ""

cd /opt/coding-agent

# Check if we're in the right directory
if [ ! -f "agent_config.json" ]; then
    echo "❌ Error: Not in /opt/coding-agent directory"
    exit 1
fi

echo "📁 Creating required directories..."
mkdir -p context outputs
echo "✓ Created context/ and outputs/"
echo ""

echo "📝 Backing up original agent..."
if [ -f "coding_agent.py" ]; then
    cp coding_agent.py coding_agent_original_backup.py
    echo "✓ Backed up to coding_agent_original_backup.py"
fi
echo ""

echo "⬇️  Downloading interactive agent..."
# If the file was uploaded via scp, it should be in /root/
if [ -f "/root/coding_agent_interactive.py" ]; then
    cp /root/coding_agent_interactive.py .
    chmod +x coding_agent_interactive.py
    echo "✓ Installed from /root/"
elif [ -f "coding_agent_interactive.py" ]; then
    chmod +x coding_agent_interactive.py
    echo "✓ Already exists, made executable"
else
    echo "❌ coding_agent_interactive.py not found!"
    echo ""
    echo "Please upload it first:"
    echo "  scp coding_agent_interactive.py root@72.62.170.164:/opt/coding-agent/"
    exit 1
fi
echo ""

echo "🧪 Testing installation..."
python3 coding_agent_interactive.py --help 2>/dev/null && echo "✓ Script is valid" || echo "⚠️  Script may have issues"
echo ""

echo "=========================================="
echo "  ✅ Installation Complete!"
echo "=========================================="
echo ""
echo "📚 Usage:"
echo ""
echo "  # Interactive mode (with prompts)"
echo "  python3 coding_agent_interactive.py"
echo ""
echo "  # Non-interactive mode (automatic)"
echo "  python3 coding_agent_interactive.py --non-interactive"
echo ""
echo "📁 Directory Structure:"
echo "  /opt/coding-agent/"
echo "  ├── coding_agent_interactive.py  ← New enhanced agent"
echo "  ├── coding_agent.py              ← Original agent"
echo "  ├── context/                     ← Upload files here"
echo "  └── outputs/                     ← Saved results here"
echo ""
echo "💡 Quick Start:"
echo "  1. (Optional) Upload context files to context/"
echo "  2. Run: python3 coding_agent_interactive.py"
echo "  3. Choose max iterations (3 for testing)"
echo "  4. Review and approve code"
echo "  5. Demo the results!"
echo ""
