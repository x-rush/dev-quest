import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from merge_evidence import classification, merge


SCRIPT = Path(__file__).with_name("merge_evidence.py")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class MergeEvidenceTest(unittest.TestCase):
    def test_timeout_and_tool_error_are_not_passes(self):
        for status in ('TIMEOUT', 'ERROR_TOOL', 'MISS'):
            self.assertEqual(classification({'l1': {'status': 'PASS'}, 'l2': {'status': status}}), 'NEEDS_REVIEW')

    def test_mixed_run_artifacts_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            source = {'id': '1', 'file': 'a.md', 'lang': 'python', 'content': 'new'}
            write_jsonl(run / 'manifest.jsonl', [source])
            write_jsonl(run / 'results.jsonl', [{'id': '1', 'source_sha256': 'stale', 'l1': {'status': 'PASS'}}])
            with self.assertRaises(ValueError):
                merge([source], [run])
    def test_later_run_wins_for_same_content_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "current.jsonl"
            first = root / "first"; first.mkdir()
            later = root / "later"; later.mkdir()
            output = root / "out"
            record = {"file": "a.md", "lang": "python", "content": "same"}
            write_jsonl(current, [{"id": "now", **record}])
            for directory, original_id, status in ((first, "before", "FAIL"), (later, "after", "PASS")):
                write_jsonl(directory / "manifest.jsonl", [{"id": original_id, **record}])
                write_jsonl(directory / "results.jsonl", [{"id": original_id, "l1": {"status": status, "detail": ""}, "l2": {"status": "NOT_VERIFIED", "detail": ""}}])
            subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(current), "--run", str(first), "--run", str(later), "--output", str(output)], check=True)
            row = json.loads((output / "results.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(row["evidence_original_id"], "after")
            self.assertEqual(row["classification"], "PASS_CHECKED_SCOPE")

    def test_legacy_marker_preserves_a_real_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "current.jsonl"
            run = root / "named-run"; run.mkdir()
            output = root / "out"
            record = {"file": "legacy.md", "lang": "python", "content": "checked", "legacy_hash_exception": True}
            write_jsonl(current, [{"id": "current", **record}])
            write_jsonl(run / "manifest.jsonl", [{"id": "old", **record}])
            write_jsonl(run / "results.jsonl", [{"id": "old", "l1": {"status": "PASS", "detail": ""}, "l2": {"status": "PASS", "detail": ""}}])
            subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(current), "--run", str(run), "--output", str(output)], check=True)
            row = json.loads((output / "results.jsonl").read_text(encoding="utf-8"))
            self.assertTrue(row["legacy_hash_exception"])
            self.assertEqual(row["classification"], "PASS_CHECKED_SCOPE")
            self.assertEqual(row["evidence_run"], "named-run")

    def test_content_key_ignores_ids_and_preserves_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "current.jsonl"
            run = root / "run"; run.mkdir()
            output = root / "out"
            write_jsonl(current, [
                {"id": "current-a", "file": "a.md", "lang": "python", "content": "same"},
                {"id": "current-b", "file": "b.md", "lang": "python", "content": "changed"},
            ])
            write_jsonl(run / "manifest.jsonl", [
                {"id": "old-99", "file": "a.md", "lang": "python", "content": "same"},
                {"id": "old-b", "file": "b.md", "lang": "python", "content": "old"},
            ])
            write_jsonl(run / "results.jsonl", [
                {"id": "old-99", "l1": {"status": "PASS", "detail": ""}, "l2": {"status": "FAIL", "detail": "boom"}},
                {"id": "old-b", "l1": {"status": "PASS", "detail": ""}, "l2": {"status": "PASS", "detail": ""}},
            ])
            subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(current), "--run", str(run), "--output", str(output)], check=True)
            rows = [json.loads(line) for line in (output / "results.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(rows[0]["evidence_original_id"], "old-99")  # same content, different ID matches
            self.assertEqual(rows[0]["classification"], "NEEDS_REVIEW")  # FAIL remains FAIL
            self.assertIsNone(rows[1]["evidence_run"])  # same ID would not rescue changed content
            self.assertEqual(rows[1]["classification"], "NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
