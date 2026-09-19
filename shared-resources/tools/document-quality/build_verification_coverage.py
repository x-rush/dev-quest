"""Build an evidence ledger for the selected language and web modules.

This report deliberately separates a source file that *contains* wording such as
"实测" from a source file for which a named, limited example was actually run.
It never promotes a whole document, framework, or project to "verified".
"""
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).resolve().parent / "reports"
MODULES = {
    "01-go-backend": "Go",
    "02-nextjs-frontend": "Next.js / TypeScript",
    "03-tanstack-stack": "TanStack / TypeScript",
    "07-php-mastery": "PHP",
    "08-java-revisited": "Java",
    "09-nodejs-backend": "Node.js",
    "10-python-discovery": "Python",
}
MARKER = re.compile(r"实测|已验证|验证通过|运行通过|测试通过|可运行|已运行|\bPASS\b")


def load(name):
    return json.loads((REPORTS / name).read_text(encoding="utf8"))


def add_record(records, path, mode, report, scope, status="PASS"):
    if path:
        records[path].append({"mode": mode, "status": status, "report": report, "scope": scope})


def records_from_reports():
    records = defaultdict(list)
    examples = load("examples.json")
    for row in examples["results"]:
        add_record(records, row.get("source"), "runtime", "examples.json", examples.get("scope", "named example"), row["status"])
    refs = load("reference-examples.json")
    for row in refs["results"]:
        add_record(records, row.get("source"), "runtime", "reference-examples.json", "selected Python reference example", row["status"])
    node = load("node-reference-examples.json")
    for row in node["results"]:
        add_record(records, row.get("source"), "runtime", "node-reference-examples.json", "selected complete Node.js reference example", row["status"])
    go = load("go-reference-examples.json")
    for row in go["results"]:
        add_record(records, row.get("path"), "runtime", "go-reference-examples.json", row.get("kind", "selected Go program"), row["status"].upper())
    foundations = load("php-java-foundations.json")
    for row in foundations.get("cases", []):
        add_record(records, row.get("document"), "runtime", "php-java-foundations.json", foundations["scope"], "PASS" if row.get("passed") else "FAIL")
    # The web report names its source set rather than assigning a result per source.
    web = load("final-web-examples.json")
    for source in web.get("sources", []):
        path = source.get("path") if isinstance(source, dict) else source
        add_record(records, path, "runtime", "final-web-examples.json", "one of seven extracted Web checks; see named cases", "PASS")
    return records


def main():
    inventory = load("after.json")
    records = records_from_reports()
    docs = [d["path"] for d in inventory["documents"] if d["active"] and d["path"].split("/", 1)[0] in MODULES]
    marker_rows = []
    document_rows = []
    for path in docs:
        text = (ROOT / path).read_text(encoding="utf8")
        evidence = records[path]
        for number, line in enumerate(text.splitlines(), 1):
            if MARKER.search(line):
                marker_rows.append({
                    "path": path, "line": number, "excerpt": line.strip()[:240],
                    "classification": "source_has_limited_runtime_evidence" if evidence else "unbound_verification_wording",
                })
        document_rows.append({
            "path": path,
            "sha256": hashlib.sha256(text.encode("utf8")).hexdigest(),
            "verification": evidence or [{"mode": "not_verified", "status": "NOT_VERIFIED", "report": None,
                                             "scope": "No named runtime or syntax evidence is recorded for this document."}],
            "marker_count": sum(1 for row in marker_rows if row["path"] == path),
        })
    counts = Counter()
    for row in document_rows:
        counts[row["verification"][0]["mode"]] += 1
    marker_counts = Counter(row["classification"] for row in marker_rows)
    output = {
        "schema_version": 1,
        "purpose": "Evidence ledger. A runtime record covers only its named extracted example or case, never an entire document.",
        "modules": MODULES,
        "summary": {"documents": len(document_rows), "by_primary_state": dict(sorted(counts.items())),
                    "verification_wording_occurrences": len(marker_rows), "marker_classification": dict(sorted(marker_counts.items()))},
        "documents": document_rows,
        "verification_wording": marker_rows,
        "corpus_checks": [
            {"mode": "syntax", "report": "tsjs-validation-2026-09-19.md", "status": "PASS_SYNTAX",
             "count": 1165, "scope": "TS/JS fenced-code parsing only; not per-document runtime or framework-build evidence."},
            {"mode": "syntax", "report": "tsjs-validation-2026-09-19.md", "status": "NOT_VERIFIED_ARKTS",
             "count": 1, "scope": "ArkTS shell example requires the OpenHarmony toolchain."},
        ],
        "known_limits": [
            "No evidence record means not verified; it is not a correctness finding.",
            "Syntax-only TS/JS coverage is recorded at corpus level in tsjs-validation-2026-09-19.md and is not promoted to per-document runtime evidence.",
            "Framework builds, devices, external services, deployments, and historical snippets outside named cases remain outside this ledger.",
        ],
    }
    (REPORTS / "verification-coverage.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    lines = ["# 验证覆盖状态台账", "", "这是一份证据台账，不是把含有“实测”“通过”等措辞的文章自动判为正确。一个运行记录只覆盖报告中命名的完整示例或检查用例，**不覆盖整篇文档、框架工程或部署环境**。", "",
             "## 汇总", "", "| 指标 | 数量 |", "|---|---:|", f"| 纳入模块文档 | {len(document_rows)} |"]
    for key, value in sorted(counts.items()): lines.append(f"| 主状态：{key} | {value} |")
    lines += [f"| 验证措辞出现次数 | {len(marker_rows)} |"]
    for key, value in sorted(marker_counts.items()): lines.append(f"| 措辞分类：{key} | {value} |")
    lines += ["", "## 语法级覆盖（不能当作运行覆盖）", "", "| 检查 | 数量 | 范围 |", "|---|---:|---|", "| `PASS_SYNTAX` | 1,165 | TS/JS 围栏纯语法解析；不验证类型、Hook、依赖版本或框架工程。 |", "| `NOT_VERIFIED_ARKTS` | 1 | ArkTS 壳工程示意，缺少 OpenHarmony 工具链。 |", "", "## 状态定义", "", "| 状态 | 含义 |", "|---|---|", "| `runtime` | 存在命名的实际运行记录；范围由该记录的 `scope` 限定。 |", "| `not_verified` | 没有找到与此文件绑定的命名运行记录。不是技术错误结论。 |", "", "## 文档级证据", "", "| 模块 | 文档 | 主状态 | 命名运行记录数 | 验证措辞数 |", "|---|---|---|---:|---:|"]
    for row in document_rows:
        module = MODULES[row["path"].split("/", 1)[0]]
        state = row["verification"][0]["mode"]
        runs = sum(item["mode"] == "runtime" for item in row["verification"])
        lines.append(f"| {module} | [{row['path']}](../../../../{row['path']}) | `{state}` | {runs} | {row['marker_count']} |")
    lines += ["", "## 重新生成", "", "先刷新结构库存，再生成本台账：", "", "```bash", "python shared-resources/tools/document-quality/finalize_validation.py", "python shared-resources/tools/document-quality/build_verification_coverage.py", "```"]
    (REPORTS / "verification-coverage.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
