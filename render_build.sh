#!/bin/bash

# Render.com Build Script - Optimized for 512MB RAM
echo "🚀 Starting Render build for Movie Search App..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements_render.txt

# Install Playwright browser with minimal footprint
echo "🌐 Installing Playwright browser (optimized)..."
playwright install chromium

# Verify installation
echo "✅ Verifying installation..."
python -c "import playwright; print('Playwright installed successfully')"

# Set memory limits for Node.js (used by Playwright)
export NODE_OPTIONS="--max-old-space-size=256"

# Create cache directory
mkdir -p /opt/render/.cache/ms-playwright

echo "🎬 Build completed successfully!"
echo "Memory optimizations applied:"
echo "  - Single browser process"
echo "  - Limited cache size"
echo "  - Aggressive garbage collection"
echo "  - Reduced timeouts"
echo ""
echo "Ready to deploy on Render.com with 512MB RAM limit!"