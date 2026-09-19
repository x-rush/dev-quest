#!/usr/bin/env python3
"""Run exactly three marked Go/Rust/PHP Markdown-body programs in containers."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
MARKER = "go-rust-php-twelfth-case"
CASES = (
    {
        "id": "go-pointer-method-set",
        "language": "Go",
        "path": "01-go-backend/reference/language-concepts/06-go-oop-concepts.md",
        "fence": "go",
        "image": "golang:1.27",
        "filename": "main.go",
        "command": ["go", "run", "main.go"],
        "expected_stdout": "1\n",
    },
    {
        "id": "rust-dyn-collection",
        "language": "Rust",
        "path": "11-rust-cross-platform/reference/language-concepts/02-trait-objects.md",
        "fence": "rust",
        "image": "rust:1-slim-bookworm",
        "filename": "main.rs",
        "command": ["rustc", "--edition", "2024", "main.rs", "-o", "/tmp/case", "&&", "/tmp/case"],
        "expected_stdout": "[按钮:提交]\n<滑杆:72%>\n预览: [按钮:取消]\n",
    },
    {
        "id": "php-precedence-remainder",
        "language": "PHP",
        "path": "07-php-mastery/reference/language-concepts/16-operators.md",
        "fence": "php",
        "image": "php:8.5-cli",
        "filename": "case.php",
        "command": ["php", "case.php"],
        "expected_stdout": "and=true &&=false\nremainders=2,0,1\n",
    },
)


def extract(document: Path, case_id: str, fence: str) -> str:
    body = document.read_text(encoding="utf-8")
    expression = rf"<!--\s*{MARKER}:\s*{re.escape(case_id)}\s*-->\s*```{fence}\s*\n(.*?)\n```"
    matches = re.findall(expression, body, re.DOTALL)
    if len(matches) != 1:
        raise ValueError(f"{document}: expected one marked {case_id!r} fence, got {len(matches)}")
    return matches[0] + "\n"


def execute(argv: list[str], cwd: Path) -> dict[str, object]:
    result = subprocess.run(argv, cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=False)
    return {"argv": argv, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def markdown(report: dict[str, object]) -> str:
    lines = [
        "# Go、Rust、PHP 第十二轮：正文提取运行验证",
        "",
        "只从三个 P1 核心基础/标准库页面中紧随具名标记的完整围栏逐字提取程序，写入临时目录后在无网络容器中运行。验证器不会补充 import、helper、stub 或替代实现。",
        "",
        "| 语言 | 页面 | 具名案例 | 容器 | 结果 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for case in report["cases"]:
        lines.append(f"| {case['language']} | `{case['path']}` | `{case['id']}` | `{case['image']}` | {case['status']} |")
    lines.extend([
        "",
        "## 范围",
        "",
        "通过只覆盖表中的三个完整程序及其精确标准输出：Go 指针接收者的方法集、Rust trait 对象异构集合与借用传参、PHP `and`/`&&` 赋值优先级和正模数下的余数规范化。它不验证整篇页面、编译失败教学步骤、网络、文件、框架、性能、并发或其他 PHP 版本行为。",
        "",
        "JSON 同伴报告保留来源和提取代码的 SHA-256、容器命令、实际 stdout/stderr、退出码与镜像工具链版本。",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    report: dict[str, object] = {
        "schema_version": 1,
        "report": "go-rust-php-twelfth-body-validation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "Extract each named Markdown fence unchanged; run it in an existing Docker image with --network none and a read-only source mount.",
        "scope": "Only three named P1 core/standard-library body programs. Passing is not whole-page or whole-module verification.",
        "not_verified": ["other fences and prose in the three pages", "compile-failure demonstrations", "network, file-system, framework, performance, concurrency, and platform behavior"],
        "docker": execute(["docker", "--version"], ROOT),
        "cases": [],
    }
    with tempfile.TemporaryDirectory(prefix="dev-quest-go-rust-php-twelfth-") as raw:
        work = Path(raw)
        for specification in CASES:
            document = ROOT / specification["path"]
            source = extract(document, specification["id"], specification["fence"])
            case_dir = work / specification["id"]
            case_dir.mkdir()
            (case_dir / specification["filename"]).write_text(source, encoding="utf-8")
            version_args = ["go", "version"] if specification["language"] == "Go" else [specification["command"][0], "--version"]
            version = execute(["docker", "run", "--rm", "--network", "none", specification["image"], *version_args], ROOT)
            docker_command = ["docker", "run", "--rm", "--network", "none", "-v", f"{case_dir}:/work:ro", "-w", "/work", specification["image"], "sh", "-c", " ".join(specification["command"])]
            execution = execute(docker_command, ROOT)
            passed = execution["returncode"] == 0 and execution["stdout"] == specification["expected_stdout"] and execution["stderr"] == ""
            report["cases"].append({**specification, "document_sha256": hashlib.sha256(document.read_bytes()).hexdigest(), "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(), "toolchain": version, "execution": execution, "status": "PASS" if passed else "FAIL"})
    report["summary"] = {"passed": sum(case["status"] == "PASS" for case in report["cases"]), "total": len(report["cases"])}
    report["status"] = "passed" if report["summary"]["passed"] == report["summary"]["total"] else "failed"
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "go-rust-php-twelfth-body-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (REPORTS / "go-rust-php-twelfth-body-validation.md").write_text(markdown(report), encoding="utf-8")
    print(f"{report['status']}: {report['summary']['passed']}/{report['summary']['total']} named body programs")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
