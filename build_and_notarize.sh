#!/bin/bash
# Complete build, sign, package, and notarize process for Logger.app

set -e

cd /Users/michaelkim/src/activity_logger

APP_PATH="dist/Logger.app"
IDENTITY="Developer ID Application: MICHAEL JUNYEOP KIM (HNJN554FAC)"
ENTITLEMENTS="entitlements.plist"
DMG_STAGING="dist/dmg-staging"
DMG_PATH="dist/Logger-1.0.0.dmg"

echo "=========================================="
echo "Building and Notarizing Logger.app"
echo "=========================================="
echo ""

# Step 1: Rebuild the app bundle
echo "Step 1/6: Rebuilding app bundle..."
rm -rf dist build

# Use Python 3.10 from Homebrew and set deployment target
export MACOSX_DEPLOYMENT_TARGET=10.13
/usr/local/bin/python3.10 setup_app.py py2app

if [ ! -d "$APP_PATH" ]; then
    echo "❌ Error: App bundle not created at $APP_PATH"
    exit 1
fi
echo "✅ App bundle created"
echo ""

# Step 2: Sign all binaries in the app
echo "Step 2/6: Signing all binaries in app bundle..."
./sign_app.sh
echo ""

# Step 3: Create DMG
echo "Step 3/6: Creating DMG..."
rm -rf "$DMG_STAGING" "$DMG_PATH"
mkdir -p "$DMG_STAGING"
cp -R "$APP_PATH" "$DMG_STAGING/"
hdiutil create -volname "Logger" -srcfolder "$DMG_STAGING" -ov -format UDZO "$DMG_PATH"
echo "✅ DMG created"
echo ""

# Step 4: Sign DMG
echo "Step 4/6: Signing DMG..."
codesign --force --sign "$IDENTITY" "$DMG_PATH"
codesign --verify --verbose=2 "$DMG_PATH" > /dev/null
echo "✅ DMG signed"
echo ""

# Step 5: Notarize DMG
echo "Step 5/6: Submitting DMG for notarization (this may take several minutes)..."
xcrun notarytool submit "$DMG_PATH" \
  --keychain-profile "logger-notary" \
  --wait
echo "✅ DMG notarized"
echo ""

# Step 6: Staple notarization ticket
echo "Step 6/6: Stapling notarization ticket..."
xcrun stapler staple "$DMG_PATH"
xcrun stapler validate "$DMG_PATH"
echo "✅ Notarization ticket stapled"
echo ""

echo "=========================================="
echo "✅ Build and Notarization Complete!"
echo "=========================================="
echo ""
echo "DMG ready for distribution:"
echo "  $DMG_PATH"
echo ""
echo "File size: $(du -h "$DMG_PATH" | cut -f1)"
echo ""

