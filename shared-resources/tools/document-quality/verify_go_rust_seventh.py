#!/usr/bin/env python3
"""Verify four newly named Go P1 Markdown body programs, and only those programs.

The script extracts the fence immediately after each HTML marker verbatim.  It
does not add imports, helpers, or replacement implementations.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
GO = ROOT.parent / "verification-lab" / "go-toolchain" / "go" / "bin" / "go.exe"
CASES = (
    ("keyword-decisions", "01-go-backend/reference/language-concepts/01-go-keywords.md", "keyword-decisions-seventh", "invalid pass perfect\nmatched 2\nran body of 99\nstring bytes: 5\n"),
    ("builtin-append-copy", "01-go-backend/reference/language-concepts/02-go-built-in-functions.md", "builtin-append-copy-seventh", "shared: [1 9 3] [1 9]\nseparate: [1 9 3] [7 8]\nempty copy: 0\ncopied: 2 [1 9]\noverlap: 2 [1 1 9]\ntext: Go 好 3 中\n"),
    ("stdlib-context-cancellation", "01-go-backend/reference/library-guides/05-context.md", "context-cancellation-seventh", "context deadline exceeded\n两个子 ctx 都已取消\n42\n"),
    ("core-data-type-value-copy", "01-go-backend/reference/language-concepts/04-go-data-types.md", "data-type-value-copy-seventh", "[7 2] [9 2] [7 2]\narray copy keeps its own first element: true\n"),
)


def extract(document: Path, marker: str) -> str:
    text = document.read_text(encoding="utf-8")
    pattern = rf"<!--\s*go-example:\s*{re.escape(marker)}\s*-->\s*```go\n(.*?)\n```"
    matches = re.findall(pattern, text, flags=re.DOTALL)
    if len(matches) != 1:
        raise ValueError(f"{document}: expected exactly one block for {marker}, found {len(matches)}")
    return matches[0] + "\n"


def command(argv: list[str], cwd: Path) -> dict[str, object]:
    result = subprocess.run(argv, cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=False)
    return {"argv": argv, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def render(report: dict[str, object]) -> str:
    rows = [
        "# Go / Rust P1 第七轮正文提取验证",
        "",
        "本报告只验证表中四个新命名的 Go Markdown 正文程序。它不声称整页、其他围栏、Rust 页面、网络服务、竞态、性能或不同工具链已经验证。",
        "",
        "每项从 HTML 标记后紧邻的 Go 围栏逐字提取，写入独立临时目录，并以精确 stdout 和零退出码断言。验证不会补充 import、helper 或 stub。",
        "",
        "| 类别 | 正文 | 标记 | 结果 |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["results"]:
        rows.append(f"| {item['category']} | `{item['path']}` | `{item['marker']}` | {'PASS' if item['passed'] else 'FAIL'} |")
    rows.extend([
        "",
        f"结果：{report['summary']['passed']}/{report['summary']['total']} 个命名正文程序通过。",
        "JSON 报告保留文档及提取源码哈希、Go 工具链、命令、退出码、stdout 和 stderr；通过只适用于表中程序。",
    ])
    return "\n".join(rows) + "\n"


def main() -> int:
    if not GO.exists():
        raise FileNotFoundError(f"bundled Go toolchain not found: {GO}")
    report: dict[str, object] = {"schema_version": 1, "scope": "four named Go P1 Markdown body programs only", "toolchain": command([str(GO), "version"], ROOT), "results": []}
    with tempfile.TemporaryDirectory(prefix="dev-quest-go-rust-seventh-") as raw:
        work = Path(raw)
        for name, relative, marker, expected in CASES:
            document = ROOT / relative
            source = extract(document, marker)
            case_dir = work / name
            case_dir.mkdir()
            (case_dir / "main.go").write_text(source, encoding="utf-8")
            execution = command([str(GO), "run", "main.go"], case_dir)
            passed = execution["returncode"] == 0 and execution["stdout"] == expected and execution["stderr"] == ""
            category = "关键词" if name.startswith("keyword") else "内置函数" if name.startswith("builtin") else "标准库" if name.startswith("stdlib") else "核心基础"
            report["results"].append({"name": name, "category": category, "path": relative, "marker": marker, "document_sha256": hashlib.sha256(document.read_bytes()).hexdigest(), "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(), "expected_stdout": expected, "execution": execution, "passed": passed})
    report["summary"] = {"passed": sum(row["passed"] for row in report["results"]), "total": len(report["results"])}
    report["status"] = "passed" if report["summary"]["passed"] == report["summary"]["total"] else "failed"
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "go-rust-seventh-body-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (REPORTS / "go-rust-seventh-body-validation.md").write_text(render(report), encoding="utf-8")
    print(f"{report['status']}: {report['summary']['passed']}/{report['summary']['total']} named body programs")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
