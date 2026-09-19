"""Extract and execute the complete PHP/Java control-flow Markdown examples."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
MARKERS = {
    "07-php-mastery/basics/05-control-flow.md": "### 可完整运行的验证示例",
    "08-java-revisited/basics/05-control-flow.md": "### 可完整编译和运行的验证示例（Java 21）",
}


def extract(document: Path, marker: str, language: str) -> str:
    text = document.read_text(encoding="utf-8")
    match = re.search(rf"```{language}\s*\n(.*?)\n```", text[text.index(marker):], re.DOTALL)
    if match is None:
        raise RuntimeError(f"missing complete {language} fence after {marker}: {document}")
    return match.group(1) + "\n"


def run(args: list[str], cwd: Path) -> dict:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    return {"command": args, "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def main() -> None:
    php_path = ROOT / "07-php-mastery/basics/05-control-flow.md"
    java_path = ROOT / "08-java-revisited/basics/05-control-flow.md"
    php_source = extract(php_path, MARKERS[php_path.relative_to(ROOT).as_posix()], "php")
    java_source = extract(java_path, MARKERS[java_path.relative_to(ROOT).as_posix()], "java")
    with tempfile.TemporaryDirectory(prefix="dq-control-flow-") as temporary:
        work = Path(temporary)
        (work / "control-flow.php").write_text(php_source, encoding="utf-8")
        php = run(["php", "-d", "display_errors=stderr", "control-flow.php"], work)
        php_case = {"id": "php-control-flow-match-enum", "document": php_path.relative_to(ROOT).as_posix(),
                    "source_sha256": hashlib.sha256(php_source.encode()).hexdigest(),
                    "expected_stdout": "integer|default|已支付\n", "commands": [php]}
        php_case["passed"] = php["exit_code"] == 0 and php["stdout"] == php_case["expected_stdout"]
        (work / "ControlFlowVerification.java").write_text(java_source, encoding="utf-8")
        javac = run(["javac", "--release", "21", "ControlFlowVerification.java"], work)
        java = run(["java", "ControlFlowVerification"], work) if javac["exit_code"] == 0 else None
        java_case = {"id": "java-control-flow-pattern-switch", "document": java_path.relative_to(ROOT).as_posix(),
                     "source_sha256": hashlib.sha256(java_source.encode()).hexdigest(),
                     "expected_stdout": "null\npositive\nnon-positive\nstring:2\n12.0\n",
                     "commands": [javac] + ([java] if java else [])}
        java_case["passed"] = java is not None and java["exit_code"] == 0 and java["stdout"] == java_case["expected_stdout"]
    cases = [php_case, java_case]
    report = {"scope": "complete fences added to two control-flow documents; excludes framework, web, random, and partial snippets",
              "documents": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in MARKERS},
              "cases": cases, "passed": all(case["passed"] for case in cases)}
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "php-java-control-flow.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# PHP / Java 控制流程正文提取验证", "", "仅验证两篇文档新增的完整代码围栏；不覆盖框架、Web 请求、随机示例或局部片段。", "", "| Case | Document | Result |", "| --- | --- | --- |"]
    lines.extend(f"| `{case['id']}` | `{case['document']}` | {'PASS' if case['passed'] else 'FAIL'} |" for case in cases)
    lines.extend(["", "JSON 保存正文提取源码 SHA-256、实际命令、stdout/stderr、退出码和 `passed`。"])
    (REPORTS / "php-java-control-flow.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
