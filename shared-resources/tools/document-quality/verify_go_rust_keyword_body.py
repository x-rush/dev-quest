"""Run two complete, named Markdown body programs and record narrow evidence.

This intentionally verifies only the exact Go and Rust fences selected below.  It
does not claim that the rest of either reference page, its prose, or its
deliberately failing examples have been executed.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
WORK = ROOT.parent / "verification-lab" / "go-rust-keyword-body"
CASES = (
    {
        "id": "go-keyword-package",
        "source": "01-go-backend/reference/language-concepts/01-go-keywords.md",
        "anchor": "<!-- go-example: keyword-package -->",
        "language": "go",
        "filename": "main.go",
        "image": "golang:1",
        "command": ["go", "run", "main.go"],
        "expected_stdout": "package name is not an import path\n",
    },
    {
        "id": "rust-keyword-task",
        "source": "11-rust-cross-platform/reference/language-concepts/09-keywords-and-syntax.md",
        "anchor": "## 一个完整的语言层实验",
        "language": "rust",
        "filename": "main.rs",
        "image": "rust:1-slim-bookworm",
        "command": ["rustc", "--edition", "2024", "main.rs", "-o", "keyword-lab"],
        "run_after": ["./keyword-lab"],
        "expected_stdout": "2\ntrue\n",
    },
)


def extract_fence(text: str, anchor: str, language: str) -> str:
    start = text.index(anchor)
    match = re.search(rf"```{language}\n(.*?)\n```", text[start:], re.DOTALL)
    if not match:
        raise ValueError(f"missing {language} fence after {anchor!r}")
    return match.group(1) + "\n"


def execute(command: list[str], cwd: Path) -> dict:
    complete = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=False)
    return {"command": command, "exit_code": complete.returncode, "stdout": complete.stdout, "stderr": complete.stderr}


def main() -> int:
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    toolchains = {
        "go": execute(["docker", "run", "--rm", "golang:1", "go", "version"], WORK),
        "rust": execute(["docker", "run", "--rm", "rust:1-slim-bookworm", "rustc", "--version"], WORK),
    }
    results = []
    for case in CASES:
        document = ROOT / case["source"]
        source = extract_fence(document.read_text(encoding="utf-8"), case["anchor"], case["language"])
        case_dir = WORK / case["id"]
        case_dir.mkdir()
        (case_dir / case["filename"]).write_text(source, encoding="utf-8")
        mount = f"{case_dir.resolve()}:/work"
        build = execute(["docker", "run", "--rm", "-v", mount, "-w", "/work", case["image"], *case["command"]], case_dir)
        run = None
        if build["exit_code"] == 0 and "run_after" in case:
            run = execute(["docker", "run", "--rm", "-v", mount, "-w", "/work", case["image"], *case["run_after"]], case_dir)
        observed = run if run else build
        passed = observed["exit_code"] == 0 and observed["stdout"] == case["expected_stdout"]
        results.append({
            "id": case["id"], "source": case["source"], "anchor": case["anchor"],
            "extraction": "complete first fenced program after named body anchor, preserved verbatim",
            "source_sha256": hashlib.sha256(source.encode()).hexdigest(), "image": case["image"],
            "build": build, "run": run, "expected_stdout": case["expected_stdout"],
            "status": "passed" if passed else "failed",
        })
    report = {
        "schema_version": 1,
        "purpose": "Narrow runtime evidence for two named, complete Markdown body programs.",
        "scope": "Only the extracted Go package/import program and Rust keyword task program are verified. Other fences, prose, compiler-error exercises, OS behavior, dependencies, and performance claims are out of scope.",
        "toolchains": toolchains,
        "results": results,
        "summary": {"passed": sum(row["status"] == "passed" for row in results), "total": len(results)},
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "go-rust-keyword-body-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Go / Rust 关键词正文提取验证", "", report["scope"], "", "| 文档 | 提取项 | 容器镜像 | 状态 | 断言 |", "|---|---|---|---|---|"]
    for row in results:
        lines.append(f"| `{row['source']}` | `{row['id']}` | `{row['image']}` | `{row['status']}` | stdout 与完整预期逐字一致 |")
    lines.extend(["", "JSON 报告保存每个容器命令、退出码、stdout/stderr 和提取内容哈希；通过只说明表内这两个命名正文程序。"])
    (REPORTS / "go-rust-keyword-body-validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if report["summary"]["passed"] == report["summary"]["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
