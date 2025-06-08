#!/bin/bash

# code in codex to run this:
# chmod +x test-docs.sh
# ./test-docs.sh

set -e

uv venv .venv
source .venv/bin/activate
uv pip install mkdocs-material
mkdocs build
