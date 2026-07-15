# VERIFY

Repository: https://github.com/necat101/c-stdlib-getenv-config-snapshot-lab
Implementation SHA: 0c90264e97c92aefec4e63a7a7dcc14c68d835bd
Documentation commit: direct descendant (to be created)

This is VERIFY v3, superseding v1 (f6c7a53) and v2 (f0a98ed).

v1 issues: classification dependence, missing case implementations, unsanitized paths, GNU/musl target mismatch, minimal tests.
v2 issues: C helper implemented strtol/bounded_copy/child_vector, but tests were source-inspection, no-Zig test missing, JSON/CSV partial comparison, scanner incomplete, RESULTS.md hardcoded, VERIFY.md committed in impl tree.

v3 fixes all of the above.

## Clean clone verification

```
git clone https://github.com/necat101/c-stdlib-getenv-config-snapshot-lab.git verify_clone_v3
cd verify_clone_v3
git checkout 0c90264e97c92aefec4e63a7a7dcc14c68d835bd
```

Zig: ~/.local/zig/zig → /portable-zig/zig
Zig version: 0.14.0
Zig cc: clang 19.1.7
Target: x86_64-unknown-linux-musl

Python: /usr/bin/python3 → /python-lab/bin/python3
Python version: 3.12.3
Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39

C: STDC_VERSION=201112, CHAR_BIT=8, sizeof(void*)=8, sizeof(size_t)=8
POSIX: getenv=yes, setenv=yes, unsetenv=yes, putenv=yes, strtol=yes, execve=yes

## Validation

```
$ZIG_BIN cc -std=c11 -D_POSIX_C_SOURCE=200809L -O2 -Wall -Wextra -Wpedantic -Werror env_lab.c -o env_lab_check
# exit 0
rm env_lab_check
python3 -m py_compile run_lab.py test_lab.py
# exit 0
python3 run_lab.py
# rows=100 pass=10 expected_error=2 local_observation=3 context_only=5 not_applicable=80 fail=0
python3 -m unittest -v
# Ran 35 tests in 1.216s OK
```

Cases: 20, Methods: 5, Rows: 100
Classifications: pass=10, expected_error=2, local_observation=3, context_only=5, not_applicable=80, fail=0, api_skip=0, toolchain_skip=0

C helper exercises:
- getenv missing → null
- setenv insert → alpha
- setenv overwrite false → retains alpha
- setenv overwrite true → beta
- unsetenv → null after
- empty value → "" distinct from null
- snapshot copy → snapshot_one preserved
- putenv alias → alias_one
- putenv mutation → alias_two
- invalid names → 4/4 rejected
- startup snapshot → 3 entries
- bounded_copy: capacities 0,1,6,7,8 with sentinel checks → 7 minimum ok
- strtol: 5 accept, 0 reject_range, 128 accept, -1 reject_range, 5x reject_trailing, "" reject_noconv, big overflow reject (errno=34, ERANGE)
- child_env_vector: 3 entries, null_terminator, lexicographic, owned copies, free'd
- precedence: default/blue/green/green
- duplicate: first=blue, last=green, reject=duplicate_error
- tiny_feature: 3 valid accept, 3 invalid reject, no model/dataset/prediction

JSON/CSV/RESULTS agreement: yes

## Regenerated vs committed

```
cd verify_clone_v3
python3 run_lab.py
git status --porcelain
# (empty – elapsed_time matched exactly 0.32s)
```

JSON comparison (ignoring elapsed_time):
```
python3 -c "import json,subprocess; a=json.load(open('results_rows.json')); b=json.loads(subprocess.run(['git','show','HEAD:results_rows.json'],capture_output=True,text=True).stdout); na=[{k:v for k,v in r.items() if k!='elapsed_time'} for r in a]; nb=[{k:v for k,v in r.items() if k!='elapsed_time'} for r in b]; print(na==nb)"
# True
```

CSV comparison:
```
# 100 rows, full field-level JSON/CSV decoded comparison – match
```

RESULTS.md comparison: identical (elapsed_time matched)

Working tree after regeneration: empty
Restoration: n/a (no changes)
Final git status --porcelain: (empty)

Artifact scanner: pass (35 tests, scans all 11 artifacts, checks credentials/tokens/paths/pointers/emails)
Paths sanitized: zig_executable=/portable-zig/zig, python_executable=/python-lab/bin/python3

Verification wall-clock: ~45s
API skips: 0 / Toolchain skips: 0 / Failures: 0
Post-VERIFY unittest: 35 tests OK

## v3 fixes

- Classification independence: actual NOT initialized from expected; handlers do NOT read expected; verified by mutating expected manifest → actual unchanged (test_actual_independent)
- C strtol: real C strtol() with errno/endptr/complete, 7 inputs
- bounded_copy: C getenv_bounded_copy(), 5 capacities, sentinel 0xAA checks
- child_env_vector: C malloc/free, owned copies, lexicographic check, null terminator
- invalid_name: requires 4/4 rejections
- Tests: 35 tests, production-code exercise (not source inspection)
  - test_actual_independent: mutates cases.json, reruns run_lab.py subprocess, verifies actual unchanged
  - test_missing_handler_becomes_fail: removes handler from dict, verifies fail+failure_reason
  - test_no_zig_path: PATH isolation + HOME isolation, verifies toolchain_skip
  - recomputation: precedence, bounded_int, duplicate, child_vector, tiny_feature – all independently recompute
  - test_results_agree: full field-level JSON/CSV comparison, all 100 rows
  - test_artifact_scanner: scans all artifacts, checks credentials/tokens/paths/pointers/emails
  - test_paths_sanitized: verifies no /home or /tmp paths, sanitization_applied=true
- RESULTS.md: generated from row collection (not hardcoded)
- Paths sanitized throughout
- Compiler target: consistently x86_64-unknown-linux-musl
- Clean impl commit WITHOUT VERIFY.md (0c90264)
