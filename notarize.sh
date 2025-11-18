#!/bin/bash
# Notarize and staple the DMG

set -e

cd /Users/michaelkim/src/activity_logger

DMG_PATH="dist/Logger-1.0.0.dmg"
IDENTITY="Developer ID Application: MICHAEL JUNYEOP KIM (HNJN554FAC)"

if [ ! -f "$DMG_PATH" ]; then
    echo "Error: DMG not found at $DMG_PATH"
    exit 1
fi

echo "Submitting DMG for notarization..."
xcrun notarytool submit "$DMG_PATH" \
  --keychain-profile "logger-notary" \
  --wait

echo "Notarization successful! Stapling ticket..."
xcrun stapler staple "$DMG_PATH"

echo "Validating stapled DMG..."
xcrun stapler validate "$DMG_PATH"

echo "✅ Notarization complete! DMG is ready for distribution."




