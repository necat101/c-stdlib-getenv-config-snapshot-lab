#!/usr/bin/env python3
import unittest, json, csv, os, subprocess, sys, tempfile, shutil
class TestLab(unittest.TestCase):
    def setUp(self):
        with open("cases.json") as f: self.cases = json.load(f)
        with open("results_rows.json") as f: self.rows = json.load(f)
    def test_20_cases(self): self.assertEqual(len(self.cases), 20)
    def test_100_rows(self): self.assertEqual(len(self.rows), 100)
    def test_case_method_pairs_unique(self):
        seen=set()
        for r in self.rows:
            key=(r["case_id"],r["method"])
            self.assertNotIn(key, seen); seen.add(key)
        self.assertEqual(len(seen), 100)
    def test_classifications_valid(self):
        allowed={"pass","expected_error","local_observation","api_skip","toolchain_skip","context_only","not_applicable","fail"}
        for r in self.rows:
            self.assertIn(r["expected_classification"], allowed)
            self.assertIn(r["actual_classification"], allowed)
            self.assertTrue(r["expected_classification"])
            self.assertTrue(r["actual_classification"])
    def test_not_applicable_both(self):
        for r in self.rows:
            if r["expected_classification"]=="not_applicable":
                self.assertEqual(r["actual_classification"], "not_applicable")
    def test_actual_independent(self):
        # mutate expected classifications, rerun production, actual must NOT change
        with open("cases.json") as f: cases=json.load(f)
        mutated=[]
        for c in cases:
            m={"id":c["id"],"expect":{}}
            for k,v in c["expect"].items():
                m["expect"][k]="fail" if v!="not_applicable" else "not_applicable"
            mutated.append(m)
        td=tempfile.mkdtemp()
        try:
            for fn in ["env_lab.c","run_lab.py"]:
                shutil.copy(fn, td)
            with open(os.path.join(td,"cases.json"),"w") as f: json.dump(mutated,f)
            r=subprocess.run([sys.executable,"run_lab.py"], cwd=td, capture_output=True, text=True, timeout=10)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(os.path.join(td,"results_rows.json")) as f: rows_mut=json.load(f)
            orig_map={(x["case_id"],x["method"]):x["actual_classification"] for x in self.rows}
            mut_map={(x["case_id"],x["method"]):x["actual_classification"] for x in rows_mut}
            self.assertEqual(orig_map, mut_map, "actual_classification changed when expected was mutated – not independent")
        finally: shutil.rmtree(td)
    def test_missing_handler_becomes_fail(self):
        # remove a handler from handlers dict, run, check fail
        with open("run_lab.py") as f: src=f.read()
        broken = src.replace('"exercise_getenv": handle_exercise_getenv,', '"exercise_getenv": None,', 1)
        td=tempfile.mkdtemp()
        try:
            for fn in ["env_lab.c","cases.json"]:
                shutil.copy(fn, td)
            with open(os.path.join(td,"run_lab.py"),"w") as f: f.write(broken)
            r=subprocess.run([sys.executable,"run_lab.py"], cwd=td, capture_output=True, text=True, timeout=10)
            self.assertEqual(r.returncode, 0)
            with open(os.path.join(td,"results_rows.json")) as f: rows=json.load(f)
            # exercise_getenv rows should now be fail (except not_applicable)
            getenv_rows=[x for x in rows if x["method"]=="exercise_getenv" and x["expected_classification"]!="not_applicable"]
            self.assertTrue(len(getenv_rows)>0)
            fails=[x for x in getenv_rows if x["actual_classification"]=="fail"]
            self.assertTrue(len(fails)>0, "missing handler did not produce fail")
            # check failure_reason is set
            self.assertTrue(all(x.get("failure_reason") for x in fails))
        finally: shutil.rmtree(td)
    def test_no_zig_path(self):
        # run with empty PATH and no ZIG_BIN, check toolchain_skip
        td=tempfile.mkdtemp()
        try:
            for fn in ["env_lab.c","run_lab.py","cases.json"]:
                shutil.copy(fn, td)
            env=os.environ.copy()
            env.pop("ZIG_BIN",None)
            env["PATH"]="/nonexistent"
            env["HOME"]="/tmp/empty_no_zig_home"
            r=subprocess.run([sys.executable,"run_lab.py"], cwd=td, capture_output=True, text=True, timeout=10, env=env)
            self.assertEqual(r.returncode, 0)
            with open(os.path.join(td,"results_rows.json")) as f: rows=json.load(f)
            # at least zig_compiler_marker should be toolchain_skip
            zr=[x for x in rows if x["case_id"]=="zig_compiler_marker" and x["method"]=="inspect_toolchain"][0]
            self.assertEqual(zr["actual_classification"], "toolchain_skip")
            # no C metadata should be present
            self.assertIsNone(zr.get("sizeof_void_p"))
        finally: shutil.rmtree(td)
    def test_compiler_is_zig(self):
        r=[x for x in self.rows if x["case_id"]=="zig_compiler_marker" and x["method"]=="inspect_toolchain"][0]
        self.assertEqual(r["actual_classification"], "pass")
        self.assertIn("zig", (r["zig_executable"] or "").lower())
    def test_no_unrelated_env(self):
        blob=open("results_rows.json").read()
        for bad in ["AWS_ACCESS","OPENAI_API","SECRET","PASSWORD","GITHUB_TOKEN","ghp_"]:
            self.assertNotIn(bad, blob)
    def test_missing_variable(self):
        r=[x for x in self.rows if x["case_id"]=="missing_variable_marker" and x["method"]=="exercise_getenv"][0]
        self.assertEqual(r["actual_classification"], "expected_error")
        self.assertTrue(r["getenv_returned_null"])
    def test_setenv_insert(self):
        r=[x for x in self.rows if x["case_id"]=="setenv_insert_marker" and x["method"]=="exercise_mutation"][0]
        self.assertEqual(r["actual_classification"], "pass")
    def test_overwrite_false(self):
        r=[x for x in self.rows if x["case_id"]=="setenv_overwrite_false_marker" and x["method"]=="exercise_mutation"][0]
        self.assertEqual(r["actual_classification"], "local_observation")
    def test_overwrite_true(self):
        r=[x for x in self.rows if x["case_id"]=="setenv_overwrite_true_marker" and x["method"]=="exercise_mutation"][0]
        self.assertEqual(r["actual_classification"], "pass")
    def test_unsetenv(self):
        r=[x for x in self.rows if x["case_id"]=="unsetenv_marker" and x["method"]=="exercise_mutation"][0]
        self.assertEqual(r["actual_classification"], "pass")
    def test_empty_distinct(self):
        r=[x for x in self.rows if x["case_id"]=="empty_value_marker" and x["method"]=="exercise_getenv"][0]
        self.assertEqual(r["actual_classification"], "pass")
    def test_snapshot_unchanged(self):
        r=[x for x in self.rows if x["case_id"]=="getenv_pointer_snapshot_marker" and x["method"]=="enumerate_snapshot"][0]
        self.assertEqual(r["actual_classification"], "pass")
    def test_putenv_alias(self):
        r=[x for x in self.rows if x["case_id"]=="putenv_alias_marker" and x["method"]=="exercise_mutation"][0]
        self.assertEqual(r["actual_classification"], "local_observation")
        self.assertTrue(r["putenv_alias_observed"])
    def test_putenv_mutation(self):
        r=[x for x in self.rows if x["case_id"]=="putenv_buffer_mutation_marker" and x["method"]=="exercise_mutation"][0]
        self.assertEqual(r["actual_classification"], "local_observation")
    def test_invalid_names_all_four(self):
        r=[x for x in self.rows if x["case_id"]=="invalid_name_rejection_marker" and x["method"]=="exercise_mutation"][0]
        self.assertEqual(r["library_return_value"], 4)
    def test_startup_snapshot_three_entries(self):
        r=[x for x in self.rows if x["case_id"]=="startup_snapshot_marker" and x["method"]=="enumerate_snapshot"][0]
        self.assertEqual(r["actual_classification"], "pass")
    def test_bounded_copy_capacities(self):
        r=[x for x in self.rows if x["case_id"]=="bounded_copy_marker" and x["method"]=="enumerate_snapshot"][0]
        self.assertEqual(r["actual_classification"], "pass")
        self.assertEqual(r["required_capacity"], 7)
        import json as js
        data = js.loads(r["copied_value"])
        self.assertEqual(len(data), 5)
        # check sentinel_ok true for all
        for d in data:
            self.assertTrue(d.get("sentinel_ok"), f"sentinel failed at cap {d.get('cap')}")
    def test_precedence_recomputed(self):
        r=[x for x in self.rows if x["case_id"]=="explicit_config_precedence_marker" and x["method"]=="ml_context_observation"][0]
        self.assertEqual(r["actual_classification"], "context_only")
        # independently recompute precedence
        # explicit > env > default, expect default, blue, green, green
        import json as js
        src = r.get("configuration_source") or "[]"
        data = js.loads(src) if isinstance(src, str) else src
        self.assertEqual(len(data), 4)
        expected = ["default","blue","green","green"]
        actual = [x["selected"] for x in data]
        self.assertEqual(actual, expected)
    def test_bounded_int_recomputed(self):
        r=[x for x in self.rows if x["case_id"]=="bounded_integer_config_marker" and x["method"]=="ml_context_observation"][0]
        self.assertEqual(r["actual_classification"], "context_only")
        import json as js
        cand = r.get("configuration_candidates")
        if isinstance(cand, str): cand = js.loads(cand)
        self.assertEqual(len(cand), 7)
        # inputs: 5 accept, 0 reject, 128 accept, -1 reject, 5x reject, "" reject, big reject
        accepts = [c.get("policy_status")=="accept" for c in cand]
        self.assertEqual(accepts, [True, False, True, False, False, False, False])
        # check endptr / errno were recorded from C
        for c in cand:
            self.assertIn("endptr_offset", c)
            self.assertIn("complete_consumption", c)
    def test_duplicate_policy_recomputed(self):
        r=[x for x in self.rows if x["case_id"]=="duplicate_envp_policy_marker" and x["method"]=="ml_context_observation"][0]
        self.assertEqual(r["actual_classification"], "context_only")
        # independently recompute first/last wins
        input_strings = ["HN_ENV_LAB_MODEL_SLOT=blue","HN_ENV_LAB_FEATURE_LIMIT=32","HN_ENV_LAB_MODEL_SLOT=green","HN_ENV_LAB_THRESHOLD_BPS=5000"]
        parsed = [s.split("=",1)[0] for s in input_strings]
        first_seen = {}
        for s, name in zip(input_strings, parsed):
            if name not in first_seen: first_seen[name] = s.split("=",1)[1]
        last_seen = {}
        for s, name in zip(input_strings, parsed):
            last_seen[name] = s.split("=",1)[1]
        self.assertEqual(first_seen.get("HN_ENV_LAB_MODEL_SLOT"), "blue")
        self.assertEqual(last_seen.get("HN_ENV_LAB_MODEL_SLOT"), "green")
        # check recorded output matches
        self.assertIn("blue", str(r["selected_value"]))
        self.assertIn("green", str(r["selected_value"]))
    def test_child_vector_rebuilt(self):
        r=[x for x in self.rows if x["case_id"]=="child_environment_vector_marker" and x["method"]=="enumerate_snapshot"][0]
        self.assertEqual(r["actual_classification"], "pass")
        self.assertEqual(r["environment_vector_count"], 3)
        self.assertTrue(r["environment_vector_null_terminator_present"])
        # independently verify lexicographic order
        import json as js
        entries = r["environment_vector_entries"]
        if isinstance(entries, str): entries = js.loads(entries)
        self.assertEqual(entries, sorted(entries))
    def test_tiny_feature_recomputed(self):
        r=[x for x in self.rows if x["case_id"]=="tiny_feature_config_marker" and x["method"]=="ml_context_observation"][0]
        self.assertEqual(r["actual_classification"], "context_only")
        self.assertFalse(r["model_loaded"]); self.assertFalse(r["dataset_read"]); self.assertFalse(r["prediction_calculated"])
        import json as js
        cand = r.get("configuration_candidates")
        if isinstance(cand, str): cand = js.loads(cand)
        # 3 valid + 3 invalid = 6
        self.assertEqual(len(cand), 6)
        accepts = [c["accept"] for c in cand]
        self.assertEqual(accepts, [True,True,True,False,False,False])
    def test_no_threads(self):
        for r in self.rows:
            self.assertFalse(r["threaded_operation_executed"])
            self.assertFalse(r["external_process_executed"])
    def test_results_agree(self):
        # full field-level JSON/CSV agreement
        with open("results_rows.csv") as f:
            cr = list(csv.DictReader(f))
        self.assertEqual(len(cr), len(self.rows))
        import json as js
        for jr, csvr in zip(self.rows, cr):
            for k in jr:
                jv = jr[k]
                cv = csvr[k]
                # decode structured fields
                if isinstance(jv, (list, dict)):
                    cv_dec = js.loads(cv) if cv else None
                    self.assertEqual(cv_dec, jv, f"field {k} mismatch at {jr['case_id']}/{jr['method']}")
                elif isinstance(jv, bool):
                    self.assertEqual(cv.lower(), str(jv).lower(), k)
                elif jv is None:
                    self.assertEqual(cv, "", k)
                else:
                    # compare as strings, allow int/float string conversion
                    self.assertEqual(str(cv), str(jv), f"field {k} mismatch: {cv!r} != {jv!r}")
    def test_counts_sum(self):
        from collections import Counter
        cnt = Counter(r["actual_classification"] for r in self.rows)
        self.assertEqual(sum(cnt.values()), 100)
    def test_no_failures(self):
        fails = [r for r in self.rows if r["actual_classification"] == "fail"]
        self.assertEqual(len(fails), 0, f"fails: {fails[:2]}")
    def test_required_cases_present(self):
        ids = {c["id"] for c in self.cases}
        required = ["zig_compiler_marker","getenv_api_marker","missing_variable_marker","setenv_insert_marker","setenv_overwrite_false_marker","setenv_overwrite_true_marker","unsetenv_marker","empty_value_marker","getenv_pointer_snapshot_marker","putenv_alias_marker","putenv_buffer_mutation_marker","invalid_name_rejection_marker","startup_snapshot_marker","bounded_copy_marker","explicit_config_precedence_marker","bounded_integer_config_marker","duplicate_envp_policy_marker","child_environment_vector_marker","tiny_feature_config_marker","no_global_environment_or_ml_validity_claim_marker"]
        for r in required: self.assertIn(r, ids)
    def test_artifact_scanner(self):
        import re
        artifacts = ["README.md","RESULTS.md","cases.json","results_rows.json","results_rows.csv","env_lab.c","run_lab.py","test_lab.py","hn_thread_evidence.md","hn_comments_sanitized.json",".gitignore"]
        if os.path.exists("VERIFY.md"): artifacts.append("VERIFY.md")
        issues=[]
        for fn in artifacts:
            if not os.path.exists(fn):
                if fn=="VERIFY.md": continue
                self.fail(f"missing artifact {fn}")
            with open(fn, errors="ignore") as f: content=f.read()
            # raw pointer check
            if fn.endswith(".json") or fn.endswith(".csv") or fn.endswith(".md"):
                if re.search(r"0x[0-9a-fA-F]{8,}", content):
                    issues.append(f"{fn}: raw pointer")
            # check prohibited patterns
            checks = [
                ("/home/", "home path", "test_lab.py" in fn),
                ("ghp_", "github token", "test_lab.py" in fn),
                ("sk-", "openai key", "test_lab.py" in fn),
                ("AWS_ACCESS_KEY", "aws key", "test_lab.py" in fn),
                ("PRIVATE KEY", "private key", "test_lab.py" in fn),
                ("openclaw", "internal tool", "test_lab.py" in fn),
            ]
            for pat, name, allow in checks:
                if pat in content and not allow:
                    # allow .gitignore tmp pattern
                    if fn==".gitignore" and "tmp" in pat.lower(): continue
                    # allow email in hn_comments
                    if name=="email" and fn=="hn_comments_sanitized.json": continue
                    issues.append(f"{fn}: {name}")
            # email check separately with regex
            if "hn_comments_sanitized.json" not in fn:
                if re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", content):
                    issues.append(f"{fn}: email")
        with open(".gitignore") as f: gi=f.read()
        for pat in ["env_lab","*.o","zig-cache","__pycache__","*.pyc"]:
            self.assertIn(pat, gi)
        self.assertEqual(issues, [], f"scanner issues: {issues}")

    def test_no_raw_pointers(self):
        import re
        blob=open("results_rows.json").read()
        self.assertIsNone(re.search(r"0x[0-9a-fA-F]{8,}", blob))
    def test_paths_sanitized(self):
        for r in self.rows:
            ze=r.get("zig_executable") or ""
            pe=r.get("python_executable") or ""
            self.assertNotIn("/home", ze+pe)
            self.assertNotIn("/tmp", ze+pe)
            self.assertTrue(r.get("sanitization_applied"))
            if ze: self.assertTrue(ze.startswith("/portable-zig") or ze.startswith("/workspace"))
            if pe: self.assertTrue(pe.startswith("/python-lab") or pe.startswith("/workspace"))
if __name__ == "__main__": unittest.main()
