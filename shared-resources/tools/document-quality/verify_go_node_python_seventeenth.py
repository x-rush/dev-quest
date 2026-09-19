#!/usr/bin/env python3
"""Extract and run three named Markdown programs in isolated Docker containers."""
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
    (
        "go-control-flow-labelled-range",
        "Go",
        "01-go-backend/reference/language-concepts/05-go-control-flow.md",
        "go",
        "main.go",
        "golang:1.27",
        ("go", "run", "main.go"),
        "kept=[1 3 5] switch=three steps=5 indexes=[0 1 2]\n",
    ),
    (
        "node-stream-decoder-pipeline",
        "Node.js",
        "09-nodejs-backend/reference/language-concepts/04-streams-api.md",
        "js",
        "stream.mjs",
        "node:24-bookworm-slim",
        ("node", "stream.mjs"),
        "text=甲\n乙 newlines=1\n",
    ),
    (
        "python-script-entry-contract",
        "Python",
        "10-python-discovery/basics/02-first-script.md",
        "python",
        "hello.py",
        "python:3.14-alpine",
        ("python", "-I", "hello.py", "Ada", "Hi"),
        "Hi, Ada!\n",
    ),
)


def run(command: list[str], cwd: Path) -> dict[str, object]:
    completed = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=False)
    return {"command": command, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def extract(document: Path, case_id: str, fence: str) -> str:
    pattern = rf"<!--\s*terra-seventeenth-case:\s*{re.escape(case_id)}\s*-->\s*```{fence}\s*\n(.*?)\n```"
    matches = re.findall(pattern, document.read_text(encoding="utf-8"), re.DOTALL)
    if len(matches) != 1:
        raise ValueError(f"{document}: expected exactly one marked {case_id} fence, got {len(matches)}")
    return matches[0] + "\n"


def docker_run(image: str, case_dir: Path, command: tuple[str, ...], language: str) -> dict[str, object]:
    language_options = ["--env", "GOCACHE=/tmp/go-build-cache"] if language == "Go" else []
    return run(
        [
            "docker", "run", "--rm", "--pull=never", "--network=none", "--read-only", "--cap-drop=ALL",
            "--pids-limit=64", "--memory=512m", "--cpus=1", "--tmpfs", "/tmp:rw,exec,nosuid,size=256m",
            *language_options, "--workdir=/work", "--mount", f"type=bind,source={case_dir},target=/work,readonly",
            image, *command,
        ],
        ROOT,
    )


def main() -> int:
    if not shutil.which("docker"):
        raise SystemExit("docker is required; this verifier pulls no images")
    report: dict[str, object] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Three named, complete P1 core/standard-library Markdown programs are extracted byte-for-byte from marked fences. PASS means only that each listed command has the specified stdout and no stderr.",
        "method": "Each source fence is copied unchanged to a fresh temporary directory and run from an already-present Docker image with network disabled, a read-only root filesystem, no Linux capabilities, and bounded CPU, memory, process, and temporary-storage resources.",
        "not_verified": ["all other prose and fences in the three documents", "deliberately incomplete snippets", "network, database, framework, deployment, performance, and platform-specific behavior"],
        "docker": run(["docker", "--version"], ROOT),
        "cases": [],
    }
    with tempfile.TemporaryDirectory(prefix="dev-quest-seventeenth-") as temporary:
        workspace = Path(temporary)
        for case_id, language, relative, fence, filename, image, command, expected in CASES:
            document = ROOT / relative
            source = extract(document, case_id, fence)
            case_dir = workspace / case_id
            case_dir.mkdir()
            (case_dir / filename).write_text(source, encoding="utf-8")
            version_command = {"Go": ("go", "version"), "Node.js": ("node", "--version"), "Python": ("python", "--version")}[language]
            toolchain = run(["docker", "run", "--rm", "--pull=never", "--network=none", image, *version_command], ROOT)
            execution = docker_run(image, case_dir, command, language)
            passed = execution["exit_code"] == 0 and execution["stdout"] == expected and execution["stderr"] == ""
            report["cases"].append({
                "id": case_id, "language": language, "source": relative, "image": image,
                "document_sha256": hashlib.sha256(document.read_bytes()).hexdigest(),
                "code_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                "expected_stdout": expected, "toolchain": toolchain, "execution": execution,
                "status": "PASS" if passed else "FAIL",
            })
    report["passed"] = sum(case["status"] == "PASS" for case in report["cases"])
    report["total"] = len(report["cases"])
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "go-node-python-seventeenth-runtime.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# Go / Node.js / Python 第十七轮正文提取运行验证", "", str(report["scope"]), "", "| Case | Source | Runtime | Result |", "| --- | --- | --- | --- |"]
    rows += [f"| `{case['id']}` | `{case['source']}` | `{case['image']}` | {case['status']} |" for case in report["cases"]]
    rows += ["", "## 边界", "", "验证仅覆盖表中原样提取的完整程序与精确标准输出：Go 的 continue、switch、带标签 break 和 rune 字节索引；Node 的跨 chunk UTF-8 解码、行数和 pipeline 完成；Python 的入口参数和成功退出码。它不覆盖整篇文档、其他围栏、错误分支、网络、数据库、框架、部署、性能或平台行为。JSON 同伴报告记录来源与提取代码 SHA-256、镜像工具链、完整命令、标准输出/错误和退出码。", ""]
    (REPORTS / "go-node-python-seventeenth-runtime.md").write_text("\n".join(rows), encoding="utf-8")
    print(f"{'PASS' if report['passed'] == report['total'] else 'FAIL'}: {report['passed']}/{report['total']} named body programs")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
