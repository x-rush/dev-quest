#!/usr/bin/env python3
"""Run a deliberately small set of verbatim Go/Rust reference-page examples.

This verifier is separate from project verification and only reports the selected
P1 reference pages.  Each source file is extracted from a fenced code block that
has a stable HTML marker in the Markdown; the verifier never supplies imports,
helpers, or replacement code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "shared-resources/tools/document-quality/reports"
CASES = (
    {
        "name": "go-builtins",
        "path": "01-go-backend/reference/language-concepts/02-go-built-in-functions.md",
        "marker": "builtin-panic-recover",
        "language": "go",
        "stdout": "normal: 4 <nil>\nfailure: 0 calculation failed: division by zero\noutside panic: true\n",
    },
    {
        "name": "go-standard-library",
        "path": "01-go-backend/reference/library-guides/01-go-standard-library.md",
        "marker": "stdlib-parse-json",
        "language": "go",
        "stdout": "42 true\ntrue\n{\"count\":42,\"name\":\"go\"} 42 go\n",
    },
)


def extract_marked_block(document: Path, marker: str, language: str) -> str:
    """Return exactly one fenced block immediately following the named marker."""
    text = document.read_text(encoding="utf-8")
    pattern = rf"<!--\s*{re.escape(language)}-example:\s*{re.escape(marker)}\s*-->\s*^```{language}\s*\n(.*?)^```\s*$"
    matches = re.findall(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if len(matches) != 1:
        raise AssertionError(f"{document}: expected one {marker!r} block, found {len(matches)}")
    return matches[0]


def tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    if name == "go":
        bundled = ROOT.parents[0] / "verification-lab/go-toolchain/go/bin/go.exe"
        if bundled.exists():
            return str(bundled)
    raise FileNotFoundError(f"{name} is required; put it on PATH or use the bundled Go toolchain")


def run(argv: list[str], cwd: Path) -> dict[str, object]:
    completed = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=120)
    return {
        "argv": argv,
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def markdown(evidence: dict[str, object]) -> str:
    lines = [
        "# Go/Rust P1 参考页正文提取验证",
        "",
        "本报告刻意只覆盖本轮此前没有命名运行证据的 P1 参考页：Go 内置函数与 Go 标准库。"
        "关键字页和两篇 Rust 标准库页已有独立的命名运行证据，未在这里重复执行。",
        "",
        "验证器从 HTML 标记后紧邻的 Markdown 围栏中逐字提取 Go 源码；不会补充 import、函数或 stub。"
        "每个程序在独立临时目录运行，精确比较 stdout 和退出码。",
        "验证工具链：`" + evidence["toolchain"]["go"]["stdout"].strip() + "`。",
        "",
        "| 正文 | 标记 | 结果 |",
        "| --- | --- | --- |",
    ]
    for case in evidence["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        lines.append(f"| [{case['path']}](../../../../{case['path']}) | `{case['marker']}` | {status} |")
    lines += [
        "",
        f"结果：{sum(1 for case in evidence['cases'] if case['passed'])}/{len(evidence['cases'])} 个正文程序通过。",
        "[完整机器可读证据](go-rust-p1-page-validation.json)保存正文与代码 SHA-256、命令、stdout、stderr 和退出码。",
        "",
        "## 限定范围",
        "",
        "这不是全库代码块覆盖率报告，也不验证网络、数据库、文件系统故障、不同 Go 版本或 Rust 工具链。"
        "Go 标准库样本仅验证 strconv 和 encoding/json 的值与错误路径；内置函数样本仅验证 panic/recover 的同 goroutine 边界。",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPORTS, help="directory for the limited JSON/Markdown report")
    args = parser.parse_args()
    go = tool("go")
    evidence: dict[str, object] = {
        "scope": "named P1 reference-page body extraction only",
        "toolchain": {"go": run([go, "version"], ROOT)},
        "cases": [],
    }
    with tempfile.TemporaryDirectory(prefix="dev-quest-go-p1-") as raw:
        work = Path(raw)
        for spec in CASES:
            path = ROOT / spec["path"]
            source = extract_marked_block(path, spec["marker"], spec["language"])
            case_dir = work / spec["name"]
            case_dir.mkdir()
            source_path = case_dir / "main.go"
            source_path.write_text(source, encoding="utf-8")
            command = run([go, "run", "main.go"], case_dir)
            passed = command["returncode"] == 0 and command["stdout"] == spec["stdout"]
            evidence["cases"].append({
                "name": spec["name"], "path": spec["path"], "marker": spec["marker"],
                "document_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                "expected_stdout": spec["stdout"], "command": command, "passed": passed,
            })
    evidence["status"] = "passed" if all(case["passed"] for case in evidence["cases"]) else "failed"
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "go-rust-p1-page-validation.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output / "go-rust-p1-page-validation.md").write_text(markdown(evidence), encoding="utf-8")
    print(f"{evidence['status']}: {len(evidence['cases'])} extracted page programs")
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
