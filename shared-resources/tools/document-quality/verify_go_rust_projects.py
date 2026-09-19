#!/usr/bin/env python3
"""Extract four reviewed documents verbatim, build and exercise their programs.

Run inside the documented disposable toolchain container. --prepare downloads and
locks Rust dependencies only; the default verification uses cargo --offline.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCS = {
    "go-cli": "01-go-backend/projects/00-stdlib-todo-cli.md",
    "rust-cli": "11-rust-cross-platform/projects/01-cli-tool.md",
    "rust-counter": "11-rust-cross-platform/reference/library-guides/15-standard-library-map.md",
    "rust-types": "11-rust-cross-platform/reference/language-concepts/10-standard-types-and-methods.md",
}


def extract(path, language):
    return re.findall(r"^```" + language + r"\s*\n(.*?)^```\s*$", path.read_text(encoding="utf-8"), re.M | re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True, help="dedicated disposable build directory")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--lockfile", type=Path, help="reuse the published Cargo.lock rather than resolve new versions")
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    evidence = {"documents": {}, "commands": []}
    for name, relative in DOCS.items():
        path = ROOT / relative
        evidence["documents"][name] = {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        dest = work / name
        dest.mkdir(exist_ok=True)
        language = "go" if name == "go-cli" else "rust"
        blocks = extract(path, language)
        assert len(blocks) == {"go-cli": 2, "rust-cli": 4, "rust-counter": 1, "rust-types": 1}[name], (name, len(blocks))
        if name == "go-cli":
            for filename, code in zip(["main.go", "main_test.go"], blocks):
                (dest / filename).write_text(code, encoding="utf-8")
            # Equivalent to the document's go mod init command, executed below.
        elif name == "rust-cli":
            (dest / "src").mkdir(exist_ok=True)
            (dest / "src/main.rs").write_text("\n".join(blocks), encoding="utf-8")
            manifests = extract(path, "toml")
            assert len(manifests) == 1
            (dest / "Cargo.toml").write_text(manifests[0], encoding="utf-8")
        else:
            (dest / "main.rs").write_text(blocks[0], encoding="utf-8")

    def command(argv, cwd, *, code=0, stdout=None, contains=None):
        result = subprocess.run(argv, cwd=cwd, text=True, encoding="utf-8", capture_output=True, timeout=240)
        entry = {"argv": [str(x) for x in argv], "cwd": str(cwd), "returncode": result.returncode,
                 "stdout": result.stdout, "stderr": result.stderr}
        evidence["commands"].append(entry)
        (work / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        assert result.returncode == code, entry
        if stdout is not None:
            assert result.stdout == stdout, entry
        if contains is not None:
            assert contains in result.stdout + result.stderr, entry
        print("PASS", " ".join(str(x) for x in argv), flush=True)
        return result

    rust_cli = work / "rust-cli"
    if args.lockfile:
        shutil.copyfile(args.lockfile, rust_cli / "Cargo.lock")
    if args.prepare:
        if not (rust_cli / "Cargo.lock").exists():
            command(["cargo", "generate-lockfile"], rust_cli)
        command(["cargo", "fetch", "--locked"], rust_cli)
        return

    for runtime in [["go", "version"], ["rustc", "--version"], ["cargo", "--version"]]:
        command(runtime, work)
    go = work / "go-cli"
    if not (go / "go.mod").exists():
        command(["go", "mod", "init", "example.com/todo-cli"], go)
    command(["go", "test", "-count=1", "./..."], go)
    command(["go", "build", "-o", "todo-cli", "."], go)
    command([str(go / "todo-cli"), "add", "买牛奶"], go, stdout="已添加 #1: 买牛奶\n")
    command([str(go / "todo-cli"), "demo"], go, stdout="#2 写 Go 测试\n")
    command([str(go / "todo-cli"), "add", ""], go, code=1, stdout="", contains="标题不能为空")
    command([str(go / "todo-cli"), "demo", "extra"], go, code=1, stdout="", contains="不接受额外参数")

    command(["cargo", "test", "--offline", "--locked"], rust_cli, contains="7 passed")
    command(["cargo", "build", "--offline", "--locked"], rust_cli)
    executable = rust_cli / "target/debug/rtask"
    # Isolated fresh data directory on each execution; never use a user's tasks.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="rtask-cases-", dir=work) as tmp:
        data = Path(tmp)
        command([str(executable), "list"], data, stdout="（暂无任务）\n")
        command([str(executable), "add", "  学习 Rust  "], data, stdout="已添加任务 #1: 学习 Rust\n")
        command([str(executable), "list"], data, contains="#1")
        command([str(executable), "done", "1"], data, stdout="已完成任务 #1: 学习 Rust\n")
        command([str(executable), "list", "--pending"], data, stdout="（暂无任务）\n")
        original = (data / "rtask.json").read_bytes()
        for argv, diagnostic in [(["add", " "], "标题不能为空"), (["done", "99"], "不存在")]:
            command([str(executable), *argv], data, code=1, stdout="", contains=diagnostic)
            assert (data / "rtask.json").read_bytes() == original
        command([str(executable), "list", "--file", "other.json"], data, stdout="（暂无任务）\n")
        command([str(executable), "rm", "1"], data, stdout="已删除任务 #1\n")
        assert json.loads((data / "rtask.json").read_text()) == []
        for raw in ['{', '[{"id":1,"text":"x","done":false},{"id":1,"text":"y","done":false}]',
                    '[{"id":4294967295,"text":"x","done":false}]']:
            (data / "rtask.json").write_text(raw, encoding="utf-8")
            command([str(executable), "add", "safe"], data, code=1, stdout="")
            assert (data / "rtask.json").read_text(encoding="utf-8") == raw
        command([str(executable), "done", "abc"], data, code=2, stdout="", contains="invalid value")

    for name in ["rust-counter", "rust-types"]:
        dest = work / name
        command(["rustc", "--edition", "2024", "main.rs", "-o", "example"], dest)
        executable = dest / "example"
        if name == "rust-types":
            command([str(executable)], dest, stdout="[2, 7, 10]\ntrue\n")
            command(["rustc", "--edition", "2024", "--test", "main.rs", "-o", "tests"], dest)
            command([str(dest / "tests")], dest, contains="4 passed")
        else:
            for filename, data, expected in [("normal.txt", b"read\n \t\ntest\n", "2\n"), ("empty.txt", b"", "0\n")]:
                (dest / filename).write_bytes(data)
                command([str(executable), filename], dest, stdout=expected)
            (dest / "invalid.txt").write_bytes(b"\xff\n")
            for argv in [[], ["missing.txt"], ["invalid.txt"], ["normal.txt", "extra"]]:
                command([str(executable), *argv], dest, code=1, stdout="")
    evidence["status"] = "passed"
    lock = rust_cli / "Cargo.lock"
    evidence["cargo_lock_sha256"] = hashlib.sha256(lock.read_bytes()).hexdigest()
    (work / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(evidence['commands'])} commands passed; evidence: {work / 'evidence.json'}")


if __name__ == "__main__":
    main()
