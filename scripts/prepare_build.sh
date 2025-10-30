#!/usr/bin/env bash
set -euo pipefail

# Prepare local env for macOS app build with py2app
# - Installs Python deps
# - Cleans build artifacts safely (keeps existing Python package dists)

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[prepare] Using ROOT_DIR=$ROOT_DIR"

if [ -d "venv" ]; then
  echo "[prepare] Activating existing venv"
  # shellcheck source=/dev/null
  source venv/bin/activate
else
  echo "[prepare] Creating venv"
  python3 -m venv venv
  # shellcheck source=/dev/null
  source venv/bin/activate
fi

python -m pip install -U pip wheel setuptools
python -m pip install -r requirements.txt

echo "[prepare] Cleaning build artifacts"
rm -rf build/

# Remove only app-bundle artifacts from dist, keep Python package artifacts
if [ -d dist ]; then
  find dist -maxdepth 1 \
    \( -name 'Logger.app' -o -name 'Logger.zip' -o -name '*.dmg' \) \
    -print -exec rm -rf {} +
fi

echo "[prepare] Done."



