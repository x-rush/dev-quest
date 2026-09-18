#!/usr/bin/env python3
"""L3 预分流：读 results.jsonl + manifest.jsonl，产出失败块分类工作清单 l3_worklist.jsonl

分类（机器预判，agent 裁决仍 100% 覆盖）：
  likely-teaching  语法级 unresolved/省略号/占位名
  likely-env       SwiftUI/Compose/浏览器/平台 API 特征
  force-deep       TS2339/TS2551 属性级错误（永不自动放行，必须查官方文档）
  needs-review    其余 FAIL
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results.jsonl")
MANIFEST = os.path.join(HERE, "manifest.jsonl")

TEACHING_PAT = re.compile(
    r"TS2304|TS2552|unresolved reference|"
    r"cannot find (?:name|symbol)|expected .* got|unexpected token|"
    r"SyntaxError|syntax error|ParseError|parse error", re.I)
ENV_PAT = re.compile(
    r"SwiftUI|Combine|UIKit|WidgetKit|@main|compose\.runtime|compose\.material|"
    r"androidx\.|@Composable|window\.|document\.|localStorage|navigator\.|"
    r"react-native|Expo|@SpringBootTest|"
    r"no such (?:table|column)|connection refused|ECONNREFUSED", re.I)
DEEP_PAT = re.compile(r"TS2339|TS2551|Property .* does not exist")


def main():
    meta = {}
    with open(MANIFEST, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            meta[r["id"]] = r
    stats = {}
    out = open(os.path.join(HERE, "l3_worklist.jsonl"), "w", encoding="utf-8")
    for line in open(RESULTS, encoding="utf-8"):
        r = json.loads(line)
        l1, l2 = r["l1"], r.get("l2")
        if l1["status"] == "PASS" and (l2 is not None and l2["status"] == "PASS"):
            continue
        b = meta[r["id"]]
        content = b.get("content", "")
        cat = "needs-review"
        detail = (l1.get("detail") or "") + " || " + (l2.get("detail") or "" if l2 else "")
        if l2 and l2["status"] == "FAIL":
            cat = "needs-review"  # L2 运行失败一律 agent 看
        elif DEEP_PAT.search(detail):
            cat = "force-deep"
        elif ENV_PAT.search(content) or ENV_PAT.search(detail):
            cat = "likely-env"
        elif TEACHING_PAT.search(detail) or "…" in content or "..." in content:
            cat = "likely-teaching"
        rec = {
            "id": r["id"], "lang": r["lang"], "module": r["module"],
            "file": r["file"], "start": r["start"], "end": r["end"],
            "headings": b.get("headings", []),
            "l1": l1, "l2": l2, "category": cat,
        }
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        key = (r["lang"], cat)
        stats[key] = stats.get(key, 0) + 1
    out.close()
    for (lang, cat), n in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"{lang:10s} {cat:16s} {n}")
    total = sum(stats.values())
    print(f"合计需 L3/复核: {total}")


if __name__ == "__main__":
    main()
