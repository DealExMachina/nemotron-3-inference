#!/bin/bash
# Test Koyeb CLI with token from .env

set -e

cd /Users/jeanbapt/nemotron-nano

echo "=== Loading .env file ==="
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    exit 1
fi

# Source .env and extract KOYEB_API_KEY
source .env

# Check which variable name is used
if [ -z "$KOYEB_API_KEY" ] && [ -z "$KOYEB_TOKEN" ]; then
    echo "❌ Neither KOYEB_API_KEY nor KOYEB_TOKEN found in .env"
    echo "Available variables:"
    grep -i koyeb .env || echo "No Koyeb variables found"
    exit 1
fi

# Use whichever is set
TOKEN="${KOYEB_API_KEY:-$KOYEB_TOKEN}"

if [ -z "$TOKEN" ]; then
    echo "❌ Token is empty"
    exit 1
fi

echo "✓ Token found (length: ${#TOKEN} characters)"

# Clean the token (remove quotes and whitespace)
echo "=== Cleaning token ==="
CLEAN_TOKEN=$(echo "$TOKEN" | sed "s/^['\"]//; s/['\"]$//" | tr -d '\r\n\t ' | xargs)
echo "Original token: '$TOKEN'"
echo "Cleaned token: '$CLEAN_TOKEN'"
echo "Cleaned token length: ${#CLEAN_TOKEN} characters"

if [ -z "$CLEAN_TOKEN" ]; then
    echo "❌ Token is empty after cleaning"
    exit 1
fi

# Export cleaned token
export KOYEB_TOKEN="$CLEAN_TOKEN"

echo ""
echo "=== Testing Koyeb CLI ==="

# Check if koyeb CLI is installed
if ! command -v koyeb &> /dev/null; then
    echo "📥 Installing Koyeb CLI..."
    curl -fsSL https://raw.githubusercontent.com/koyeb/koyeb-cli/master/install.sh | bash
    export PATH="$HOME/.koyeb/bin:$PATH"
fi

echo "✓ Koyeb CLI version:"
koyeb version

echo ""
echo "=== Testing authentication ==="
echo "Testing with KOYEB_TOKEN environment variable..."

# Test authentication by listing apps
echo "Listing apps..."
if koyeb app list 2>&1; then
    echo "✅ Authentication successful!"
else
    echo "❌ Authentication failed"
    echo ""
    echo "Debug info:"
    echo "Token starts with: ${CLEAN_TOKEN:0:10}..."
    echo "Token ends with: ...${CLEAN_TOKEN: -10}"
    exit 1
fi

echo ""
echo "=== Testing app operations ==="
echo "Checking for app: nemotron-3-inference"
if koyeb app get nemotron-3-inference 2>&1; then
    echo "✓ App exists"
else
    echo "ℹ️  App does not exist (this is OK for first run)"
fi

echo ""
echo "✅ All tests passed!"

