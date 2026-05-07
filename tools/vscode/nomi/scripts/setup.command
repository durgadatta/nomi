#!/bin/zsh
cd "$(dirname "$0")/.."
python3 scripts/nomi-vscode.py setup
echo
echo "Done. You can close this window."
