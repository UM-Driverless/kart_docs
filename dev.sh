#!/bin/bash
set -e

# Create and activate virtual environment
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  uv venv .venv
fi

source .venv/bin/activate

# Install dependencies
uv pip install mkdocs-material

# Serve docs
mkdocs serve
