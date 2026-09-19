#!/usr/bin/env python3
"""Run named complete Rust fences verbatim; no source wrapping or missing imports.

Use --prepare once online, then the default --offline --locked run in a
network-disabled disposable container. A dedicated --work directory is required.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "tokio": ("12-tokio-guide.md", {"tokio-tasks", "tokio-channels", "tokio-reserve", "tokio-time"}),
    "serde": ("13-serde-guide.md", {"serde-fields", "serde-visitor", "serde-serialize", "serde-with"}),
    "errors": ("14-error-libraries.md", {"error-std", "error-anyhow"}),
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--prepare", action="store_true")
    p.add_argument("--locks", type=Path, help="directory with tokio/serde/errors Cargo.lock files")
    args = p.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    report = {"documents": {}, "commands": [], "cases": []}

    def command(argv, cwd):
        result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=240)
        record = {"argv": list(map(str, argv)), "cwd": str(cwd), "returncode": result.returncode,
                  "stdout": result.stdout, "stderr": result.stderr}
        report["commands"].append(record)
        (work / "evidence.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        if result.returncode:
            raise RuntimeError(record)
        return result

    for tool in ("rustc", "cargo"):
        command([tool, "--version"], work)
    for group, (filename, expected) in SOURCES.items():
        path = ROOT / "11-rust-cross-platform/reference/library-guides" / filename
        source = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        report["documents"][group] = {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        cases = re.findall(r"<!-- rust-ecosystem: ([a-z-]+) -->\s*```rust\s*\n(.*?)^```", source, re.M | re.S)
        assert len(cases) == len(expected) and {name for name, _ in cases} == expected, filename
        manifest = re.findall(r"^```toml\s*\n(.*?)^```", source, re.M | re.S)[0]
        dest = work / group
        (dest / "src/bin").mkdir(parents=True, exist_ok=True)
        # Remove only previously generated case files; reject unexpected stale bins.
        existing = {f.stem for f in (dest / "src/bin").glob("*.rs")}
        assert existing <= expected, "Use a dedicated clean work directory"
        (dest / "Cargo.toml").write_text(
            f'[package]\nname = "reference-{group}"\nversion = "0.1.0"\nedition = "2024"\n' + manifest,
            encoding="utf-8")
        for name, code in cases:
            (dest / "src/bin" / (name + ".rs")).write_text(code, encoding="utf-8")
        if args.locks:
            shutil.copyfile(args.locks / group / "Cargo.lock", dest / "Cargo.lock")
        if args.prepare:
            if not (dest / "Cargo.lock").exists():
                command(["cargo", "generate-lockfile"], dest)
            command(["cargo", "fetch", "--locked"], dest)
            print("PREPARED", group, flush=True)
            continue
        command(["cargo", "build", "--offline", "--locked", "--bins"], dest)
        for name, code in cases:
            result = command([str(dest / "target/debug" / name)], dest)
            expected_output = name + ": ok\n"
            if name == "error-std":
                expected_output = "  - 加载 db/users.json 失败\n  - 未找到: users.json\n" + expected_output
            assert result.stdout == expected_output, (name, result.stdout)
            report["cases"].append({"id": name, "document": relative,
                "code_sha256": hashlib.sha256(code.encode()).hexdigest(), "status": "PASS"})
            print("PASS", name, flush=True)
    report["scope"] = "10 named complete programs only; unmarked snippets and framework integration are outside this run"
    (work / "evidence.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.prepare:
        assert len(report["cases"]) == 10
        print("10/10 passed", flush=True)


if __name__ == "__main__":
    main()
