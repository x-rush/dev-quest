#!/usr/bin/env python3
"""Run the named minimal Gin example exactly as it appears in the document.

The check intentionally uses httptest, not a listening server.  It proves the
documented route, JSON-binding and status-code behavior, but not deployment,
TLS, reverse proxies, databases, authentication or load characteristics.
"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = "01-go-backend/frameworks/01-gin-framework-basics.md"
GIN_VERSION = "v1.12.0"


def fenced(source: str, name: str) -> str:
    match = re.search(rf"```go verify:{re.escape(name)}\n(.*?)\n```", source, re.S)
    if not match:
        raise RuntimeError(f"missing named code block: {name}")
    return match.group(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    source = (ROOT / DOCUMENT).read_text(encoding="utf8")
    main_go = fenced(source, "gin-basics-main")
    test_go = fenced(source, "gin-basics-test")
    with tempfile.TemporaryDirectory(prefix="dev-quest-gin-") as folder:
        work = Path(folder)
        (work / "go.mod").write_text(
            "module example/gin-basics\n\ngo 1.26\n\nrequire github.com/gin-gonic/gin " + GIN_VERSION + "\n",
            encoding="utf8",
        )
        (work / "main.go").write_text(main_go + "\n", encoding="utf8")
        (work / "main_test.go").write_text(test_go + "\n", encoding="utf8")
        # The temporary module starts without go.sum. -mod=mod permits Go to
        # resolve the pinned dependency and write its checksum before testing.
        command = [args.docker, "run", "--rm", "-v", f"{work.resolve()}:/src", "-w", "/src", "golang:1.27", "go", "test", "-mod=mod", "./..."]
        run = subprocess.run(command, capture_output=True, text=True, encoding="utf8", timeout=180)
        if run.returncode:
            raise RuntimeError("command failed:\n" + " ".join(command) + "\n" + run.stdout + run.stderr)

    report = {
        "runtime": "Docker golang:1.27",
        "dependency": f"github.com/gin-gonic/gin {GIN_VERSION}",
        "scope": "The two named Gin blocks are extracted verbatim and tested with net/http/httptest: health route, malformed JSON, required field, success response and unknown route. No port listener, deployment, database, authorization, TLS or performance behavior is claimed.",
        "results": [{
            "document": DOCUMENT,
            "status": "PASS",
            "main_sha256": hashlib.sha256(main_go.encode()).hexdigest(),
            "test_sha256": hashlib.sha256(test_go.encode()).hexdigest(),
            "command": "docker run --rm -v <temporary-directory>:/src -w /src golang:1.27 go test -mod=mod ./...",
        }],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("PASS", DOCUMENT)


if __name__ == "__main__":
    main()
