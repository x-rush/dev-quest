#!/usr/bin/env python3
"""dev-quest 代码块全量验证主驱动：读 manifest.jsonl，产出 results.jsonl

用法: python3 verify.py [REPO_ROOT]
默认: REPO_ROOT=仓库根（脚本上三级目录）
依赖: manifest.jsonl（由 extract_blocks.py 产出）；/tmp/dq-verify/ 下:
  - parsego/parsego          Go 语法 runner（三级包装梯）
  - ts-02/ ts-03/ ts-04/ ts-09/  四个 tsc 项目（模块技术基线 pin 版本）
  - venv/                    pyyaml（yaml 解析用）

层级:
  L1 语法层: go(包装梯)/ts(tsc)/php(php -l)/python(ast)/kotlin(kotlinc 包装梯)
            swift(swiftc -parse)/java(jshell)/bash(bash -n 绝不执行)
            yaml/json/jsonc/toml(解析器)/protobuf(protoc)
  L2 运行层: go(has_package+has_func_main → go run/vet)、python(三道闸)、php(危险 token 过滤)
其余语言 → status=SKIP_NOTOOL（dockerfile/nginx/blade 等交 L3 目检）
"""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.dirname(HERE)))
MANIFEST = os.path.join(HERE, "manifest.jsonl")
RESULTS = os.path.join(HERE, "results.jsonl")
WORK = "/tmp/dq-verify"
BLOCKS = os.path.join(WORK, "blocks")
PARSEGO = os.path.join(WORK, "parsego", "parsego")
SWIFTC = os.path.expanduser(
    "~/.asdf/installs/swift/6.3.3/versions/6.3.3/usr/bin/swiftc")

TS_PROJECT = {
    "02-nextjs-frontend": "ts-02",
    "03-tanstack-stack": "ts-03",
    "04-multiplatform-apps": "ts-04",
    "09-nodejs-backend": "ts-09",
}
GO_THIRD_PARTY_PREFIXES = (
    "github.com/", "gorm.io/", "google.golang.org/", "go.opentelemetry.io/",
    "go.uber.org/", "golang.org/x/", "go.mongodb.org/", "gopkg.in/",
    "firebase.google.com/",
)
PHP_DANGER = re.compile(
    r"\b(exec|shell_exec|system|passthru|proc_open|popen|unlink|rmdir|"
    r"file_put_contents|fwrite|eval|assert|include|require|include_once"
    r"|require_once|fopen|file_get_contents)\s*[\(\s]", re.M)
PY_RUN_WHITELIST = {
    "re", "json", "math", "random", "datetime", "itertools", "functools",
    "collections", "typing", "dataclasses", "enum", "abc", "string",
    "textwrap", "heapq", "bisect", "copy", "decimal", "fractions",
    "statistics", "operator", "time", "calendar", "uuid", "base64",
    "hashlib", "pathlib", "os.path", "sys", "struct", "zlib", "array",
    "queue", "types", "contextlib", "secrets", "weakref", "logging",
    "asyncio", "doctest", "glob", "fnmatch", "zipfile", "gzip", "csv",
    "io", "abc", "inspect", "warnings", "traceback", "platform",
}
PY_DANGER_CALLS = re.compile(
    r"\b(eval|exec|compile|__import__|input|globals|locals|breakpoint|open)\s*\(")
PY_DANGER_MODULES = re.compile(
    r"^\s*(?:import|from)\s+(subprocess|socket|http|urllib|requests|httpx|shutil"
    r"|pickle|multiprocessing|ctypes|signal|webbrowser)\b", re.M)
EXT = {"go": "go", "php": "php", "python": "py", "kotlin": "kt", "swift": "swift",
       "java": "java", "bash": "sh", "yaml": "yaml", "yml": "yaml",
       "json": "json", "jsonc": "json", "json5": "json", "toml": "toml",
       "protobuf": "proto", "ts": "ts", "tsx": "tsx", "typescript": "ts",
       "js": "js", "jsx": "jsx", "javascript": "js"}
TS_LANGS = {"ts", "tsx", "typescript", "js", "jsx", "javascript"}


def load_manifest():
    recs = []
    with open(MANIFEST, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if not r.get("skipped"):
                recs.append(r)
    return recs


def block_path(b):
    ext = EXT.get(b["lang"], "frag")
    return os.path.join(BLOCKS, f"b{b['id']}.{ext}")


def write_blocks(recs):
    os.makedirs(BLOCKS, exist_ok=True)
    for b in recs:
        with open(block_path(b), "w", encoding="utf-8") as f:
            f.write(b.get("content", ""))


def run(cmd, timeout=60, cwd=None, stdin_text=None, env=None):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           cwd=cwd, input=stdin_text, env=env)
        return p.returncode, (p.stderr or p.stdout or "")[:600]
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except FileNotFoundError:
        return 127, "tool-not-found: " + cmd[0]


# ---------------- L1 ----------------

def verify_go_l1(recs):
    flist = os.path.join(WORK, "golist.txt")
    with open(flist, "w") as f:
        for b in recs:
            f.write(block_path(b) + "\n")
    try:
        p = subprocess.run([PARSEGO, flist], capture_output=True, text=True,
                           timeout=600)
        lines = p.stdout.splitlines()
    except subprocess.TimeoutExpired:
        lines = []
    results = {}
    for line in lines:
        r = json.loads(line)
        results[os.path.basename(r["file"])] = (r["ok"], r.get("err", ""))
    for b in recs:
        key = os.path.basename(block_path(b))
        if key not in results:
            results[key] = (False, "parsego no-output")
    return results


def verify_phplike_l1(recs, results):
    for b in recs:
        src = open(block_path(b), encoding="utf-8").read()
        if "<?php" not in src:
            src = "<?php\n" + src
        tmp = os.path.join(WORK, "tmp.php")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(src)
        rc, err = run(["php", "-l", tmp], timeout=30)
        ok = rc == 0
        detail = "" if ok else err.strip().splitlines()[0] if err.strip() else f"rc={rc}"
        results[b["id"]]["l1"] = {"status": "PASS" if ok else "FAIL", "detail": detail}


def verify_python_l1(recs, results):
    for b in recs:
        src = open(block_path(b), encoding="utf-8").read()
        try:
            ast.parse(src)
            results[b["id"]]["l1"] = {"status": "PASS", "detail": ""}
        except SyntaxError as e:
            results[b["id"]]["l1"] = {"status": "FAIL",
                                      "detail": f"line {e.lineno}: {e.msg}"}


def verify_bash_l1(recs, results):
    for b in recs:
        rc, err = run(["bash", "-n", block_path(b)], timeout=30)
        ok = rc == 0
        detail = "" if ok else (err.strip().splitlines() or [""])[-1]
        results[b["id"]]["l1"] = {"status": "PASS" if ok else "FAIL", "detail": detail}


def wrap_kotlin(src):
    """kotlin 片段包装：import/注释保留原位，其余代码包进 fun _s(){}"""
    lines = src.splitlines()
    head, body = [], []
    for ln in lines:
        s = ln.strip()
        if s.startswith("import ") or s.startswith("package "):
            head.append(ln)
        else:
            body.append(ln)
    return "\n".join(head) + "\n\nfun _s() {\n" + "\n".join(body) + "\n}\n"


def verify_kotlin_l1(recs, results):
    def work(b):
        src = open(block_path(b), encoding="utf-8").read()
        cand = [src, wrap_kotlin(src)]
        last = ""
        for i, c in enumerate(cand):
            tmp = os.path.join(WORK, f"kt_{b['id']}.kt")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(c)
            rc, err = run(["kotlinc", "-nowarn", tmp, "-d", WORK],
                          timeout=180)
            if rc == 0:
                return {"status": "PASS", "detail": ""}
            msgs = [l for l in err.splitlines() if "error" in l.lower()]
            last = (msgs[0] if msgs else (err.strip().splitlines() or [""])[-1]
                    if err.strip() else f"rc={rc}")
        return {"status": "FAIL", "detail": last[:300]}

    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(work, b): b for b in recs}
        for fu in as_completed(futs):
            results[futs[fu]["id"]]["l1"] = fu.result()


def verify_swift_l1(recs, results):
    def work(b):
        # -swift-version 6：仓库基线 Swift 6；默认 Swift 5 模式对裸斜杠正则字面量误报
        rc, err = run([SWIFTC, "-swift-version", "6", "-parse", block_path(b)], timeout=60)
        if rc == 0:
            return {"status": "PASS", "detail": ""}
        msgs = [l for l in err.splitlines() if "error" in l.lower()]
        detail = msgs[0] if msgs else (err.strip().splitlines() or [""])[-1] if err.strip() else "rc=%d" % rc
        return {"status": "FAIL", "detail": detail[:300]}

    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(work, b): b for b in recs}
        for fu in as_completed(futs):
            results[futs[fu]["id"]]["l1"] = fu.result()


def verify_java_l1(recs, results):
    def work(b):
        src = open(block_path(b), encoding="utf-8").read()
        lines = [l for l in src.splitlines()
                 if not l.strip().startswith("package ")]
        rc, err = run(["jshell", "-q", "-"], timeout=60,
                      stdin_text="\n".join(lines) + "\n/exit\n")
        if rc == 0 and "Error" not in err:
            return {"status": "PASS", "detail": ""}
        lines_e = err.splitlines()
        errs = [i for i, l in enumerate(lines_e)
                if "Error" in l or "错误" in l]
        if errs:
            i = errs[0]
            detail = " ".join(x.strip() for x in lines_e[i:i + 2])
        else:
            detail = "jshell rc=%d" % rc
        return {"status": "FAIL", "detail": detail[:300]}

    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(work, b): b for b in recs}
        for fu in as_completed(futs):
            results[futs[fu]["id"]]["l1"] = fu.result()


def _parse_jsonc(src):
    out = []
    in_str, esc, in_cm = False, False, False
    i = 0
    while i < len(src):
        c = src[i]
        if in_cm:
            if c == "*" and i + 1 < len(src) and src[i + 1] == "/":
                in_cm = False
                i += 2
                out.append("\n")
                continue
            if c == "\n":
                out.append(c)
            i += 1
            continue
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
        elif c == "/" and i + 1 < len(src) and src[i + 1] == "/":
            # 行注释：跳到行尾即可，不得设置 in_cm（真值会让下一轮误入块注释分支吞掉全部后续内容）
            j = src.find("\n", i)
            i = j if j >= 0 else len(src)
            out.append("\n")
            continue
        elif c == "/" and i + 1 < len(src) and src[i + 1] == "*":
            in_cm = True
            i += 2
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def verify_datafmt_l1(recs, results):
    import yaml
    try:
        import tomllib
    except ImportError:
        tomllib = None
    for b in recs:
        lang = b["lang"]
        src = open(block_path(b), encoding="utf-8").read()
        try:
            if lang == "yaml":
                list(yaml.safe_load_all(src))
            elif lang in ("json", "jsonc", "json5"):
                # json 块允许首行 `// 文件名` 注释惯例：纯解析失败则按 jsonc 剥注释重试
                try:
                    json.loads(src)
                except Exception:
                    if "//" in src or "/*" in src:
                        json.loads(_parse_jsonc(src))
                    else:
                        raise
            elif lang == "toml":
                if tomllib is None:
                    results[b["id"]]["l1"] = {"status": "SKIP_NOTOOL",
                                              "detail": "python<3.11 no tomllib"}
                    continue
                tomllib.loads(src)
            results[b["id"]]["l1"] = {"status": "PASS", "detail": ""}
        except Exception as e:
            results[b["id"]]["l1"] = {"status": "FAIL", "detail": str(e)[:300]}


def verify_protobuf_l1(recs, results):
    for b in recs:
        tmp = os.path.join(WORK, f"pb_{b['id']}.proto")
        shutil.copy(block_path(b), tmp)
        rc, err = run(["protoc", f"-I{WORK}", f"--descriptor_set_out=/dev/null",
                       os.path.basename(tmp)], timeout=30, cwd=WORK)
        ok = rc == 0
        results[b["id"]]["l1"] = {"status": "PASS" if ok else "FAIL",
                                  "detail": "" if ok else err.strip().splitlines()[0][:300]
                                  if err.strip() else f"rc={rc}"}


def verify_ts_l1(recs, results, log):
    groups = {}
    for b in recs:
        proj = TS_PROJECT.get(b["module"], "ts-09")
        groups.setdefault(proj, []).append(b)
    for proj, items in sorted(groups.items()):
        proj_dir = os.path.join(WORK, proj)
        for i in range(0, len(items), 60):
            batch = items[i:i + 60]
            src_dir = os.path.join(proj_dir, "src")
            if os.path.exists(src_dir):
                shutil.rmtree(src_dir)
            os.makedirs(src_dir, exist_ok=True)
            manifest_lines = []
            for b in batch:
                ext = "tsx" if b["lang"] in ("tsx", "jsx") else "ts"
                name = f"b{b['id']}.{ext}"
                with open(os.path.join(src_dir, name), "w",
                          encoding="utf-8") as f:
                    f.write(b.get("content", ""))
                manifest_lines.append({"id": b["id"], "file": name})
            with open(os.path.join(src_dir, "_batch.json"), "w") as f:
                json.dump(manifest_lines, f)
            try:
                p = subprocess.run(["npx", "tsc", "-p", proj_dir, "--noEmit",
                                    "--pretty", "false"], capture_output=True,
                                   text=True, timeout=600, cwd=proj_dir)
                rc, err = p.returncode, (p.stderr or "") + (p.stdout or "")
            except subprocess.TimeoutExpired:
                rc, err = 124, "tsc timeout"
            if rc == 0:
                for b in batch:
                    results[b["id"]]["l1"] = {"status": "PASS", "detail": ""}
                continue
            per_block = {m["id"]: m["file"] for m in manifest_lines}
            errs = {}
            for line in err.splitlines():
                m = re.match(r"^(?:src/)([\w.]+)\((\d+),\d+\):\s*error\s+(TS\d+):(.*)$",
                             line)
                if m:
                    fname, ecode, msg = m.group(1), m.group(3), m.group(4).strip()
                    bid = next((k for k, v in per_block.items() if v == fname),
                               None)
                    if bid:
                        errs.setdefault(bid, []).append(f"{ecode}: {msg}")
            for b in batch:
                if b["id"] in errs:
                    results[b["id"]]["l1"] = {"status": "FAIL",
                                              "detail": " | ".join(errs[b["id"]][:3])[:300]}
                else:
                    results[b["id"]]["l1"] = {"status": "PASS", "detail": ""}
            log(f"ts {proj} batch {i//60+1}: rc={rc}, {len(errs)}/{len(batch)} 块有错")
        shutil.rmtree(src_dir, ignore_errors=True)


# ---------------- L2 ----------------

def verify_go_l2(recs, results, log):
    proj = os.path.join(WORK, "goproj")
    for b in recs:
        f = b.get("flags", {})
        if not (f.get("has_package") and f.get("has_func_main")):
            continue
        src = b["content"]
        imports = re.findall(r'^\s*"([\w/.-]+)"', src, re.M)
        third = [i for i in imports if i.startswith(GO_THIRD_PARTY_PREFIXES)]
        name = f"b{b['id']}"
        d = os.path.join(WORK, "gorun", name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "main.go"), "w", encoding="utf-8") as fh:
            fh.write(src)
        if third:
            # 第三方 import：写入 goproj 子目录做编译级验证（go vet 单包）
            pkg = f"v_{name}"
            dp = os.path.join(proj, pkg)
            os.makedirs(dp, exist_ok=True)
            with open(os.path.join(dp, "main.go"), "w", encoding="utf-8") as fh:
                fh.write(src)
            rc, err = run(["go", "vet", f"./{pkg}/"], timeout=120, cwd=proj)
            shutil.rmtree(dp, ignore_errors=True)
            results[b["id"]]["l2"] = {
                "status": "PASS" if rc == 0 else "FAIL",
                "detail": "" if rc == 0 else (err.strip().splitlines() or [""])[-1][:300]}
            continue
        rc, err = run(["go", "run", "."], timeout=15, cwd=d,
                      env={**os.environ, "GO111MODULE": "auto"})
        if rc == 0 or rc == 124:
            results[b["id"]]["l2"] = {"status": "PASS" if rc == 0 else "TIMEOUT",
                                      "detail": ""}
        else:
            results[b["id"]]["l2"] = {"status": "FAIL",
                                      "detail": (err.strip().splitlines() or [""])[-1][:300]}
    log("go L2 done")


def verify_python_l2(recs, results):
    for b in recs:
        src = b["content"]
        mods = []
        for m in re.finditer(r"^\s*(?:import\s+([\w.,\s]+)|from\s+([\w.]+))",
                             src, re.M):
            for part in (m.group(1) or "").split(","):
                p = part.strip().split()[0] if part.strip() else ""
                if p:
                    mods.append(p.split(".")[0])
            if m.group(2):
                mods.append(m.group(2).split(".")[0])
        bad_mods = [m for m in mods if m not in PY_RUN_WHITELIST]
        if bad_mods:
            results[b["id"]]["l2"] = {"status": "GATED", "detail": "非白名单 import: " + ",".join(bad_mods)}
            continue
        if PY_DANGER_MODULES.search(src):
            results[b["id"]]["l2"] = {"status": "GATED", "detail": "危险模块 import"}
            continue
        if PY_DANGER_CALLS.search(src):
            results[b["id"]]["l2"] = {"status": "GATED", "detail": "危险调用"}
            continue
        d = tempfile.mkdtemp(prefix="pyrun_")
        with open(os.path.join(d, "main.py"), "w", encoding="utf-8") as f:
            f.write(src)
        rc, err = run([sys.executable, "-I", "main.py"], timeout=10, cwd=d,
                      env={**os.environ, "PYTHONSAFEPATH": "1"})
        shutil.rmtree(d, ignore_errors=True)
        if rc == 0:
            results[b["id"]]["l2"] = {"status": "PASS", "detail": ""}
        elif rc == 124:
            results[b["id"]]["l2"] = {"status": "TIMEOUT", "detail": "timeout 10s"}
        else:
            results[b["id"]]["l2"] = {"status": "FAIL",
                                      "detail": (err.strip().splitlines() or [""])[-1][:300]}


def verify_php_l2(recs, results):
    for b in recs:
        src = b["content"]
        if "<?php" not in src:
            results[b["id"]]["l2"] = {"status": "GATED", "detail": "非完整脚本"}
            continue
        if PHP_DANGER.search(src):
            results[b["id"]]["l2"] = {"status": "GATED", "detail": "危险 token"}
            continue
        if "PHPUnit" in src or "extends TestCase" in src:
            results[b["id"]]["l2"] = {"status": "GATED", "detail": "PHPUnit 测试类"}
            continue
        d = tempfile.mkdtemp(prefix="phprun_")
        with open(os.path.join(d, "main.php"), "w", encoding="utf-8") as f:
            f.write(src)
        rc, err = run(["php", os.path.join(d, "main.php")], timeout=10, cwd=d)
        shutil.rmtree(d, ignore_errors=True)
        if rc == 0:
            results[b["id"]]["l2"] = {"status": "PASS", "detail": ""}
        elif rc == 124:
            results[b["id"]]["l2"] = {"status": "TIMEOUT", "detail": "timeout 10s"}
        else:
            results[b["id"]]["l2"] = {"status": "FAIL",
                                      "detail": (err.strip().splitlines() or [""])[-1][:300]}


# ---------------- main ----------------

def main():
    args = sys.argv[1:]
    root = next((a for a in args if not a.startswith("--")), None)
    if root:
        globals()["ROOT"] = root
    langs_filter = None
    sample = 0
    if "--langs" in args:
        langs_filter = set(args[args.index("--langs") + 1].split(","))
    if "--sample" in args:
        sample = int(args[args.index("--sample") + 1])
    log = lambda m: print(m, flush=True)
    global RESULTS
    if sample:
        RESULTS += ".sample"
    recs = load_manifest()
    if langs_filter:
        recs = [b for b in recs if b["lang"] in langs_filter]
    if sample:
        by = {}
        for b in recs:
            by.setdefault(b["lang"], []).append(b)
        recs = [b for v in by.values() for b in v[:sample]]
    log(f"代码块总数: {len(recs)}")
    write_blocks(recs)

    by_lang = {}
    for b in recs:
        by_lang.setdefault(b["lang"], []).append(b)

    results = {b["id"]: {"id": b["id"], "lang": b["lang"], "module": b["module"],
                         "file": b["file"], "start": b["start"], "end": b["end"],
                         "l1": None, "l2": None} for b in recs}

    # L1
    if "go" in by_lang:
        log(f"L1 go: {len(by_lang['go'])}")
        go_res = verify_go_l1(by_lang["go"])
        for k, (ok, e) in go_res.items():
            bid = k[1:-3]  # b{id}.go
            if bid in results:
                results[bid]["l1"] = {"status": "PASS" if ok else "FAIL", "detail": e}

    phplike = by_lang.get("php", [])
    if phplike:
        log(f"L1 php: {len(phplike)}")
        verify_phplike_l1(phplike, results)

    if "python" in by_lang:
        log(f"L1 python: {len(by_lang['python'])}")
        verify_python_l1(by_lang["python"], results)

    if "bash" in by_lang:
        log(f"L1 bash: {len(by_lang['bash'])}")
        verify_bash_l1(by_lang["bash"], results)

    if "kotlin" in by_lang:
        log(f"L1 kotlin: {len(by_lang['kotlin'])}")
        verify_kotlin_l1(by_lang["kotlin"], results)

    if "swift" in by_lang:
        log(f"L1 swift: {len(by_lang['swift'])}")
        verify_swift_l1(by_lang["swift"], results)

    if "java" in by_lang:
        log(f"L1 java: {len(by_lang['java'])}")
        verify_java_l1(by_lang["java"], results)

    datafmt = [b for b in recs if b["lang"] in ("yaml", "json", "jsonc", "json5", "toml")]
    if datafmt:
        log(f"L1 datafmt: {len(datafmt)}")
        verify_datafmt_l1(datafmt, results)

    if "protobuf" in by_lang:
        log(f"L1 protobuf: {len(by_lang['protobuf'])}")
        verify_protobuf_l1(by_lang["protobuf"], results)

    tslangs = [b for b in recs if b["lang"] in TS_LANGS]
    if tslangs:
        log(f"L1 ts族: {len(tslangs)}")
        verify_ts_l1(tslangs, results, log)

    # 其余语言 → SKIP_NOTOOL
    handled = {"go", "php", "python", "bash", "kotlin", "swift", "java",
               "yaml", "json", "jsonc", "json5", "toml", "protobuf"} | TS_LANGS
    for b in recs:
        if results[b["id"]]["l1"] is None:
            if b["lang"] in handled:
                results[b["id"]]["l1"] = {"status": "MISS", "detail": "L1 未覆盖"}
            else:
                results[b["id"]]["l1"] = {"status": "SKIP_NOTOOL",
                                          "detail": f"lang={b['lang']} 无机器验证器"}

    # L2
    if "go" in by_lang:
        verify_go_l2(by_lang["go"], results, log)
    if "python" in by_lang:
        log("L2 python")
        verify_python_l2(by_lang["python"], results)
    if "php" in by_lang:
        log("L2 php")
        verify_php_l2(by_lang["php"], results)

    with open(RESULTS, "w", encoding="utf-8") as f:
        for b in recs:
            f.write(json.dumps(results[b["id"]], ensure_ascii=False) + "\n")

    # 汇总
    from collections import Counter
    c1 = Counter(r["l1"]["status"] for r in results.values())
    c2 = Counter(r["l2"]["status"] for r in results.values() if r["l2"])
    log(f"L1 终态: {dict(c1)}")
    log(f"L2 终态: {dict(c2)}")
    log(f"results: {RESULTS}")
    assert len(results) == len(recs), "results 与 manifest 数量不一致"


if __name__ == "__main__":
    main()
