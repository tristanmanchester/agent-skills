"""Tests of maintenance code, not an evaluation of model-generated writing."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evaluate  # noqa: E402
import check_package  # noqa: E402


class EvaluationTests(unittest.TestCase):
    def original(self, case_id: str) -> str:
        case = evaluate.get_case(case_id)
        return (ROOT / case["files"][0]).read_text(encoding="utf-8")

    def status(self, case_id: str, text: str) -> str:
        return evaluate.check_output(evaluate.get_case(case_id), text)["status"]

    def test_twenty_complete_cases(self):
        cases = evaluate.load_cases()
        self.assertEqual(len(cases), 20)
        self.assertEqual(len({c["id"] for c in cases}), 20)
        for case in cases:
            self.assertTrue(case["hard_gates"] and case["assertions"])
            self.assertTrue(evaluate.render_task(case).strip())

    def test_export_does_not_leak_rubric(self):
        for case in evaluate.load_cases():
            task = evaluate.render_task(case)
            self.assertIn(case["prompt"], task)
            self.assertNotIn(case["expected_output"], task)
            for gate in case["hard_gates"]:
                self.assertNotIn(gate, task)

    def test_prepare_only_task_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "fresh"
            path = evaluate.prepare_case(evaluate.get_case("Q03"), out)
            self.assertEqual(path.name, "task.md")
            self.assertEqual([p.name for p in out.iterdir()], ["task.md"])
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                evaluate.prepare_case(evaluate.get_case("Q03"), out)
            self.assertEqual(path.read_bytes(), before)

    def test_prepare_rejects_output_inside_skill(self):
        with self.assertRaises(ValueError):
            evaluate.prepare_case(evaluate.get_case("Q03"), ROOT / "forbidden-test-output")
        self.assertFalse((ROOT / "forbidden-test-output").exists())

    def test_unknown_case_rejected(self):
        with self.assertRaises(ValueError):
            evaluate.get_case("Q99")

    def test_empty_output_fails(self):
        self.assertEqual(self.status("Q01", " \n"), "mechanical_fail")

    def test_exact_good_paragraph_passes(self):
        self.assertEqual(self.status("Q04", self.original("Q04")), "mechanical_pass")

    def test_unnecessary_dialect_change_fails(self):
        self.assertEqual(self.status("Q04", self.original("Q04").replace("analyser", "analyzer")), "mechanical_fail")

    def test_line_endings_and_final_newline_normalized(self):
        source = self.original("Q04")
        self.assertEqual(self.status("Q04", source.replace("\n", "\r\n") + "\r\n"), "mechanical_pass")

    def test_internal_whitespace_not_normalized(self):
        self.assertEqual(self.status("Q04", self.original("Q04").replace("The analyser", "The  analyser")), "mechanical_fail")

    def test_standalone_warning_order_passes(self):
        self.assertEqual(self.status("Q05", self.original("Q05")), "mechanical_pass")

    def test_deduplicated_warning_fails(self):
        source = self.original("Q05")
        warning = "This action permanently deletes every object in the selected sandbox."
        self.assertEqual(self.status("Q05", source.replace(warning, "", 1)), "mechanical_fail")

    def test_command_before_warning_fails(self):
        source = self.original("Q05")
        first = "Run `sandboxctl remove A --all-objects`."
        source = first + "\n" + source.replace(first, "", 1)
        self.assertEqual(self.status("Q05", source), "mechanical_fail")

    def test_allowed_section_change_passes(self):
        source = self.original("Q08").replace("In order to configure", "To configure")
        self.assertEqual(self.status("Q08", source), "mechanical_pass")

    def test_outside_section_change_fails(self):
        source = self.original("Q08").replace("The visualiser opens saved traces.", "The app opens traces.")
        self.assertEqual(self.status("Q08", source), "mechanical_fail")

    def test_anchor_change_fails(self):
        source = self.original("Q08").replace('id="configuration"', 'id="config"')
        self.assertEqual(self.status("Q08", source), "mechanical_fail")

    def test_unrequested_fenced_wrapper_fails(self):
        self.assertEqual(self.status("Q08", "```md\n" + self.original("Q08") + "```"), "mechanical_fail")

    def test_missing_protected_literal_fails(self):
        self.assertEqual(self.status("Q01", "Returns a collection."), "mechanical_fail")

    def test_heading_restriction_is_format_specific(self):
        text = "# Results\nLinux passed; no macOS result was supplied."
        self.assertEqual(self.status("Q12", text), "mechanical_fail")

    def test_explicit_word_limit_fails(self):
        text = "48 s 25 s 2 GiB " + "word " * 181
        self.assertEqual(self.status("Q13", text), "mechanical_fail")

    def test_mechanical_pass_never_implies_semantic_pass(self):
        # These tokens meet literal checks while the invented runtime assertion
        # fails semantic review. The checker must not claim an overall pass.
        text = "Release 2.6 definitely retains records for either 60 or 14 days in every deployment."
        result = evaluate.check_output(evaluate.get_case("Q03"), text)
        self.assertEqual(result["status"], "mechanical_pass")
        self.assertIs(result["semantic_review_required"], True)
        self.assertNotIn("overall_pass", result)

    def test_unknown_check_type_rejected(self):
        with self.assertRaises(ValueError):
            evaluate.validate_check({"type": "semantic_magic"}, evaluate.get_case("Q01"), ROOT)

    def test_bad_regex_rejected(self):
        with self.assertRaises(re.error):
            evaluate.validate_check({"type": "not_regex", "value": "["}, evaluate.get_case("Q01"), ROOT)

    def test_boolean_count_rejected(self):
        with self.assertRaises(ValueError):
            evaluate.validate_check({"type": "max_words", "count": True}, evaluate.get_case("Q01"), ROOT)

    def test_absolute_and_traversal_paths_rejected(self):
        for path in ("/etc/passwd", "../SKILL.md", "..\\SKILL.md"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                evaluate.package_path(ROOT, path)

    def test_undeclared_file_check_rejected(self):
        with self.assertRaises(ValueError):
            evaluate.validate_check({"type": "equals_fixture", "file": "SKILL.md"}, evaluate.get_case("Q01"), ROOT)

    def test_duplicate_case_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "write-good-docs"
            shutil.copytree(ROOT / "evals", root / "evals")
            path = root / "evals/evals.json"
            data = json.loads(path.read_text())
            data["evals"][1]["id"] = data["evals"][0]["id"]
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                evaluate.load_cases(root)

    def test_cli_reports_unknown_case_as_error(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            code = evaluate.main(["check", "--case", "Q99", "--output", "missing"])
        self.assertEqual(code, 2)
        self.assertIn("Unknown case", err.getvalue())

    def test_cli_handles_missing_file(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stderr(io.StringIO()):
            code = evaluate.main(["check", "--case", "Q01", "--output", str(Path(d) / "missing.md")])
        self.assertEqual(code, 2)

    def test_cli_runs_from_another_directory(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "answer.md"
            output.write_text(self.original("Q04"))
            run = subprocess.run([sys.executable, str(ROOT / "scripts/evaluate.py"), "check", "--case", "Q04", "--output", str(output)], cwd=d, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIs(json.loads(run.stdout)["semantic_review_required"], True)


class PackageTests(unittest.TestCase):
    def test_frontmatter_matches_version(self):
        self.assertEqual(check_package.check_frontmatter(ROOT)["version"], "2.1.0")

    def test_local_links_resolve(self):
        self.assertGreater(check_package.check_links(ROOT, check_package.package_files(ROOT)), 0)

    def test_broken_local_link_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            page = root / "README.md"
            page.write_text("[Missing](missing.md)\n")
            with self.assertRaises(ValueError):
                check_package.check_links(root, [page])

    def test_link_inside_fence_is_not_followed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            page = root / "README.md"
            page.write_text("```md\n[Example](missing.md)\n```\n")
            self.assertEqual(check_package.check_links(root, [page]), 0)

    def test_heading_and_html_anchors(self):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "README.md"
            page.write_text('# Title\n\n## Next step\n\n## Next step\n\n<a id="fixed"></a>\n')
            self.assertTrue({"title", "next-step", "next-step-1", "fixed"}.issubset(check_package.anchors(page)))

    def test_manifest_detects_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / "example.txt"
            target.write_bytes(b"original\n")
            manifest = root / "MANIFEST.json"
            manifest.write_text(json.dumps({"schema_version": 1, "skill_name": "write-good-docs", "version": "2.1.0", "files": {"example.txt": {"bytes": len(target.read_bytes()), "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}}}))
            self.assertIn("verified 1", check_package.verify_manifest(root, [target, manifest], "2.1.0"))
            target.write_bytes(b"changed\n")
            with self.assertRaises(ValueError):
                check_package.verify_manifest(root, [target, manifest], "2.1.0")


if __name__ == "__main__":
    unittest.main()
