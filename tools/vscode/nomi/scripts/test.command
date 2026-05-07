#!/bin/zsh
cd "$(dirname "$0")/.."
python3 scripts/nomi-vscode.py test
echo
echo "Done. You can close this window."
