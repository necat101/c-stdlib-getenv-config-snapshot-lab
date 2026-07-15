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

elapsed: 0.19s

missing_variable_null: True
setenv_insert_value: alpha
overwrite_false_result: alpha
overwrite_true_result: beta
unsetenv_null_after: True
empty_is_empty_string: True
snapshot_first: snapshot_one, second: snapshot_two
putenv_alias_value: alias_one
putenv_mutation_value: alias_two
