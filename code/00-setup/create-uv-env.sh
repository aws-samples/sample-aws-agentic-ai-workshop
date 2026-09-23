#!/bin/bash

# UV environment setup and Jupyter kernel registration script (pyproject.toml based)
# Usage: ./create-uv-env.sh <env-name> [python-version]

set -e  # stop the script on any error

# Remember the script directory (used later)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions: output messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print usage
usage() {
    echo "Usage: $0 <env-name> [python-version]"
    echo ""
    echo "Examples:"
    echo "  $0 myenv"
    echo "  $0 myenv 3.12"
    echo ""
    echo "Options:"
    echo "  env-name        : name of the environment to create (required)"
    echo "  python-version  : Python version to use (optional, default: 3.12)"
    echo ""
    echo "pyproject.toml requires Python >=3.12, so use 3.12 or later."
    exit 1
}

# Validate arguments
if [ $# -lt 1 ]; then
    print_error "An environment name is required."
    usage
fi

ENV_NAME=$1
PYTHON_VERSION=${2:-3.12}
VENV_PATH=".venv"  # set the virtual environment path explicitly

print_info "Starting environment setup..."
print_info "Environment name: $ENV_NAME"
print_info "Python version: $PYTHON_VERSION"
print_info "Virtual environment path: $VENV_PATH"

# Clean up any existing virtual environment
if [ -d "$VENV_PATH" ]; then
    print_warning "Removing the existing virtual environment: $VENV_PATH"
    rm -rf .venv
    print_success "The existing virtual environment has been removed."
fi

# Check for UV and install it automatically
install_uv() {
    print_info "Installing UV..."

    # Use the official installer (recommended)
    print_info "Using the official installer script..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Update PATH (add the possible install locations)
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

    # Source the env file if there is one
    if [ -f "$HOME/.local/bin/env" ]; then
        source "$HOME/.local/bin/env"
    fi

    # Verify the installation
    if command -v uv &> /dev/null; then
        print_success "UV has been installed successfully!"
        uv --version
    else
        print_error "UV installation failed."
        print_info "Manual installation options:"
        echo "  1. Official script: curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "  2. pip: pip install uv"
        echo "  3. pipx: pipx install uv"
        exit 1
    fi
}

if ! command -v uv &> /dev/null; then
    print_warning "UV is not installed."
    read -p "Install UV automatically? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_uv
    else
        print_error "UV is required. Please install it manually."
        print_info "Installation options:"
        echo "  1. Official script (recommended): curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "  2. pip: pip install uv"
        echo "  3. pipx: pipx install uv"
        exit 1
    fi
fi

# 1. Set the Python version (before creating the virtual environment)
print_info "Setting Python $PYTHON_VERSION..."
uv python pin $PYTHON_VERSION
print_success "Python $PYTHON_VERSION has been set."

# 2. Initialize the project
print_info "Initializing the project..."
if [ ! -f "pyproject.toml" ]; then
    uv init --name "$ENV_NAME"
    print_success "The project has been initialized as '$ENV_NAME'."
else
    print_warning "pyproject.toml already exists. Using the existing project."
fi

# 3. Add the required packages
print_info "Adding the required Jupyter packages..."
uv add ipykernel jupyter

# 4. Check pyproject.toml and install dependencies
if [ -f "pyproject.toml" ]; then
    print_info "Found pyproject.toml. Syncing dependencies..."

    # Sync the environment from the dependencies in pyproject.toml
    uv sync

    print_success "Dependencies have been installed from pyproject.toml."
    print_info "The lock file was created/updated automatically: uv.lock"
else
    print_error "pyproject.toml is missing. Project initialization may have failed."
    exit 1
fi

print_info "Installing system packages..."

# Install Node.js and npm
print_info "Checking for Node.js and npm..."
if ! command -v node &> /dev/null; then
    print_warning "Node.js is not installed."

    # On macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            print_info "Installing Node.js with Homebrew..."
            brew install node
        else
            print_warning "Homebrew is not installed."
            print_info "Please install Node.js manually: https://nodejs.org/"
        fi
    # On Linux
    else
        print_info "Installing the Node.js LTS release via NodeSource..."
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo dnf install -y nodejs
    fi

    # Verify the installation
    if command -v node &> /dev/null; then
        print_success "Node.js has been installed successfully!"
        node --version
        npm --version
    else
        print_warning "Node.js installation failed. Please install it manually."
        print_info "Installation URL: https://nodejs.org/"
    fi
else
    print_success "Node.js is already installed."
    node --version
    npm --version
fi

# 5. Register the Jupyter kernel
print_info "Registering the Jupyter kernel..."
DISPLAY_NAME="$ENV_NAME (UV)"

# Remove the existing kernel if there is one
if jupyter kernelspec list 2>/dev/null | grep -q "$ENV_NAME"; then
    print_warning "Removing the existing '$ENV_NAME' kernel..."
    jupyter kernelspec remove -f "$ENV_NAME" || {
        print_warning "Kernel removal failed, continuing anyway..."
    }
fi

# Register the new kernel (with error handling)
uv run python -m ipykernel install --user --name "$ENV_NAME" --display-name "$DISPLAY_NAME" || {
    print_error "Jupyter kernel registration failed."
    print_info "To register it manually: uv run python -m ipykernel install --user --name \"$ENV_NAME\" --display-name \"$DISPLAY_NAME\""
    exit 1
}
print_success "The Jupyter kernel has been registered as '$DISPLAY_NAME'."

# 6. Verify the installation
print_info "Verifying the installation..."
echo ""
echo "=== Installed Python version ==="
uv run python --version

echo ""
echo "=== Installed packages ==="
uv pip list

echo ""
echo "=== pyproject.toml dependencies ==="
if command -v grep &> /dev/null && [ -f "pyproject.toml" ]; then
    grep -A 20 "dependencies = \[" pyproject.toml || echo "Could not read the dependency information."
fi

echo ""
echo "=== Registered Jupyter kernels ==="
jupyter kernelspec list 2>/dev/null | grep -E "(Available|$ENV_NAME)" || echo "Could not retrieve the kernel list."

# 7. Link the environment files into the root directory (create symlinks)
print_info "Linking the UV environment files into the root directory..."
cd ..

# Back up and remove any existing files
for file in pyproject.toml .venv uv.lock; do
    if [ -e "$file" ] && [ ! -L "$file" ]; then
        print_warning "Backing up the existing $file as ${file}.backup."
        mv "$file" "${file}.backup"
    elif [ -L "$file" ]; then
        print_info "Removing the existing symlink $file."
        rm -f "$file"
    fi
done

# Create the symlinks (using absolute paths)
SOURCE_DIR="$SCRIPT_DIR"

ln -sf "$SOURCE_DIR/pyproject.toml" . || {
    print_error "Failed to create the pyproject.toml symlink"
    print_error "Current directory: $(pwd)"
    print_error "Source path: $SOURCE_DIR/pyproject.toml"
    exit 1
}

ln -sf "$SOURCE_DIR/.venv" . || {
    print_error "Failed to create the .venv symlink"
    print_error "Current directory: $(pwd)"
    print_error "Source path: $SOURCE_DIR/.venv"
    exit 1
}

if [ -f "$SOURCE_DIR/uv.lock" ]; then
    ln -sf "$SOURCE_DIR/uv.lock" . || {
        print_warning "Failed to create the uv.lock symlink"
    }
fi

print_success "The UV environment files have been linked into the root directory!"

echo ""
print_success "Environment setup is complete!"
echo ""
echo "=== How to use it ==="
echo "1. Add a package: uv add <package-name>"
echo "2. Remove a package: uv remove <package-name>"
echo "3. Sync dependencies: uv sync"
echo "4. Run a script: uv run python main.py (works from the root!)"
echo "5. Start Jupyter Lab: uv run jupyter lab"
echo "6. When creating a new notebook, select the '$DISPLAY_NAME' kernel"
echo ""
echo "=== File information ==="
echo "- pyproject.toml: project settings and dependencies (managed in 00-setup/, symlinked at the root)"
echo "- uv.lock: exact version lock file (recommended to keep in version control)"
echo "- .venv/: virtual environment directory (excluded from version control)"
echo ""
print_info "You can now run 'uv run python main.py' from the root directory!"
print_info "Activate it the traditional way: source .venv/bin/activate"
print_info "The UV-recommended way: uv run <command>"
