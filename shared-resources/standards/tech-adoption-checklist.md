# 技术收录 Checklist

> **用途**：新增模块或新增框架/库收录前的**统一判据清单**。本仓库定位是"当前前沿、高热度、长半衰期"技术栈，收录门槛高于流行度——**宁缺毋滥**，每一条拒绝都应留下记录（拒绝理由是知识库的一部分）。

## 一、收录判据（全部满足才收录）

### 1. 半衰期评估（首要判据）
- [ ] **语言/运行时层**：有向后兼容承诺机制（如 Rust edition 系统、Java LTS、Go 兼容性承诺），预期半衰期 ≥ 10 年
- [ ] **框架层**：主版本迭代收敛（不再半年一个大破坏），或被事实标准锁定
- [ ] **协议层**：独立于任何 SDK/框架，规范以年计稳定（如 MCP、LSP）
- ❌ 一票否决项：尚在"框架战争"阶段的赛道（多个竞争者未收敛，如 WASM UI 框架 Yew/Leptos）

### 2. 社区活跃度（registry / GitHub 实核，禁止凭印象）
- [ ] registry 数据实核（crates.io / npm / PyPI / Maven Central 下载量，记录核实日期）
- [ ] GitHub 活跃度实核（⭐ 数 + 最近 6 个月 release 频率，记录核实日期）
- [ ] **更新频率红线**：6 个月无 release 且无 LTS 承诺 → 拒收（实例：Rocket 迭代慢被拒）
- [ ] 生态收敛判据：该赛道是否已有 1-2 个明显主流（实例：Rust Web 框架 Axum vs Actix，Axum 胜出因 tower 生态收敛）

### 3. 与现有模块的关系
- [ ] 不与现有模块定位重叠（重叠时判断是否"对标替代"——如 11-rust Tauri 对标 04-multiplatform-apps 三端原生，属补充视角而非重复）
- [ ] 能与现有模块形成交叉引用（如 Axum ↔ 09-nodejs Express 对照）
- [ ] 收录形式优先级：**协议/模式层 > 语言全量参考 > 框架教程 > 项目实战**

### 4. 形态判断：协议优先于框架
- [ ] 若主题处于"框架竞争未收敛"阶段（典型：AI/LLM 应用层），只收录**协议层与模式层**（如 MCP 协议精要、Agent 模式语言），不收录任何框架教程
- [ ] 框架绑定文档必须文末附「模式不变量」小结（见 [documentation-guidelines.md](./documentation-guidelines.md)）

### 5. 维护成本预估
- [ ] 该主题纳入哪一层维护强度（见 [module-development-standards.md](./module-development-standards.md) 维护冻结策略）
- [ ] 版本号统一指向模块 README「技术基线」区块，遵守抗过时三层原则

## 二、核实工具链

| 判据 | 工具 | 命令/入口 |
|------|------|----------|
| registry 最新版 | [baseline-check](../tools/baseline-check/README.md) | `python3 baseline_check.py` |
| crates.io | HTTP API | `https://crates.io/api/v1/crates/<name>` |
| npm | CLI | `npm view <pkg> version` |
| PyPI | JSON API | `https://pypi.org/pypi/<pkg>/json` |
| GitHub ⭐/release | API | `https://api.github.com/repos/<o>/<r>`（限额 60/h，建议 GITHUB_TOKEN） |

**纪律**：所有版本/热度数据必须当次实核并记日期；检索摘要不能作为版本事实来源。

## 三、拒绝项记录格式

新增收录讨论时，被拒对象登记于此（拒绝理由是复用资产——避免重复评估）：

| 对象 | 拒绝日期 | 理由 | 判据条目 |
|------|---------|------|---------|
| Actix Web | 2026-09 | vs Axum 生态收敛，避免双收录 | 1-半衰期 / 3-重叠 |
| Rocket | 2026-09 | 迭代慢，6 个月无 release | 2-活跃度红线 |
| Yew / Leptos（WASM UI） | 2026-09 | 框架战争未收敛 | 1-一票否决 |
| AI/LLM 应用框架（各 SDK 教程） | 2026-09 | 过时风险高，只收协议/模式层（见 `shared-resources/ai-protocols/`） | 4-形态判断 |
| Claude Code 插件 / marketplace 机制 | 2026-09 | 单一产品私有机制，非开放标准 | 1-半衰期 / 4-形态判断 |

> **修正记录**：Agent Skills 曾被初步归入"AI/LLM 应用层待观察"，经 2026-09-16 复核——2025-12-18 已发布为开放标准（agentskills.io），40+ 竞品工具采用（OpenAI Codex / Gemini CLI / GitHub Copilot / Cursor 等），满足判据 1/2/4，**收录**为协议层文档 [03-agent-skills.md](../ai-protocols/03-agent-skills.md)。教训：拒绝项也应定期复核，标准的收敛速度可能快于直觉。

## 四、收录后义务

1. README 顶部建「技术基线」区块（版本表 + 核实日期），为该模块全部版本号单一事实来源
2. 规划文档列入四象限导览并标注建设状态，新建篇目同步 [document-index](../tools/document-index.md) 与 [learning-progress](../progress/learning-progress.md)
3. 纳入季度基线对齐 ritual（baseline-check 复跑）与年度时效评估
