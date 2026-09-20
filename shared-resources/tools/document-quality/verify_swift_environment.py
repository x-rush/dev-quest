#!/usr/bin/env python3
"""Run the named pure-Swift environment example exactly as documented."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = "06-swift-swiftui/basics/01-environment-setup.md"
CASE = "swift-environment-toolchain"
IMAGE = "swift:6.3.3-noble"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source = (ROOT / DOCUMENT).read_text(encoding="utf8")
    match = re.search(rf"```swift verify:{CASE}\n(.*?)\n```", source, re.S)
    if not match:
        raise RuntimeError(f"missing named code block: {CASE}")
    code = match.group(1)
    command = [args.docker, "run", "--rm", "-i", IMAGE, "swift", "-"]
    run = subprocess.run(command, input=code + "\n", capture_output=True, text=True, encoding="utf8", timeout=120)
    if run.returncode or run.stdout != "Swift toolchain check passed\n" or run.stderr:
        raise RuntimeError(f"unexpected result: exit={run.returncode}, stdout={run.stdout!r}, stderr={run.stderr!r}")
    report = {"runtime": f"Docker {IMAGE}", "scope": "The named Swift block is extracted verbatim and run once with the Linux Swift toolchain. It proves only this pure Swift standard-library program; it does not cover Xcode, macOS, iOS SDKs, SwiftUI, SwiftData, simulators, signing, a device, or distribution.", "results": [{"document": DOCUMENT, "case": CASE, "status": "PASS", "source_sha256": hashlib.sha256(code.encode()).hexdigest(), "stdout": run.stdout, "command": "docker run --rm -i swift:6.3.3-noble swift -"}]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("PASS", DOCUMENT)


if __name__ == "__main__":
    main()
