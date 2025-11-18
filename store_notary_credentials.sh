#!/bin/bash
# Store notarytool credentials
# Usage: ./store_notary_credentials.sh YOUR_APPLE_ID_EMAIL YOUR_APP_SPECIFIC_PASSWORD

if [ $# -lt 2 ]; then
    echo "Usage: $0 <apple-id-email> <app-specific-password>"
    echo ""
    echo "To create an app-specific password:"
    echo "1. Go to https://appleid.apple.com"
    echo "2. Sign in with your Apple ID"
    echo "3. Go to Sign-In and Security → App-Specific Passwords"
    echo "4. Generate a new password for 'notarytool'"
    exit 1
fi

APPLE_ID="$1"
APP_SPECIFIC_PASSWORD="$2"
TEAM_ID="HNJN554FAC"
PROFILE_NAME="logger-notary"

echo "Storing notarytool credentials..."
xcrun notarytool store-credentials "$PROFILE_NAME" \
  --apple-id "$APPLE_ID" \
  --team-id "$TEAM_ID" \
  --password "$APP_SPECIFIC_PASSWORD"

echo "Credentials stored successfully!"
echo "You can now run ./notarize.sh to notarize your DMG."

