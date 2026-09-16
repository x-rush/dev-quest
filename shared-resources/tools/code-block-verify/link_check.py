#!/usr/bin/env python3
"""站内链接全量检查：扫描全仓 .md 的相对链接，校验目标文件存在。

- 跳过外链（http/https/mailto）与纯锚点（#...）
- 剥离围栏代码块与行内代码后再提取链接（代码示例中的 markdown 链接不计入）
- 锚点段（path#anchor）只校验 path 部分，锚点存在性不在本工具职责内
- 模板占位符（ALLOWED_PLACEHOLDERS）不计断链
- --strict：发现断链时退出码 1（供 CI 门禁）

用法：
    python3 link_check.py [REPO_ROOT]            # 打印断链清单 + 汇总
    python3 link_check.py --strict               # CI 用：断链退出码 1
"""
import argparse
import os
import re
import sys

# 围栏代码块（``` 或 ~~~，含嵌套与未闭合兜底）
FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
# 行内链接 [text](target "title")，target 可为 <...> 包裹
LINK_RE = re.compile(r"!?\[(?:[^\[\]]*)\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
# 行内代码（逐行剥，防止跨行反引号错位拼接出假链接）
INLINE_CODE_RE = re.compile(r"`[^`]*`")

ALLOWED_PLACEHOLDERS = {
    "URL",
    "../path/to/doc.md",
    "../../module/path/to/doc.md",
    "./相邻条目.md",
    "相关链接",
}


def extract_links(md_path):
    """返回 [(target, 原文件行号)]；围栏内与行内代码中的内容不计。"""
    links = []
    with open(md_path, encoding="utf-8") as f:
        fence = None
        for lineno, line in enumerate(f, 1):
            m = FENCE_RE.match(line.rstrip("\n"))
            if m:
                char = m.group(2)[0]
                if fence is None:
                    fence = char
                elif char == fence:
                    fence = None
                continue
            if fence is not None:
                continue
            body = INLINE_CODE_RE.sub("", line)
            for lm in LINK_RE.finditer(body):
                target = lm.group(1)
                if target.startswith("<") and target.endswith(">"):
                    target = target[1:-1]
                links.append((target, lineno))
    return links


def iter_md_files(repo_root):
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root", nargs="?", default=os.getcwd())
    ap.add_argument("--strict", action="store_true", help="断链时退出码 1")
    args = ap.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    total, broken, checked = 0, [], 0
    for md in iter_md_files(repo_root):
        rel_md = os.path.relpath(md, repo_root)
        for target, lineno in extract_links(md):
            total += 1
            if re.match(r"^(https?:|mailto:|#)", target):
                continue
            checked += 1
            if target in ALLOWED_PLACEHOLDERS:
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            dest = os.path.normpath(os.path.join(os.path.dirname(md), path_part))
            if not os.path.exists(dest):
                broken.append((rel_md, lineno, target))

    print(f"links_total={total} links_checked={checked} broken={len(broken)}")
    for rel_md, lineno, target in broken:
        print(f"BROKEN {rel_md}:{lineno} -> {target}")
    if broken and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
