#!/usr/bin/env python3
"""Run three named Markdown programs unchanged in isolated Docker containers."""
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
    ("go-control-flow-contract", "Go", "01-go-backend/basics/06-control-structures.md", "go", "main.go", "golang:1.27", ("go", "run", "main.go"), "sum=5 skipped=1 stopped=true\nresult=complete-before-sentinel\n"),
    ("node-buffer-view-and-bounds", "Node.js", "09-nodejs-backend/reference/library-guides/05-buffer.md", "js", "buffer.mjs", "node:24-bookworm-slim", ("node", "buffer.mjs"), "shared=1,9,3,4 copy=2,3,4\ntrailer=772\nshort=trailer needs two bytes\n"),
    ("python-context-lifecycle", "Python", "10-python-discovery/reference/language-concepts/08-context-managers.md", "python", "lifecycle.py", "python:3.14-alpine", ("python", "-I", "lifecycle.py"), "context-lifecycle: open:first | open:second | close:second | close:first | handled:work failed\n"),
)


def run(command: list[str], cwd: Path) -> dict[str, object]:
    completed = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=False)
    return {"command": command, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def extract(document: Path, case_id: str, fence: str) -> str:
    matches = re.findall(rf"<!--\s*terra-fifteenth-case:\s*{re.escape(case_id)}\s*-->\s*```{fence}\s*\n(.*?)\n```", document.read_text(encoding="utf-8"), re.DOTALL)
    if len(matches) != 1:
        raise ValueError(f"{document}: expected one marked {case_id} fence, got {len(matches)}")
    return matches[0] + "\n"


def main() -> int:
    if not shutil.which("docker"):
        raise SystemExit("docker is required; this verifier pulls no images")
    report: dict[str, object] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Three named, complete P1 core/standard-library Markdown programs extracted byte-for-byte from their marked fences. A pass verifies only the listed output contracts.",
        "method": "Each marked fence is written unchanged to a temporary directory and executed in a pre-existing Docker image with network disabled, a read-only root filesystem, dropped capabilities, and bounded resources.",
        "not_verified": ["all other prose and code fences in these documents", "compile-failure snippets and deliberately unsafe examples", "network, database, framework, performance, concurrency, and platform-specific behavior"],
        "docker": run(["docker", "--version"], ROOT),
        "cases": [],
    }
    with tempfile.TemporaryDirectory(prefix="dev-quest-fifteenth-") as temporary:
        workspace = Path(temporary)
        for case_id, language, relative, fence, filename, image, command, expected in CASES:
            document = ROOT / relative
            source = extract(document, case_id, fence)
            case_dir = workspace / case_id
            case_dir.mkdir()
            (case_dir / filename).write_text(source, encoding="utf-8")
            version_command = {"Go": ("go", "version"), "Node.js": ("node", "--version"), "Python": ("python", "--version")}[language]
            toolchain = run(["docker", "run", "--rm", "--pull=never", "--network=none", image, *version_command], ROOT)
            language_options = ["--env", "GOCACHE=/tmp/go-build-cache"] if language == "Go" else []
            execution = run(["docker", "run", "--rm", "--pull=never", "--network=none", "--read-only", "--cap-drop=ALL", "--pids-limit=64", "--memory=512m", "--cpus=1", "--tmpfs", "/tmp:rw,exec,nosuid,size=256m", *language_options, "--workdir=/work", "--mount", f"type=bind,source={case_dir},target=/work,readonly", image, *command], ROOT)
            passed = execution["exit_code"] == 0 and execution["stdout"] == expected and execution["stderr"] == ""
            report["cases"].append({"id": case_id, "language": language, "source": relative, "image": image, "document_sha256": hashlib.sha256(document.read_bytes()).hexdigest(), "code_sha256": hashlib.sha256(source.encode()).hexdigest(), "expected_stdout": expected, "toolchain": toolchain, "execution": execution, "status": "PASS" if passed else "FAIL"})
    report["passed"] = sum(case["status"] == "PASS" for case in report["cases"])
    report["total"] = len(report["cases"])
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "go-node-python-fifteenth-runtime.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# Go / Node.js / Python 第十五轮正文提取运行验证", "", str(report["scope"]), "", "| Case | Source | Runtime | Result |", "| --- | --- | --- | --- |"]
    rows += [f"| `{case['id']}` | `{case['source']}` | `{case['image']}` | {case['status']} |" for case in report["cases"]]
    rows += ["", "## 边界", "", "只验证表中的完整程序和精确标准输出：Go 的 continue、switch 与循环停止边界；Node Buffer 的共享视图、复制和长度校验；Python ExitStack 的反序清理及异常传播。不覆盖整篇文档、其他围栏、网络、数据库、框架、并发、性能或平台行为。JSON 同伴报告保留每个来源和提取代码的 SHA-256、镜像工具链、完整命令、标准输出/错误与退出码。", ""]
    (REPORTS / "go-node-python-fifteenth-runtime.md").write_text("\n".join(rows), encoding="utf-8")
    print(f"{'PASS' if report['passed'] == report['total'] else 'FAIL'}: {report['passed']}/{report['total']} named body programs")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
