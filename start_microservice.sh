#!/bin/bash

echo "🚀 Starting Playwright Microservice Setup..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements_microservice.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Playwright browsers installed successfully"
else
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi

# Start the microservice
echo "🎬 Starting Playwright microservice..."
python playwright_microservice.py