#!/bin/bash
# Reset Output Directory Script
# Clears ./output and clones ./_output to ./output

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Define directories
OUTPUT_DIR="./output"
SOURCE_DIR="./_output"

echo "Resetting output directory..."

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "ERROR: Source directory '$SOURCE_DIR' does not exist!"
    exit 1
fi

# Remove output directory if it exists
if [ -d "$OUTPUT_DIR" ]; then
    echo "Removing existing output directory..."
    rm -rf "$OUTPUT_DIR"
fi

# Copy _output to output
echo "Cloning '$SOURCE_DIR' to '$OUTPUT_DIR'..."
cp -r "$SOURCE_DIR" "$OUTPUT_DIR"

echo "Output directory reset complete!"
echo "Contents of '$OUTPUT_DIR':"
ls -la "$OUTPUT_DIR"

# chmod serve.py to be executable
chmod +x "$OUTPUT_DIR/serve.py"