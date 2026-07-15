# RESULTS

zig: 0.14.0
zig_cc_target: x86_64-unknown-linux-musl
python: 3.12.3
platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39

cases: 20
methods: 5
rows: 100

Classifications:
- pass: 10
- expected_error: 2
- local_observation: 3
- api_skip: 0
- toolchain_skip: 0
- context_only: 5
- not_applicable: 80
- fail: 0

elapsed: 0.23s

missing_variable_null: True
setenv_insert_value: alpha
overwrite_false_result: alpha
overwrite_true_result: beta
unsetenv_null_after: True
empty_is_empty_string: True
snapshot_first: snapshot_one, second: snapshot_two
putenv_alias_value: alias_one
putenv_mutation_value: alias_two

## Bounded copy
test_val=abcdef, capacities 0,1,6,7,8
results: insufficient, insufficient, insufficient, ok, ok
minimum_success_capacity: 7

## Explicit config precedence
candidates: default, blue (env), green (explicit)
precedence: explicit > env_snapshot > compiled_default
results: default, blue, green, green

## Bounded integer config
variable: HN_ENV_LAB_TOP_K, range 1..128
inputs: 5 accept, 0 reject_range, 128 accept, -1 reject_range, 5x reject_trailing, "" reject_no_conversion, 999... reject_range

## Duplicate envp policy
input: MODEL_SLOT=blue, FEATURE_LIMIT=32, MODEL_SLOT=green, THRESHOLD_BPS=5000
first_wins: blue
last_wins: green
reject_dup: duplicate_error

## Child environment vector
entries: HN_ENV_LAB_FEATURE_LIMIT=64, HN_ENV_LAB_MODEL_SLOT=blue, HN_ENV_LAB_THRESHOLD_BPS=5000
count: 3, null_terminator: yes, lexicographic: yes

## Tiny feature config
feature_limit 64 accept, threshold_bps 5000 accept, model_slot blue accept
invalid: feature_limit 64x reject, threshold_bps 10001 reject, model_slot production reject
model_loaded: false, dataset_read: false, prediction_calculated: false
