#!/bin/bash
# VeriFAI LLM - Interactive CLI Launcher
PROJECT_DIR="/home/bruns/Documents/VeriFAI 1/VeriFAI LLM"
VENV_PATH="$PROJECT_DIR/venv"

cd "$PROJECT_DIR"

if [ -d "$VENV_PATH" ]; then
    "$VENV_PATH/bin/python" cli.py --interactive "$@"
else
    python3 cli.py --interactive "$@"
fi
