#!/bin/bash
# Setup Xcode for notarization

XCODE_PATH="/Users/Shared/Relocated Items/Security/Applications/Xcode.app"

echo "Setting Xcode path..."
sudo xcode-select --switch "$XCODE_PATH"

echo "Accepting Xcode license..."
sudo xcodebuild -license accept

echo "Verifying setup..."
xcode-select -p
xcrun --find notarytool

echo "Xcode setup complete!"




