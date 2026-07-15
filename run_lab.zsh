#!/usr/bin/env zsh
set -euo pipefail

# c-stdlib-getenv-config-snapshot-lab runner (zsh)
# Resolves Zig compiler, builds env_lab.c, runs the lab, runs tests.

cd "${0:a:h}"

# --- Resolve Zig ---
if [[ -n "${ZIG_BIN:-}" && -x "$ZIG_BIN" ]]; then
    ZIG="$ZIG_BIN"
elif (( $+commands[zig] )); then
    ZIG="${commands[zig]}"
elif [[ -x "$HOME/.local/zig/zig" ]]; then
    ZIG="$HOME/.local/zig/zig"
elif [[ -x "$HOME/.local/bin/zig" ]]; then
    ZIG="$HOME/.local/bin/zig"
elif [[ -x "$HOME/bin/zig" ]]; then
    ZIG="$HOME/bin/zig"
else
    print -u2 "error: zig not found"
    print -u2 "Tried: \$ZIG_BIN, (( \$+commands[zig] )), ~/.local/zig/zig, ~/.local/bin/zig, ~/bin/zig"
    exit 1
fi

print "==> zig: $("$ZIG" version) ($ZIG)"

# --- Resolve Python ---
if [[ -n "${PYTHON_BIN:-}" && -x "$PYTHON_BIN" ]]; then
    PYTHON="$PYTHON_BIN"
elif (( $+commands[python3] )); then
    PYTHON="${commands[python3]}"
elif (( $+commands[python] )); then
    PYTHON="${commands[python]}"
else
    print -u2 "error: python not found"
    exit 1
fi

print "==> python: $("$PYTHON" --version 2>&1)"

# --- Compile check ---
print "==> compiling env_lab.c"
"$ZIG" cc -std=c11 -D_POSIX_C_SOURCE=200809L -O2 -Wall -Wextra -Wpedantic -Werror env_lab.c -o env_lab_check
rm -f env_lab_check env_lab_check.exe
print "    compile ok"

# --- Python compile check ---
print "==> py_compile"
"$PYTHON" -m py_compile run_lab.py test_lab.py
print "    py_compile ok"

# --- Run lab ---
print "==> run_lab.py"
"$PYTHON" run_lab.py

# --- Run tests ---
print "==> unittest"
"$PYTHON" -m unittest -v

print ""
print "Done. See RESULTS.md, results_rows.json, results_rows.csv"
