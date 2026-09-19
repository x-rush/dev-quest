"""Extract three marked Go fences from documentation and record isolated runtime evidence."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).with_name("reports")
CASES = (
    ("go-first-program-hello", "01-go-backend/basics/02-first-program.md", "Hello, World!\n欢迎来到Go语言的世界!\n"),
    ("go-method-receiver-mutation", "01-go-backend/basics/05-functions-methods.md", "初始值: 0\n值接收者内部: 1\n值接收者调用后: 0\n指针接收者内部: 1\n指针接收者调用后: 1\n"),
    ("go-error-wrap-is", "01-go-backend/reference/language-concepts/07-error-handling.md", "文件不存在，使用默认配置\nloadConfig \"missing.toml\": open missing.toml: no such file or directory\n"),
    ("go-channel-close-select", "01-go-backend/reference/language-concepts/12-channel-semantics.md", "worker: 工作\n1 2\n0 false\n收到 42\n退出 1\n100\n"),
    ("go-interface-typed-nil", "01-go-backend/reference/language-concepts/13-interface-semantics.md", "误判为失败！动态类型: *main.MyErr\n正确：err == nil\n是 int: 42\nint 42\n"),
    ("go-defer-panic-recover", "01-go-backend/reference/language-concepts/14-defer-panic-recover.md", "defer 闭包（延迟求值）: 99\ndefer 参数（立即求值）: 1\nbody\nsecond registered\nfirst registered\ndouble(3) = 30\nrecovered: boom\n"),
    ("go-csv-reader-writer", "01-go-backend/reference/library-guides/17-std-package-map.md", "\"北京,中国\",2\n上海,1\n"),
    ("go-nil-value-boundaries", "01-go-backend/reference/language-concepts/15-nil-semantics.md", "0 0\n[1]\n0\n0\ntrue\ntrue\ntrue\n"),
)

def fence(text: str, identifier: str) -> str:
    hit = re.search(rf"<!-- doc-verify:{re.escape(identifier)} -->\s*```go\n(.*?)\n```", text, re.S)
    if not hit:
        raise RuntimeError(f"marked Go fence missing: {identifier}")
    return hit.group(1) + "\n"

def run(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "run", "--rm", "-i", "--pull=never", "--network=none", "--read-only",
         "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pids-limit=64", "--memory=512m",
         "--cpus=1", "--tmpfs", "/tmp:rw,exec,nosuid,nodev,size=256m", "golang:1.25-alpine",
         "sh", "-c", "cat > /tmp/main.go && GOCACHE=/tmp/go-build go run /tmp/main.go"],
        input=code, text=True, encoding="utf-8", errors="strict", capture_output=True, check=False,
    )

def main() -> None:
    requested = sys.argv[1:]
    selected = tuple(case for case in CASES if not requested or case[0] in requested)
    if requested and len(selected) != len(requested):
        raise SystemExit("unknown verification case")
    prepared = []
    for identifier, document, expected in selected:
        document_text = (ROOT / document).read_text(encoding="utf8").replace("\r\n", "\n")
        code = fence(document_text, identifier)
        prepared.append((identifier, document, expected, document_text, code))
    # Each case remains a separate locked-down container. Parallel launches avoid
    # serial cold compilation making the verifier exceed an interactive time window.
    with ThreadPoolExecutor(max_workers=min(2, len(prepared))) as executor:
        completed_cases = list(executor.map(lambda item: run(item[4]), prepared))
    results = []
    for (identifier, document, expected, document_text, code), completed in zip(prepared, completed_cases):
        passed = completed.returncode == 0 and completed.stdout == expected
        results.append({
            "id": identifier, "language": "go", "document": document,
            "image": "golang:1.25-alpine", "document_sha256": hashlib.sha256(document_text.encode()).hexdigest(),
            "code_sha256": hashlib.sha256(code.encode()).hexdigest(), "command": "GOCACHE=/tmp/go-build go run /tmp/main.go",
            "expected_stdout": expected, "stdout": completed.stdout, "stderr": completed.stderr,
            "exit_code": completed.returncode, "status": "PASS" if passed else "FAIL",
        })
    report = {
        "schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Twenty-fifth-round runtime evidence for eight marked Go core-document fences.",
        "isolation": "No network, read-only container root, dropped capabilities, no-new-privileges, bounded CPU/memory/PIDs, and tmpfs-only writable workspace. Image must already exist because --pull=never is used.",
        "scope": "Only the eight named complete Go fences extracted unchanged after CRLF-to-LF normalization were executed. Other fences, toolchain setup, web services, filesystem integrations, concurrency scheduling, performance, and projects remain outside this evidence.",
        "results": results, "summary": {"passed": sum(x["status"] == "PASS" for x in results), "total": len(results)},
    }
    REPORTS.mkdir(exist_ok=True)
    if requested:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if any(x["status"] != "PASS" for x in results):
            raise SystemExit(1)
        return
    (REPORTS / "go-core-twentyfive-runtime.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    lines = ["# Go 核心基础页第二十五批运行验证", "", "仅运行下列八个正文中有 `doc-verify` 标记的完整 Go 围栏。报告不将结果扩大为整页、工具链或项目验证。", "", "| 文档 | 示例 | 结果 |", "|---|---|---|"]
    lines += [f"| [{x['document']}](../../../../{x['document']}) | `{x['id']}` | {x['status']} |" for x in results]
    lines += ["", "隔离条件、原文与代码 SHA-256、完整输出和命令见同名 JSON。"]
    (REPORTS / "go-core-twentyfive-runtime.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    print(json.dumps(report["summary"]))
    if any(x["status"] != "PASS" for x in results):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
