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
    "04-multiplatform-apps": "React Native / Multi-platform",
    "05-kotlin-compose": "Kotlin / Compose",
    "06-swift-swiftui": "Swift / SwiftUI",
    "07-php-mastery": "PHP",
    "08-java-revisited": "Java",
    "09-nodejs-backend": "Node.js",
    "10-python-discovery": "Python",
    "11-rust-cross-platform": "Rust / Cross-platform",
}
MARKER = re.compile(r"实测|已验证|验证通过|运行通过|测试通过|可运行|已运行|\bPASS\b")


def load(name):
    return json.loads((REPORTS / name).read_text(encoding="utf8"))


def add_record(records, path, mode, report, scope, status="PASS"):
    if path and path.startswith("dev-quest/"):
        path = path.removeprefix("dev-quest/")
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
    frontend = load("frontend-foundations.json")
    for row in frontend.get("results", []):
        add_record(records, row.get("source"), "runtime", "frontend-foundations.json", frontend["scope"], row.get("status", "FAIL"))
    php_java_projects = load("php-java-projects.json")
    for path in php_java_projects.get("documents", {}):
        add_record(records, path, "runtime", "php-java-projects.json", php_java_projects.get("scope", "selected local CLI project checks"), "PASS" if php_java_projects.get("passed") == php_java_projects.get("total") else "FAIL")
    go_rust_projects = load("go-rust-project-validation.json")
    for document in go_rust_projects.get("documents", {}).values():
        add_record(records, document.get("path"), "runtime", "go-rust-project-validation.json", "selected Go/Rust CLI and standard-library project checks", "PASS" if go_rust_projects.get("status") == "passed" else "FAIL")
    mobile = load("mobile-foundations.json")
    for row in mobile.get("results", []):
        add_record(records, row.get("source"), "runtime", "mobile-foundations.json", mobile.get("scope", "selected portable mobile-language check"), "PASS" if row.get("status") == "PASS" else "FAIL")
    security = load("security-examples.json")
    for row in security.get("results", []):
        add_record(records, row.get("source"), "runtime", "security-examples.json", row.get("scope", "selected security-boundary program"), "PASS" if row.get("status", "").lower() == "pass" else "FAIL")
    testing = load("testing-projects.json")
    for row in testing.get("results", []):
        add_record(records, row.get("source"), "runtime", "testing-projects.json", testing.get("scope", "selected testing/project behavior block"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    client_storage = load("client-storage.json")
    add_record(records, client_storage.get("source"), "runtime", "client-storage.json", client_storage.get("scope", "selected React/jsdom and SSR storage checks"), "PASS" if client_storage.get("passed") else "FAIL")
    kotlin_swift = load("kotlin-swift-core.json")
    for row in kotlin_swift.get("results", []):
        add_record(records, row.get("source"), "runtime", "kotlin-swift-core.json", kotlin_swift.get("scope", "selected Kotlin/Swift core program"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    node_python = load("node-python-libraries.json")
    for row in node_python.get("results", []):
        add_record(records, row.get("source"), "runtime", "node-python-libraries.json", node_python.get("scope", "selected Node/Python standard-library program"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    node_python_core_p1 = load("node-python-core-p1.json")
    for row in node_python_core_p1.get("results", []):
        add_record(records, row.get("source"), "runtime", "node-python-core-p1.json", node_python_core_p1.get("scope", "selected Node/Python P1 core example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    node_python_p1_next = load("node-python-p1-next.json")
    for row in node_python_p1_next.get("results", []):
        add_record(records, row.get("source"), "runtime", "node-python-p1-next.json", node_python_p1_next.get("scope", "selected Node/Python P1 example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    node_python_p1_final = load("node-python-p1-final.json")
    for row in node_python_p1_final.get("results", []):
        add_record(records, row.get("source"), "runtime", "node-python-p1-final.json", node_python_p1_final.get("scope", "selected Node/Python P1 final example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    node_python_p1_seventh = load("node-python-p1-seventh.json")
    for row in node_python_p1_seventh.get("results", []):
        add_record(records, row.get("source"), "runtime", "node-python-p1-seventh.json", node_python_p1_seventh.get("scope", "selected Node/Python P1 seventh example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    frontend_mobile_core_p1 = load("p1-frontend-mobile-core-runtime.json")
    for row in frontend_mobile_core_p1.get("results", []):
        add_record(records, row.get("source"), "runtime", "p1-frontend-mobile-core-runtime.json", frontend_mobile_core_p1.get("scope", "selected frontend/mobile P1 core example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    next_web_mobile_p1 = load("p1-next-web-mobile-runtime.json")
    for row in next_web_mobile_p1.get("results", []):
        add_record(records, row.get("source"), "runtime", "p1-next-web-mobile-runtime.json", next_web_mobile_p1.get("scope", "selected Next.js/TanStack/mobile P1 example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    p1_runtime_evidence = load("p1-runtime-evidence.json")
    for row in p1_runtime_evidence.get("results", []):
        add_record(records, row.get("source"), "runtime", "p1-runtime-evidence.json", p1_runtime_evidence.get("scope", "selected P1 runtime example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    frontend_mobile_p1 = load("frontend-mobile-p1-runtime.json")
    for row in frontend_mobile_p1.get("results", []):
        add_record(records, row.get("source"), "runtime", "frontend-mobile-p1-runtime.json", frontend_mobile_p1.get("scope", "selected frontend/mobile P1 contract"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    go_rust_p1_pages = load("go-rust-p1-page-validation.json")
    for row in go_rust_p1_pages.get("cases", []):
        add_record(records, row.get("path"), "runtime", "go-rust-p1-page-validation.json", go_rust_p1_pages.get("scope", "selected Go/Rust P1 page example"), "PASS" if row.get("passed") else "FAIL")
    go_rust_seventh = load("go-rust-seventh-body-validation.json")
    for row in go_rust_seventh.get("cases", []):
        add_record(records, row.get("path"), "runtime", "go-rust-seventh-body-validation.json", go_rust_seventh.get("scope", "selected Go/Rust seventh body example"), "PASS" if row.get("passed") else "FAIL")
    go_php_java_ninth = load("go-php-java-ninth-runtime.json")
    for row in go_php_java_ninth.get("results", []):
        add_record(records, row.get("document"), "runtime", "go-php-java-ninth-runtime.json", go_php_java_ninth.get("scope", "selected Go/PHP/Java ninth runtime example"), "PASS" if row.get("passed") else "FAIL")
    go_rust_node_tenth = load("go-rust-node-tenth-runtime.json")
    for row in go_rust_node_tenth.get("results", []):
        add_record(records, row.get("source"), "runtime", "go-rust-node-tenth-runtime.json", go_rust_node_tenth.get("scope", "selected Go/Rust/Node tenth runtime example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    go_php_java_python_eleventh = load("go-php-java-python-eleventh-runtime.json")
    for row in go_php_java_python_eleventh.get("results", []):
        add_record(records, row.get("file"), "runtime", "go-php-java-python-eleventh-runtime.json", go_php_java_python_eleventh.get("scope", "selected Go/PHP/Java/Python eleventh runtime example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    go_rust_php_twelfth = load("go-rust-php-twelfth-body-validation.json")
    for row in go_rust_php_twelfth.get("cases", []):
        add_record(records, row.get("path"), "runtime", "go-rust-php-twelfth-body-validation.json", go_rust_php_twelfth.get("scope", "selected Go/Rust/PHP twelfth body example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    php_java_p1_runtime = load("php-java-p1-runtime-results.json")
    for row in php_java_p1_runtime.get("cases", []):
        add_record(records, row.get("document"), "runtime", "php-java-p1-runtime-results.json", php_java_p1_runtime.get("scope", "selected PHP/Java P1 runtime example"), "PASS" if row.get("passed") else "FAIL")
    php_java_reference_cases = load("php-java-reference-cases-results.json")
    for row in php_java_reference_cases.get("cases", []):
        add_record(records, row.get("document"), "runtime", "php-java-reference-cases-results.json", php_java_reference_cases.get("scope", "selected PHP/Java reference case"), "PASS" if row.get("passed") else "FAIL")
    rust_php_java_eighth = load("rust-php-java-eighth-body-validation.json")
    for row in rust_php_java_eighth.get("cases", []):
        add_record(records, row.get("document"), "runtime", "rust-php-java-eighth-body-validation.json", rust_php_java_eighth.get("scope", "selected Rust/PHP/Java eighth body example"), "PASS" if row.get("status", "").upper() == "PASSED" else "FAIL")
    php_java_python_tenth = load("php-java-python-tenth-body-validation.json")
    for row in php_java_python_tenth.get("results", []):
        add_record(records, row.get("path"), "runtime", "php-java-python-tenth-body-validation.json", php_java_python_tenth.get("scope", "selected PHP/Java/Python tenth body example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    java_node_python_exceptions = load("java-node-python-exceptions-results.json")
    for row in java_node_python_exceptions.get("cases", []):
        add_record(records, row.get("document"), "runtime", "java-node-python-exceptions-results.json", java_node_python_exceptions.get("scope", "selected Java/Node/Python exception example"), "PASS" if row.get("passed") else "FAIL")
    go_node_python_thirteenth = load("go-node-python-thirteenth-runtime.json")
    for row in go_node_python_thirteenth.get("cases", []):
        add_record(records, row.get("source"), "runtime", "go-node-python-thirteenth-runtime.json", go_node_python_thirteenth.get("scope", "selected Go/Node/Python thirteenth body example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    php_java_rust_fourteenth = load("php-java-rust-fourteenth-body-validation.json")
    for row in php_java_rust_fourteenth.get("results", []):
        add_record(records, row.get("document"), "runtime", "php-java-rust-fourteenth-body-validation.json", php_java_rust_fourteenth.get("scope", "selected PHP/Java/Rust fourteenth body example"), "PASS" if row.get("status", "").upper() == "PASSED" else "FAIL")
    go_node_python_fifteenth = load("go-node-python-fifteenth-runtime.json")
    for row in go_node_python_fifteenth.get("cases", []):
        add_record(records, row.get("source"), "runtime", "go-node-python-fifteenth-runtime.json", go_node_python_fifteenth.get("scope", "selected Go/Node/Python fifteenth body example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    php_java_rust_sixteenth = load("php-java-rust-sixteenth-body-validation.json")
    for row in php_java_rust_sixteenth.get("results", []):
        add_record(records, row.get("document"), "runtime", "php-java-rust-sixteenth-body-validation.json", php_java_rust_sixteenth.get("scope", "selected PHP/Java/Rust sixteenth body example"), "PASS" if row.get("status", "").upper() == "PASSED" else "FAIL")
    next_node_python_basics = load("next-node-python-basics-results.json")
    for row in next_node_python_basics.get("results", []):
        add_record(records, row.get("source"), "runtime", "next-node-python-basics-results.json", row.get("scope", "selected Next/Node/Python basic example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    next_tanstack_mobile_eleventh = load("next-tanstack-mobile-eleventh-body-validation.json")
    for row in next_tanstack_mobile_eleventh.get("results", []):
        if row.get("status", "").upper() == "PASS":
            add_record(records, row.get("path"), "runtime", "next-tanstack-mobile-eleventh-body-validation.json", row.get("limits", "selected Next/TanStack/mobile eleventh body example"), "PASS")
    next_first_project = load("next-first-project-2026-09-19.json")
    add_record(records, next_first_project.get("source"), "runtime", "next-first-project-2026-09-19.json", next_first_project.get("limits", "selected Next first-project JSDOM check"), next_first_project.get("status", "FAIL"))
    php_java_core = load("php-java-core-boundaries.json")
    for row in php_java_core.get("cases", []):
        add_record(records, row.get("document"), "runtime", "php-java-core-boundaries.json", php_java_core.get("scope", "selected PHP/Java core-boundary example"), "PASS" if row.get("passed") else "FAIL")
    php_java_types = load("php-java-types.json")
    for row in php_java_types.get("cases", []):
        add_record(records, row.get("document"), "runtime", "php-java-types.json", php_java_types.get("scope", "selected PHP/Java type example"), "PASS" if row.get("passed") else "FAIL")
    php_java_pipelines = load("php-java-pipelines.json")
    for row in php_java_pipelines.get("cases", []):
        add_record(records, row.get("document"), "runtime", "php-java-pipelines.json", php_java_pipelines.get("scope", "selected PHP/Java pipeline example"), "PASS" if row.get("passed") else "FAIL")
    go_rust_basics = load("go-rust-basics.json")
    for row in go_rust_basics.get("results", []):
        mode = "runtime" if row.get("mode") == "runtime" else "compile_contract"
        add_record(records, row.get("source"), mode, "go-rust-basics.json", go_rust_basics.get("scope", "selected Go/Rust basic example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    go_composite_rust_macros = load("go-composite-rust-macros.json")
    for row in go_composite_rust_macros.get("results", []):
        mode = "runtime" if row.get("mode") == "runtime" else "compile_contract"
        add_record(records, row.get("source"), mode, "go-composite-rust-macros.json", go_composite_rust_macros.get("scope", "selected Go composite-type and Rust macro example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    go_rust_p1 = load("go-rust-p1-basics-runtime.json")
    for row in go_rust_p1.get("results", []):
        if row.get("status", "").upper() == "PASSED":
            add_record(records, row.get("source"), "runtime", "go-rust-p1-basics-runtime.json", go_rust_p1.get("scope", "selected Go/Rust P1 basic program"), "PASS")
    php_java_control_flow = load("php-java-control-flow.json")
    for row in php_java_control_flow.get("cases", []):
        add_record(records, row.get("document"), "runtime", "php-java-control-flow.json", php_java_control_flow.get("scope", "selected PHP/Java control-flow program"), "PASS" if row.get("passed") else "FAIL")
    php_java_json_math = load("php-java-json-math.json")
    for row in php_java_json_math.get("cases", []):
        add_record(records, row.get("document"), "runtime", "php-java-json-math.json", php_java_json_math.get("scope", "selected PHP JSON/Java math program"), "PASS" if row.get("passed") else "FAIL")
    go_rust_keyword_body = load("go-rust-keyword-body-validation.json")
    for row in go_rust_keyword_body.get("results", []):
        add_record(records, row.get("source"), "runtime", "go-rust-keyword-body-validation.json", go_rust_keyword_body.get("scope", "selected Go/Rust keyword body program"), "PASS" if row.get("status", "").upper() == "PASSED" else "FAIL")
    rust_ecosystem = load("rust-ecosystem-runtime.json")
    for row in rust_ecosystem.get("cases", []):
        add_record(records, row.get("document"), "runtime", "rust-ecosystem-runtime.json", rust_ecosystem.get("scope", "selected Rust ecosystem example"), "PASS" if row.get("status", "").upper() == "PASS" else "FAIL")
    # A source inventory alone does not bind any result to a document.
    web = load("final-web-examples.json")
    for row in web.get("results", []):
        if row.get("source") and row.get("case"):
            add_record(records, row["source"], row.get("mode", "runtime"), "final-web-examples.json",
                       row["case"] + "; " + web.get("scope", "selected named case only"), row.get("status", "NOT_VERIFIED"))
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
            {"mode": "mixed_report", "report": "final-web-examples.json", "status": "REPORT_ONLY",
             "results": load("final-web-examples.json").get("results", []),
             "sources": load("final-web-examples.json").get("sources", []),
             "scope": "Historical report contains runtime and TypeScript compile checks but no per-case source bindings. Source inventory is retained as corpus evidence, not file-level runtime/PASS."},
            {"mode": "syntax", "report": "tsjs-validation-2026-09-19.md", "status": "PASS_SYNTAX",
             "count": 1165, "scope": "TS/JS fenced-code parsing only; not per-document runtime or framework-build evidence."},
            {"mode": "syntax", "report": "tsjs-validation-2026-09-19.md", "status": "NOT_VERIFIED_ARKTS",
             "count": 1, "scope": "ArkTS shell example requires the OpenHarmony toolchain."},
        ],
        "known_limits": [
            "final-web-examples.json source inventory does not establish per-document runtime evidence; its unbound cases are retained under corpus_checks.",
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
    lines[-5:-5] = ["", "历史 Web 报告 `final-web-examples.json` 的结果混合运行与 TypeScript 编译检查，未逐用例绑定来源。其结果与来源集合保留在 JSON 的 `corpus_checks`，不能据此给来源文档自动赋予 `runtime/PASS`。", ""]
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
