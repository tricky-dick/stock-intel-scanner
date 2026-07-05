#!/bin/bash

echo "Starting Stock Intel Scanner..."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Launching scanner..."
python3 scanner.py
