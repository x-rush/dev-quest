"""Inventory observable foundation-reference coverage by active module.

The result is a review queue, not a correctness score.  It distinguishes
documented topics from mechanically detectable evidence, and never labels a
snippet runnable merely because it has a language fence.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORTS = Path(__file__).with_name("reports")
MODULES = {
    "01-go-backend": {"language": "Go", "fences": {"go"}},
    "02-nextjs-frontend": {"language": "JavaScript / TypeScript", "fences": {"js", "javascript", "jsx", "ts", "typescript", "tsx"}},
    "03-tanstack-stack": {"language": "JavaScript / TypeScript", "fences": {"js", "javascript", "jsx", "ts", "typescript", "tsx"}},
    "04-multiplatform-apps": {"language": "JavaScript / TypeScript / ArkTS", "fences": {"js", "javascript", "jsx", "ts", "typescript", "tsx", "arkts"}},
    "05-kotlin-compose": {"language": "Kotlin", "fences": {"kotlin", "kt"}},
    "06-swift-swiftui": {"language": "Swift", "fences": {"swift"}},
    "07-php-mastery": {"language": "PHP", "fences": {"php"}},
    "08-java-revisited": {"language": "Java", "fences": {"java"}},
    "09-nodejs-backend": {"language": "JavaScript / TypeScript", "fences": {"js", "javascript", "jsx", "ts", "typescript", "tsx"}},
    "10-python-discovery": {"language": "Python", "fences": {"py", "python"}},
    "11-rust-cross-platform": {"language": "Rust", "fences": {"rust", "rs"}},
}
TOPICS = {
    "keywords": (r"关键字", r"\bkeywords?\b"),
    "builtins": (r"内置函数", r"内置能力", r"\bbuilt[ -]?ins?\b"),
    "standard_library": (r"标准库", r"\bstandard library\b", r"\bstdlib\b"),
}
FENCE = re.compile(r"^```([^\s`]*)[^\n]*\n(.*?)^```\s*$", re.M | re.S)


def docs(module: str) -> list[Path]:
    result: list[Path] = []
    for relative in ("reference/language-concepts", "reference/library-guides"):
        directory = ROOT / module / relative
        result.extend(sorted(directory.rglob("*.md")) if directory.is_dir() else [])
    return result


def topic_files(files: list[Path], patterns: tuple[str, ...]) -> list[str]:
    expression = re.compile("|".join(patterns), re.I)
    matches = []
    for path in files:
        source = path.read_text(encoding="utf-8")
        if expression.search(path.name) or expression.search(source[:6000]):
            matches.append(path.relative_to(ROOT).as_posix())
    return matches


def fence_inventory(files: list[Path], accepted: set[str]) -> tuple[Counter, int, int]:
    languages: Counter = Counter()
    candidate = 0
    explicitly_runnable = 0
    for path in files:
        source = path.read_text(encoding="utf-8")
        for match in FENCE.finditer(source):
            language = match.group(1).lower().strip()
            languages[language or "unlabeled"] += 1
            body = match.group(2).strip()
            if language in accepted and body:
                candidate += 1
                # A marker must be written by the author; this script does not infer it.
                before = source[max(0, match.start() - 400):match.start()]
                if re.search(r"(?:可运行|运行方式|run(?:nable)? example)\s*[:：]", before, re.I):
                    explicitly_runnable += 1
    return languages, candidate, explicitly_runnable


def row(module: str, config: dict) -> dict:
    files = docs(module)
    languages, candidate, marked = fence_inventory(files, config["fences"])
    topics = {name: topic_files(files, patterns) for name, patterns in TOPICS.items()}
    gaps = [name for name, paths in topics.items() if not paths]
    # Only a dedicated validation report can change this field.  No report is
    # parsed here because validation scopes are intentionally heterogeneous.
    return {
        "module": module,
        "language_or_runtime": config["language"],
        "reference_documents": len(files),
        "topic_signals": topics,
        "missing_topic_signals": gaps,
        "fence_languages": dict(sorted(languages.items())),
        "language_fence_candidates": candidate,
        "author_marked_runnable_examples": marked,
        "verification_status": "未由本盘点推断；需链接到具名验证报告或真实工具链记录。",
    }


def status(topics: dict[str, list[str]]) -> str:
    return "；".join("有机械线索" if topics[key] else "待人工确认" for key in TOPICS)


def main() -> None:
    rows = [row(module, config) for module, config in MODULES.items()]
    data = {
        "generated_on": date.today().isoformat(),
        "scope": "11 个现行模块的 reference/language-concepts 与 reference/library-guides。",
        "method": "文件名和前 6000 个字符的主题信号，加上 Markdown 围栏计数；不评价定义完整性、示例正确性或工具链可运行性。",
        "important_boundary": "语言围栏候选不是可运行程序；除作者紧邻围栏明确标记外，本工具不推断可运行身份。验证状态也不会从围栏或目录自动推断。",
        "modules": rows,
        "totals": {
            "reference_documents": sum(item["reference_documents"] for item in rows),
            "language_fence_candidates": sum(item["language_fence_candidates"] for item in rows),
            "author_marked_runnable_examples": sum(item["author_marked_runnable_examples"] for item in rows),
            "modules_with_missing_topic_signal": sum(bool(item["missing_topic_signals"]) for item in rows),
        },
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "foundation-coverage-inventory.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# 基础知识覆盖缺口盘点（机械证据）", "",
        f"生成日期：{data['generated_on']}。范围：{data['scope']}", "",
        "这份报告用于安排全库深审，不能作为完成证明。文件名、标题或正文关键词命中，只表示可能存在相应主题；语言围栏只表示候选代码，**不等于可运行示例**。", "",
        "## 模块总览", "",
        "| 模块 | 主要语言/运行时 | 参考文档 | 关键词 | 内置能力 | 标准库 | 语言围栏候选 | 作者显式标为可运行 | 验证状态 |", "|---|---|---:|---|---|---|---:|---:|---|",
    ]
    for item in rows:
        signals = item["topic_signals"]
        values = ["有机械线索" if signals[key] else "待人工确认" for key in TOPICS]
        lines.append("| {module} | {language_or_runtime} | {reference_documents} | {0} | {1} | {2} | {language_fence_candidates} | {author_marked_runnable_examples} | 待具名证据关联 |".format(*values, **item))
    lines += [
        "", "## 需要优先确认的缺口", "",
        "下列项目是机械信号缺失，不是自动判错。审查时应先查看共享参考、模块 README 和文章正文，确认是否以不同命名覆盖；如果确实缺失，再新增或重构基础参考。", "",
    ]
    for item in rows:
        missing = item["missing_topic_signals"]
        if missing:
            labels = {"keywords": "关键词", "builtins": "内置函数/能力", "standard_library": "标准库"}
            lines.append(f"- **{item['module']}**：{'、'.join(labels[name] for name in missing)}。")
    lines += [
        "", "## 如何使用这份队列", "",
        "1. 为每个基础条目记录权威来源、适用版本、定义、输入输出、边界、反例和最小可运行示例。",
        "2. 只有验证器直接提取并执行原始围栏，且记录工具链、命令、输出和来源哈希后，才能把示例标为已验证。",
        "3. 对平台型内容（移动端、UI、框架）记录真实构建或设备验证的范围；无法验证时保留未验证状态。",
        "4. 此文件可由仓库根目录的 `python shared-resources/tools/document-quality/inventory_foundation_coverage.py` 重建。", "",
        "## 汇总", "",
        f"- reference 文档：{data['totals']['reference_documents']} 篇。",
        f"- 与模块主要语言匹配的非空围栏候选：{data['totals']['language_fence_candidates']} 个。",
        f"- 作者在围栏前明确写出可运行/运行方式标记的候选：{data['totals']['author_marked_runnable_examples']} 个。",
        f"- 有至少一个基础主题机械缺口的模块：{data['totals']['modules_with_missing_topic_signal']} 个。",
    ]
    (REPORTS / "foundation-coverage-inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(data["totals"], ensure_ascii=False))


if __name__ == "__main__":
    main()
