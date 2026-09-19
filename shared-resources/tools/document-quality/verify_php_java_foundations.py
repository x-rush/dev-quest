#!/usr/bin/env python3
"""Run the explicitly marked, complete PHP/Java reference examples unchanged."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENTS = {
    "07-php-mastery/reference/language-concepts/01-php-keywords.md": ("php", 3),
    "07-php-mastery/reference/language-concepts/02-built-in-functions.md": ("php", 5),
    "08-java-revisited/reference/language-concepts/01-java-keywords.md": ("java", 4),
    "08-java-revisited/reference/library-guides/01-standard-library.md": ("java", 5),
}
PATTERN = re.compile(
    r'<!-- reference-case: (\{[^\n]+\}) -->\n```(php|java)\n(.*?)\n```', re.S
)


def command(args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", timeout=45)
    return {"command": args, "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--language", choices=("php", "java", "all"), default="all")
    args = parser.parse_args()
    report = {"scope": "marked complete examples only; not framework or network validation",
              "versions": {}, "documents": {}, "cases": []}
    selected = {p: v for p, v in DOCUMENTS.items() if args.language in ("all", v[0])}
    languages = {v[0] for v in selected.values()}
    for executable in ((["php"] if "php" in languages else []) +
                       (["javac", "java"] if "java" in languages else [])):
        if not shutil.which(executable):
            raise SystemExit(f"required executable not found: {executable}")
        report["versions"][executable] = command(
            [executable, "--version" if executable == "php" else "-version"], ROOT)
    seen = set()
    for relative, (language, count) in selected.items():
        path = ROOT / relative
        raw = path.read_bytes()
        text = raw.decode("utf-8").replace("\r\n", "\n")
        cases = PATTERN.findall(text)
        if len(cases) != count:
            raise SystemExit(f"{relative}: expected {count} marked cases, got {len(cases)}")
        report["documents"][relative] = hashlib.sha256(raw).hexdigest()
        for metadata, actual_language, source in cases:
            spec = json.loads(metadata)
            if actual_language != language or spec["id"] in seen:
                raise SystemExit(f"invalid or duplicated case: {spec['id']}")
            seen.add(spec["id"])
            item = {"id": spec["id"], "document": relative,
                    "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                    "expected_stdout": spec["stdout"], "commands": []}
            try:
                with tempfile.TemporaryDirectory(prefix="reference-") as tmp:
                    filename = "Main.java" if language == "java" else "main.php"
                    (Path(tmp) / filename).write_text(source + "\n", encoding="utf-8")
                    if language == "java":
                        item["commands"].append(command(
                            ["javac", "--release", "21", "-encoding", "UTF-8", filename], tmp))
                        if item["commands"][-1]["exit_code"] != 0:
                            raise RuntimeError("compilation failed")
                        run = command(["java", "-cp", tmp, "Main"], tmp)
                    else:
                        run = command(["php", "-d", "display_errors=stderr",
                                       "-d", "error_reporting=-1", filename], tmp)
                    item["commands"].append(run)
                    item["passed"] = (run["exit_code"] == 0 and not run["stderr"]
                                      and run["stdout"] == spec["stdout"])
            except (subprocess.TimeoutExpired, RuntimeError) as exc:
                item["passed"] = False
                item["error"] = str(exc)
            report["cases"].append(item)
            print(f"{'PASS' if item['passed'] else 'FAIL'} {item['id']}")
    report["passed"] = sum(case["passed"] for case in report["cases"])
    report["total"] = len(report["cases"])
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['passed']}/{report['total']} passed")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
