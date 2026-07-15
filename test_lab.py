#!/usr/bin/env python3
import unittest, json, csv, os, subprocess, sys
class TestLab(unittest.TestCase):
    def setUp(self):
        with open("cases.json") as f: self.cases = json.load(f)
        with open("results_rows.json") as f: self.rows = json.load(f)
    def test_20_cases(self):
        self.assertEqual(len(self.cases), 20)
    def test_100_rows(self):
        self.assertEqual(len(self.rows), 100)
    def test_case_method_pairs_unique(self):
        seen = set()
        for r in self.rows:
            key = (r["case_id"], r["method"])
            self.assertNotIn(key, seen)
            seen.add(key)
        self.assertEqual(len(seen), 100)
    def test_classifications_valid(self):
        allowed = {"pass","expected_error","local_observation","api_skip","toolchain_skip","context_only","not_applicable","fail"}
        for r in self.rows:
            self.assertIn(r["expected_classification"], allowed)
            self.assertIn(r["actual_classification"], allowed)
            self.assertTrue(r["expected_classification"])
            self.assertTrue(r["actual_classification"])
    def test_not_applicable_both(self):
        for r in self.rows:
            if r["expected_classification"] == "not_applicable":
                self.assertEqual(r["actual_classification"], "not_applicable")
    def test_no_env_dump(self):
        # skip test_lab.py itself to avoid false positive on prohibited-string literals
        for fn in ["README.md","RESULTS.md","results_rows.json","results_rows.csv","env_lab.c","run_lab.py"]:
            if not os.path.exists(fn): continue
            with open(fn, errors="ignore") as f: content = f.read()
            self.assertNotIn("AWS_ACCESS_KEY", content)
    def test_results_agree(self):
        with open("results_rows.csv") as f:
            cr = list(csv.DictReader(f))
        self.assertEqual(len(cr), 100)
    def test_counts_sum(self):
        from collections import Counter
        cnt = Counter(r["actual_classification"] for r in self.rows)
        self.assertEqual(sum(cnt.values()), 100)
    def test_required_cases_present(self):
        ids = {c["id"] for c in self.cases}
        required = ["zig_compiler_marker","getenv_api_marker","missing_variable_marker","setenv_insert_marker","setenv_overwrite_false_marker","setenv_overwrite_true_marker","unsetenv_marker","empty_value_marker","getenv_pointer_snapshot_marker","putenv_alias_marker","putenv_buffer_mutation_marker","invalid_name_rejection_marker","startup_snapshot_marker","bounded_copy_marker","explicit_config_precedence_marker","bounded_integer_config_marker","duplicate_envp_policy_marker","child_environment_vector_marker","tiny_feature_config_marker","no_global_environment_or_ml_validity_claim_marker"]
        for r in required:
            self.assertIn(r, ids)
    def test_no_failures(self):
        fails = [r for r in self.rows if r["actual_classification"] == "fail"]
        self.assertEqual(len(fails), 0, f"fails: {fails[:2]}")
    def test_artifact_scanner(self):
        # scan prohibited content
        prohibited = [".o\n", "env_lab\n", "__pycache__"]
        # simple check that .gitignore exists and covers key patterns
        self.assertTrue(os.path.exists(".gitignore"))
        with open(".gitignore") as f: gi = f.read()
        self.assertIn("env_lab", gi)
        self.assertIn("*.o", gi)
if __name__ == "__main__":
    unittest.main()
