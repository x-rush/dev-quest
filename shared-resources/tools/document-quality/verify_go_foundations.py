#!/usr/bin/env python3
"""Build the exact complete Go foundations fences, then compare documented output."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

DOCUMENTS = (
    "01-go-backend/reference/language-concepts/01-go-keywords.md",
    "01-go-backend/reference/language-concepts/02-go-built-in-functions.md",
)
CASE = re.compile(
    r"<!-- go-(example|compile-error): ([\w-]+)(?: \| ([^\n]*?))? -->\s*"
    r"(?:<!-- go-stderr: ([^\n]*?) -->\s*)?"
    r"```go\n(.*?)\n```",
    re.DOTALL,
)


def run(command: list[str], cwd: Path, env: dict[str, str]) -> dict:
    try:
        process = subprocess.run(
            command, cwd=cwd, env=env, capture_output=True, text=True,
            encoding="utf-8", timeout=60,
        )
        return {
            "command": command, "cwd": str(cwd), "returncode": process.returncode,
            "stdout": process.stdout, "stderr": process.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        def decode(value):
            return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else (value or "")
        return {
            "command": command, "cwd": str(cwd), "returncode": None,
            "stdout": decode(exc.stdout), "stderr": decode(exc.stderr),
            "error": "timeout after 60 seconds",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--go", default="go")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    env = os.environ.copy()
    env.update(GOTOOLCHAIN="local", GOPROXY="off", GOSUMDB="off", GOWORK="off")
    version = run([args.go, "version"], root, env)
    if version["returncode"] != 0:
        raise SystemExit(f"Go unavailable: {version}")
    results = []
    identifiers = set()
    for relative in DOCUMENTS:
        document = (root / relative).read_text(encoding="utf-8")
        matches = list(CASE.finditer(document))
        go_fences = len(re.findall(r"^```go$", document, re.MULTILINE))
        if len(matches) != go_fences:
            raise ValueError(f"{relative}: {go_fences} Go fences but {len(matches)} marked cases")
        for index, match in enumerate(matches):
            kind, identifier, diagnostic, stderr, source = match.groups()
            if identifier in identifiers:
                raise ValueError(f"Duplicate case: {identifier}")
            identifiers.add(identifier)
            source += "\n"
            expected_output = ""
            if kind == "example":
                end = matches[index + 1].start() if index + 1 < len(matches) else len(document)
                output = re.search(r"```text\n(.*?)\n```", document[match.end():end], re.DOTALL)
                if not output:
                    raise ValueError(f"{identifier}: missing documented expected output")
                expected_output = output.group(1) + "\n"
            elif not diagnostic:
                raise ValueError(f"{identifier}: missing expected compiler diagnostic")
            with tempfile.TemporaryDirectory(prefix="go-foundations-") as temporary:
                working = Path(temporary)
                (working / "main.go").write_text(source, encoding="utf-8")
                module = "module example.com/devquest/foundations\n\ngo 1.27\n"
                (working / "go.mod").write_text(module, encoding="utf-8")
                binary = working / ("example.exe" if os.name == "nt" else "example")
                build = run([args.go, "build", "-o", str(binary), "."], working, env)
                execution = None
                if kind == "compile-error":
                    passed = (
                        build["returncode"] not in (0, None)
                        and re.search(diagnostic, build["stderr"]) is not None
                    )
                elif build["returncode"] == 0:
                    execution = run([str(binary)], working, env)
                    passed = (
                        execution["returncode"] == 0
                        and execution["stdout"] == expected_output
                        and execution["stderr"] == ((stderr + "\n") if stderr else "")
                    )
                else:
                    passed = False
                results.append({
                    "id": identifier, "file": relative,
                    "line": document.count("\n", 0, match.start()) + 1,
                    "kind": kind, "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                    "project_files": {"main.go": source, "go.mod": module},
                    "expected_stdout": expected_output,
                    "expected_stderr": ((stderr + "\n") if stderr else ""),
                    "expected_diagnostic": diagnostic,
                    "build": build, "execution": execution, "passed": passed,
                })
                print(f"{'PASS' if passed else 'FAIL'} {identifier}", flush=True)
    report = {
        "scope": list(DOCUMENTS), "tool": version,
        "environment": {key: env[key] for key in ("GOTOOLCHAIN", "GOPROXY", "GOSUMDB", "GOWORK")},
        "total": len(results), "passed": sum(item["passed"] for item in results),
        "results": results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['passed']}/{report['total']} passed")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
