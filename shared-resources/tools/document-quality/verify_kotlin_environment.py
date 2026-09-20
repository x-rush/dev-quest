#!/usr/bin/env python3
"""Compile and run the named Kotlin/JVM environment case verbatim."""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = "05-kotlin-compose/basics/01-environment-setup.md"
CASE = "kotlin-environment-jvm"
IMAGE = "dev-quest-validation:local"


def extract(source: str) -> str:
    match = re.search(rf"```kotlin verify:{CASE}\n(.*?)\n```", source, re.S)
    if not match:
        raise RuntimeError(f"missing named code block: {CASE}")
    return match.group(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    code = extract((ROOT / DOCUMENT).read_text(encoding="utf8"))
    with tempfile.TemporaryDirectory(prefix="dev-quest-kotlin-environment-") as folder:
        work = Path(folder)
        (work / "EnvironmentCheck.kt").write_text(code + "\n", encoding="utf8")
        command = [args.docker, "run", "--rm", "-v", f"{work.resolve()}:/work", "-w", "/work", IMAGE, "sh", "-c", "kotlinc EnvironmentCheck.kt -include-runtime -d /tmp/environment-check.jar && java -jar /tmp/environment-check.jar"]
        run = subprocess.run(command, capture_output=True, text=True, encoding="utf8", timeout=120)
        if run.returncode or run.stdout != "Kotlin JVM environment check passed\n" or run.stderr:
            raise RuntimeError(f"unexpected result: exit={run.returncode}, stdout={run.stdout!r}, stderr={run.stderr!r}")
    report = {"runtime": f"Docker {IMAGE}", "scope": "The named Kotlin block is extracted verbatim, compiled with kotlinc, and run on the JVM. It proves only this pure Kotlin/JVM program; it does not cover Android Studio, Gradle, Android SDK, Compose, an emulator, a device, or an APK.", "results": [{"document": DOCUMENT, "case": CASE, "status": "PASS", "source_sha256": hashlib.sha256(code.encode()).hexdigest(), "stdout": run.stdout, "command": "docker run --rm -v <temporary-directory>:/work -w /work dev-quest-validation:local sh -c 'kotlinc EnvironmentCheck.kt -include-runtime -d /tmp/environment-check.jar && java -jar /tmp/environment-check.jar'"}]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("PASS", DOCUMENT)


if __name__ == "__main__":
    main()
