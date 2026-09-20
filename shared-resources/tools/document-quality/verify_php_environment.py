#!/usr/bin/env python3
"""Run the named PHP environment program exactly as documented."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = "07-php-mastery/basics/01-environment-setup.md"
CASE = "php-environment-runtime"
IMAGE = "php:8.5-cli"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    text = (ROOT / DOCUMENT).read_text(encoding="utf8")
    match = re.search(rf"```php verify:{CASE}\n(.*?)\n```", text, re.S)
    if not match:
        raise RuntimeError(f"missing named code block: {CASE}")
    code = match.group(1)
    run = subprocess.run([args.docker, "run", "--rm", "-i", IMAGE, "php"], input=code + "\n", capture_output=True, text=True, encoding="utf8", timeout=120)
    if run.returncode or not re.fullmatch(r'\{"name":"PHP"\}\nstrict-type-error\nmbstring-(loaded|missing)\n', run.stdout) or run.stderr:
        raise RuntimeError(f"unexpected result: exit={run.returncode}, stdout={run.stdout!r}, stderr={run.stderr!r}")
    report = {"runtime": f"Docker {IMAGE}", "scope": "The named PHP block is extracted verbatim and run once in PHP CLI. It proves strict scalar calls, JSON encoding and the observed mbstring state for that container; it does not cover Composer, Xdebug, FPM, web-server configuration, databases, or a host installation.", "results": [{"document": DOCUMENT, "case": CASE, "status": "PASS", "source_sha256": hashlib.sha256(code.encode()).hexdigest(), "stdout": run.stdout, "command": "docker run --rm -i php:8.5-cli php"}]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("PASS", DOCUMENT)


if __name__ == "__main__":
    main()
