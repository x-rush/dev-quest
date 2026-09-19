#!/usr/bin/env python3
"""Extract named Go/Rust foundations programs unchanged and verify their contracts.

Run in the isolated container documented in reports/go-rust-basics.md. All Go
programs enable the race detector. Rust failures require the exact error code.
Expected stdout comes from the following Markdown text fence, not from this tool.
"""
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
    "01-go-backend/basics/07-concurrency-basics.md": ("go", 4),
    "01-go-backend/basics/08-error-handling.md": ("go", 5),
    "11-rust-cross-platform/reference/language-concepts/04-advanced-lifetimes.md": ("rust", 7),
}
PATTERN = re.compile(
    r"<!-- verified-case: ([\w-]+)(?:; error=(E\d{4}))? -->\s*"
    r"```(go|rust)\n(.*?)\n```", re.S,
)


def execute(argv, cwd, env):
    try:
        p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True,
                           encoding="utf-8", timeout=180)
        return {"command": [str(a) for a in argv], "returncode": p.returncode,
                "stdout": p.stdout, "stderr": p.stderr}
    except subprocess.TimeoutExpired:
        return {"command": [str(a) for a in argv], "returncode": None,
                "stdout": "", "stderr": "TIMEOUT after 180 seconds"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    env = dict(os.environ, GOTOOLCHAIN="local", GOPROXY="off", GOSUMDB="off",
               GOWORK="off", CGO_ENABLED="1")
    versions = {name: execute(cmd, root, env) for name, cmd in {
        "go": ["go", "version"], "rust": ["rustc", "--version"],
        "platform": ["uname", "-sm"],
    }.items()}
    if any(v["returncode"] != 0 for v in versions.values()):
        raise SystemExit(f"toolchain unavailable: {versions}")
    result = {"scope": "9 complete Go programs built with -race, 4 Rust programs and 3 expected compile failures; no unmarked snippets or external services",
              "toolchains": versions, "results": []}
    identifiers = set()
    for relative, (language, count) in DOCUMENTS.items():
        document = (root / relative).read_text(encoding="utf-8")
        matches = list(PATTERN.finditer(document))
        if len(matches) != count:
            raise ValueError(f"{relative}: expected {count} marked cases, found {len(matches)}")
        if language == "go" and len(re.findall(r"^```go$", document, re.M)) != count:
            raise ValueError(f"{relative}: unmarked Go block")
        for index, match in enumerate(matches):
            name, diagnostic, lang, source = match.groups()
            if name in identifiers or lang != language:
                raise ValueError(f"invalid case identifier or language: {name}")
            identifiers.add(name)
            expected = None
            if not diagnostic:
                end = matches[index + 1].start() if index + 1 < len(matches) else len(document)
                output = re.search(r"```text\n(.*?)\n```", document[match.end():end], re.S)
                if not output:
                    raise ValueError(f"missing expected stdout: {name}")
                expected = output.group(1) + "\n"
            with tempfile.TemporaryDirectory(prefix="go-rust-basics-") as temp:
                work = Path(temp)
                source += "\n"
                filename = work / ("main.go" if lang == "go" else "main.rs")
                filename.write_text(source, encoding="utf-8")
                binary = work / "example"
                if lang == "go":
                    command = ["go", "build", "-race", "-o", str(binary), str(filename)]
                else:
                    command = ["rustc", "--edition", "2024", "--error-format=json", str(filename), "-o", str(binary)]
                build = execute(command, work, env)
                execution = None
                if diagnostic:
                    codes = []
                    for line in build["stderr"].splitlines():
                        try:
                            item = json.loads(line)
                            if item.get("level") == "error" and isinstance(item.get("code"), dict):
                                codes.append(item["code"].get("code"))
                        except json.JSONDecodeError:
                            pass
                    passed = build["returncode"] not in (0, None) and diagnostic in codes
                else:
                    if build["returncode"] == 0:
                        execution = execute([str(binary)], work, env)
                    passed = bool(execution and execution["returncode"] == 0
                                  and execution["stdout"] == expected and not execution["stderr"])
                row = {"case": name, "source": relative,
                       "source_line": document[:match.start()].count("\n") + 1,
                       "document_sha256": hashlib.sha256(document.encode()).hexdigest(),
                       "code_sha256": hashlib.sha256(source.encode()).hexdigest(),
                       "mode": "compile_error" if diagnostic else "runtime",
                       "expected_error": diagnostic, "expected_stdout": expected,
                       "build": build, "execution": execution,
                       "status": "PASS" if passed else "FAIL"}
                result["results"].append(row)
                print(f"{row['status']} {name}", flush=True)
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["passed"] = sum(r["status"] == "PASS" for r in result["results"])
    result["total"] = len(result["results"])
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['passed']}/{result['total']} passed")
    return 0 if result["passed"] == result["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
