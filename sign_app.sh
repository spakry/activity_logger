#!/bin/bash
# Properly sign all binaries in the app bundle recursively

set -e

APP_PATH="/Users/michaelkim/src/activity_logger/dist/Logger.app"
IDENTITY="Developer ID Application: MICHAEL JUNYEOP KIM (HNJN554FAC)"
ENTITLEMENTS="/Users/michaelkim/src/activity_logger/entitlements.plist"

if [ ! -d "$APP_PATH" ]; then
    echo "Error: App not found at $APP_PATH"
    exit 1
fi

echo "Signing all binaries in $APP_PATH..."

# Function to sign a file if it's a binary
sign_binary() {
    local file="$1"
    if [ -f "$file" ] && file "$file" | grep -q "Mach-O"; then
        echo "  Signing: $file"
        codesign --force --options runtime --sign "$IDENTITY" "$file" 2>&1 | grep -v "replacing existing signature" || true
    fi
}

# Find and sign all .so, .dylib, and .framework files first (dependencies)
echo "Step 1: Signing all .so, .dylib, and framework files..."
find "$APP_PATH" -type f \( -name "*.so" -o -name "*.dylib" \) -print0 | while IFS= read -r -d '' file; do
    sign_binary "$file"
done

# Sign all frameworks
find "$APP_PATH" -type d -name "*.framework" -print0 | while IFS= read -r -d '' framework; do
    if [ -f "$framework/$(basename "$framework" .framework)" ]; then
        sign_binary "$framework/$(basename "$framework" .framework)"
    fi
    # Sign any binaries inside the framework
    find "$framework" -type f -print0 | while IFS= read -r -d '' file; do
        if file "$file" | grep -q "Mach-O"; then
            sign_binary "$file"
        fi
    done
done

# Sign all Python extension modules (.so files in lib-dynload and elsewhere)
echo "Step 2: Signing Python extension modules..."
find "$APP_PATH/Contents/Resources" -type f -name "*.so" -print0 | while IFS= read -r -d '' file; do
    sign_binary "$file"
done

# Sign all Mach-O binaries (executables)
echo "Step 3: Signing all executables..."
find "$APP_PATH" -type f -perm +111 -print0 | while IFS= read -r -d '' file; do
    if file "$file" | grep -q "Mach-O"; then
        sign_binary "$file"
    fi
done

# Finally, sign the main app bundle with entitlements
echo "Step 4: Signing main app bundle with entitlements..."
codesign --force --options runtime \
  --entitlements "$ENTITLEMENTS" \
  --sign "$IDENTITY" "$APP_PATH"

echo ""
echo "Verifying signature..."
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

echo ""
echo "✅ App signing complete!"


