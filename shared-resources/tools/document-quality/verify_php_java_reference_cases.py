"""Execute named PHP/Java P1 reference fences extracted from Markdown bodies."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
DOCUMENTS = {
    "php": [
        "07-php-mastery/reference/language-concepts/01-php-keywords.md",
        "07-php-mastery/reference/language-concepts/02-built-in-functions.md",
    ],
    "java": [
        "08-java-revisited/reference/language-concepts/01-java-keywords.md",
        "08-java-revisited/reference/library-guides/01-standard-library.md",
    ],
}
CASE = re.compile(r"<!-- reference-case: (\{.*?\}) -->\s*```(php|java)\s*\n(.*?)\n```", re.DOTALL)


def completed(command: list[str], cwd: Path) -> dict:
    result = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    return {"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--report", type=Path, default=Path(__file__).resolve().parent / "reports/php-java-reference-cases-results.json")
    parser.add_argument("--markdown", type=Path, default=Path(__file__).resolve().parent / "reports/php-java-reference-cases-report.md")
    return parser.parse_args()


def main() -> int:
    args = arguments()
    tools = {"php": shutil.which("php"), "javac": shutil.which("javac"), "java": shutil.which("java")}
    missing = [name for name in ("php", "javac", "java") if not tools[name]]
    if missing:
        raise RuntimeError("missing required runtime(s): " + ", ".join(missing))
    cases: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="dq-reference-cases-") as temporary:
        work = Path(temporary)
        for language, paths in DOCUMENTS.items():
            for relative in paths:
                document = args.root / relative
                body = document.read_text(encoding="utf-8")
                if "runtime-evidence" in body:
                    raise RuntimeError(f"selected page already has runtime evidence: {relative}")
                matches = list(CASE.finditer(body))
                if not matches:
                    raise RuntimeError(f"no reference cases in {relative}")
                for number, match in enumerate(matches, 1):
                    metadata = json.loads(match.group(1))
                    fence_language, source = match.group(2), match.group(3) + "\n"
                    if fence_language != language:
                        raise RuntimeError(f"case language mismatch: {metadata['id']}")
                    if language == "php":
                        source_path = work / f"{number}-{metadata['id']}.php"
                        source_path.write_text(source, encoding="utf-8")
                        commands = [completed([tools["php"], "-d", "display_errors=stderr", source_path.name], work)]
                    else:
                        source_path = work / "Main.java"
                        source_path.write_text(source, encoding="utf-8")
                        commands = [completed([tools["javac"], "--release", "21", "-encoding", "UTF-8", "Main.java"], work)]
                        if commands[0]["exit_code"] == 0:
                            commands.append(completed([tools["java"], "Main"], work))
                    actual = commands[-1]["stdout"] if commands else ""
                    passed = all(command["exit_code"] == 0 for command in commands) and actual == metadata["stdout"]
                    cases.append({"id": metadata["id"], "document": relative, "language": language, "source_sha256": hashlib.sha256(source.encode()).hexdigest(), "expected_stdout": metadata["stdout"], "commands": commands, "passed": passed})
    data = {"scope": "Only reference-case fences extracted directly from four PHP/Java P1 core pages. Pages with runtime-evidence are rejected.", "toolchain": {name: completed([path, "--version"], Path.cwd()) for name, path in tools.items()}, "documents": {path: hashlib.sha256((args.root / path).read_bytes()).hexdigest() for paths in DOCUMENTS.values() for path in paths}, "cases": cases, "passed": all(case["passed"] for case in cases)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# PHP / Java P1 正文提取运行验证", "", "范围仅为四篇没有 `runtime-evidence` 的核心页。每个案例直接提取 `reference-case` 注释紧随的完整代码围栏；JSON 保存源码哈希、工具链版本、命令、标准输出、错误输出、退出码与断言。", "", "| Case | Document | Language | Result |", "| --- | --- | --- | --- |"]
    rows.extend(f"| `{case['id']}` | `{case['document']}` | {case['language']} | {'PASS' if case['passed'] else 'FAIL'} |" for case in cases)
    rows.extend(["", "只有实际执行并匹配预期输出的 `PASS` 才构成此报告的运行证据；运行环境缺少所需工具时，验证器直接失败且不会生成可计数状态。"])
    args.markdown.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"wrote {args.report}")
    return 0 if data["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
