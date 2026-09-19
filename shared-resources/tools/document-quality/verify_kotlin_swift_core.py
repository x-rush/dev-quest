#!/usr/bin/env python3
"""Run exact portable Kotlin/Swift documentation programs, without Android stubs."""
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "shared-resources/tools/document-quality/reports/kotlin-swift-core.json"


def extract_marked(text, name, language):
    matches = re.findall(r"<!-- dq-case: " + re.escape(name) + r" -->\s*```" + language + r"\n(.*?)^```", text, re.M | re.S)
    if len(matches) != 1:
        raise ValueError(f"Expected one unchanged marked program: {name}")
    return matches[0]


def main():
    kotlin = "05-kotlin-compose/basics/03-kotlin-syntax-essentials.md"
    swift = "06-swift-swiftui/basics/03-swift-syntax-essentials.md"
    project = "05-kotlin-compose/basics/08-first-project.md"
    documents = {path: (ROOT / path).read_text(encoding="utf-8") for path in (kotlin, swift, project)}
    blocks = re.findall(r"^```kotlin\n(.*?)^```", documents[project], re.M | re.S)
    repository = next(block for block in blocks if "class NoteRepository(" in block)
    rules = repository[repository.index("data class NoteDraft"):repository.index("class NoteRepository(")]
    entry = next(block for block in blocks if block.startswith("fun main()") and "Kotlin note rules passed" in block)
    kotlin_image = os.environ.get("DEV_QUEST_KOTLIN_IMAGE", "dev-quest-validation:local")
    cases = [
        ("kotlin-syntax-contracts", kotlin, extract_marked(documents[kotlin], "kotlin-syntax-contracts", "kotlin"), "Main.kt", kotlin_image, "kotlinc Main.kt -include-runtime -d /tmp/main.jar && java -jar /tmp/main.jar", "Kotlin syntax contracts passed\n"),
        ("kotlin-note-rules", project, rules + entry, "Main.kt", kotlin_image, "kotlinc Main.kt -include-runtime -d /tmp/main.jar && java -jar /tmp/main.jar", "Kotlin note rules passed\n"),
        ("swift-syntax-contracts", swift, extract_marked(documents[swift], "swift-syntax-contracts", "swift"), "Main.swift", "swift:6.3.3-noble", "swift Main.swift", "Swift syntax contracts passed\n"),
    ]
    results = []
    for name, path, code, filename, image, command, expected in cases:
        with tempfile.TemporaryDirectory(prefix="devquest-core-") as directory:
            work = Path(directory)
            (work / filename).write_text(code, encoding="utf-8")
            prefix = ["docker", "run", "--rm", "--network", "none", "--read-only", "--cap-drop", "ALL", "--pids-limit", "256", "--memory", "1g", "--cpus", "2", "--tmpfs", "/tmp:rw,exec,nosuid,size=512m", "-e", "HOME=/tmp", "-v", f"{work}:/work:ro", "-w", "/work", image, "sh", "-c"]
            version_command = "kotlinc -version && java -version" if filename.endswith(".kt") else "swift --version"
            version = subprocess.run(prefix + [version_command], capture_output=True, text=True, encoding="utf-8", timeout=60)
            result = subprocess.run(prefix + [command], capture_output=True, text=True, encoding="utf-8", timeout=120)
            passed = version.returncode == 0 and result.returncode == 0 and result.stdout == expected
            results.append({"case": name, "source": path,
                            "source_sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                            "extracted_code_sha256": hashlib.sha256(code.encode()).hexdigest(),
                            "extracted_code": code, "image": image,
                            "toolchain": version.stdout + version.stderr,
                            "command": command, "exit_code": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr,
                            "expected_stdout": expected, "status": "PASS" if passed else "FAIL"})
            print(name, results[-1]["status"], flush=True)
            if not passed:
                print(result.stderr, flush=True)
    report = {"scope": "Exact marked Kotlin/Swift programs and unchanged Kotlin project input rules plus the documented main entry. No synthetic Android/Room APIs.",
              "not_verified": ["Android SDK/Gradle/KSP build", "Compose UI/lifecycle and Room persistence", "SwiftUI/SwiftData/macOS/iOS builds", "Concurrent lifecycle and device behavior"],
              "results": results}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if all(result["status"] == "PASS" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
