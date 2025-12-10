#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  SIR'S THISVID RIPPER"
echo "════════════════════════════════════════════════════════════════"
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Install it from https://python.org/downloads or via your package manager."
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
pip3 install -r requirements.txt --quiet

echo
echo "Starting ripper..."
echo
python3 thisvid_scraper.py
