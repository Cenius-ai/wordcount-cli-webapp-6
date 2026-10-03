#!/usr/bin/env bash
# wordcount-cli — project setup. Installs dependencies, installs the console
# entry point and self-checks the import, then EXITS (it never starts anything
# long-running). Safe to re-run. Run it with:  bash install.sh
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

echo "[1/4] Upgrading packaging tooling (old pip breaks PEP 660 editable installs)"
"$PY" -m pip install --upgrade pip setuptools wheel

echo "[2/4] Installing project dependencies from requirements.txt"
"$PY" -m pip install --disable-pip-version-check -r requirements.txt

echo "[3/4] Installing the 'wordcount' console entry point"
"$PY" -m pip install --disable-pip-version-check --no-build-isolation -e .

echo "[4/4] Self-check"
"$PY" -c 'import wordcount; print("      wordcount-cli", wordcount.__version__, "imports cleanly")'
"$PY" wordcount.py --version

echo
echo "Setup complete (nothing was started). Try:"
echo "  bash demo.sh                                  # full end-to-end demo"
echo "  python3 wordcount.py examples/release-notes.txt"
echo "  python3 -m pytest                             # run the test suite"
