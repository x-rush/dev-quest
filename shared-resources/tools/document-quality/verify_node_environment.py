#!/usr/bin/env python3
"""Run the named Node 24 ESM environment example exactly as documented."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = "09-nodejs-backend/basics/01-environment-setup.md"
CASE = "node-environment-esm"
IMAGE = "node:24-bookworm-slim"


def source_block(text: str) -> str:
    found = re.search(rf"```js verify:{CASE}\n(.*?)\n```", text, re.S)
    if not found:
        raise RuntimeError(f"missing named code block: {CASE}")
    return found.group(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    program = source_block((ROOT / DOCUMENT).read_text(encoding="utf8"))
    command = [args.docker, "run", "--rm", "-i", IMAGE, "node", "--input-type=module", "-"]
    run = subprocess.run(command, input=program + "\n", capture_output=True, text=True, encoding="utf8", timeout=120)
    if run.returncode or not re.fullmatch(r"Node v24\.\d+\.\d+ executed this ESM module\n", run.stdout) or run.stderr:
        raise RuntimeError(f"unexpected result: exit={run.returncode}, stdout={run.stdout!r}, stderr={run.stderr!r}")
    report = {
        "runtime": f"Docker {IMAGE}",
        "scope": "The named JavaScript block is extracted verbatim and executed once as stdin ESM. It proves Node 24 can run this minimal ESM/assertion example; it does not prove a host installation, a version-manager hook, pnpm, TypeScript type stripping, dependencies, a server, or project scripts.",
        "results": [{"document": DOCUMENT, "case": CASE, "status": "PASS", "source_sha256": hashlib.sha256(program.encode()).hexdigest(), "stdout": run.stdout, "command": "docker run --rm -i node:24-bookworm-slim node --input-type=module -"}],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("PASS", DOCUMENT)


if __name__ == "__main__":
    main()
