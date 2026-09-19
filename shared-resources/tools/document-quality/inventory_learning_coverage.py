"""Create a reproducible structural inventory for the learning knowledge base.

This tool records observable coverage only.  A present directory, filename, or
heading is never treated as proof that the prose or example is correct.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("reports")
CATEGORIES = (
    "basics", "reference", "frameworks", "projects", "testing", "deployment", "advanced-topics"
)
LANGUAGE_MODULES = {
    "01-go-backend", "05-kotlin-compose", "06-swift-swiftui", "07-php-mastery",
    "08-java-revisited", "10-python-discovery", "11-rust-cross-platform",
}
SHARED_JS_MODULES = {"02-nextjs-frontend", "03-tanstack-stack", "04-multiplatform-apps", "09-nodejs-backend"}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def md_files(path: Path) -> list[Path]:
    if not path.is_dir():
        return []
    return sorted(p for p in path.rglob("*.md") if p.name != "README.md")


def signal(files: list[Path], patterns: tuple[str, ...]) -> list[str]:
    matched: list[str] = []
    expression = re.compile("|".join(patterns), re.I)
    for path in files:
        if expression.search(path.name) or expression.search(text(path)[:4000]):
            matched.append(path.relative_to(ROOT).as_posix())
    return matched


def has_path_evidence(contents: str, stage: str) -> bool:
    """Recognise equivalent path labels used by legacy module READMEs."""
    patterns = {
        "入门": r"(入门|基础学习路径|系统学习路径)",
        "进阶": r"(进阶|框架学习路径|快速参考路径)",
        "精通": r"(精通|高级主题路径|生产导向|项目实战路径)",
    }
    return bool(re.search(patterns[stage], contents, re.I))


def first_h1(path: Path) -> str | None:
    for line in text(path).splitlines():
        matched = re.match(r"^#\s+(.+?)\s*$", line)
        if matched:
            return re.sub(r"\s+", " ", matched.group(1)).strip()
    return None


def module_row(module: Path) -> dict:
    readme = module / "README.md"
    guide = module / "LEARNING_GUIDE.md"
    readme_text = text(readme) if readme.exists() else ""
    categories = {}
    all_reference = md_files(module / "reference")
    for category in CATEGORIES:
        files = md_files(module / category)
        categories[category] = {
            "directory_exists": (module / category).is_dir(),
            "document_count": len(files),
            "documents": [p.relative_to(ROOT).as_posix() for p in files],
        }

    shared = module.name in SHARED_JS_MODULES
    ref_signals = {
        "keyword_reference": signal(all_reference, (r"keyword", r"关键字")),
        "built_in_reference": signal(all_reference, (r"built.?in", r"内置")),
        "standard_library_reference": signal(all_reference, (r"standard.?library", r"标准库")),
    }
    if shared:
        ref_signals["shared_javascript_reference"] = [
            "shared-resources/javascript-keywords.md",
            "shared-resources/javascript-builtins.md",
            "shared-resources/javascript-standard-library.md",
        ]
    basics = md_files(module / "basics")
    projects = md_files(module / "projects")
    exercise_docs = signal(basics, (r"练习", r"自测", r"检查点", r"挑战"))
    acceptance_docs = signal(projects, (r"验收", r"完成标准", r"检查清单"))
    module_docs = [readme, guide] + [path for category in CATEGORIES for path in md_files(module / category)]
    by_h1: dict[str, list[str]] = {}
    for path in module_docs:
        if path.exists() and (heading := first_h1(path)):
            by_h1.setdefault(heading, []).append(path.relative_to(ROOT).as_posix())
    duplicate_h1_groups = [
        {"title": heading, "documents": paths}
        for heading, paths in sorted(by_h1.items()) if len(paths) > 1
    ]
    volatile_pattern = re.compile(r"最新|latest|当前版本|最新稳定|弃用|deprecated|维护模式", re.I)
    time_sensitive_claim_documents = [
        path.relative_to(ROOT).as_posix() for path in module_docs
        if path.exists() and volatile_pattern.search(text(path))
    ]

    gaps: list[dict[str, str]] = []
    for category in CATEGORIES:
        state = categories[category]
        if not state["directory_exists"]:
            gaps.append({"kind": "missing_directory", "path": category,
                         "evidence": "模块结构规范列出该目录；需人工确认是否为有意适配。"})
        elif state["document_count"] == 0:
            gaps.append({"kind": "empty_directory", "path": category,
                         "evidence": "目录存在但没有 Markdown 教学文档。"})
    if module.name in LANGUAGE_MODULES:
        for key, label in (("keyword_reference", "关键词"), ("built_in_reference", "内置函数/能力"),
                           ("standard_library_reference", "标准库")):
            if not ref_signals[key]:
                gaps.append({"kind": "missing_reference_signal", "path": "reference",
                             "evidence": f"语言模块的 reference 中未找到文件名或开头正文含“{label}”的条目；需人工核对是否以不同名称覆盖。"})
    if not guide.exists():
        gaps.append({"kind": "missing_learning_guide", "path": "LEARNING_GUIDE.md",
                     "evidence": "README 的模块入口链接指向模块学习导读。"})
    if basics and not exercise_docs:
        gaps.append({"kind": "no_exercise_signal", "path": "basics",
                     "evidence": "basics 文档中未在文件名或前 4000 字内找到练习/自测/检查点/挑战信号。"})
    if projects and not acceptance_docs:
        gaps.append({"kind": "no_project_acceptance_signal", "path": "projects",
                     "evidence": "projects 文档中未在文件名或前 4000 字内找到验收/完成标准/检查清单信号。"})

    return {
        "module": module.name,
        "readme_exists": readme.exists(),
        "learning_guide_exists": guide.exists(),
        "readme_path_evidence": {stage: has_path_evidence(readme_text, stage) for stage in ("入门", "进阶", "精通")},
        "categories": categories,
        "reference_signals": ref_signals,
        "exercise_signal_documents": exercise_docs,
        "project_acceptance_signal_documents": acceptance_docs,
        "duplicate_h1_groups": duplicate_h1_groups,
        "time_sensitive_claim_documents": time_sensitive_claim_documents,
        "gaps": gaps,
    }


def main() -> None:
    modules = sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"^\d\d-", p.name))
    rows = [module_row(module) for module in modules]
    data = {
        "generated_on": date.today().isoformat(),
        "scope": "11 个现行模块；不含 refactor-archives 和验证报告。",
        "method": "目录、Markdown 文件、指定标题及文件名/开头正文信号的机械盘点；不评价正文正确性。",
        "modules": rows,
        "gap_counts": dict(sorted(Counter(gap["kind"] for row in rows for gap in row["gaps"]).items())),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "learning-reference-inventory.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# 学习路径与参考覆盖清单（机械盘点）", "",
        f"生成日期：{data['generated_on']}。范围：{data['scope']}", "",
        "本清单只记录可观察的结构证据。文档存在、标题存在或关键词命中，都**不等于**内容正确、示例可运行或讲解足够；它用于排定人工深审与真实项目验证的顺序。", "",
        "## 模块总览", "",
        "| 模块 | basics | reference | frameworks | projects | testing | deployment | advanced | 导读 | 三阶段路径证据 | 机械缺口 |", "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|",
    ]
    for row in rows:
        cats = row["categories"]
        path_state = "/".join("✓" if value else "×" for value in row["readme_path_evidence"].values())
        category_counts = {key: cats[key]["document_count"] for key in CATEGORIES}
        category_counts["advanced"] = category_counts["advanced-topics"]
        lines.append("| {module} | {basics} | {reference} | {frameworks} | {projects} | {testing} | {deployment} | {advanced} | {guide} | {paths} | {gaps} |".format(
            module=row["module"], guide="✓" if row["learning_guide_exists"] else "×", paths=path_state, gaps=len(row["gaps"]),
            **category_counts))
    lines += ["", "`三阶段路径证据` 的顺序是入门/进阶/精通，接受旧模块的等价名称；数字是相应目录下的 Markdown 文档数。", "", "## 参考覆盖信号", "",
        "以下信号只用来发现可能漏项。JavaScript 生态模块在根 README 明确复用 shared-resources 的 JavaScript 关键词、内置能力与标准库参考，因此单列为共享入口。", ""]
    for row in rows:
        signals = row["reference_signals"]
        lines.append(f"### {row['module']}")
        lines.append("")
        for key, label in (("keyword_reference", "关键词"), ("built_in_reference", "内置能力"), ("standard_library_reference", "标准库"), ("shared_javascript_reference", "共享 JavaScript 基础参考（关键词、内置能力、标准库）")):
            if key in signals:
                value = signals[key]
                lines.append(f"- {label}：{'；'.join(value) if value else '未找到机械信号'}")
        lines.append(f"- basics 练习/自测信号：{len(row['exercise_signal_documents'])} 篇；projects 验收信号：{len(row['project_acceptance_signal_documents'])} 篇。")
        lines.append(f"- 完全相同的一级标题组：{len(row['duplicate_h1_groups'])} 组；含易变版本/API 用语的文档：{len(row['time_sensitive_claim_documents'])} 篇（仅表示需要随技术基线复核，不表示已过期）。")
        lines.append("")
    lines += ["## 待人工确认的结构缺口", "",
        "这些是待办线索，不是自动判定的质量缺陷。不同技术栈可以按结构适配原则省略或合并目录，但需要在模块 README 或导读中写出理由与替代入口。", ""]
    for row in rows:
        if row["gaps"]:
            lines.append(f"### {row['module']}")
            lines.append("")
            for gap in row["gaps"]:
                lines.append(f"- `{gap['kind']}` · `{gap['path']}`：{gap['evidence']}")
            lines.append("")
    lines += ["## 重复与过期风险的机械线索", "",
        "- `duplicate_h1_groups` 只统计同一模块内完全相同的一级标题，便于人工判断是否是重复文章或同名但不同语境的内容。",
        "- `time_sensitive_claim_documents` 匹配“最新 / latest / 当前版本 / 弃用”等用语。它标示版本、维护状态或 API 变化的复核队列，不能单凭文字命中断言内容过期。",
        "- 本次结构盘点没有发现空目录或缺失的一级模块目录；这只说明骨架齐全，不能证明目录内的解释已达到交付标准。",
        "", "## 下一轮人工验收的固定口径", "",
        "1. 先确认结构缺口是有意适配还是实际缺失；确认后更新模块 README 和本清单。",
        "2. 对每个 reference 条目核对定义、签名/输入输出、边界、反例、版本来源和可执行最小示例。",
        "3. 对每个 basics 链路核对前置知识、可观察结果与练习反馈；对每个 project 核对需求、运行方式、阶段产物和验收标准。",
        "4. 框架与平台内容按真实最小项目安装依赖并构建；无法在当前平台验证的内容明确标为待验证，不以目录或静态检查代替。",
        ""]
    (OUT / "learning-reference-inventory.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT / 'learning-reference-inventory.json'}")
    print(f"wrote {OUT / 'learning-reference-inventory.md'}")
    print(json.dumps(data['gap_counts'], ensure_ascii=False))


if __name__ == "__main__":
    main()
