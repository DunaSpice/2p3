#!/bin/bash

# Installer script for your Python script

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python3 is not installed. Please install Python3 before running this script."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &>/dev/null; then
    echo "pip3 is not installed. Please install pip3 before running this script."
    exit 1
fi

# Install Python packages from requirements.txt
if [ -f requirements.txt ]; then
    echo "Installing Python packages from requirements.txt..."
    pip3 install -r requirements.txt
else
    echo "requirements.txt not found. Skipping Python package installation."
fi

# Check and install any system-level dependencies here if needed

# Run the Python script
python3 your_script.py

# Exit
exit 0
