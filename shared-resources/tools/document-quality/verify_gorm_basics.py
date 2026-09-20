#!/usr/bin/env python3
"""Execute the two named GORM/SQLite blocks from the framework document."""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = "01-go-backend/frameworks/03-gorm-orm-complete.md"


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
    main_go, test_go = fenced(source, "gorm-basics-main"), fenced(source, "gorm-basics-test")
    with tempfile.TemporaryDirectory(prefix="dev-quest-gorm-") as folder:
        work = Path(folder)
        (work / "go.mod").write_text(
            "module example/gorm-basics\n\ngo 1.24\n\nrequire (\n\tgorm.io/driver/sqlite v1.6.0\n\tgorm.io/gorm v1.31.2\n)\n",
            encoding="utf8",
        )
        (work / "main.go").write_text(main_go + "\n", encoding="utf8")
        (work / "main_test.go").write_text(test_go + "\n", encoding="utf8")
        command = [args.docker, "run", "--rm", "-v", f"{work.resolve()}:/src", "-w", "/src", "golang:1.27", "go", "test", "-mod=mod", "./..."]
        run = subprocess.run(command, capture_output=True, text=True, encoding="utf8", timeout=180)
        if run.returncode:
            raise RuntimeError("command failed:\n" + " ".join(command) + "\n" + run.stdout + run.stderr)
    output = {
        "runtime": "Docker golang:1.27",
        "dependencies": ["gorm.io/gorm v1.31.2", "gorm.io/driver/sqlite v1.6.0"],
        "scope": "The named source blocks are extracted verbatim into a temporary SQLite in-memory module. It verifies migration, create/read, ErrRecordNotFound and rollback after a returned transaction error; it does not verify other database dialects, connection pools, concurrent clients, deployment or production migrations.",
        "results": [{"document": DOCUMENT, "status": "PASS", "main_sha256": hashlib.sha256(main_go.encode()).hexdigest(), "test_sha256": hashlib.sha256(test_go.encode()).hexdigest()}],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("PASS", DOCUMENT)


if __name__ == "__main__":
    main()
