#!/usr/bin/env python3
"""Run the named Java environment smoke example exactly as documented.

This proves only that the displayed Hello.java can be compiled for Java 21 and
executed in the pinned container. It deliberately does not prove SDKMAN, an
editor, Maven, Gradle, a host installation, or a newer JDK.
"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = "08-java-revisited/basics/01-environment-setup.md"
CASE = "java-environment-hello"
IMAGE = "eclipse-temurin:21-jdk"


def named_java_block(source: str) -> str:
    match = re.search(rf"```java verify:{CASE}\n(.*?)\n```", source, re.S)
    if not match:
        raise RuntimeError(f"missing named code block: {CASE}")
    program = match.group(1)
    if "public class Hello" not in program:
        raise RuntimeError("the named case must declare public class Hello")
    return program


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    source = (ROOT / DOCUMENT).read_text(encoding="utf8")
    program = named_java_block(source)
    with tempfile.TemporaryDirectory(prefix="dev-quest-java-environment-") as folder:
        work = Path(folder)
        (work / "Hello.java").write_text(program + "\n", encoding="utf8")
        command = [
            args.docker, "run", "--rm", "-v", f"{work.resolve()}:/src", "-w", "/src",
            IMAGE, "sh", "-c", "javac --release 21 -encoding UTF-8 Hello.java && java Hello",
        ]
        run = subprocess.run(command, capture_output=True, text=True, encoding="utf8", timeout=120)
        if run.returncode != 0:
            raise RuntimeError("command failed:\n" + " ".join(command) + "\n" + run.stdout + run.stderr)
        if run.stdout != "42\n" or run.stderr:
            raise RuntimeError(f"unexpected output: stdout={run.stdout!r}, stderr={run.stderr!r}")

    report = {
        "runtime": f"Docker {IMAGE}",
        "scope": "The named Hello.java block is extracted verbatim, compiled with javac --release 21, and run once. This is limited evidence for Java 21 compilation and execution; it does not cover SDKMAN, host PATH configuration, IDE integration, Maven, Gradle, JDK 25, or a project build.",
        "results": [{
            "document": DOCUMENT,
            "case": CASE,
            "status": "PASS",
            "source_sha256": hashlib.sha256(program.encode("utf8")).hexdigest(),
            "stdout": run.stdout,
            "command": "docker run --rm -v <temporary-directory>:/src -w /src eclipse-temurin:21-jdk sh -c 'javac --release 21 -encoding UTF-8 Hello.java && java Hello'",
        }],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("PASS", DOCUMENT)


if __name__ == "__main__":
    main()
