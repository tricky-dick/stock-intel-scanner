@echo off
title Stock Intel Scanner

echo Starting Stock Intel Scanner...

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Launching scanner...
python scanner.py

pause
