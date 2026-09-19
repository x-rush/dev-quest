#!/usr/bin/env python3
"""Turn the verification evidence ledger into a prioritised next-work queue.

This is deliberately a planning artifact, not a correctness verdict.  It reads
only active learning documents already present in ``verification-coverage``;
generated reports, archived material, and inactive inventory entries therefore
cannot inflate the work queue.  Each document without named runtime evidence
gets one file-level task.  Each unbound "verified/passed/runnable" claim gets
an additional, line-level P0 task so reviewers can either attach evidence or
make the claim's scope honest.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).with_name("reports")
DEFAULT_INPUT = REPORTS / "verification-coverage.json"

KIND_ORDER = {"核心基础": 0, "首项目": 1, "框架": 2, "部署": 3, "进阶与测试": 4}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
MARKER = re.compile(r"实测|已验证|验证通过|运行通过|测试通过|可运行|已运行|\bPASS\b")


def category(path: str) -> str:
    """Classify active teaching paths by the learner's next validation need."""
    parts = path.split("/")
    segments = set(parts[1:-1])
    filename = parts[-1]
    if ("projects" in segments and re.match(r"(?:00|01)[-_]", filename)) or "first-project" in filename:
        return "首项目"
    if "deployment" in segments:
        return "部署"
    if (
        "frameworks" in segments
        or "framework-essentials" in segments
        or "library-guides" in segments and any(
            token in filename.lower() for token in ("third-party", "framework", "orm", "router")
        )
    ):
        return "框架"
    if (
        "basics" in segments
        or "language-concepts" in segments
        or "library-guides" in segments
        or "quick-references" in segments
        or filename in {"README.md", "LEARNING_GUIDE.md"}
    ):
        return "核心基础"
    return "进阶与测试"


def file_priority(kind: str) -> str:
    return {"核心基础": "P1", "首项目": "P1", "框架": "P2", "部署": "P2"}.get(kind, "P3")


def marker_priority(source_line: str, kind: str) -> tuple[str, str, str]:
    """Keep broad lexical matches without falsely escalating disclosures."""
    compact = re.sub(r"\s+", "", source_line)
    honest_disclosure = re.search(
        r"(?:未|不|不能|不代表|尚未|缺少).{0,16}(?:实测|验证|通过|可运行|已运行)|"
        r"(?:实测|验证|通过|可运行|已运行).{0,16}(?:未|不|不能|尚未|缺少)", compact
    )
    instructional = re.search(
        r"(?:最小可运行骨架|开始.*项目|重新.*(?:验证|构建|测试)|需要.*(?:验证|运行|测试)|"
        r"^[-*]\s*\[[ xX]\].*(?:验证|通过|测试|运行)|^\*\*Q\d+:|"
        r"预期(?:的)?(?:示例)?输出|示例输出格式|不能单独编译|非可运行块)",
        source_line,
        re.IGNORECASE,
    )
    # Acceptance targets ask the learner to produce a result; they do not
    # certify that the author already ran it. Keep this anchored to avoid
    # suppressing a real claim merely because it mentions acceptance later.
    acceptance_target = re.search(
        r"^(?:[-*]\s+|\d+[.)、]\s*)?(?:\*\*)?(?:验收(?:要求|标准|条件|目标)?|练习要求|完成标准)(?:\*\*)?\s*[:：]",
        source_line,
    )
    conditional_or_next_step = re.search(
        r"(?:先|再|然后|后).{0,18}(?:实测|验证|测试|运行)|(?:实测|验证|测试|运行).{0,18}(?:候选|实现|步骤|方法)",
        compact,
    )
    if honest_disclosure or instructional or conditional_or_next_step or acceptance_target:
        return (
            file_priority(kind),
            "保留诚实的验证边界，并在补证据时决定是否增加最小练习",
            "这行是未验证范围或验证步骤的披露，不是声称已经通过的证据。",
        )
    return (
        "P0",
        "绑定命名验证证据，或把验证措辞收窄为可证明的范围",
        "正文含有未绑定到该文件运行记录的验证性措辞；这不是自动技术错误结论。",
    )


def excerpt(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())[:280]


def markdown_cell(value: str) -> str:
    """Quote source text so source links cannot become report links."""
    return (value.replace("&", "&amp;").replace("[", "&#91;").replace("]", "&#93;")
            .replace("|", "\\|").replace("\n", " "))


def build(data: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    modules = data["modules"]
    docs = {row["path"]: row for row in data["documents"]}
    items: list[dict[str, Any]] = []
    excluded = {"inactive_or_archived": 0, "generated_or_report": 0, "runtime_document": 0}

    # The source ledger was built from active documents in the eleven teaching
    # modules.  Retain defensive filters here so using a future wider ledger
    # cannot silently schedule reports or archives as learner-facing work.
    for path, row in sorted(docs.items()):
        module_id = path.split("/", 1)[0]
        if module_id not in modules:
            excluded["generated_or_report"] += 1
            continue
        lowered = path.lower()
        if "/archive/" in lowered or "/archives/" in lowered or "/reports/" in lowered:
            excluded["inactive_or_archived"] += 1
            continue
        primary = row["verification"][0]["mode"]
        if primary != "not_verified":
            excluded["runtime_document"] += 1
            continue
        kind = category(path)
        items.append({
            "priority": file_priority(kind),
            "kind": kind,
            "task": "为文档选择一个最小可复现案例并记录限定运行证据",
            "reason": "当前没有与此文件绑定的命名运行或语法证据。",
            "module": modules[module_id],
            "path": path,
            "line": None,
            "source_excerpt": None,
            "evidence_action": "抽取完整示例；记录工具链版本、命令、预期输出或可观察行为，以及未覆盖边界。",
        })

    # Re-scan the current source for the ledger's marker vocabulary.  This is
    # intentional: writers may have edited a document after the ledger was
    # generated, so copying its old line number would make a follow-up queue
    # point at the wrong source line.  Only documents with no named evidence
    # are scanned; their markers are therefore unbound by definition.
    for path, row in sorted(docs.items()):
        module_id = path.split("/", 1)[0]
        if module_id not in modules:
            excluded["generated_or_report"] += 1
            continue
        lowered = path.lower()
        if "/archive/" in lowered or "/archives/" in lowered or "/reports/" in lowered:
            excluded["inactive_or_archived"] += 1
            continue
        if row["verification"][0]["mode"] != "not_verified":
            continue
        kind = category(path)
        for line, source_line in enumerate((ROOT / path).read_text(encoding="utf-8").splitlines(), 1):
            if not MARKER.search(source_line):
                continue
            source_excerpt = excerpt(source_line)
            priority, task, reason = marker_priority(source_excerpt, kind)
            items.append({
                "priority": priority,
                "kind": kind,
                "task": task,
                "reason": reason,
                "module": modules[module_id],
                "path": path,
                "line": line,
                "source_excerpt": source_excerpt,
                "evidence_action": "优先复跑该行承诺的完整示例；若环境不可得，删除绝对化结果并说明实际未验证范围。" if priority == "P0" else "保持已有边界说明；若新增示例，记录工具链、命令、预期行为和未覆盖范围。",
            })

    items.sort(key=lambda item: (
        PRIORITY_ORDER[item["priority"]], KIND_ORDER[item["kind"]], item["module"],
        item["path"], item["line"] is None, item["line"] or 0,
    ))
    return items, excluded


def write_markdown(output: Path, result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# 后续验证优先队列",
        "",
        f"生成日期：{result['generated_on']}。输入：[验证覆盖状态台账](verification-coverage.md)。",
        "",
        "这份队列把当前证据缺口转成下一步工作，**不把 `not_verified` 当作内容错误，也不把语法解析当作框架运行**。范围只来自 11 个现行教学模块的活动文档；生成报告、归档材料和不在台账内的文件均被排除。",
        "",
        "## 排序规则",
        "",
        "- **P0**：正文作出“实测”“验证通过”“可运行”等通过性断言，却没有与该文件绑定的命名运行记录。先补证据，或把表述缩小到能证明的范围。",
        "- **P1**：核心基础或首项目没有命名运行证据。它们直接影响初学者建立正确心智模型与完成第一个可交付项目。",
        "- **P2**：框架与部署文档没有命名运行证据。优先建立版本锁定的最小工程、构建或部署演练。",
        "- **P3**：进阶、测试和其他专题没有命名运行证据。按依赖关系排入后续批次。",
        "",
        f"台账对应的 {summary['unbound_wording_items']} 条未绑定措辞全部保留，并在生成时重新定位到当前源码行。明确写出“尚未验证”、说明如何验证或给出练习要求的行，按所属文件的普通优先级排序，不会被误报成 P0 通过性断言。同一文件可同时有一条文件级缺口和多条逐行任务；两者不能互相抵消。每次验证只能声明其命名案例和环境覆盖的范围。",
        "",
        "## 汇总",
        "",
        f"- 队列条目：{summary['items']} 条，其中文件级证据缺口 {summary['file_level_items']} 条，逐行未绑定验证措辞 {summary['unbound_wording_items']} 条。",
        f"- 优先级：P0 {summary['by_priority'].get('P0', 0)}；P1 {summary['by_priority'].get('P1', 0)}；P2 {summary['by_priority'].get('P2', 0)}；P3 {summary['by_priority'].get('P3', 0)}。",
        f"- 分类：核心基础 {summary['by_kind'].get('核心基础', 0)}；首项目 {summary['by_kind'].get('首项目', 0)}；框架 {summary['by_kind'].get('框架', 0)}；部署 {summary['by_kind'].get('部署', 0)}；进阶与测试 {summary['by_kind'].get('进阶与测试', 0)}。",
        "",
        "## 明细",
        "",
        "| 优先级 | 分类 | 模块 | 文件:行 | 下一步 | 原因 / 定位文字 |",
        "|---|---|---|---|---|---|",
    ]
    for item in result["items"]:
        suffix = f"#L{item['line']}" if item["line"] else ""
        location = f"[{item['path']}](../../../../{item['path']}{suffix})"
        if item["line"]:
            location += f":{item['line']}"
        detail = item["source_excerpt"] or item["reason"]
        lines.append(
            f"| {item['priority']} | {item['kind']} | {item['module']} | {location} | "
            f"{item['task']}<br/>{item['evidence_action']} | {markdown_cell(detail)} |"
        )
    lines += [
        "",
        "## 可重复生成",
        "",
        "```bash",
        "python shared-resources/tools/document-quality/build_verification_coverage.py",
        "python shared-resources/tools/document-quality/build_followup_validation_queue.py",
        "```",
        "",
        "先刷新覆盖台账，再生成本队列。JSON 保留结构化排序、排除计数和逐行原文，方便后续验证器消费。",
        "",
    ]
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--markdown-output", type=Path, default=REPORTS / "followup-validation-queue.md")
    parser.add_argument("--json-output", type=Path, default=REPORTS / "followup-validation-queue.json")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    items, excluded = build(data)
    by_priority = dict(sorted(Counter(item["priority"] for item in items).items(), key=lambda row: PRIORITY_ORDER[row[0]]))
    by_kind = dict(sorted(Counter(item["kind"] for item in items).items(), key=lambda row: KIND_ORDER[row[0]]))
    result = {
        "schema_version": 1,
        "generated_on": date.today().isoformat(),
        "input": args.input.name,
        "scope": "verification-coverage.json 的 11 个现行教学模块；不含生成报告、归档和不活跃文件。",
        "method": "为 not_verified 文件建立文件级任务，并按覆盖台账同一标记规则重新扫描当前源码以定位逐行任务；仅通过性断言升为 P0，不判断教学内容真伪。",
        "summary": {
            "items": len(items),
            "file_level_items": sum(item["line"] is None for item in items),
            "unbound_wording_items": sum(item["line"] is not None for item in items),
            "by_priority": by_priority,
            "by_kind": by_kind,
            "excluded": excluded,
        },
        "items": items,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(args.markdown_output, result)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
