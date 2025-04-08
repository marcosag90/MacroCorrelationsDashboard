#!/bin/bash

echo "Cleaning environment..."

# Remove the virtual environment
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Recreate the virtual environment
echo "Creating a new virtual environment..."
python3 -m venv venv

# Install dependencies
echo "Installing dependencies..."
source venv/bin/activate

pip install -r requirements.txt

echo "Environment reset complete."
