"""Extract named fenced programs from two P1 basics pages and run them.

This checker deliberately records evidence for only the selected fenced programs.
It does not claim that every snippet or prose statement in either page was executed.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
WORK = ROOT.parent / "verification-lab" / "go-rust-p1-basics"
GO = ROOT.parent / "verification-lab" / "go-toolchain" / "go" / "bin" / "go.exe"
GO_PAGE = ROOT / "01-go-backend/basics/03-variables-constants.md"
RUST_PAGE = ROOT / "11-rust-cross-platform/basics/06-collections-iterators.md"


def fenced_after(markdown: str, heading: str) -> str:
    start = markdown.index(heading)
    match = re.search(r"```(?:go|rust)\n(.*?)\n```", markdown[start:], re.DOTALL)
    if not match:
        raise ValueError(f"no fenced program after {heading!r}")
    return match.group(1)


def run(command: list[str], cwd: Path) -> tuple[str, str, int]:
    completed = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=False)
    return completed.stdout, completed.stderr, completed.returncode


def result(source: str, case: str, command: list[str], stdout: str, stderr: str, code: int, expected: str) -> dict:
    return {
        "source": source,
        "case": case,
        "status": "passed" if code == 0 and expected in stdout else ("blocked" if "Application Control policy" in stderr else "failed"),
        "command": command,
        "exit_code": code,
        "stdout": stdout,
        "stderr": stderr,
        "assertion": f"stdout contains {expected!r}",
    }


def main() -> None:
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    go_text = GO_PAGE.read_text(encoding="utf-8")
    rust_text = RUST_PAGE.read_text(encoding="utf-8")
    go_cases = [
        ("zero-values", "### 3. 零值", "string零值: \"\" (长度: 0)"),
        ("iota", "### 2. iota枚举", "GB: 1073741824"),
        ("circle-calculation", "### 示例3: 数据计算", "面积(整数部分): 78"),
    ]
    results = []
    for name, heading, expected in go_cases:
        directory = WORK / "go" / name
        directory.mkdir(parents=True)
        (directory / "main.go").write_text(fenced_after(go_text, heading), encoding="utf-8")
        stdout, stderr, code = run([str(GO), "run", "main.go"], directory)
        results.append(result(GO_PAGE.relative_to(ROOT).as_posix(), name, [str(GO), "run", "main.go"], stdout, stderr, code, expected))

    # Use the page's complete test block as its runtime entry point and run it in a
    # minimal Cargo crate. The named program also covers normalize's failure boundary.
    rust_dir = WORK / "rust" / "collections-iterators"
    rust_dir.mkdir(parents=True)
    (rust_dir / "Cargo.toml").write_text('[package]\nname = "collections-iterators-evidence"\nversion = "0.1.0"\nedition = "2024"\n', encoding="utf-8")
    (rust_dir / "src").mkdir()
    (rust_dir / "src" / "lib.rs").write_text(fenced_after(rust_text, "### 示例五：适配器 + 单元测试"), encoding="utf-8")
    rust_command = ["docker", "run", "--rm", "-v", f"{rust_dir.resolve()}:/work", "-w", "/work", "rust:1-slim-bookworm", "cargo", "test", "--quiet"]
    stdout, stderr, code = run(rust_command, rust_dir)
    results.append(result(RUST_PAGE.relative_to(ROOT).as_posix(), "normalize-unit-tests", rust_command, stdout, stderr, code, "2 passed"))

    report = {
        "schema_version": 1,
        "purpose": "Runtime evidence for named, fully extracted body programs only.",
        "scope": "Three standalone Go programs and one Rust test module extracted verbatim from the named pages. No whole-document, benchmark, panic, network, or external-service claim is made.",
        "results": results,
        "summary": {
            "passed": sum(item["status"] == "passed" for item in results),
            "blocked": sum(item["status"] == "blocked" for item in results),
            "failed": sum(item["status"] == "failed" for item in results),
        },
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "go-rust-p1-basics-runtime.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Go / Rust P1 基础正文运行验证", "", report["scope"], "", "| 来源 | 正文完整提取项 | 状态 | 断言 |", "|---|---|---|---|"]
    for item in results:
        lines.append(f"| `{item['source']}` | `{item['case']}` | `{item['status']}` | {item['assertion']} |")
    lines.extend(["", "JSON 报告保留精确命令、退出码和 stdout/stderr；`passed` 仅表示表中命名提取项通过。"])
    (REPORTS / "go-rust-p1-basics-runtime.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if report["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
