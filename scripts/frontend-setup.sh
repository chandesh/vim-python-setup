#!/bin/bash

# Frontend Setup Script for AI Agent Hub
# This script sets up Node.js via nvm and installs all dependencies

set -e

echo "=================================="
echo "AI Agent Hub - Frontend Setup"
echo "=================================="
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend" || exit 1

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Check if nvm is available after loading
if ! type nvm &> /dev/null; then
    echo "[ERROR] nvm is not installed."
    echo "Please install nvm from: https://github.com/nvm-sh/nvm"
    echo ""
    echo "Installation command:"
    echo "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    exit 1
fi

echo "[1/5] Using nvm to set Node.js version..."

# Check if .nvmrc exists
if [ ! -f .nvmrc ]; then
    echo "[WARN] .nvmrc file not found! Using Node 20.19.5 as default"
    echo "20.19.5" > .nvmrc
fi

# Install and use the Node version from .nvmrc
NODE_VERSION=$(cat .nvmrc)
echo "Required Node.js version: $NODE_VERSION"

if ! nvm list | grep -q "$NODE_VERSION"; then
    echo "Installing Node.js $NODE_VERSION..."
    nvm install "$NODE_VERSION"
else
    echo "Node.js $NODE_VERSION is already installed"
fi

nvm use "$NODE_VERSION"

echo ""
echo "[2/5] Verifying Node.js and npm versions..."
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"

echo ""
echo "[3/5] Cleaning previous installations..."
rm -rf node_modules package-lock.json

echo ""
echo "[4/5] Installing npm dependencies..."
npm install

echo ""
echo "[5/5] Installing TailwindCSS and dependencies..."
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest

# Initialize Tailwind config
if [ ! -f tailwind.config.js ]; then
    echo "Creating Tailwind configuration..."
    npx tailwindcss init -p
fi

echo ""
echo "=================================="
echo "[OK] Frontend setup complete!"
echo "=================================="
echo ""
echo "Environment:"
echo "  Node.js: $(node --version)"
echo "  npm: $(npm --version)"
echo "  Directory: $(pwd)"
echo ""
echo "Next steps:"
echo "  cd frontend"
echo "  npm start          # Start development server"
echo "  npm run build      # Build for production"
echo ""
echo "Development server will be available at:"
echo "  http://localhost:4200"
echo ""
