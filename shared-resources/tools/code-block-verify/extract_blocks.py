#!/usr/bin/env python3
"""dev-quest 全仓代码块提取器：扫描全部 Markdown 围栏代码块，输出 manifest.jsonl

用法: python3 extract_blocks.py [REPO_ROOT] [OUTPUT_JSONL]
默认: REPO_ROOT=仓库根, OUTPUT=脚本同目录 manifest.jsonl

排除目录: refactor-archives（历史归档）/.git/.remember/node_modules
"""
import hashlib
import json
import os
import re
import sys

SKIP_DIRS = {"refactor-archives", ".git", ".remember", "node_modules"}
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")

IMPORT_RES = {
    "go_import_line": re.compile(r"^\s*\"([\w/.-]+)\"", re.M),
    "python": re.compile(r"^\s*(?:import\s+([\w.,\s]+)|from\s+([\w.]+)\s+import)", re.M),
    "kotlin": re.compile(r"^\s*import\s+([\w.*]+)", re.M),
    "swift": re.compile(r"^\s*import\s+(\w+)", re.M),
    "java": re.compile(r"^\s*import\s+([\w.*]+)", re.M),
}
PY_DANGER_CALLS = re.compile(
    r"\b(eval|exec|compile|__import__|input|globals|locals|breakpoint|open)\s*\(")
PY_DANGER_MODULES = re.compile(
    r"^\s*(?:import|from)\s+(subprocess|socket|http|urllib|requests|httpx|shutil|pickle"
    r"|multiprocessing|ctypes|signal|webbrowser)\b", re.M)
TS_IMPORT = re.compile(
    r"^\s*import\s+(?:type\s+)?(?:\{[^}]*\}|[\w*]+|[\w{},*\s]+)\s+from\s+['\"]([^'\"]+)['\"]", re.M)
DECL_KEYWORDS = {
    "go": ("func ", "type ", "var ", "const "),
    "kotlin": ("fun ", "class ", "val ", "var ", "object ", "interface ", "@Composable"),
    "swift": ("func ", "class ", "struct ", "enum ", "protocol ", "extension ",
              "let ", "var ", "@"),
    "java": ("public ", "private ", "class ", "record ", "interface ", "void ", "static "),
}
# 纯展示类围栏（无机器验证价值，标记 skipped 供覆盖统计）
NONCODE_LANGS = {"mermaid", "markdown", "text", "txt", "output", "console",
                 "plaintext", ""}


def first_code_token(body: str, keywords) -> bool:
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("//") or s.startswith("/*") or s.startswith("*"):
            continue
        return s.startswith(keywords)
    return False


def extract_file(path: str):
    """返回该文件的 blocks 列表。手写状态机，支持嵌套围栏（闭合标记长度>=开启）。"""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []
    blocks, headings, stack = [], [], []
    buf, lang, info_raw, start, pre_lines = [], "", "", 0, []
    in_code = False
    for lineno, line in enumerate(lines, 1):
        m = FENCE_RE.match(line)
        if not in_code and m:
            info = m.group(2).strip()
            token = info.split()[0] if info else ""
            token = re.sub(r"\{.*\}$", "", token).lower()
            if token in NONCODE_LANGS:
                stack.append(len(m.group(1)))
                buf, lang, info_raw, start = [], token or "unlabeled", info, lineno
                in_code = True
                continue
            in_code = True
            stack.append(len(m.group(1)))
            buf, lang, info_raw, start = [], token, info, lineno
            pre_lines = [l.rstrip() for l in lines[max(0, lineno - 9):lineno - 1]]
        elif in_code and m and len(m.group(1)) >= stack[-1] and not m.group(2).strip():
            stack.pop()
            if not stack:
                in_code = False
                content = "".join(buf)
                if lang in NONCODE_LANGS:
                    blocks.append({
                        "skipped": True, "lang": lang, "info_raw": info_raw,
                        "start": start, "end": lineno,
                        "headings": list(headings),
                    })
                    buf = []
                    continue
                flags = {}
                if lang == "go":
                    flags["has_package"] = bool(re.search(r"^\s*package\s+\w+", content, re.M))
                    flags["has_func_main"] = bool(re.search(r"^\s*func\s+main\s*\(", content, re.M))
                    flags["imports"] = IMPORT_RES["go_import_line"].findall(content)
                    flags["starts_with_decl"] = first_code_token(content, DECL_KEYWORDS["go"])
                elif lang == "python":
                    flags["imports"] = [a or b for a, b in IMPORT_RES["python"].findall(content)]
                    flags["danger_calls"] = PY_DANGER_CALLS.findall(content)
                    flags["danger_modules"] = PY_DANGER_MODULES.findall(content)
                elif lang in ("ts", "tsx", "typescript", "js", "jsx", "javascript"):
                    flags["import_specifiers"] = TS_IMPORT.findall(content)
                elif lang == "kotlin":
                    flags["imports"] = IMPORT_RES["kotlin"].findall(content)
                    flags["starts_with_decl"] = first_code_token(content, DECL_KEYWORDS["kotlin"])
                elif lang == "swift":
                    flags["imports"] = IMPORT_RES["swift"].findall(content)
                    flags["starts_with_decl"] = first_code_token(content, DECL_KEYWORDS["swift"])
                elif lang == "java":
                    flags["imports"] = IMPORT_RES["java"].findall(content)
                    flags["starts_with_decl"] = first_code_token(content, DECL_KEYWORDS["java"])
                elif lang == "php":
                    flags["has_open_tag"] = "<?php" in content
                after = [l.rstrip() for l in lines[lineno:lineno + 4]]
                blocks.append({
                    "skipped": False, "lang": lang, "info_raw": info_raw,
                    "start": start, "end": lineno, "content": content,
                    "headings": list(headings), "before": pre_lines, "after": after,
                    "flags": flags,
                })
                buf = []
        elif in_code:
            buf.append(line)
        else:
            hm = HEADING_RE.match(line)
            if hm:
                level = len(hm.group(1))
                headings = [h for h in headings if h[0] < level]
                headings.append((level, hm.group(2).strip()))
    if in_code and stack:
        # 文件尾未闭合围栏：仍收块，标记 unterminated 供 L3 目检
        blocks.append({
            "skipped": lang in NONCODE_LANGS, "lang": lang or "unlabeled",
            "info_raw": info_raw, "start": start, "end": len(lines),
            "content": "".join(buf), "unterminated": True,
            "headings": list(headings),
        })
    return blocks


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "manifest.jsonl")
    seq = 0
    n_code, n_skip = 0, 0
    index = {}
    with open(out, "w", encoding="utf-8") as w:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in sorted(filenames):
                if not fn.endswith(".md"):
                    continue
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, root)
                parts = rel.split(os.sep)
                module = parts[0] if len(parts) > 1 else "(root)"
                for b in extract_file(path):
                    seq += 1
                    if b.get("skipped"):
                        n_skip += 1
                    else:
                        n_code += 1
                    rec = {
                        "id": f"{seq:05d}",
                        "hash": hashlib.sha1(b.get("content", "").encode()).hexdigest()[:10],
                        "module": module,
                        "file": rel,
                        "start": b["start"],
                        "end": b.get("end"),
                        "lang": b["lang"],
                        "skipped": b.get("skipped", False),
                    }
                    if not rec["skipped"]:
                        rec["content"] = b["content"]
                        rec["headings"] = [t for _, t in b["headings"]]
                        rec["before"] = b["before"]
                        rec["after"] = b["after"]
                        rec["flags"] = b["flags"]
                    index.setdefault(rec["lang"], {}).setdefault(module, 0)
                    index[rec["lang"]][module] += 1
                    w.write(json.dumps(rec, ensure_ascii=False) + "\n")
    summary = {"total": seq, "code": n_code, "skipped_noncode": n_skip, "by_lang": index}
    with open(out + ".index.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"总块数: {seq}  代码块: {n_code}  非代码(mermaid/text/无标注等): {n_skip}")
    print(f"manifest: {out}\nindex: {out}.index.json")


if __name__ == "__main__":
    main()
