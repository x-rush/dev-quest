#!/usr/bin/env python3
"""Verify unchanged, named Go composite and Rust macro examples from Markdown."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

DOCUMENTS = {
    "01-go-backend/basics/04-composite-types.md": ("go", 4),
    "11-rust-cross-platform/reference/language-concepts/05-macros.md": ("rust", 6),
}
PATTERN = re.compile(r"<!-- verified-case: ([\w-]+)(?:; error=(E\d{4}))? -->\s*```(go|rust)\n(.*?)\n```", re.S)


def run(command, cwd, env):
    try:
        process = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                 text=True, encoding="utf-8", timeout=180)
        return {"command": list(map(str, command)), "returncode": process.returncode,
                "stdout": process.stdout, "stderr": process.stderr}
    except subprocess.TimeoutExpired:
        return {"command": list(map(str, command)), "returncode": None,
                "stdout": "", "stderr": "TIMEOUT after 180 seconds"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    env = dict(os.environ, GOTOOLCHAIN="local", GOPROXY="off", GOSUMDB="off", GOWORK="off", CGO_ENABLED="1")
    versions = {name: run(command, root, env) for name, command in {
        "go": ["go", "version"], "rust": ["rustc", "--version"], "platform": ["uname", "-sm"]}.items()}
    if any(item["returncode"] != 0 for item in versions.values()):
        raise SystemExit(f"toolchain unavailable: {versions}")
    report = {"scope": "4 Go programs, 4 Rust programs, 2 expected Rust compilation errors; only named cases", "toolchains": versions, "results": []}
    identifiers = set()
    for relative, (language, count) in DOCUMENTS.items():
        document = (root / relative).read_text(encoding="utf-8")
        matches = list(PATTERN.finditer(document))
        if len(matches) != count:
            raise ValueError(f"{relative}: expected {count} cases, got {len(matches)}")
        for index, match in enumerate(matches):
            name, diagnostic, lang, code = match.groups()
            if name in identifiers or lang != language:
                raise ValueError(f"invalid case: {name}")
            identifiers.add(name)
            expected = None
            if not diagnostic:
                end = matches[index + 1].start() if index + 1 < len(matches) else len(document)
                output = re.search(r"```text\n(.*?)\n```", document[match.end():end], re.S)
                if not output:
                    raise ValueError(f"missing stdout: {name}")
                expected = output.group(1) + "\n"
            code += "\n"
            with tempfile.TemporaryDirectory(prefix="composite-macros-") as temp:
                work = Path(temp)
                source = work / ("main.go" if lang == "go" else "main.rs")
                source.write_text(code, encoding="utf-8")
                binary = work / "example"
                command = (["go", "build", "-race", "-o", str(binary), str(source)] if lang == "go" else
                           ["rustc", "--edition", "2024", "--error-format=json", str(source), "-o", str(binary)])
                build = run(command, work, env)
                execution = None
                if diagnostic:
                    codes = []
                    for line in build["stderr"].splitlines():
                        item = json.loads(line)
                        if item.get("level") == "error" and isinstance(item.get("code"), dict):
                            codes.append(item["code"].get("code"))
                    passed = build["returncode"] not in (0, None) and diagnostic in codes
                else:
                    if build["returncode"] == 0:
                        execution = run([str(binary)], work, env)
                    passed = bool(execution and execution["returncode"] == 0 and
                                  execution["stdout"] == expected and not execution["stderr"])
                row = {"case": name, "source": relative, "source_line": document[:match.start()].count("\n") + 1,
                       "document_sha256": hashlib.sha256(document.encode()).hexdigest(),
                       "code_sha256": hashlib.sha256(code.encode()).hexdigest(), "mode": "compile_error" if diagnostic else "runtime",
                       "expected_error": diagnostic, "expected_stdout": expected, "build": build, "execution": execution,
                       "status": "PASS" if passed else "FAIL"}
                report["results"].append(row)
                print(f"{row['status']} {name}", flush=True)
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["passed"] = sum(row["status"] == "PASS" for row in report["results"])
    report["total"] = len(report["results"])
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['passed']}/{report['total']} passed")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
