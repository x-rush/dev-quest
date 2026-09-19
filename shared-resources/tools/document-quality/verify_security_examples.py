"""Execute complete security examples extracted unchanged from Markdown in offline Docker containers."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
CASES = [
    ("go-boundaries", "01-go-backend/advanced-topics/security/01-security-best-practices.md",
     "go", "main.go", "golang:1", ["go", "run", "/input/main.go"],
     ["go", "version"], "security-boundaries: 6 checks passed\n"),
    ("php-pdo", "07-php-mastery/advanced-topics/security/01-security-practices.md",
     "php", "security.php", "php:8.5-cli-alpine", ["php", "/input/security.php"],
     ["php", "--version"], "pdo-security: 3 checks passed\n"),
    ("node-boundaries", "09-nodejs-backend/advanced-topics/security/01-security-practices.md",
     "javascript", "security.mjs", "node:24-bookworm-slim", ["node", "/input/security.mjs"],
     ["node", "--version"], "node-security: 6 checks passed\n"),
    ("python-sqlite", "10-python-discovery/advanced-topics/security/01-security-practices.md",
     "python", "security.py", "python:3.14-alpine", ["python", "/input/security.py"],
     ["python", "--version"], "python-security: 3 checks passed\n"),
]


def run(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=timeout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    results = []
    for name, source, language, filename, image, command, version, expected in CASES:
        document = (ROOT / source).read_text(encoding="utf-8")
        pattern = rf"<!-- security-check: {re.escape(name)} -->\s*```{language}\n(.*?)\n```"
        matches = list(re.finditer(pattern, document, re.S))
        record = {"id": name, "source": source, "image": image, "command": command,
                  "scope": "marked complete program only; framework integrations are not verified"}
        try:
            if len(matches) != 1:
                raise ValueError(f"expected exactly one marked {name} fence, found {len(matches)}")
            code = matches[0].group(1) + "\n"
            record.update(source_sha256=hashlib.sha256(document.encode()).hexdigest(),
                          code_sha256=hashlib.sha256(code.encode()).hexdigest(),
                          line=document.count("\n", 0, matches[0].start()) + 1)
            inspected = run(["docker", "image", "inspect", image, "--format", "{{.Id}}"])
            if inspected.returncode:
                raise RuntimeError(inspected.stderr.strip())
            image_id = inspected.stdout.strip()
            record["image_id"] = image_id
            # Use the inspected image ID to prevent a moving tag between inspection and execution.
            with tempfile.TemporaryDirectory(prefix="dev-quest-security-") as temp:
                (Path(temp) / filename).write_text(code, encoding="utf-8", newline="\n")
                base = ["docker", "run", "--rm", "--network", "none", "--read-only",
                        "--cap-drop", "ALL", "--pids-limit", "256", "--memory", "1g",
                        "--cpus", "2", "--tmpfs", "/work:rw,exec,nosuid,size=768m",
                        "--tmpfs", "/tmp:rw,noexec,nosuid,size=32m",
                        "-e", "GOCACHE=/work/cache", "-e", "TMPDIR=/work", "-e", "HOME=/work",
                        "-v", f"{temp}:/input:ro", "-w", "/work", image_id]
                runtime = run(base + version)
                if runtime.returncode:
                    raise RuntimeError(runtime.stderr.strip())
                result = run(base + command)
                record.update(runtime=runtime.stdout.strip(), exit_code=result.returncode,
                              stdout=result.stdout, stderr=result.stderr, expected_stdout=expected,
                              status="pass" if result.returncode == 0 and result.stdout == expected and not result.stderr else "fail")
        except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            record.update(status="fail", error=str(exc))
        results.append(record)
        print(f"{name}: {record['status']}")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({"results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if all(r["status"] == "pass" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
