#!/bin/bash

# Kart Documentation Installation Script
# This script ensures all dependencies are properly installed

set -e  # Exit on any error

echo "🚀 Starting Kart Documentation installation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Linux/macOS
if [[ "$OSTYPE" != "linux-gnu"* && "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for Linux and macOS only"
    exit 1
fi

# Install system dependencies
print_status "Installing system dependencies..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y curl git build-essential libssl-dev zlib1g-dev \
            libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
            libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
            liblzma-dev python3-openssl
    # CentOS/RHEL/Fedora
    elif command -v yum &> /dev/null; then
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y curl git openssl-devel bzip2-devel libffi-devel \
            zlib-devel readline-devel sqlite-devel wget xz-devel tk-devel
    elif command -v dnf &> /dev/null; then
        sudo dnf groupinstall -y "Development Tools"
        sudo dnf install -y curl git openssl-devel bzip2-devel libffi-devel \
            zlib-devel readline-devel sqlite-devel wget xz-devel tk-devel
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v brew &> /dev/null; then
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install openssl readline sqlite3 xz zlib tcl-tk
fi

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    print_status "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add uv to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"

    # Add to shell profile
    SHELL_PROFILE=""
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_PROFILE="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_PROFILE="$HOME/.bashrc"
    fi

    if [[ -n "$SHELL_PROFILE" ]] && ! grep -q "/.local/bin" "$SHELL_PROFILE"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_PROFILE"
        print_status "Added uv to $SHELL_PROFILE"
    fi
else
    print_status "uv is already installed"
fi

# Ensure uv is in PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Install project dependencies
print_status "Installing project dependencies with uv..."
uv sync

# Install Playwright browsers
print_status "Installing Playwright browsers..."
uv run playwright install --force chrome

# Verify installation
print_status "Verifying installation..."
uv run python --version
uv run mkdocs --version

# Test that MkDocs can build the docs
print_status "Testing MkDocs build..."
uv run mkdocs build --clean

print_status "✅ Installation completed successfully!"
print_status ""
print_status "To start the documentation server, run:"
print_status "  uv run mkdocs serve"
print_status ""
print_status "To activate the virtual environment for development:"
print_status "  source .venv/bin/activate"
print_status ""
print_warning "Note: You may need to restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc) to use uv commands."