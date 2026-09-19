"""Extract and run the six named P1 PHP/Java reference examples.

This deliberately has a narrow scope: each case is taken from one named
keyword, built-in/API, or standard-library document.  It does not claim that
every illustrative fence in those documents is a complete program.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


# This verifier lives at shared-resources/tools/document-quality/.  Keeping
# paths relative to it makes the tool runnable from the repository root and
# avoids coupling evidence artifacts to a workspace-level scratch directory.
ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
OUT = REPORTS / "php-java-p1-runtime-results.json"
REPORT = REPORTS / "php-java-p1-runtime-report.md"

CASES = (
    ("php-keyword-values", "07-php-mastery/reference/language-concepts/01-php-keywords.md", "reference-case", "php", "strict rejected\n6\n10\nstring\n", "keyword"),
    ("php-array", "07-php-mastery/reference/language-concepts/02-built-in-functions.md", "reference-case", "php", "int(0)\nbool(true)\n{\"1\":2,\"2\":4}\n[2,4]\nbool(true)\nbool(false)\n", "built-in functions"),
    ("php-spl-core", "07-php-mastery/reference/library-guides/01-standard-library-spl.md", "runtime-evidence", "php", "first\n2\n[\"a\",\"b\"]\n", "standard library"),
    ("java-flow", "08-java-revisited/reference/language-concepts/01-java-keywords.md", "reference-case", "java", "5\nmedium\n", "keyword"),
    ("java-java-lang-contract", "08-java-revisited/reference/library-guides/03-java-lang.md", "runtime-evidence", "java", "true\nPoint[x=1, y=2]\ncba\nfalse\n", "built-in APIs (java.lang)"),
    ("java-text", "08-java-revisited/reference/library-guides/01-standard-library.md", "reference-case", "java", "4\n3\n[a, b]\n[a, b, ]\nhello\n", "standard library"),
)


def extract(document: Path, marker_kind: str, case_id: str, language: str) -> str:
    text = document.read_text(encoding="utf-8")
    marker = f'<!-- {marker_kind}: {{"id":"{case_id}"'
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"missing named marker {case_id} in {document}")
    marker_match = re.search(rf"<!-- {re.escape(marker_kind)}:\s*(\{{.*?\}})\s*-->", text[start:])
    if marker_match is None:
        raise RuntimeError(f"malformed named marker {case_id} in {document}")
    metadata = json.loads(marker_match.group(1))
    if metadata.get("id") != case_id:
        raise RuntimeError(f"marker id changed near {case_id} in {document}")
    match = re.search(rf"```{language}\s*\n(.*?)\n```", text[start:], re.DOTALL)
    if match is None:
        raise RuntimeError(f"missing {language} fence after {case_id} in {document}")
    return match.group(1) + "\n"


def completed(args: list[str], *, input_text: str | None = None, cwd: Path | None = None) -> dict:
    run = subprocess.run(
        args, input=input_text, cwd=cwd, text=True, encoding="utf-8", errors="replace",
        capture_output=True, check=False,
    )
    return {"command": args, "exit_code": run.returncode, "stdout": run.stdout, "stderr": run.stderr}


def run_php(source: str, work: Path) -> tuple[str, list[dict]]:
    php = shutil.which("php")
    if php:
        path = work / "case.php"
        path.write_text(source, encoding="utf-8")
        return "local php", [completed([php, "-d", "display_errors=stderr", path.name], cwd=work)]
    return "php:8.5-cli-alpine container", [completed(["docker", "run", "--rm", "-i", "php:8.5-cli-alpine", "php", "-d", "display_errors=stderr"], input_text=source)]


def run_java(source: str, work: Path) -> tuple[str, list[dict]]:
    class_match = re.search(r"public\s+class\s+([A-Za-z_$][A-Za-z0-9_$]*)", source)
    if class_match is None:
        raise RuntimeError("Java evidence must declare one public class")
    class_name = class_match.group(1)
    javac, java = shutil.which("javac"), shutil.which("java")
    if javac and java:
        path = work / f"{class_name}.java"
        path.write_text(source, encoding="utf-8")
        compile_run = completed([javac, "--release", "21", "-encoding", "UTF-8", path.name], cwd=work)
        commands = [compile_run]
        if compile_run["exit_code"] == 0:
            commands.append(completed([java, class_name], cwd=work))
        return "local JDK", commands
    script = f"cat > {class_name}.java && javac --release 21 -encoding UTF-8 {class_name}.java && java {class_name}"
    return "eclipse-temurin:21-jdk-noble container", [completed(["docker", "run", "--rm", "-i", "eclipse-temurin:21-jdk-noble", "sh", "-c", script], input_text=source)]


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="dq-p1-runtime-") as temporary:
        work = Path(temporary)
        for case_id, relative, marker_kind, language, expected, category in CASES:
            document = ROOT / relative
            source = extract(document, marker_kind, case_id, language)
            marker_text = document.read_text(encoding="utf-8")
            marker_start = marker_text.find(f'<!-- {marker_kind}: {{"id":"{case_id}"')
            marker_metadata = json.loads(re.search(rf"<!-- {re.escape(marker_kind)}:\s*(\{{.*?\}})\s*-->", marker_text[marker_start:]).group(1))
            if marker_metadata.get("stdout") != expected:
                raise RuntimeError(f"marker stdout disagrees with verifier expectation for {case_id}")
            if language == "php":
                runner, commands = run_php(source, work)
            else:
                runner, commands = run_java(source, work)
            actual = commands[-1]["stdout"] if commands else ""
            passed = all(command["exit_code"] == 0 for command in commands) and actual == expected
            records.append({
                "id": case_id,
                "category": category,
                "language": language,
                "document": relative,
                "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                "runner": runner,
                "expected_stdout": expected,
                "commands": commands,
                "passed": passed,
            })
    data = {
        "scope": "Six explicitly marked, complete reference examples: PHP and Java keyword, built-in/API, and standard-library pages. Excludes existing control-flow evidence and all unmarked partial snippets.",
        "documents": {relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() for _, relative, *_ in CASES},
        "cases": records,
        "passed": all(record["passed"] for record in records),
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = [
        "# PHP / Java P1 正文提取运行验证",
        "",
        "范围只包括六个带命名标记的完整代码围栏：每种语言各覆盖关键字、内置 API/函数和标准库一篇。控制流程页已有独立证据，未重新计入；无标记的教学片段也不计入。",
        "",
        "| Case | Category | Document | Runner | Result |",
        "| --- | --- | --- | --- | --- |",
    ]
    rows.extend(f"| `{r['id']}` | {r['category']} | `{r['document']}` | {r['runner']} | {'PASS' if r['passed'] else 'FAIL'} |" for r in records)
    rows.extend(["", "JSON 记录从正文提取的源码 SHA-256、完整命令、stdout/stderr、退出码与断言结果；它不是全库覆盖率报告。"])
    REPORT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    if not data["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
