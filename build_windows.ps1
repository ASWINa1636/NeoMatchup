Write-Host "Cleaning up old builds..."
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

Write-Host "Building NeoPlato for Windows..."
python -m PyInstaller --noconfirm --onedir --windowed --name "NeoPlato" `
  --add-data "games;games" `
  --add-data "pages;pages" `
  --add-data "core;core" `
  --add-data "multiplayer;multiplayer" `
  --add-data "hub.pyc;." `
  --add-data "icon.png;." `
  --icon="icon.ico" `
  --collect-all games `
  --collect-all pages `
  --collect-all core `
  --collect-all multiplayer `
  main.py

Write-Host "Build complete! Executable is in dist/NeoPlato"
