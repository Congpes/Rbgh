#!/usr/bin/env bash
set -euo pipefail


PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

python_cmd() {
  if command -v python3 >/dev/null 2>&1; then echo python3; else echo python; fi
}

PY="$(python_cmd)"

echo "[1/4] Python: $($PY --version 2>/dev/null || echo 'not found')"

if [ ! -d "$VENV_DIR" ]; then
  echo "[2/4] Creating virtualenv at $VENV_DIR"
  $PY -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip wheel setuptools >/dev/null

echo "[3/4] Installing Python dependencies"
pip install -r "$PROJECT_DIR/requirements.txt"

echo "[Info] If audio does not play, install system packages (Debian/Ubuntu):"
echo "  sudo apt update && sudo apt install -y \\
       libqt5multimedia5 libqt5multimedia5-plugins \\
       gstreamer1.0-plugins-base gstreamer1.0-plugins-good \\
       libasound2"

echo "[4/4] Launching app"
export QT_QPA_PLATFORM=xcb
python -m src.main

