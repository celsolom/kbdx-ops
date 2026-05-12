#!/usr/bin/env bash
#
# Build script for kbdx-ops — KeePass file operations.
# Creates a standalone binary using PyInstaller.
#
# Licensed under the Apache License, Version 2.0.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== kbdx-ops build ==="
echo ""

# ── Activate virtualenv (create if missing) ────────────────────────────
if [ ! -d .venv ]; then
    echo "Creating virtualenv..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# ── Install dependencies ───────────────────────────────────────────────
echo "Installing dependencies..."
pip install -q pykeepass pyinstaller

# ── Clean previous build ───────────────────────────────────────────────
echo "Cleaning previous build artifacts..."
rm -rf dist build __pycache__ *.spec

# ── Build binary ───────────────────────────────────────────────────────
echo "Building binary..."
pyinstaller --onefile --name kbdx-ops --strip \
    --hidden-import pykeepass \
    --hidden-import pykeepass.exceptions \
    --hidden-import pykeepass.group \
    --hidden-import pykeepass.entry \
    --hidden-import argon2_cffi \
    --hidden-import construct \
    --hidden-import pycryptodomex \
    --hidden-import lxml \
    --hidden-import pyotp \
    --hidden-import cffi \
    kbdx-ops.py

# ── Cleanup ────────────────────────────────────────────────────────────
rm -rf build __pycache__ *.spec

echo ""
echo "✅ Build complete!"
echo "   Binary: $SCRIPT_DIR/dist/kbdx-ops"
ls -lh dist/kbdx-ops
