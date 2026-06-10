#!/bin/bash
set -e

# Find a free port starting at 8000 (override the start with: PORT=9000 ./dev.sh).
# We never kill whatever else is running — we just step to the next free port,
# so you don't have to think about "address already in use".
PORT="${PORT:-8000}"
while lsof -ti ":$PORT" >/dev/null 2>&1; do
  echo "Port $PORT busy, trying $((PORT+1))..."
  PORT=$((PORT+1))
done

# Create and activate virtual environment
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  uv venv .venv
fi

source .venv/bin/activate

# Install dependencies
uv pip install mkdocs-material

# Serve docs on the free port we found
echo "Serving docs at http://127.0.0.1:$PORT"
mkdocs serve -a "127.0.0.1:$PORT"
