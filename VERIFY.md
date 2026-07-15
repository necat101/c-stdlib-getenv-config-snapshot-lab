# VERIFY

Repository: https://github.com/necat101/c-stdlib-getenv-config-snapshot-lab
Implementation SHA: c4a5cba7cb857e1e94b465f6abb440f1faf5882b
Documentation commit: direct descendant (to be created)

## Clean clone verification

```
git clone https://github.com/necat101/c-stdlib-getenv-config-snapshot-lab.git verify_clone
cd verify_clone
git checkout c4a5cba7cb857e1e94b465f6abb440f1faf5882b
```

Zig candidates: $ZIG_BIN, command -v zig, ~/.local/zig/zig, ~/.local/bin/zig, ~/bin/zig
Selected: ~/.local/zig/zig (sanitized: /portable-zig/zig)
Zig version: 0.14.0
Zig cc version: clang 19.1.7 (via zig cc)
Compiler target: x86_64-linux-gnu

Python: /usr/bin/python3
Python version: 3.12.3
Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39

C markers: STDC_VERSION=201112, CHAR_BIT=8, sizeof(void*)=8, sizeof(size_t)=8

POSIX API: getenv=yes, setenv=yes, unsetenv=yes, putenv=yes, strtol=yes, execve=yes

## Validation commands

```
$ZIG_BIN cc -std=c11 -D_POSIX_C_SOURCE=200809L -O2 -Wall -Wextra -Wpedantic -Werror env_lab.c -o env_lab_check
python3 -m py_compile run_lab.py test_lab.py
python3 run_lab.py
python3 -m unittest -v
```

All exit codes: 0
Unittests: 11 tests, OK

Cases: 20
Methods: 5
Rows: 100

Classifications:
- pass: 10
- expected_error: 2
- local_observation: 3
- api_skip: 0
- toolchain_skip: 0
- context_only: 5
- not_applicable: 80
- fail: 0

missing_variable_null: True
setenv_insert_value: alpha
overwrite_false_result: alpha
overwrite_true_result: beta
unsetenv_null_after: True
empty_is_empty_string: True
snapshot_first: snapshot_one, second: snapshot_two
putenv_alias_value: alias_one
putenv_mutation_value: alias_two

JSON/CSV/RESULTS agree: yes

Regenerated vs committed: identical except elapsed_time field (0.19s vs 0.32s)
Working tree after regeneration: RESULTS.md modified (timing only)
Restoration: git checkout HEAD -- RESULTS.md
Final git status --porcelain: empty

Artifact scanner: pass
Verification wall-clock: ~45s

API skips: 0
Toolchain skips: 0
Failures: 0

Post-VERIFY local unittest rerun: 11 tests OK
