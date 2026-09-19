#!/usr/bin/env python3
"""Extract and run the two marked JSON / java.math Markdown programs unchanged."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = Path(__file__).resolve().parent / "reports"
OUT = REPORT_DIR / "php-java-json-math.json"
MARKDOWN = REPORT_DIR / "php-java-json-math-validation.md"
CASES = {
    "07-php-mastery/reference/library-guides/04-json.md": ("php", "php-json-boundaries"),
    "08-java-revisited/reference/library-guides/06-java-math.md": ("java", "java-math-boundaries"),
}
REQUIRED = {"php": ("php",), "java": ("javac", "java")}
PATTERN = re.compile(r'<!-- reference-case: (\{[^\n]+\}) -->\n```(php|java)\n(.*?)\n```', re.S)


def run(args: list[str], cwd: Path) -> dict[str, object]:
    completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    return {"command": args, "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


def extract(relative: str, language: str, case_id: str) -> tuple[dict[str, str], str]:
    source_text = (ROOT / relative).read_text(encoding="utf-8").replace("\r\n", "\n")
    for raw_spec, actual_language, source in PATTERN.findall(source_text):
        spec = json.loads(raw_spec)
        if actual_language == language and spec.get("id") == case_id:
            return spec, source + "\n"
    raise RuntimeError(f"marked {language} case {case_id} not found in {relative}")


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    missing = [binary for binary in ("php", "javac", "java") if shutil.which(binary) is None]
    cases: list[dict[str, object]] = []
    for relative, (language, case_id) in CASES.items():
        spec, source = extract(relative, language, case_id)
        item: dict[str, object] = {
            "id": case_id, "document": relative,
            "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "expected_stdout": spec["stdout"], "commands": [],
        }
        case_missing = [binary for binary in REQUIRED[language] if binary in missing]
        if case_missing:
            item.update({"status": "not-run", "passed": False,
                         "reason": "missing required executable(s): " + ", ".join(case_missing)})
        else:
            with tempfile.TemporaryDirectory(prefix="dq-json-math-") as temp:
                work = Path(temp)
                filename = "main.php" if language == "php" else "Main.java"
                (work / filename).write_text(source, encoding="utf-8")
                if language == "php":
                    commands = [run(["php", "-d", "display_errors=stderr", "main.php"], work)]
                else:
                    commands = [run(["javac", "--release", "21", "-encoding", "UTF-8", "Main.java"], work)]
                    if commands[-1]["exit_code"] == 0:
                        commands.append(run(["java", "Main"], work))
                item["commands"] = commands
                final = commands[-1]
                item.update({"status": "run", "passed": final["exit_code"] == 0 and
                             final["stdout"] == spec["stdout"] and final["stderr"] == ""})
        cases.append(item)
    data = {"scope": "only the two explicitly marked complete Markdown programs; excludes snippets, frameworks, HTTP, and other documents",
            "required_executables": ["php", "javac", "java"], "missing_executables": missing,
            "cases": cases, "passed": all(bool(case["passed"]) for case in cases)}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# PHP JSON / Java math 正文提取验证", "",
            "范围仅为两篇标准库文档中带 `reference-case` 标记的完整程序；不验证其余片段、框架、HTTP 或其他页面。", "",
            "| Case | Document | Status | Result |", "| --- | --- | --- | --- |"]
    for case in cases:
        result = "PASS" if case["passed"] else "NOT RUN" if case["status"] == "not-run" else "FAIL"
        rows.append(f"| `{case['id']}` | `{case['document']}` | {case['status']} | {result} |")
    if missing:
        rows.extend(["", "当前环境缺少：`" + "`, `".join(missing) + "`。安装 PHP 与 JDK 21 后运行 `python verify_php_java_json_math.py` 会重新提取正文、编译/执行并覆盖本报告。"])
    else:
        rows.extend(["", "JSON 报告保留每个正文源码的 SHA-256、实际命令、stdout/stderr、退出码和结论。"])
    MARKDOWN.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0 if data["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
