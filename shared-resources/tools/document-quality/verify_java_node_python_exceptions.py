"""Extract and execute complete exception examples from the three Markdown pages."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
OUT = REPORTS / "java-node-python-exceptions-results.json"
REPORT = REPORTS / "java-node-python-exceptions-report.md"
CASES = (
    ("java-try-with-resources-suppressed", "08-java-revisited/basics/06-exceptions.md",
     "public class ExceptionResourcesVerification", "java", "ExceptionResourcesVerification.java",
     [["javac", "--release", "21", "ExceptionResourcesVerification.java"], ["java", "ExceptionResourcesVerification"]],
     "work\nclose:second\nclose:first\n"),
    ("node-error-cause", "09-nodejs-backend/basics/06-error-handling.md",
     "class ServiceError extends Error", "js", "error-cause.js",
     [["node", "error-cause.js"]], "ServiceError|query failed|database unavailable\n"),
    ("python-exception-chain-context-manager", "10-python-discovery/basics/06-exceptions.md",
     "class Marker:", "python", "exception-context.py",
     [[sys.executable, "exception-context.py"]], "enter|RuntimeError\ninvalid port|ValueError\n"),
)


def extract(path: Path, needle: str, language: str) -> str:
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(rf"```{language}\s*\n(.*?)\n```", text, re.DOTALL):
        if needle in match.group(1):
            return match.group(1) + "\n"
    raise RuntimeError(f"missing {language} fence containing {needle}: {path}")


def execute(args: list[str], cwd: Path) -> dict:
    actual_args = args
    container_command = {"javac": "javac", "java": "java", "node": "node", sys.executable: "python3"}.get(args[0])
    if container_command is not None:
        actual_args = ["docker", "run", "--rm", "-v", f"{cwd}:/work", "-w", "/work",
                       "dev-quest-validation:local", container_command, *args[1:]]
    completed = subprocess.run(actual_args, cwd=cwd, text=True, capture_output=True, check=False)
    return {"command": actual_args, "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


def main() -> None:
    results = []
    with tempfile.TemporaryDirectory(prefix="dq-exceptions-") as raw_work:
        work = Path(raw_work)
        for case_id, relative, marker, language, filename, commands, expected in CASES:
            document = ROOT / relative
            source = extract(document, marker, language)
            (work / filename).write_text(source, encoding="utf-8")
            records = []
            for command in commands:
                record = execute(command, work)
                records.append(record)
                if record["exit_code"] != 0:
                    break
            final = records[-1]
            results.append({"id": case_id, "document": relative,
                            "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                            "expected_stdout": expected, "commands": records,
                            "passed": final["exit_code"] == 0 and final["stdout"] == expected})
    data = {"scope": "One complete fenced program extracted verbatim from each named Java, Node.js, and Python P1 foundation page and run in dev-quest-validation:local. No framework, network, process-crash, or whole-document claim is made.",
            "documents": {relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
                          for _, relative, *_ in CASES}, "cases": results,
            "passed": all(case["passed"] for case in results)}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# Java / Node.js / Python 异常正文提取验证", "",
            "从三篇 P1 基础页面各提取一个完整代码围栏并实际运行。验证仅覆盖命名围栏，未覆盖框架、网络、进程级崩溃策略或整篇文档。", "",
            "| Case | Document | Result |", "| --- | --- | --- |"]
    rows.extend(f"| `{case['id']}` | `{case['document']}` | {'PASS' if case['passed'] else 'FAIL'} |" for case in results)
    rows.extend(["", "JSON 记录提取源码 SHA-256、实际命令、stdout/stderr、退出码和 `passed` 字段。"])
    REPORT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    if not data["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
