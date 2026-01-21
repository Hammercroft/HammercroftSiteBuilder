#!/bin/bash
# HCS Builder launcher script for Linux/macOS
# This script checks for Python 3 and runs hcsbuilder.py

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/hcsbuilder.py"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# Check if virtual environment exists and use it
if [ -f "$VENV_PYTHON" ]; then
    # Use virtual environment Python
    "$VENV_PYTHON" "$PYTHON_SCRIPT" "$@"
    exit $?
elif command -v python3 &> /dev/null; then
    # Fall back to system Python 3
    echo "WARNING: Virtual environment not found, using system Python 3"
    python3 "$PYTHON_SCRIPT" "$@"
    exit $?
else
    # Python 3 not found
    echo "ERROR: Python 3 is not installed or not in your PATH."
    echo ""
    echo "Please install Python 3 to use HCS Builder:"
    echo "  - On Ubuntu/Debian: sudo apt-get install python3"
    echo "  - On Fedora/RHEL: sudo dnf install python3"
    echo "  - On macOS: brew install python3"
    echo "  - Or download from: https://www.python.org/downloads/"
    echo ""
    exit 1
fi
