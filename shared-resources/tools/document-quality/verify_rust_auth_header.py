#!/usr/bin/env python3
"""Compile and run the complete dependency-free Bearer-header example verbatim."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "11-rust-cross-platform/frameworks/06-auth-middleware.md"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    text = SOURCE.read_text(encoding="utf-8")
    match = re.search(r"### 示例三：.*?```rust\n(.*?)^```", text, re.M | re.S)
    assert match, "named dependency-free example is missing"
    code = match.group(1)
    assert code.count("assert_eq!") == 6
    work = args.work.resolve(); work.mkdir(parents=True, exist_ok=True)
    program = work / "extract.rs"; executable = work / "extract"
    program.write_text(code, encoding="utf-8")
    commands = []
    for command in (["rustc", "--edition", "2024", str(program), "-o", str(executable)], [str(executable)]):
        result = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", timeout=60)
        commands.append({"argv": command, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        assert result.returncode == 0, commands[-1]
    assert commands[-1]["stdout"] == "extract_bearer 6 项断言全部通过\n"
    report = {"status": "passed", "scope": "The named dependency-free Authorization header parser only; Axum/JWT/router integration is excluded.", "documents": [{"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(text.encode()).hexdigest(), "code_sha256": hashlib.sha256(code.encode()).hexdigest()}], "cases": [{"id": "extract-bearer-six-assertions", "status": "PASS"}], "commands": commands}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS extract-bearer-six-assertions")


if __name__ == "__main__":
    main()
