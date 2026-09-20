"""Re-run evidence attribution and instructional wording regression checks.

Run from any directory: python path/to/check_coverage_integrity.py
These checks inspect reporting rules, not tutorial runtime correctness.
"""
import json
from unittest.mock import patch

import build_followup_validation_queue as queue
import build_verification_coverage as coverage


def main():
    checks = []
    for line in (
        "验收：测试通过并保存日志。",
        "**验收标准**：示例可运行。",
        "- 验收要求：所有测试通过。",
        "1. 完成标准：测试通过。",
        "- [ ] 至少 3 条服务层测试通过",
        "PASS # 预期的示例输出",
        "该工程尚未实测。",
    ):
        assert queue.marker_priority(line, "首项目")[0] == "P1", line
        checks.append({"check": line, "status": "PASS", "expected": "P1"})
    for line in ("本机实测通过。", "已验证：运行通过。", "示例可运行。"):
        assert queue.marker_priority(line, "首项目")[0] == "P0", line
        checks.append({"check": line, "status": "PASS", "expected": "P0"})
    assert coverage.classify_marker("本轮未实测，不能据此记为运行通过。", []) == "explicit_not_runtime_claim"
    assert coverage.classify_marker("PASS  # 成功时的预期示例输出", []) == "expected_example_output"
    assert coverage.classify_marker("示例运行通过。", []) == "unbound_verification_wording"
    assert coverage.classify_marker("本机实测通过。", [{"mode": "runtime"}]) == "source_has_limited_runtime_evidence"
    checks.append({"check": "negative verification wording is distinct from positive evidence", "status": "PASS"})

    original_load = coverage.load
    source = "02-nextjs-frontend/regression-fixture.md"
    def records(web):
        with patch.object(coverage, "load", side_effect=lambda name: web if name == "final-web-examples.json" else original_load(name)):
            return coverage.records_from_reports()

    for status in ("PASS", "FAIL"):
        result = records({"sources": [{"path": source}], "results": [{"case": "unbound", "status": status}]})
        assert source not in result, result.get(source)
        checks.append({"check": f"source inventory with {status} cannot imply file runtime", "status": "PASS"})
    result = records({"results": [{"source": source, "case": "named compile check", "mode": "compile_contract", "status": "FAIL"}]})
    assert result[source][0]["mode"] == "compile_contract"
    assert result[source][0]["status"] == "FAIL"
    checks.append({"check": "explicit case binding preserves mode and failure", "status": "PASS"})
    report = {"status": "PASS", "scope": "Reporting rule regression only; no tutorial execution", "checks": checks}
    output = coverage.REPORTS / "coverage-integrity-regression.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
