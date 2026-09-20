#!/usr/bin/env python3
"""Compile, run, and test the named dependency-free Cargo example verbatim."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = "11-rust-cross-platform/basics/01-environment-setup.md"
CASE = "rust-environment-cargo"
IMAGE = "rust:1-slim-bookworm"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source = (ROOT / DOCUMENT).read_text(encoding="utf8")
    match = re.search(rf"```rust verify:{CASE}\n(.*?)\n```", source, re.S)
    if not match:
        raise RuntimeError(f"missing named code block: {CASE}")
    code = match.group(1)
    with tempfile.TemporaryDirectory(prefix="dev-quest-rust-environment-") as folder:
        work = Path(folder)
        (work / "Cargo.toml").write_text('[package]\nname = "environment-check"\nversion = "0.1.0"\nedition = "2024"\n', encoding="utf8")
        (work / "src").mkdir()
        (work / "src/main.rs").write_text(code + "\n", encoding="utf8")
        command = [args.docker, "run", "--rm", "--network", "none", "--user", f"{os.getuid()}:{os.getgid()}", "-v", f"{work.resolve()}:/work", "-w", "/work", IMAGE, "sh", "-c", "cargo check --offline && cargo run --offline --quiet && cargo test --offline --quiet"]
        run = subprocess.run(command, capture_output=True, text=True, encoding="utf8", timeout=180)
        if run.returncode or "Hello, Rust!\n" not in run.stdout or "test result: ok. 1 passed" not in run.stdout:
            raise RuntimeError(f"unexpected result: exit={run.returncode}, stdout={run.stdout!r}, stderr={run.stderr!r}")
    report = {"runtime": f"Docker {IMAGE}", "scope": "The named Rust block is extracted verbatim into a dependency-free Cargo crate with edition 2024. cargo check, cargo run and cargo test execute offline. This does not cover rustup, a host toolchain, third-party crates, cross-compilation, networking, native linkers, or publishing.", "results": [{"document": DOCUMENT, "case": CASE, "status": "PASS", "source_sha256": hashlib.sha256(code.encode()).hexdigest(), "command": "docker run --rm --network none -v <temporary-directory>:/work -w /work rust:1-slim-bookworm sh -c 'cargo check --offline && cargo run --offline --quiet && cargo test --offline --quiet'"}]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("PASS", DOCUMENT)


if __name__ == "__main__":
    main()
