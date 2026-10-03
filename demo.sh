#!/usr/bin/env bash
# wordcount-cli — non-interactive end-to-end demo.
#
# Runs the real CLI against the bundled sample files, shows the exit-code
# contract a caller can rely on, and times a 10 MB file. Safe to re-run,
# never prompts, always exits 0. Run it with:  bash demo.sh
set -euo pipefail
cd "$(dirname "$0")"

# ── DESIGN TOKENS — source of truth for this build (see DESIGN.md) ───────────
#   surface  : terminal dark          type    : system monospace (the terminal)
#   density  : compact                accent  : oklch(0.58 0.12 201) = #008e97
#   signature: aligned columns, box-drawing separators, one accent for the
#              primary status, and never a colour-only signal.
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  ACCENT=$'\033[38;5;30m'
  MUTED=$'\033[38;5;245m'
  OFF=$'\033[0m'
else
  # Plain output for pipes, CI and NO_COLOR: no escapes at all.
  ACCENT=""
  MUTED=""
  OFF=""
fi

PY="${PYTHON:-python3}"
WIDTH=68
printf -v RULE '%*s' "$WIDTH" ''
RULE=${RULE// /─}

heading() {
  printf '\n%s%s%s\n' "$ACCENT" "$1" "$OFF"
  printf '%s%s%s\n' "$MUTED" "$RULE" "$OFF"
}

row() { printf '  %-40s %8s  %s\n' "$1" "$2" "$3"; }

# ── 1. Count the words in the bundled sample files ───────────────────────────
heading "wordcount-cli — words per file"

sample_files=(examples/release-notes.txt examples/onboarding.txt examples/empty.txt)
total=0
for file in "${sample_files[@]}"; do
  words=$("$PY" wordcount.py "$file")
  row "$file" "$words" "words"
  total=$((total + words))
done
printf '%s%s%s\n' "$MUTED" "$RULE" "$OFF"
row "total across ${#sample_files[@]} files" "$total" "words"

# ── 2. The exit-code contract a shell script can rely on ─────────────────────
heading "exit-code contract"

show_case() {
  local label="$1"
  shift
  local err_file out code detail
  err_file=$(mktemp)
  set +e
  out=$("$PY" wordcount.py "$@" 2>"$err_file")
  code=$?
  set -e
  detail=$(printf '%s\n' "$out" | head -n 1)
  if [ -z "$detail" ]; then
    detail=$(head -n 1 "$err_file")
  fi
  rm -f "$err_file"
  printf '  %-30s %s%-4s%s %s\n' "$label" "$MUTED" "exit $code" "$OFF" "$detail"
}

show_case "no path argument"
show_case "examples/empty.txt" examples/empty.txt
show_case "missing.txt" missing.txt
show_case "--help" --help

# ── 3. It is fast enough for habit-forming use ───────────────────────────────
heading "scale check — 10 MB file"

work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT
big_file="$work_dir/big.txt"

"$PY" - "$big_file" <<'GENERATE'
import sys

line = "alpha beta gamma delta epsilon zeta eta theta\n"
with open(sys.argv[1], "w", encoding="utf-8") as handle:
    for _ in range(240_000):
        handle.write(line)
GENERATE

read -r big_words big_seconds big_mb < <("$PY" - "$big_file" "$PWD/wordcount.py" <<'TIMEIT'
import os
import subprocess
import sys
import time

path, cli = sys.argv[1], sys.argv[2]
started = time.perf_counter()
done = subprocess.run(
    [sys.executable, cli, path], capture_output=True, text=True, check=False
)
elapsed = time.perf_counter() - started
if done.returncode != 0:
    sys.stderr.write(done.stderr)
    raise SystemExit(done.returncode)
print(done.stdout.strip(), f"{elapsed:.2f}", f"{os.path.getsize(path) / 1048576:.1f}")
TIMEIT
)

row "generated ${big_mb} MB of text" "$big_words" "words"
row "python3 wordcount.py big.txt" "${big_seconds}s" "wall clock"

# ── 4. Done ──────────────────────────────────────────────────────────────────
heading "summary"
printf '  %s%s%s\n' "$ACCENT" "demo complete — exit code 0" "$OFF"
printf '  %s\n' "try it yourself: python3 wordcount.py examples/release-notes.txt"
