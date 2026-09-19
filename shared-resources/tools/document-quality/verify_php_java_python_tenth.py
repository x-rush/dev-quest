#!/usr/bin/env python3
"""Extract and run three named examples from the Markdown source bodies.

The generated files live in a temporary directory.  The durable verifier and
its JSON/Markdown evidence are kept under the repository root.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def extract_fence(source: Path, language: str, needle: str) -> str:
    body = source.read_text(encoding="utf-8")
    pattern = re.compile(rf"^```{re.escape(language)}\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(body):
        code = match.group(1)
        # The PHP page has a signature fence and a runnable fence that both
        # mention preg_replace_callback; only the latter is executable source.
        if needle in code and (language != "php" or "<?php" in code):
            return code
    raise ValueError(f"No {language} fence containing {needle!r} in {source}")


def run(command: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return completed.returncode, (completed.stdout + completed.stderr).strip()


def command_or_none(name: str) -> str | None:
    return shutil.which(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    root = args.root.resolve()
    reports = root / "shared-resources/tools/document-quality/reports"
    cases: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="php-java-python-tenth-") as temporary:
        work = Path(temporary)

        php_source = root / "07-php-mastery/reference/language-concepts/09-strings-regex.md"
        php_file = work / "strings-regex.php"
        php_file.write_text(
            extract_fence(php_source, "php", "preg_replace_callback(")
            + "\nif ($text !== 'Hello, Grace!') { throw new RuntimeException('callback output mismatch'); }\n",
            encoding="utf-8",
        )
        php = command_or_none("php")
        if php:
            code, output = run([php, str(php_file)], work)
            status = "PASS" if code == 0 and "ada" in output and "Hello, Grace!" in output else "FAIL"
            detail = output
        else:
            status, detail = "NOT_RUN_TOOLCHAIN_UNAVAILABLE", "php executable was not available on PATH."
        cases.append({"language": "PHP", "path": str(php_source.relative_to(root)).replace("\\", "/"), "source": "PCRE example fence containing preg_replace_callback", "status": status, "exit_code": code if php else None, "detail": detail})

        java_source = root / "08-java-revisited/reference/library-guides/07-java-text-and-time-format.md"
        java_file = work / "FormatDemo.java"
        java_file.write_text(extract_fence(java_source, "java", "public class FormatDemo"), encoding="utf-8")
        javac, java = command_or_none("javac"), command_or_none("java")
        if javac and java:
            compile_code, compile_output = run([javac, str(java_file)], work)
            run_code, run_output = (run([java, "-cp", str(work), "FormatDemo"], work) if compile_code == 0 else (None, "not run because compilation failed"))
            status = "PASS" if compile_code == 0 and run_code == 0 and run_output == "2026-09-14\n2026-09-15" else "FAIL"
            detail = f"compile: {compile_output}\nrun: {run_output}".strip()
            exit_code: int | None = run_code if run_code is not None else compile_code
        else:
            status, detail, exit_code = "NOT_RUN_TOOLCHAIN_UNAVAILABLE", "javac and/or java was not available on PATH.", None
        cases.append({"language": "Java", "path": str(java_source.relative_to(root)).replace("\\", "/"), "source": "complete FormatDemo fence", "status": status, "exit_code": exit_code, "detail": detail})

        python_source = root / "10-python-discovery/basics/04-functions-oop.md"
        python_file = work / "functions-oop.py"
        python_file.write_text(
            extract_fence(python_source, "python", "from dataclasses import dataclass, field")
            + "\nassert bm.tags == []\nassert bm == Bookmark('uv', 'https://astral.sh')\nassert bm.tags is not Bookmark('x', 'https://example.test').tags\n",
            encoding="utf-8",
        )
        python = command_or_none("python3") or command_or_none("python")
        if python:
            code, output = run([python, str(python_file)], work)
            status = "PASS" if code == 0 else "FAIL"
            detail = output
        else:
            status, detail = "NOT_RUN_TOOLCHAIN_UNAVAILABLE", "python3/python executable was not available on PATH."
        cases.append({"language": "Python", "path": str(python_source.relative_to(root)).replace("\\", "/"), "source": "dataclass example fence", "status": status, "exit_code": code if python else None, "detail": detail})

    report = {
        "report": "php-java-python-tenth-body-validation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_environment": "dev-quest-validation:local when invoked through the documented Docker command",
        "method": "Each named Markdown fence is extracted at run time. Assertions are appended only after the extracted source; temporary files are deleted after execution.",
        "scope": "Only the named cases are verified. A passing case is not whole-document verification.",
        "cases": cases,
    }
    (reports / "php-java-python-tenth-body-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# PHP、Java、Python 第十轮：正文提取验证",
        "",
        "验证器直接从三篇 Markdown 正文抽取具名围栏代码，在临时目录追加断言并运行；临时文件会删除，不依赖 `verification-lab` 产物。",
        "",
        "| 语言 | 页面 | 提取案例 | 状态 |",
        "|---|---|---|---|",
    ]
    lines.extend(f"| {case['language']} | `{case['path']}` | {case['source']} | {case['status']} |" for case in cases)
    lines.extend([
        "",
        "## 执行环境与范围",
        "",
        "- 通过 `dev-quest-validation:local` 容器执行：PHP 8.3.6、OpenJDK 21.0.12、Python 3.12.3。",
        "- 每个 PASS 仅覆盖表中具名的源代码围栏及其追加断言，不表示整页或外部框架已验证。",
        "- JSON 报告保留实际退出码和标准输出/错误输出。",
    ])
    (reports / "php-java-python-tenth-body-validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 1 if any(case["status"] == "FAIL" for case in cases) else 0


if __name__ == "__main__":
    sys.exit(main())
