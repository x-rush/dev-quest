#!/usr/bin/env python3
"""Extract three P1 Markdown programs unchanged and validate them in Docker."""
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
    ("go-io-bufio-read-contract", "Go", "01-go-backend/reference/library-guides/10-io-bufio.md", "go", "main.go", "golang:1.27", ("go", "run", "main.go"), "exact", "io-bufio: final-bytes, default-limit, configured-limit\n"),
    ("node-test-async-rejection", "Node.js", "09-nodejs-backend/reference/library-guides/08-test-runner.md", "js", "async-boundary.test.mjs", "node:24-bookworm-slim", ("node", "--test", "--test-reporter=tap", "async-boundary.test.mjs"), "tap", ""),
    ("python-stdlib-time-json-contract", "Python", "10-python-discovery/reference/library-guides/01-standard-library.md", "python", "case.py", "python:3.14-alpine", ("python", "-I", "case.py"), "exact", "stdlib-time-json: UTC round-trip, naive-aware boundary\n"),
)


def run(command: list[str], cwd: Path) -> dict[str, object]:
    result = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=False)
    return {"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def extract(document: Path, case_id: str, fence: str) -> str:
    matches = re.findall(rf"<!--\s*terra-twentyfirst-case:\s*{re.escape(case_id)}\s*-->\s*```{fence}\s*\n(.*?)\n```", document.read_text(encoding="utf-8"), re.DOTALL)
    if len(matches) != 1:
        raise ValueError(f"{document}: expected one marked {case_id} fence, got {len(matches)}")
    return matches[0] + "\n"


def isolated_run(image: str, case_dir: Path, command: tuple[str, ...], language: str) -> dict[str, object]:
    environment = ["--env", "GOCACHE=/tmp/go-build-cache"] if language == "Go" else []
    return run([
        "docker", "run", "--rm", "--pull=never", "--network=none", "--read-only", "--cap-drop=ALL",
        "--security-opt=no-new-privileges", "--pids-limit=64", "--memory=512m", "--cpus=1",
        "--tmpfs", "/tmp:rw,exec,nosuid,size=256m", *environment, "--workdir=/work",
        "--mount", f"type=bind,source={case_dir},target=/work,readonly", image, *command,
    ], ROOT)


def passes(kind: str, execution: dict[str, object], expected: str) -> bool:
    if execution["exit_code"] != 0 or execution["stderr"]:
        return False
    if kind == "exact":
        return execution["stdout"] == expected
    stdout = str(execution["stdout"])
    return bool(re.search(r"^ok 1 - async boundary accepts valid input and waits for rejection assertions$", stdout, re.MULTILINE) and re.search(r"^# pass 1$", stdout, re.MULTILINE) and re.search(r"^# fail 0$", stdout, re.MULTILINE) and not re.search(r"^not ok\b", stdout, re.MULTILINE))


def main() -> int:
    if not shutil.which("docker"):
        raise SystemExit("docker is required; this verifier never pulls images")
    report: dict[str, object] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Three named complete P1 core/standard-library Markdown programs are extracted byte-for-byte from marked fences. PASS covers only each listed command and assertion.",
        "method": "Each fence is copied unchanged to a fresh temporary directory and run from a pre-existing Docker image with no network, read-only root filesystem, dropped capabilities, no-new-privileges, bounded CPU/memory/PIDs, and tmpfs-only writable storage.",
        "not_verified": ["all other prose and fences in the three documents", "network, database, framework, deployment, performance, and platform-specific behavior", "Node test-runner timing output, which is deliberately checked as TAP fields rather than fixed text"],
        "docker": run(["docker", "--version"], ROOT), "cases": [],
    }
    with tempfile.TemporaryDirectory(prefix="dev-quest-twentyfirst-") as temporary:
        workspace = Path(temporary)
        for case_id, language, relative, fence, filename, image, command, assertion, expected in CASES:
            document = ROOT / relative
            source = extract(document, case_id, fence)
            case_dir = workspace / case_id
            case_dir.mkdir()
            (case_dir / filename).write_text(source, encoding="utf-8")
            version = {"Go": ("go", "version"), "Node.js": ("node", "--version"), "Python": ("python", "--version")}[language]
            toolchain = run(["docker", "run", "--rm", "--pull=never", "--network=none", image, *version], ROOT)
            execution = isolated_run(image, case_dir, command, language)
            report["cases"].append({"id": case_id, "language": language, "source": relative, "image": image, "document_sha256": hashlib.sha256(document.read_bytes()).hexdigest(), "code_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(), "assertion": assertion, "expected_stdout": expected or None, "toolchain": toolchain, "execution": execution, "status": "PASS" if passes(assertion, execution, expected) else "FAIL"})
    report["passed"] = sum(case["status"] == "PASS" for case in report["cases"])
    report["total"] = len(report["cases"])
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "go-node-python-twentyfirst-runtime.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# Go / Node.js / Python 第二十一轮正文提取运行验证", "", str(report["scope"]), "", "| Case | Source | Runtime | Result |", "| --- | --- | --- | --- |"]
    rows += [f"| `{case['id']}` | `{case['source']}` | `{case['image']}` | {case['status']} |" for case in report["cases"]]
    rows += ["", "## 边界", "", "验证仅覆盖表中从 Markdown 原样提取的完整程序：Go 的 final-bytes、Scanner 默认/配置 token 上限；Node 测试运行器对异步拒绝的等待；Python UTC 字符串 JSON 往返及 naive/aware 比较边界。它不覆盖整篇文档、其他围栏、网络、数据库、框架、部署、性能或平台行为。Node 的 TAP 时长由运行器生成，因此只断言通过/失败字段；JSON 同伴报告保留来源与代码 SHA-256、镜像工具链、完整命令、标准输出/错误和退出码。", ""]
    (REPORTS / "go-node-python-twentyfirst-runtime.md").write_text("\n".join(rows), encoding="utf-8")
    print(f"{'PASS' if report['passed'] == report['total'] else 'FAIL'}: {report['passed']}/{report['total']} named body programs")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
