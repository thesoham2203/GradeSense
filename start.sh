#!/bin/bash
# Railway startup script
echo "Starting GradeSense API..."

# Copy minimal requirements for Railway
cp requirements-minimal.txt requirements.txt

# Install minimal dependencies
pip install --no-cache-dir -r requirements.txt

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port $PORT
