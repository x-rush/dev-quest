"""Run nine marked Node/Python library programs verbatim in offline containers."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
DOCUMENTS = {
    "09-nodejs-backend/reference/library-guides/04-child-process.md": {
        "node-child-buffer": "child-buffer: literal, nonzero, maxBuffer\n",
        "node-child-stream": "child-stream: 131072 stdout, 98304 stderr, exit 0\n",
    },
    "09-nodejs-backend/reference/library-guides/09-zlib.md": {
        "node-zlib-roundtrip": "zlib-roundtrip: 4 formats, mismatch, output limit\n",
        "node-zlib-stream-limit": "zlib-stream: exact limit, overflow, invalid format\n",
    },
    "10-python-discovery/reference/library-guides/06-functools-subprocess.md": {
        "python-functools-cache": "functools-cache: hit, eviction, invalid key, shared result, copy\n",
        "python-functools-dispatch": "functools-dispatch: metadata, override, inheritance, specialization\n",
        "python-subprocess-contract": "subprocess: literal, nonzero, run timeout, communicate cleanup\n",
    },
    "10-python-discovery/reference/library-guides/05-enum-module.md": {
        "python-enum-contract": "enum-contract: identity, alias, lookup, unique, mixed types\n",
        "python-enum-transition": "enum-transition: input boundary, state rule, flags\n",
    },
}


def run(command, timeout=30):
    return subprocess.run(command, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=REPORTS / "node-python-libraries.json")
    parser.add_argument("--node-image", default="node:24-bookworm-slim")
    parser.add_argument("--python-image", default="python:3.14-alpine")
    args = parser.parse_args()
    environment = {}
    for image, version_command in [(args.node_image, ["node", "--version"]),
                                   (args.python_image, ["python", "--version"])]:
        info = run(["docker", "image", "inspect", image, "--format", "{{.Id}}"])
        if info.returncode:
            raise RuntimeError(f"Required local image unavailable: {image}: {info.stderr}")
        version = run(["docker", "run", "--rm", "--pull=never", "--network=none", image, *version_command])
        if version.returncode:
            raise RuntimeError(f"Runtime unavailable: {image}: {version.stderr}")
        environment[image] = {"image_id": info.stdout.strip(), "version": version.stdout.strip()}

    # Validate the complete manifest before running or replacing any report.
    programs = []
    for source, expected in DOCUMENTS.items():
        document = (ROOT / source).read_text(encoding="utf-8")
        language = "js" if source.startswith("09-") else "python"
        pattern = rf"<!-- library-case: ([a-z-]+) -->\n```{language}\n(.*?)\n```"
        matches = list(re.finditer(pattern, document, re.S))
        ids = [match.group(1) for match in matches]
        if len(ids) != len(set(ids)) or set(ids) != set(expected):
            raise ValueError(f"Missing, duplicate, unknown or malformed cases in {source}: {ids}")
        if document.count("<!-- library-case:") != len(ids):
            raise ValueError(f"Unparsed case marker in {source}")
        for match in matches:
            programs.append({
                "id": match.group(1), "source": source,
                "line": document.count("\n", 0, match.start()) + 2,
                "source_sha256": sha(document), "code": match.group(2) + "\n",
                "language": language, "expected_stdout": expected[match.group(1)],
            })

    results = []
    for program in programs:
        is_node = program["language"] == "js"
        image = args.node_image if is_node else args.python_image
        filename = "case.mjs" if is_node else "case.py"
        command = ["node", f"/input/{filename}"] if is_node else ["python", "-I", f"/input/{filename}"]
        record = dict(program, image=image, command=command, code_sha256=sha(program["code"]))
        name = "dev-quest-library-" + uuid.uuid4().hex[:12]
        with tempfile.TemporaryDirectory(prefix="dev-quest-library-") as temporary:
            (Path(temporary) / filename).write_text(program["code"], encoding="utf-8")
            docker = ["docker", "run", "--name", name, "--rm", "--pull=never",
                      "--network=none", "--read-only", "--cap-drop=ALL", "--pids-limit=64",
                      "--memory=256m", "--cpus=1", "--tmpfs", "/tmp:rw,nosuid,size=16m",
                      "--workdir=/tmp", "--mount", f"type=bind,source={temporary},target=/input,readonly",
                      image, *command]
            try:
                result = run(docker)
                passed = (result.returncode == 0 and result.stdout == program["expected_stdout"]
                          and result.stderr == "")
                record.update(status="PASS" if passed else "FAIL", stdout=result.stdout,
                              stderr=result.stderr, exit_code=result.returncode)
            except subprocess.TimeoutExpired as error:
                record.update(status="FAIL", error=f"runner timeout: {error.timeout}s")
            finally:
                # A timed-out Docker client can leave its container running.
                run(["docker", "rm", "--force", name], timeout=10)
        results.append(record)
        print(f"{record['status']} {record['id']}")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Nine named complete programs extracted unchanged from four standard-library documents. "
                 "No external commands, HTTP middleware, Windows batch, fork IPC, process-tree management "
                 "or entire-document runtime coverage is claimed.",
        "source_hash_normalization": "UTF-8 read_text normalizes CRLF to LF; code ends in one LF",
        "environment": environment,
        "command": "python shared-resources/tools/document-quality/verify_node_python_libraries.py",
        "passed": sum(row["status"] == "PASS" for row in results),
        "total": len(results), "results": results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['passed']}/{report['total']} passed")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
