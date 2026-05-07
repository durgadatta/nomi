#!/bin/zsh
cd "$(dirname "$0")/.."
python3 scripts/nomi-vscode.py package
echo
echo "Done. You can close this window."
