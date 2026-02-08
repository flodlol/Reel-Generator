#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Meme Video Generator"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ICON_PATH="$PROJECT_ROOT/public/logo/1024.png"

cd "$PROJECT_ROOT"

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "pyinstaller is not installed. Install it with:"
  echo "  $PROJECT_ROOT/Project-Env/bin/python -m pip install pyinstaller"
  exit 1
fi

$PROJECT_ROOT/Project-Env/bin/python -m PyInstaller \
  --noconfirm \
  --windowed \
  --name "$APP_NAME" \
  --icon "$ICON_PATH" \
  --add-data "public/logo:public/logo" \
  --add-data "config:config" \
  --add-data "assets:assets" \
  --add-data "src:src" \
  run_app.py

echo "Build complete. Find the app in dist/$APP_NAME.app"
