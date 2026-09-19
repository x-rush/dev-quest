#!/usr/bin/env python3
"""Inventory teaching signals, not a semantic quality score. No network or execution."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def inspect(path):
    text = path.read_text(encoding="utf-8")
    prose, code = [], []
    opened = None
    blocks = 0
    repeated_terms = []
    for line_number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if match:
            marker, tail = match.groups()
            if opened is None:
                opened = marker
                blocks += 1
            elif marker[0] == opened[0] and len(marker) >= len(opened) and not tail.strip():
                opened = None
            continue
        (code if opened else prose).append(line)
        if opened is None:
            item = re.match(r"^\s*[-*]\s+\*\*([^*：:]+)\*\*\s*[：:]\s*(.+)$", line)
            if item:
                term, explanation = (part.strip() for part in item.groups())
                # Narrow signal only: short explanations repeating their label.
                # Lists after a full explanation may legitimately match; review context.
                if len(term) >= 2 and term in explanation and len(explanation) <= len(term) + 10:
                    repeated_terms.append({"line": line_number, "term": term, "text": line.strip()})
    body = "\n".join(prose)
    relative = path.relative_to(ROOT).as_posix()
    module = relative.split("/")[0]
    active = bool(re.match(r"\d\d-", module))
    kind = relative.split("/")[1] if active and "/" in relative else "support"
    flags = []
    if active and repeated_terms:
        flags.append("短条目重复术语，需核查是否缺少解释")
    if opened:
        flags.append("未闭合代码围栏")
    if active and path.name != "README.md" and not re.search(r"前置|先修|阅读准备", body):
        flags.append("未显式说明阅读前提")
    if active and kind in {"basics", "projects", "frameworks", "testing", "deployment"}:
        if not re.search(r"预期|期望|应看到|应得到|验收|评估标准|通过条件|输出[：:]", body):
            flags.append("缺少明确结果信号")
        if not re.search(r"练习|自测|检查点|验收", body):
            flags.append("缺少练习或验收信号")
    omissions = [i for i, line in enumerate(text.splitlines(), 1)
                 if re.search(r"其余.*省略|实现省略|此处省略|TODO:|//\s*\.\.\.", line)]
    if active and kind in {"basics", "projects"} and omissions:
        flags.append("教程代码含省略标记，需人工判断")
    if active and re.search(r"无门槛|无阅读门槛|无难度门槛", body):
        flags.append("任意查阅与零前提混淆")
    return {
        "path": relative,
        "title": next((x.lstrip("# ") for x in prose if x.startswith("# ")), path.stem),
        "module": module, "kind": kind, "active": active,
        "lines": len(text.splitlines()), "code_blocks": blocks,
        "prose_chars": len(body), "code_chars": len("\n".join(code)),
        "signals": flags, "omission_lines": omissions,
        "repeated_term_candidates": repeated_terms,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted(p for p in ROOT.rglob("*.md")
                   if not set(p.relative_to(ROOT).parts) & {".git", "node_modules", ".venv"}
                   and "document-quality/reports" not in p.as_posix())
    rows = [inspect(p) for p in paths]
    summary = {
        "documents": len(rows), "active_documents": sum(r["active"] for r in rows),
        "modules": dict(sorted(Counter(r["module"] for r in rows if r["active"]).items())),
        "signals": dict(Counter(s for r in rows for s in r["signals"])),
        "method": "结构信号全量扫描；没有信号不等于内容正确，命中也不等于文档有错。"
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"summary": summary, "documents": rows},
                                     ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
