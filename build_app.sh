#!/bin/bash
# Build script for Activity Logger macOS app

set -e

echo "Building Activity Logger macOS app..."
echo ""

# Clean previous build
echo "Cleaning previous builds..."
rm -rf build dist

# Build the app
echo "Building with py2app..."
python setup_app.py py2app

echo ""
echo "Build complete!"
echo "Application bundle created in: dist/Activity Logger.app"
echo ""
echo "To install:"
echo "  cp -r 'dist/Activity Logger.app' /Applications/"
echo ""
echo "To run:"
echo "  open 'dist/Activity Logger.app'"
