"""Verify two explicitly marked Rust lifetime contracts extracted from one lesson."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).with_name("reports")
DOCUMENT = "11-rust-cross-platform/basics/07-lifetimes.md"
IMAGE = "rust:1-slim-bookworm"
SUCCESS_ID = "rust-lifetime-borrowed-and-owned"
FAIL_ID = "rust-lifetime-local-reference"
EXPECTED_STDOUT = "borrowed=banana\nowned=owned\n"


def extract(text: str, marker: str, identifier: str) -> str:
    match = re.search(rf"<!-- {re.escape(marker)}:{re.escape(identifier)}(?:; error=E\d{{4}})? -->\s*```rust\n(.*?)\n```", text, re.S)
    if not match:
        raise RuntimeError(f"missing marked Rust fence: {identifier}")
    return match.group(1) + "\n"


def invoke(code: str, command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "run", "--rm", "-i", "--pull=never", "--network=none", "--read-only",
         "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pids-limit=64", "--memory=512m",
         "--cpus=1", "--tmpfs", "/tmp:rw,exec,nosuid,nodev,size=128m", IMAGE,
         "sh", "-c", command],
        input=code, text=True, encoding="utf-8", errors="strict", capture_output=True, check=False,
    )


def result(identifier: str, mode: str, code: str, document_text: str) -> dict:
    if mode == "runtime":
        completed = invoke(code, "cat > /tmp/main.rs && rustc --edition=2024 /tmp/main.rs -o /tmp/example && /tmp/example")
        passed = completed.returncode == 0 and completed.stdout == EXPECTED_STDOUT
        expectation = {"stdout": EXPECTED_STDOUT}
    else:
        completed = invoke(code, "cat > /tmp/main.rs && rustc --edition=2024 --error-format=json /tmp/main.rs -o /tmp/example")
        error_codes = []
        for line in completed.stderr.splitlines():
            if not line.startswith("{"):
                continue
            diagnostic = json.loads(line)
            if isinstance(diagnostic, dict) and isinstance(diagnostic.get("code"), dict):
                error_codes.append(diagnostic["code"].get("code"))
        passed = completed.returncode != 0 and "E0515" in error_codes
        expectation = {"compile_error": "E0515", "observed_error_codes": error_codes}
    return {"id": identifier, "document": DOCUMENT, "language": "rust", "mode": mode, "image": IMAGE, "document_sha256": hashlib.sha256(document_text.encode()).hexdigest(), "code_sha256": hashlib.sha256(code.encode()).hexdigest(), "expected": expectation, "stdout": completed.stdout, "stderr": completed.stderr, "exit_code": completed.returncode, "status": "PASS" if passed else "FAIL"}


def main() -> None:
    text = (ROOT / DOCUMENT).read_text(encoding="utf-8").replace("\r\n", "\n")
    cases = [result(SUCCESS_ID, "runtime", extract(text, "doc-verify", SUCCESS_ID), text), result(FAIL_ID, "compile_fail_contract", extract(text, "doc-verify-compile-fail", FAIL_ID), text)]
    report = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "purpose": "Direct Rust lifetime lesson evidence for one successful borrowed/owned result and one rejected local-reference contract.", "scope": "Only the two named complete Rust fences extracted unchanged after CRLF-to-LF normalization were checked. The rest of the lesson, other compiler diagnostics, crates, async code, and projects remain outside this evidence.", "isolation": "No network, read-only container root, dropped capabilities, no-new-privileges, bounded CPU/memory/PIDs, and tmpfs-only writable workspace. The cached Rust image is required because --pull=never is used.", "results": cases, "summary": {"passed": sum(case["status"] == "PASS" for case in cases), "total": len(cases)}}
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "rust-lifetime-basics-runtime.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Rust 生命周期基础页限定验证", "", "只验证正文中两个具名 Rust 围栏：一个运行输出契约与一个 `E0515` 编译失败契约；不代表整页或整个 Rust 模块已完成验证。", "", "| 页面 | 示例 | 类型 | 结果 |", "|---|---|---|---|"]
    lines += [f"| [{case['document']}](../../../../{case['document']}) | `{case['id']}` | {case['mode']} | {case['status']} |" for case in cases]
    lines += ["", "隔离条件、源码哈希、编译器输出与完整诊断见同名 JSON 报告。"]
    (REPORTS / "rust-lifetime-basics-runtime.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"]))
    if any(case["status"] != "PASS" for case in cases):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
