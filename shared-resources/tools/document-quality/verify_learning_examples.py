#!/usr/bin/env python3
"""Run only the named complete learning examples, never all documentation blocks.

Usage: python verify_learning_examples.py [--node /path/to/node] [--report result.json]
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PYTHON_CASES = [
    ("10-python-discovery/reference/language-concepts/02-built-in-functions.md",
     "[7, 2, 10] [2, 7, 10]\n19 2 10\n[(1, 2), (2, 7), (3, 10)]\n2 7 10 结束\nFalse True\nTrue False\n"),
    ("10-python-discovery/reference/language-concepts/01-python-keywords.md",
     "keywords-control-flow: first=3; missing=True\n"),
    ("10-python-discovery/reference/language-concepts/06-decorators.md", "开始\n完成\n你好，Ada\ngreet\n"),
]


def first_block(relative, language):
    text = (ROOT / relative).read_text(encoding="utf-8")
    match = re.search(r"^```" + re.escape(language) + r"\n(.*?)^```\s*$", text, re.M | re.S)
    if match is None:
        raise ValueError(f"No {language} example in {relative}")
    return match.group(1)


def marked_block(relative, language, marker):
    """Extract the fence attached to an explicit verification-case marker.

    First-fence extraction is deliberately avoided for documents that contain
    several teaching snippets: adding an introductory example must not silently
    change which contract this verifier executes.
    """
    text = (ROOT / relative).read_text(encoding="utf-8")
    pattern = (r"<!--\s*verification-case:\s*" + re.escape(marker) +
               r"\s*-->\s*\n```" + re.escape(language) + r"\n(.*?)^```\s*$")
    match = re.search(pattern, text, re.M | re.S)
    if match is None:
        raise ValueError(f"No marked {language} example {marker!r} in {relative}")
    return match.group(1)


def run_case(command, file, content, expected):
    file.write_text(content, encoding="utf-8")
    result = subprocess.run(command + [str(file)], cwd=file.parent, capture_output=True,
                            text=True, encoding="utf-8", timeout=15)
    if result.returncode != 0 or result.stdout != expected:
        raise AssertionError({"file": str(file), "code": result.returncode,
                              "stdout": result.stdout, "stderr": result.stderr,
                              "expected": expected})
    return {"case": file.name, "status": "PASS", "output": result.stdout}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", default=shutil.which("node"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory(prefix="dev-quest-examples-") as temporary:
        work = Path(temporary)
        for index, (relative, expected) in enumerate(PYTHON_CASES):
            result = run_case([sys.executable, "-X", "utf8"], work / f"python-{index}.py",
                              first_block(relative, "python"), expected)
            result["source"] = relative
            results.append(result)
        if args.node:
            source = "09-nodejs-backend/basics/04-async-promises.md"
            for suffix, expected in [
                ("cjs", "sync\nnextTick\nmicrotask\npromise\n"),
                ("mjs", "sync\nmicrotask\npromise\nnextTick\n"),
            ]:
                result = run_case([args.node], work / f"order.{suffix}",
                                  first_block(source, "js"), expected)
                result["source"] = source
                results.append(result)
            source = "09-nodejs-backend/reference/library-guides/01-core-modules.md"
            result = run_case([args.node], work / "core-lab.mjs", first_block(source, "js"),
                              "core-lab.mjs\ntrue\nfunction\n")
            result["source"] = source
            results.append(result)
            for source, name, marker, expected in [
                ("shared-resources/javascript-keywords.md", "keywords.mjs",
                 "shared-js-keywords-binding-flow", "read\ntrue\nfinished\n"),
                ("shared-resources/javascript-builtins.md", "builtins.mjs",
                 "shared-js-builtins-data-cleaning", "2,7,10\n19\nfalse\ntrue\ntrue\n"),
                ("shared-resources/javascript-standard-library.md", "standard-library.mjs",
                 "shared-js-standard-library-map-set", "saved\nundefined\na,b\n"),
            ]:
                result = run_case([args.node], work / name, marked_block(source, "js", marker), expected)
                result["source"] = source
                results.append(result)
        else:
            results.append({"case": "Node examples", "status": "SKIP_NOTOOL"})
    report = {"python": sys.version.split()[0], "results": results,
              "scope": "Only named complete examples; no Java, Go, Rust, PHP or native UI execution."}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
