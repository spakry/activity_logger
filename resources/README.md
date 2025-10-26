# Activity Logger Resources

This directory contains resources for the macOS application bundle.

## Icons

Place the app icon file here as `app.icns`.

To create an `.icns` file:

1. Create PNG images at various sizes (16x16, 32x32, 128x128, 256x256, 512x512, 1024x1024)
2. Use `iconutil` to create the .icns file:
   ```bash
   mkdir Icon.iconset
   # Copy your PNG files to Icon.iconset with appropriate naming
   iconutil -c icns Icon.iconset
   ```

For now, the app will work without a custom icon (using system default).
