# VERIFY

Repository: https://github.com/necat101/c-stdlib-getenv-config-snapshot-lab
Implementation SHA: 287d16ddf2966a89a8b389fcd5612890f6899131
Documentation commit: direct descendant (to be created)

This is VERIFY v2, superseding the v1 verification (commit f6c7a53) which contained target-triple inconsistencies and incomplete case implementations.

## Clean clone verification

```
git clone https://github.com/necat101/c-stdlib-getenv-config-snapshot-lab.git verify_clone_v2
cd verify_clone_v2
git checkout 287d16ddf2966a89a8b389fcd5612890f6899131
```

Zig candidates attempted: $ZIG_BIN, command -v zig, ~/.local/zig/zig, ~/.local/bin/zig, ~/bin/zig
Selected: ~/.local/zig/zig
Sanitized executable representation: /portable-zig/zig
Zig version: 0.14.0
Zig cc version: clang 19.1.7 (zig cc frontend)
Compiler target: x86_64-unknown-linux-musl

Python candidates: $PYTHON_BIN, python3, python
Selected: /usr/bin/python3
Sanitized: /python-lab/bin/python3
Python version: 3.12.3
Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39

C markers: STDC_VERSION=201112, CHAR_BIT=8, sizeof(void*)=8, sizeof(size_t)=8

POSIX API: getenv=yes, setenv=yes, unsetenv=yes, putenv=yes, strtol=yes, execve=yes

## Validation commands

```
$ZIG_BIN cc -std=c11 -D_POSIX_C_SOURCE=200809L -O2 -Wall -Wextra -Wpedantic -Werror env_lab.c -o env_lab_check
# exit code: 0
rm env_lab_check

python3 -m py_compile run_lab.py test_lab.py
# exit code: 0

python3 run_lab.py
# exit code: 0
# rows=100 pass=10 expected_error=2 local_observation=3 context_only=5 not_applicable=80 fail=0 api_skip=0 toolchain_skip=0

python3 -m unittest -v
# exit code: 0
# Ran 36 tests in 0.144s
# OK
```

Unittests: 36 tests, OK

Cases: 20
Methods: 5 (inspect_toolchain, exercise_getenv, exercise_mutation, enumerate_snapshot, ml_context_observation)
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

Bounded copy: test_val=abcdef, capacities 0,1,6,7,8 → insufficient, insufficient, insufficient, ok, ok, minimum_success_capacity=7
Explicit config precedence: default, blue, green, green (explicit > env > default)
Bounded integer config: 5 accept, 0 reject_range, 128 accept, -1 reject_range, 5x reject_trailing, "" reject_no_conversion, 999... reject_range
Duplicate envp policy: first_wins=blue, last_wins=green, reject_dup=duplicate_error
Child environment vector: 3 entries, null_terminator=yes, lexicographic=yes
Tiny feature config: feature_limit 64 accept, threshold_bps 5000 accept, model_slot blue accept; invalid cases rejected; model_loaded=false, dataset_read=false, prediction_calculated=false

JSON/CSV/RESULTS agreement: yes

## Regenerated vs committed comparison

```
cd verify_clone_v2
python3 run_lab.py
git diff RESULTS.md
```

Output:
```
- elapsed: 0.23s
+ elapsed: 0.32s
```

Only elapsed_time differs.

JSON comparison (ignoring elapsed_time):
```
python3 -c "import json,subprocess; a=json.load(open('results_rows.json')); b=json.loads(subprocess.run(['git','show','HEAD:results_rows.json'],capture_output=True,text=True).stdout); na=[{k:v for k,v in r.items() if k!='elapsed_time'} for r in a]; nb=[{k:v for k,v in r.items() if k!='elapsed_time'} for r in b]; print(na==nb)"
# True
```

CSV comparison: 100 rows match, field-level decoding agrees.

Working tree after regeneration: RESULTS.md modified (timing only)
Restoration: git checkout HEAD -- RESULTS.md
Final git status --porcelain: (empty)

Artifact scanner: pass (36 tests, including full artifact scan of all 11 required files, prohibited path/token/pointer checks, .gitignore coverage)

Verification wall-clock: ~45s

API skips: 0
Toolchain skips: 0
Failures: 0

Post-VERIFY local unittest rerun: 36 tests OK

## Fixes vs v1 (commit c4a5cba)

- Classification independence: actual is NOT initialized from expected; handlers do not read expected_classification
- Paths sanitized: zig_executable=/portable-zig/zig, python_executable=/python-lab/bin/python3, sanitization_applied=true
- explicit_config_precedence: now implements all 4 combinations with real precedence logic
- bounded_integer_config: now tests all 7 inputs with strtol-like parsing, endptr, complete_consumption, range checks
- duplicate_envp_policy: now parses all 4 entries, implements first/last/reject policies
- tiny_feature_config: now validates feature_limit/threshold_bps/model_slot with accept/reject
- bounded_copy: now records/checks all 5 capacities, verifies minimum_success_capacity=7
- child_environment_vector: now independently validates lexicographic ordering, byte count, null terminator
- invalid_name: now requires all 4 rejections (was 2/4)
- Tests: 36 tests (was 11), full independent reconstruction coverage
- Artifact scanner: full scan of all required artifacts, prohibited path/token/pointer checks
- RESULTS.md: includes bounded_copy, precedence, bounded_int, duplicate, child_vector, tiny_feature sections
- README: sanitized OpenClaw internal tool path
- Compiler target: consistently x86_64-unknown-linux-musl throughout (v1 had GNU vs musl mismatch in VERIFY.md)
