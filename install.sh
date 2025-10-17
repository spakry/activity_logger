#!/bin/bash

# Activity Logger Installation Script

echo "🚀 Installing Activity Logger..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ is required. Found Python $python_version"
    echo "Please install Python 3.8 or later and try again."
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed. Please install pip and try again."
    exit 1
fi

echo "✅ pip3 found"

# Install the package in development mode
echo "📦 Installing package dependencies..."
pip3 install -e .

if [ $? -eq 0 ]; then
    echo "✅ Installation successful!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Set your OpenAI API key:"
    echo "   export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "2. Grant Accessibility permissions:"
    echo "   - Open System Preferences → Security & Privacy → Privacy"
    echo "   - Select 'Accessibility' from the left sidebar"
    echo "   - Add your Terminal application and enable it"
    echo ""
    echo "3. Start the activity logger:"
    echo "   activity-logger"
    echo ""
    echo "🎉 Enjoy tracking your activities!"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
