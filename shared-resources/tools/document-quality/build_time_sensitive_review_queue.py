#!/usr/bin/env python3
"""Build a source-review queue for version-sensitive documentation claims.

The tool deliberately does not access the network and does not decide whether a
claim is true.  It turns the document-level signal from
``learning-reference-inventory.json`` into line-level review items.  A future
reviewer must verify every item against the relevant official source and record
that source separately; this queue is not evidence of correctness.
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
DEFAULT_INVENTORY = REPORTS / "learning-reference-inventory.json"

# A line may be placed in more than one category.  Keeping the literal matched
# terms makes the queue auditable and prevents a reviewer from mistaking this
# mechanical discovery pass for a semantic judgement.
CATEGORY_PATTERNS: dict[str, re.Pattern[str]] = {
    "版本": re.compile(
        r"(?:\b(?:v?\d+(?:\.\d+){1,3}|latest|current|stable|LTS)\b|"
        r"当前版本|最新(?:稳定)?(?:版本)?|版本(?:号|要求|范围|兼容|更新)?|"
        r"升级到|降级到|镜像标签|ubuntu-latest)",
        re.IGNORECASE,
    ),
    "弃用": re.compile(r"(?:弃用|废弃|已移除|不再推荐|deprecated|obsolete|sunset)", re.IGNORECASE),
    "API": re.compile(
        r"(?:\bAPI\b.{0,36}(?:弃用|废弃|移除|变更|迁移|替代|兼容|不兼容|breaking|"
        r"支持|不再)|(?:弃用|废弃|移除|变更|迁移|替代|兼容|不兼容|breaking|"
        r"支持|不再).{0,36}\bAPI\b|接口(?:已|将|会|不再|兼容|变更|迁移|替代|支持)|"
        r"签名(?:变更|改变)|参数(?:已|将|会|不再|变更))",
        re.IGNORECASE,
    ),
    "维护状态": re.compile(
        r"(?:维护模式|停止维护|终止维护|不再维护|维护(?:中|状态|周期)|"
        r"支持(?:周期|至|到|已结束|已经结束)|end.?of.?life|EOL|maintenance)",
        re.IGNORECASE,
    ),
}
CATEGORY_ORDER = {name: number for number, name in enumerate(CATEGORY_PATTERNS)}


def load_candidate_paths(inventory: Path) -> set[str]:
    """Return only the active-document candidates selected by the inventory."""
    data = json.loads(inventory.read_text(encoding="utf-8"))
    paths: set[str] = set()
    for module in data.get("modules", []):
        paths.update(module.get("time_sensitive_claim_documents", []))
    return paths


def matched_categories(line: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}
    for category, pattern in CATEGORY_PATTERNS.items():
        found = [item.group(0) for item in pattern.finditer(line)]
        if found:
            matches[category] = list(dict.fromkeys(found))
    return matches


def normalise_excerpt(line: str) -> str:
    """Preserve source wording while making table cells readable."""
    return re.sub(r"\s+", " ", line.strip())


def is_non_claim_table_header(line: str) -> bool:
    """Do not queue Markdown table headings such as ``| 技术 | 版本 |``."""
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return False
    cells = [cell.strip().lower() for cell in stripped.strip("|").split("|")]
    return bool(cells) and all(
        cell in {"技术", "版本", "核实日期", "来源", "名称", "说明", "状态", "api"}
        for cell in cells
    )


def document_title(lines: list[str], fallback: str) -> str:
    for line in lines:
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1)
    return fallback


def build_items(paths: set[str]) -> tuple[list[dict[str, Any]], list[str]]:
    items: list[dict[str, Any]] = []
    missing: list[str] = []
    for relative in sorted(paths):
        path = ROOT / relative
        if not path.is_file():
            missing.append(relative)
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        title = document_title(lines, path.stem)
        module, *rest = relative.split("/")
        section = rest[0] if rest else "根目录"
        for number, line in enumerate(lines, 1):
            if is_non_claim_table_header(line):
                continue
            categories = matched_categories(line)
            if not categories:
                continue
            # Ignore a bare Markdown heading only when it has no text beyond a
            # discovered term; headings remain useful claims when they do.
            excerpt = normalise_excerpt(line)
            if not excerpt:
                continue
            items.append({
                "module": module,
                "section": section,
                "path": relative,
                "line": number,
                "title": title,
                "categories": list(categories),
                "matched_terms": categories,
                "source_excerpt": excerpt,
                "review_status": "待官方来源复核",
                "official_source": None,
                "review_note": None,
            })
    items.sort(key=lambda item: (
        item["module"], item["path"], item["line"],
        min(CATEGORY_ORDER[category] for category in item["categories"]),
    ))
    return items, missing


def markdown_cell(value: str) -> str:
    # The excerpt is source text, not report Markdown.  Escape link openers so
    # a relative link written in a reviewed document is not resolved relative
    # to this generated report and reported as a false broken link.
    return (value.replace("&", "&amp;").replace("[", "&#91;").replace("]", "&#93;")
            .replace("|", "\\|").replace("\n", " "))


def write_markdown(output: Path, data: dict[str, Any]) -> None:
    counts = data["summary"]["by_category"]
    lines = [
        "# 易变事实官方来源复核队列",
        "",
        f"生成日期：{data['generated_on']}。范围：{data['scope']}",
        "",
        "这是一个**待复核队列**，不是事实核验结论。脚本只在学习库存已标出的文档中定位可能随版本、弃用策略、API 和维护状态变化的行；它不联网，不判断原句正确或过期，也不修改教学正文。",
        "",
        "复核时请以相应技术的官方文档、官方发布说明或官方生命周期政策为准，在后续审查记录中写下来源链接、访问日期和结论。代码中的 `latest`、镜像标签和 CI 的 `*-latest` 也会入队，因为它们会随时间改变；它们不是自动错误。",
        "",
        "## 汇总",
        "",
        f"- 候选文档：{data['summary']['candidate_documents']} 篇；找到定位项：{data['summary']['items']} 条。",
        f"- 类别计数：版本 {counts.get('版本', 0)}；弃用 {counts.get('弃用', 0)}；API {counts.get('API', 0)}；维护状态 {counts.get('维护状态', 0)}。一行可属于多个类别，因此类别合计可能大于条目数。",
        f"- 读取不到的库存路径：{len(data['missing_inventory_paths'])} 条。",
        "",
        "## 复核顺序",
        "",
        "先处理每个模块 README 的技术基线和明确的弃用/API 迁移结论；再处理框架、部署与项目文档；最后处理安装命令、镜像标签和 CI 运行器标签。任何结论变更都要连同示例、依赖清单和相邻说明一起检查。",
        "",
        "## 明细",
        "",
        "| 模块 | 文件:行 | 类别 | 原句/源码行 | 状态 |",
        "|---|---|---|---|---|",
    ]
    current_module: str | None = None
    for item in data["items"]:
        if item["module"] != current_module:
            current_module = item["module"]
            lines.extend(["", f"<!-- {current_module} -->"])
        categories = "、".join(item["categories"])
        location = f"[{item['path']}](../../../../{item['path']}#L{item['line']}):{item['line']}"
        lines.append(
            f"| {item['module']} | {location} | {categories} | "
            f"{markdown_cell(item['source_excerpt'])} | {item['review_status']} |"
        )
    if data["missing_inventory_paths"]:
        lines.extend(["", "## 库存与文件不一致", ""])
        lines.extend(f"- `{path}`" for path in data["missing_inventory_paths"])
    lines.extend([
        "",
        "## 可重复生成",
        "",
        "```bash",
        "python shared-resources/tools/document-quality/build_time_sensitive_review_queue.py",
        "```",
        "",
        "默认读取 `reports/learning-reference-inventory.json`，输出本 Markdown 文件和同目录的 JSON 明细。可用 `--inventory`、`--markdown-output`、`--json-output` 指定其他路径。",
        "",
    ])
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY,
                        help="learning-reference-inventory.json 的路径")
    parser.add_argument("--markdown-output", type=Path,
                        default=REPORTS / "time-sensitive-review-queue.md")
    parser.add_argument("--json-output", type=Path,
                        default=REPORTS / "time-sensitive-review-queue.json")
    args = parser.parse_args()

    candidates = load_candidate_paths(args.inventory)
    items, missing = build_items(candidates)
    by_module = dict(sorted(Counter(item["module"] for item in items).items()))
    by_category = dict(sorted(
        Counter(category for item in items for category in item["categories"]).items(),
        key=lambda pair: CATEGORY_ORDER[pair[0]],
    ))
    data = {
        "generated_on": date.today().isoformat(),
        "scope": "learning-reference-inventory.json 中 11 个现行模块的 time_sensitive_claim_documents；不含重构档案和生成报告。",
        "method": "离线正则定位可能易变表述，保留原始文件、行号和命中词；不联网、不判真伪、不修改教学正文。",
        "summary": {
            "candidate_documents": len(candidates),
            "items": len(items),
            "by_module": by_module,
            "by_category": by_category,
        },
        "missing_inventory_paths": missing,
        "items": items,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(args.markdown_output, data)
    print(json.dumps(data["summary"], ensure_ascii=False, indent=2))
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")


if __name__ == "__main__":
    main()
