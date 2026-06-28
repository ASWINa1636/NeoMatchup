#!/bin/bash
echo "Cleaning up old builds..."
rm -rf build dist

echo "Building NeoPlato for Linux..."
python3 -m PyInstaller --noconfirm --onedir --windowed --name "NeoPlato" \
  --add-data "games:games" \
  --add-data "pages:pages" \
  --add-data "core:core" \
  --add-data "multiplayer:multiplayer" \
  --add-data "hub.pyc:." \
  --collect-all games \
  --collect-all pages \
  --collect-all core \
  --collect-all multiplayer \
  main.py

echo "Build complete! Executable is in dist/NeoPlato"
