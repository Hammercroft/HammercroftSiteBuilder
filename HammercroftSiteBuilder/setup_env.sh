#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Change to the script directory to ensure relative paths work as expected
cd "$SCRIPT_DIR"

echo "=== HCS Builder Setup ==="

# 1. Create .venv directory
if [ -d ".venv" ]; then
    echo ".venv directory already exists."
else
    echo "Creating .venv directory..."
    mkdir .venv
fi

# 2. Create virtual environment
echo "Initializing virtual environment..."
python3 -m venv .venv

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment."
    echo "Please ensure python3-venv is installed."
    exit 1
fi

# 3. Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# 4. Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install requirements."
        deactivate
        exit 1
    fi
else
    echo "WARNING: requirements.txt not found!"
fi

echo ""
echo "=== Setup Complete ==="
echo "You can now run the builder using: ./hcsbuilder.sh"
echo ""

# Deactivate before exiting to be clean, though script exit clears it anyway for the parent shell
deactivate
