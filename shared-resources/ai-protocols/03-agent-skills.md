# Agent Skills 规范精要（框架无关）

> **形态说明**：本篇是**开放格式规范**参考（agentskills.io，2025-12-18 发布为开放标准），不是任何单一产品（Claude Code / Codex CLI 等）的功能教程。
> **规范基线**：agentskills.io specification（本仓基线，2026-09-16 对官方 spec 与 agentskills/agentskills 仓库实核；后续修订以官方为准）。

## 一、Agent Skills 是什么

一个 Skill 是一个**包含 `SKILL.md` 文件的目录**：YAML frontmatter 元数据 + Markdown 指令正文，可附带脚本、参考文档、模板等资源。它把"领域专长"（法务审查流程、数据分析管线、代码评审清单）封装为**可复用、可审计、跨产品**的静态规程包。

采用时间线：

| 时间 | 事件 |
|------|------|
| 2025-10 | Anthropic 在 Claude Code / Claude 应用中引入 Skills（feature） |
| 2025-12-18 | 发布为**开放标准**：规范 + `skills-ref` 校验 CLI + 开放治理（agentskills.io / GitHub agentskills） |
| 2026 年中 | **40+ 竞品工具采用**（Claude 全家桶、OpenAI Codex、Gemini CLI、GitHub Copilot、VS Code、Cursor、JetBrains Junie、Goose、OpenCode 等）——跨厂商采用速度快于 MCP 第一年 |

## 二、SKILL.md 格式

```
my-skill/
├── SKILL.md          # 必需：frontmatter + 指令正文
├── scripts/          # 可选：agent 可执行的脚本
├── references/       # 可选：按需加载的参考文档
└── assets/           # 可选：模板与静态资源
```

frontmatter 字段（YAML）：

| 字段 | 必填 | 约束 |
|------|------|------|
| `name` | ✅ | ≤64 字符；仅小写字母/数字/连字符；不得以连字符开头结尾、不得含连续连字符；**必须与父目录名一致** |
| `description` | ✅ | ≤1024 字符；须同时说明"做什么"与"何时使用"（含任务识别关键词——它是 agent 决定是否加载的唯一依据） |
| `license` | ⬜ | 许可证名或指向随附许可文件 |
| `compatibility` | ⬜ | ≤500 字符；环境要求（目标产品、系统依赖、网络需求） |
| `metadata` | ⬜ | 任意 string→string 映射，供实现方扩展 |
| `allowed-tools` | ⬜ | **实验性**：预批准工具的空格分隔列表；各实现支持程度不一 |

正文（frontmatter 之后的 Markdown）无格式限制——但整份文件在激活时**全量载入上下文**，官方建议 ≤500 行，详细参考材料拆到 `references/`。校验：`skills-ref validate <目录>`。

## 三、渐进式披露（Progressive Disclosure）

Skills 的核心机制，按需逐层加载以保护稀缺的上下文窗口：

1. **元数据（~100 tokens/skill）**：启动时将全部已安装技能的 `name` + `description` 注入系统提示——agent 据此判断何时用哪个技能
2. **指令正文（<5000 tokens 建议）**：任务匹配后加载完整 `SKILL.md`
3. **资源（按需）**：`references/`、`assets/`、`scripts/` 仅在需要时读取/执行

## 四、与 MCP 的关系（互补不竞争）

| | Agent Skills | MCP |
|---|---|---|
| 提供 | **静态规程**（团队希望任务怎么做） | **动态能力**（调 API、查数据库） |
| 形态 | 纯文件目录，无运行时 | JSON-RPC 服务进程 |
| 上下文成本 | 渐进式披露，按需加载 | 工具描述常驻上下文 |

两者可组合：MCP server 提供工具，Skill 教 agent 如何编排这些工具完成复杂工作流（MCP 官方扩展 *Skills over MCP* 即技能分发通道）。**发现目录各实现不同**（Claude Code 读 `.claude/skills/`，Codex 等读 `.agents/skills/`）——同一份 `SKILL.md` 跨产品有效是标准的意义所在，目录约定不是。

## 五、安全原则

1. **技能指令是不可信输入**：指令被注入 agent 上下文——第三方技能按与开源依赖同等的审查标准对待（通读 SKILL.md/脚本/资源，识别越权指令、数据外泄、篡改配置的对抗性内容）
2. **脚本即代码执行**：`scripts/` 内脚本按任意代码执行路径对待，敏感操作须用户同意
3. **审计留痕**：记录加载了哪些技能、读了哪些资源、跑了哪些脚本，行为可回溯

## 六、模式不变量（跨实现、跨版本）

- 技能的价值锚点是 `description`——它是 agent 决定加载的唯一依据，写清"何时用"比写全"怎么做"更影响命中率
- 上下文成本三层递进：元数据常驻、正文激活时、资源按需——任何实现偏离该分层都会放大上下文消耗
- 格式与发现解耦：文件格式是标准，发现目录是各实现约定——跨产品复用依赖前者而非后者
- 技能内容属不可信输入：与 MCP 工具描述同级别的审查义务，不因"只是 Markdown"而豁免
- 规程 vs 能力分属两层：静态工作流进 Skill，动态集成进 MCP，混装会导致更新与权限管理混乱

## 相关

- [01-mcp-protocol.md](./01-mcp-protocol.md) — 动态工具接入的协议标准（Skills 常经 MCP 分发）
- [02-agent-patterns.md](./02-agent-patterns.md) — 上下文工程模式（渐进式披露是其实例化）
- 官方规范：<https://agentskills.io/specification>；示例库：<https://github.com/anthropics/skills>
- 各产品功能层（Claude Code 插件/marketplace 等）不在本仓收录范围
