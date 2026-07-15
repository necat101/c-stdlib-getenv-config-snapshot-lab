#!/usr/bin/env bash
set -euo pipefail

# c-stdlib-getenv-config-snapshot-lab runner (Linux / macOS / WSL)
# Resolves Zig compiler, builds env_lab.c, runs the lab, runs tests.

cd "$(dirname "$0")"

# --- Resolve Zig ---
if [ -n "${ZIG_BIN:-}" ] && [ -x "${ZIG_BIN}" ]; then
    ZIG="$ZIG_BIN"
elif command -v zig >/dev/null 2>&1; then
    ZIG="$(command -v zig)"
elif [ -x "$HOME/.local/zig/zig" ]; then
    ZIG="$HOME/.local/zig/zig"
elif [ -x "$HOME/.local/bin/zig" ]; then
    ZIG="$HOME/.local/bin/zig"
elif [ -x "$HOME/bin/zig" ]; then
    ZIG="$HOME/bin/zig"
else
    echo "error: zig not found" >&2
    echo "Tried: \$ZIG_BIN, command -v zig, ~/.local/zig/zig, ~/.local/bin/zig, ~/bin/zig" >&2
    exit 1
fi

echo "==> zig: $("$ZIG" version) ($ZIG)"

# --- Resolve Python ---
if [ -n "${PYTHON_BIN:-}" ] && [ -x "${PYTHON_BIN}" ]; then
    PYTHON="$PYTHON_BIN"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
else
    echo "error: python not found" >&2
    exit 1
fi

echo "==> python: $("$PYTHON" --version 2>&1)"

# --- Compile check ---
echo "==> compiling env_lab.c"
"$ZIG" cc -std=c11 -D_POSIX_C_SOURCE=200809L -O2 -Wall -Wextra -Wpedantic -Werror env_lab.c -o env_lab_check
rm -f env_lab_check env_lab_check.exe
echo "    compile ok"

# --- Python compile check ---
echo "==> py_compile"
"$PYTHON" -m py_compile run_lab.py test_lab.py
echo "    py_compile ok"

# --- Run lab ---
echo "==> run_lab.py"
"$PYTHON" run_lab.py

# --- Run tests ---
echo "==> unittest"
"$PYTHON" -m unittest -v

echo ""
echo "Done. See RESULTS.md, results_rows.json, results_rows.csv"
