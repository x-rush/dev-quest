#!/usr/bin/env python3
"""Verify portable logic only; this is not an Android/iOS/HarmonyOS build."""
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "shared-resources/tools/document-quality/reports/mobile-foundations.json"


def fences(path, language):
    text = (ROOT / path).read_text(encoding="utf-8")
    return re.findall(r"^```" + language + r"\n(.*?)^```", text, re.M | re.S)


def case(name, source_path, source, executable, harness, image, command):
    with tempfile.TemporaryDirectory(prefix="devquest-mobile-") as directory:
        work = Path(directory)
        (work / executable).write_text(source + "\n" + harness, encoding="utf-8")
        args = ["docker", "run", "--rm", "--network", "none", "--read-only",
                "--cap-drop", "ALL", "--pids-limit", "256", "--memory", "1g",
                "--cpus", "2", "--tmpfs", "/tmp:rw,exec,nosuid,size=512m",
                "-e", "HOME=/tmp", "-v", f"{work}:/work:rw", "-w", "/work",
                image, "sh", "-c", command]
        result = subprocess.run(args, capture_output=True, text=True,
                                encoding="utf-8", timeout=120)
        expected = {"kotlin-scope-1": "true\n2\nnull\n",
                    "kotlin-scope-2": "scope contracts passed\n",
                    "rn-ledger-pure-contracts": "RN pure input and storage-schema contracts passed\n",
                    "swift-money-contracts": "Swift money contracts passed\n"}[name]
        return {"case": name, "source": source_path,
                "source_sha256": hashlib.sha256((ROOT / source_path).read_bytes()).hexdigest(),
                "extracted_code_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "extracted_code": source, "assertion_harness": harness,
                "image": image, "command": command, "exit_code": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr,
                "expected_stdout_suffix": expected,
                "status": "PASS" if result.returncode == 0 and result.stdout.endswith(expected) else "FAIL"}


def main():
    results = []
    kotlin = "05-kotlin-compose/reference/language-concepts/07-scope-functions.md"
    candidates = [x for x in fences(kotlin, "kotlin") if x.startswith("fun main()")]
    if len(candidates) != 2:
        raise RuntimeError("Kotlin example structure changed; review extraction")
    for index, code in enumerate(candidates, 1):
        results.append(case(f"kotlin-scope-{index}", kotlin, code, "Scope.kt", "",
                            os.environ.get("DEV_QUEST_KOTLIN_IMAGE", "dev-quest-validation:local"),
                            "kotlinc -version && kotlinc Scope.kt -include-runtime -d scope.jar && java -jar scope.jar"))

    rn = "04-multiplatform-apps/basics/08-first-project.md"
    hook = next(x for x in fences(rn, "tsx") if "export function useLedger" in x)
    # Extract the unchanged type and pure functions. The hook/native storage is excluded.
    interface = hook[hook.index("export interface LedgerEntry"):hook.index("const KEY")]
    pure = hook[hook.index("export function parseCents"):hook.index("export function useLedger")]
    rn_harness = '''
import assert from 'node:assert/strict';
for (const [input, expected] of [['0.1', 10], ['0.20', 20], ['999999.99', 99999999], [' 12.50 ', 1250]]) {
  assert.equal(parseCents(input), expected);
}
for (const input of ['', ' ', '0', '-1', '12abc', 'Infinity', 'NaN', '1.234', '1.', '.1', '1000000', '１']) {
  assert.equal(parseCents(input), null, input);
}
assert.equal(parseCents('0.1')! + parseCents('0.2')!, 30);
assert.deepEqual(decodeEntries(null), []);
assert.deepEqual(decodeEntries('[]'), []);
const entry = {id: 'a', amount: 10, note: 'tea', createdAt: '2026-09-19T00:00:00.000Z'};
assert.deepEqual(decodeEntries(JSON.stringify([entry])), [entry]);
for (const raw of ['{', '{}', 'null', '[null]', JSON.stringify([entry, entry]),
  JSON.stringify([{...entry, amount: -1}]), JSON.stringify([{...entry, amount: 1.5}]),
  JSON.stringify([{...entry, createdAt: 'invalid'}]), JSON.stringify([{...entry, note: 3}])]) {
  assert.throws(() => decodeEntries(raw));
}
console.log('RN pure input and storage-schema contracts passed');
'''
    results.append(case("rn-ledger-pure-contracts", rn, interface + pure,
                        "ledger.ts", rn_harness, "node:24-bookworm-slim",
                        "node --version && node ledger.ts"))

    swift = "06-swift-swiftui/basics/08-first-project.md"
    app = fences(swift, "swift")[0]
    # Only the pure function; SwiftUI/SwiftData are not available in Linux.
    parse = app[app.index("func parseCents"):app.index("@Model")]
    swift_harness = '''
let expected = [("0.1", 10), ("0.20", 20), ("999999.99", 99999999), (" 12.50 ", 1250)]
for (input, cents) in expected { precondition(parseCents(input) == cents) }
for input in ["", " ", "0", "-1", "12abc", "Infinity", "NaN", "1.234", "1.", ".1", "1000000", "１"] {
    precondition(parseCents(input) == nil, input)
}
precondition(parseCents("0.1")! + parseCents("0.2")! == 30)
print("Swift money contracts passed")
'''
    results.append(case("swift-money-contracts", swift, "import Foundation\n" + parse,
                        "Money.swift", swift_harness, "swift:6.3.3-noble",
                        "swift --version && swift Money.swift"))
    report = {"scope": "Portable Kotlin standard-library programs; extracted unchanged RN and Swift pure functions with assertion harnesses.",
              "not_verified": ["RN Hook lifecycle and native AsyncStorage", "Android/iOS/HarmonyOS builds and device behavior", "SwiftUI/SwiftData type checking and persistence"],
              "results": results}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(result["case"], result["status"])
        if result["status"] != "PASS":
            print(result["stderr"])
    return 0 if all(x["status"] == "PASS" for x in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
