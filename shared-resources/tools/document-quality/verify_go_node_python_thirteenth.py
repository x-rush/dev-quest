#!/usr/bin/env python3
"""Extract and execute three named P1 Markdown programs without modifying them."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
CASES = (
    ("go-generics-named-type", "Go", "01-go-backend/reference/language-concepts/09-generics.md", "go", "main.go", "golang:1.27", ("go", "run", "main.go"), "score=6\nmissing=0,false\n"),
    ("node-exports-resolution", "Node.js", "09-nodejs-backend/reference/language-concepts/06-esm-module-resolution.md", "js", "case.mjs", "node:24-bookworm-slim", ("node", "case.mjs"), "sum=5 relative-ok\nblocked=ERR_PACKAGE_PATH_NOT_EXPORTED\n"),
    ("python-default-factory", "Python", "10-python-discovery/basics/04-functions-oop.md", "python", "case.py", "python:3.14-alpine", ("python", "-I", "case.py"), "unsafe=['one'],['one', 'two']\nsafe=['one'],['two']; tasks=['urgent'],[]\n"),
)


def run(command: list[str], cwd: Path) -> dict[str, object]:
    result = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=False)
    return {"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def extract(path: Path, case_id: str, fence: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.findall(rf"<!--\s*terra-thirteenth-case:\s*{re.escape(case_id)}\s*-->\s*```{fence}\s*\n(.*?)\n```", text, re.DOTALL)
    if len(match) != 1:
        raise ValueError(f"{path}: expected exactly one {case_id} fence, got {len(match)}")
    return match[0] + "\n"


def main() -> int:
    if not shutil.which("docker"):
        raise SystemExit("docker is required: this validator only uses pre-existing local images")
    report: dict[str, object] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Three named complete programs, extracted unchanged from the listed P1 core/standard-library Markdown documents. A passing result covers only these contracts, not an entire page or module.",
        "method": "The validator writes each exact marked fence to a temporary directory and runs it in a pre-existing Docker image with no network, read-only root filesystem, dropped capabilities, and bounded resources.",
        "not_verified": ["other prose and fences in the three documents", "compile-failure examples", "network, database, framework, performance, concurrency, and platform behavior"],
        "docker": run(["docker", "--version"], ROOT), "cases": [],
    }
    with tempfile.TemporaryDirectory(prefix="dev-quest-thirteenth-") as temp:
        work = Path(temp)
        for case_id, language, relative, fence, filename, image, command, expected in CASES:
            document = ROOT / relative
            source = extract(document, case_id, fence)
            case_dir = work / case_id
            case_dir.mkdir()
            (case_dir / filename).write_text(source, encoding="utf-8")
            version_command = {"Go": ("go", "version"), "Node.js": ("node", "--version"), "Python": ("python", "--version")}[language]
            toolchain = run(["docker", "run", "--rm", "--pull=never", "--network=none", image, *version_command], ROOT)
            runtime_environment = ["--env", "GOCACHE=/tmp/go-build-cache"] if language == "Go" else []
            docker_command = ["docker", "run", "--rm", "--pull=never", "--network=none", "--read-only", "--cap-drop=ALL", "--pids-limit=64", "--memory=512m", "--cpus=1", "--tmpfs", "/tmp:rw,exec,nosuid,size=256m", *runtime_environment, "--workdir=/work", "--mount", f"type=bind,source={case_dir},target=/work,readonly", image, *command]
            execution = run(docker_command, ROOT)
            passed = execution["exit_code"] == 0 and execution["stdout"] == expected and execution["stderr"] == ""
            report["cases"].append({"id": case_id, "language": language, "source": relative, "image": image, "document_sha256": hashlib.sha256(document.read_bytes()).hexdigest(), "code_sha256": hashlib.sha256(source.encode()).hexdigest(), "expected_stdout": expected, "toolchain": toolchain, "execution": execution, "status": "PASS" if passed else "FAIL"})
    report["passed"] = sum(case["status"] == "PASS" for case in report["cases"])
    report["total"] = len(report["cases"])
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "go-node-python-thirteenth-runtime.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# Go / Node.js / Python 第十三轮正文提取运行验证", "", report["scope"], "", "| Case | Source | Runtime | Result |", "| --- | --- | --- | --- |"]
    rows += [f"| `{c['id']}` | `{c['source']}` | `{c['image']}` | {c['status']} |" for c in report["cases"]]
    rows += ["", "## 边界", "", "仅验证表中的完整程序及精确标准输出：Go 命名类型与泛型约束、Node `exports` 的公开边界与相对 ESM 导入、Python 可变默认参数与 dataclass `default_factory`。不覆盖整篇文档、其他围栏、网络、数据库、框架、并发、性能或平台行为。JSON 同伴报告保留来源和提取代码哈希、镜像工具链、完整命令、标准输出/错误与退出码。", ""]
    (REPORTS / "go-node-python-thirteenth-runtime.md").write_text("\n".join(rows), encoding="utf-8")
    print(f"{'PASS' if report['passed'] == report['total'] else 'FAIL'}: {report['passed']}/{report['total']} named body programs")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
