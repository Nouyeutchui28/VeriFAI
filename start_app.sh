#!/bin/bash
# VeriFAI LLM - Multi-component Start Script
# This script starts both the FastAPI backend and the Streamlit frontend.

# Configuration
PROJECT_DIR="/home/bruns/Pictures/VeriFAI LLM"
VENV_PATH="$PROJECT_DIR/venv"
BACKEND_PORT=8000
FRONTEND_PORT=8502

echo "🚀 Starting VeriFAI LLM..."
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Export variables from .env if needed
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 1. Start FastAPI Backend in background
echo "📡 Starting Backend on port $BACKEND_PORT..."
python -m uvicorn src.api.main:app --host 0.0.0.0 --port $BACKEND_PORT > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/health > /dev/null; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start (timeout). Check backend.log"
        kill $BACKEND_PID
        exit 1
    fi
    sleep 1
done

# 2. Start Streamlit Frontend
echo "🎨 Starting Frontend on port $FRONTEND_PORT..."
streamlit run app.py --server.port $FRONTEND_PORT
