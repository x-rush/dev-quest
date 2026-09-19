#!/usr/bin/env python3
"""Extract complete first-project files unchanged; run real CLI acceptance cases."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
DOCS = {
    "php": "07-php-mastery/basics/08-first-project.md",
    "java": "08-java-revisited/basics/08-first-project.md",
}
PATTERN = re.compile(r"<!-- project-file: ([^\n]+) -->\n```(?:php|java|json)\n(.*?)\n```", re.S)


class Runner:
    def __init__(self, language, directory, report):
        self.language, self.directory, self.report = language, directory, report
        self.file = directory / ("tasks.json" if language == "php" else "books.tsv")
        self.current = None

    def command(self, argv, expected=0, env=None):
        result = subprocess.run(argv, cwd=self.directory, env=env, capture_output=True,
                                text=True, encoding="utf-8", timeout=40)
        item = {"command": argv, "exit_code": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr}
        self.current["commands"].append(item)
        assert result.returncode == expected, item
        assert not result.stderr if expected == 0 else bool(result.stderr), item
        if expected != 0:
            assert "已保存" not in result.stdout and "已添加" not in result.stdout, item
        return result.stdout

    def cli(self, *args, expected=0, file=None):
        file = file or self.file
        if self.language == "php":
            env = dict(os.environ, TASK_FILE=str(file))
            argv = ["php", "-d", "display_errors=stderr", "-d", "error_reporting=-1", "bin/task", *args]
        else:
            env = dict(os.environ)
            argv = ["java", "-cp", str(self.directory), "Main", str(file), *args]
        return self.command(argv, expected, env)

    def unchanged_failure(self, *args):
        before = self.file.read_bytes()
        self.cli(*args, expected=1)
        assert self.file.read_bytes() == before, "failed operation modified stored bytes"

    def case(self, name, fn):
        self.current = {"id": self.language + "-" + name, "document": DOCS[self.language], "commands": []}
        try:
            fn()
            self.current["passed"] = True
        except Exception as exc:
            self.current.update(passed=False, error=repr(exc))
        self.report["cases"].append(self.current)
        print(("PASS " if self.current["passed"] else "FAIL ") + self.current["id"], flush=True)

    def corruption(self, data, args):
        original = self.file.read_bytes()
        try:
            self.file.write_bytes(data)
            self.unchanged_failure(*args)
        finally:
            self.file.write_bytes(original)

    def bad_path(self, args):
        target = self.directory / "directory-as-file"
        target.mkdir(exist_ok=True)
        self.cli(*args, expected=1, file=target)
        assert target.is_dir()

    def denied(self, args):
        assert os.name == "posix" and os.geteuid() != 0, "permission test requires non-root POSIX user"
        target = self.directory / "denied"
        target.mkdir(exist_ok=True)
        target.chmod(0o555)
        try:
            self.cli(*args, expected=1, file=target / "data")
            assert not (target / "data").exists()
        finally:
            target.chmod(0o755)


def php_cases(r, composer):
    r.case("composer-autoload", lambda: r.command(["php", composer, "dump-autoload", "--no-interaction"]))
    def roundtrip():
        r.cli("add", "写周报", "--priority", "high")
        r.cli("add", "第二条")
        rows = json.loads(r.file.read_text())
        assert len(rows) == 2 and rows[0]["priority"] == "high"
        task = rows[0]["id"]
        r.cli("done", task)
        assert "写周报" not in r.cli("list")
        assert "写周报" in r.cli("list", "--all")
        r.cli("done", task)  # idempotent
        r.cli("remove", task)
        assert len(json.loads(r.file.read_text())) == 1
        r.unchanged_failure("remove", task)
    r.case("roundtrip-remove-and-idempotency", roundtrip)
    for name, args in {
        "empty-title": ("add", "   "), "control-title": ("add", "x\ny"),
        "unknown-priority": ("add", "x", "--priority", "urgent"),
        "incomplete-option": ("add", "x", "--priority"),
        "unknown-option": ("list", "--unknown"),
        "extra-argument": ("done", "00000000", "extra"),
        "missing-id": ("done", "00000000"),
    }.items():
        r.case(name, lambda args=args: r.unchanged_failure(*args))
    row = {"id": "11223344", "title": "valid", "priority": "normal", "status": "pending",
           "created_at": "2026-09-19T00:00:00+00:00"}
    for name, data in {
        "broken-json": b"{", "object-root": b"{}", "scalar-root": b"null",
        "bad-record": b"[{}]", "invalid-utf8": b'["\xff"]',
        "duplicate-id": json.dumps([row, row]).encode(),
        "invalid-date": json.dumps([{**row, "created_at": "2026-02-30T00:00:00+00:00"}]).encode(),
    }.items():
        r.case(name, lambda data=data: r.corruption(data, ("add", "new")))
    r.case("directory-path", lambda: r.bad_path(("add", "new")))
    r.case("permission-denied", lambda: r.denied(("add", "new")))
    def concurrent():
        count = len(json.loads(r.file.read_text()))
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda i: r.cli("add", f"concurrent-{i}"), range(8)))
        rows = json.loads(r.file.read_text())
        assert len(rows) == count + 8 and len({row["id"] for row in rows}) == len(rows)
    r.case("concurrent-writers", concurrent)


def java_cases(r):
    r.case("compile", lambda: r.command(["javac", "--release", "21", "-encoding", "UTF-8", "Main.java"]))
    def roundtrip():
        r.cli("add", "978-1", 'Java; "入门"', "Alice", "2024")
        assert 'Java; "入门"' in r.cli("find", "978-1")
        r.cli("borrow", "978-1")
        assert r.cli("find", "978-1").endswith("BORROWED\n")
        r.unchanged_failure("borrow", "978-1")
        r.cli("return", "978-1")
        assert r.cli("find", "978-1").endswith("AVAILABLE\n")
        r.unchanged_failure("return", "978-1")
        assert 'Java;' in r.cli("search", "JAVA")
        assert r.cli("search", "nothing") == ""
    r.case("roundtrip-and-state-machine", roundtrip)
    for name, args in {
        "duplicate-isbn": ("add", "978-1", "other", "Bob", "2025"),
        "empty-title": ("add", "978-2", " ", "Bob", "2025"),
        "control-title": ("add", "978-2", "x\ty", "Bob", "2025"),
        "invalid-year": ("add", "978-2", "title", "Bob", "abc"),
        "unknown-id": ("borrow", "missing"), "extra-argument": ("list", "extra"),
    }.items():
        r.case(name, lambda args=args: r.unchanged_failure(*args))
    prefix = b"dev-quest-books-v1\n"
    row = b"978-2\tTitle\tAuthor\t2025\tAVAILABLE\n"
    for name, data in {
        "broken-header": b"broken", "short-record": prefix + b"978-2\tTitle\n",
        "invalid-state": prefix + row.replace(b"AVAILABLE", b"LOST"),
        "duplicate-record": prefix + row + row, "invalid-utf8": prefix + b"\xff\n",
    }.items():
        r.case(name, lambda data=data: r.corruption(data, ("add", "new", "Title", "Author", "2025")))
    args = ("add", "new", "Title", "Author", "2025")
    r.case("directory-path", lambda: r.bad_path(args))
    r.case("permission-denied", lambda: r.denied(args))
    def concurrent():
        count = len(r.cli("list").splitlines())
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda i: r.cli("add", f"book-{i}", "Title", "Author", "2025"), range(8)))
        assert len(r.cli("list").splitlines()) == count + 8
    r.case("concurrent-writers", concurrent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--composer", required=True, help="absolute path to Composer 2 phar")
    args = parser.parse_args()
    report = {"scope": "two local CLI projects; no frameworks, NFS or power-loss guarantees",
              "documents": {}, "versions": {}, "cases": []}
    for executable, argv in {"php": ["php", "--version"], "java": ["java", "-version"],
                             "composer": ["php", args.composer, "--version"]}.items():
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        report["versions"][executable] = {"exit_code": result.returncode,
                                         "stdout": result.stdout, "stderr": result.stderr}
        if result.returncode:
            raise SystemExit(f"toolchain unavailable: {executable}")
    for language, relative in DOCS.items():
        raw = (ROOT / relative).read_bytes()
        files = PATTERN.findall(raw.decode().replace("\r\n", "\n"))
        expected = 7 if language == "php" else 1
        if len(files) != expected or len({name for name, _ in files}) != expected:
            raise SystemExit(f"{relative}: expected {expected} complete unique project files")
        report["documents"][relative] = {"sha256": hashlib.sha256(raw).hexdigest(),
            "files": {name: hashlib.sha256(source.encode()).hexdigest() for name, source in files}}
        with tempfile.TemporaryDirectory(prefix=f"devquest-{language}-") as tmp:
            root = Path(tmp)
            for name, source in files:
                path = root / name
                if not path.resolve().is_relative_to(root):
                    raise SystemExit(f"invalid project path: {name}")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source + "\n", encoding="utf-8")
            runner = Runner(language, root, report)
            if language == "php":
                php_cases(runner, args.composer)
            else:
                java_cases(runner)
    report["passed"] = sum(case["passed"] for case in report["cases"])
    report["total"] = len(report["cases"])
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['passed']}/{report['total']} passed")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
