# CLAUDE.md

本文件为 Claude Code 在此仓库中工作时提供指引。

## 项目定位

Dev Quest 是一个**个人学习路径仓库**（纯文档项目，无可运行代码），采用双轨制学习模式组织 11 个技术模块：

- **应用帝国矩阵（核心重点）**: `01-go-backend`、`02-nextjs-frontend`、`03-tanstack-stack`、`04-multiplatform-apps`、`05-kotlin-compose`、`06-swift-swiftui`
- **技术探索系列（零散时间）**: `07-php-mastery`、`08-java-revisited`、`09-nodejs-backend`、`10-python-discovery`（维护冻结：只修确认级错误，不主动扩展）、`11-rust-cross-platform`（建设层）

## 模块结构规范

每个模块遵循统一的**双轴结构**（内容用途四象限 + ⭐/⭐⭐/⭐⭐⭐ 难度标记，详见 `shared-resources/standards/module-structure-guide.md`）：

```
NN-<tech>/
├── README.md              # 模块入口：四象限导览 + 入门/进阶/精通三路径视图
├── basics/                # 教程：按序学习入门（编号文档 01-xx.md）
├── reference/             # 字典：全量参考（本模块知识字典，无难度门槛）
├── frameworks/            # 操作指南：框架生态
├── projects/              # 操作指南：实战项目（⭐ 递进）
├── testing/               # 操作指南：测试工程
├── deployment/            # 操作指南：部署运维
└── advanced-topics/       # 解释：高级主题（按专题分子目录）
```

**单一事实来源**：概念的完整解释只在 `reference/` 中存在一份，其他目录链接过去。

**技术基线**：每模块 README 顶部的"技术基线"区块是该模块版本号的单一事实来源（抗过时三层原则详见 `shared-resources/standards/documentation-guidelines.md`）。10 个模块均已具备标准结构内容。

## 规范文件（修改文档前必读）

所有规范位于 `shared-resources/standards/`：

| 文件 | 用途 |
|------|------|
| `module-structure-guide.md` | 模块目录结构标准 |
| `module-development-standards.md` | 模块开发流程标准 |
| `documentation-guidelines.md` | 文档写作规范与质量标准 |
| `cross-reference-system.md` | 交叉引用与知识关联规范 |

配套资源：

- `shared-resources/templates/` — 标准文档模板与快速模板
- `shared-resources/tools/document-index.md` — 智能文档索引
- `shared-resources/progress/learning-progress.md` — 学习进度总览
- `refactor-archives/` — 重构计划与日志归档（`completed/<模块名>/`）

## 工作流约定

### 新建或修改文档

1. 先读对应模块 README 了解该模块定位与路径规划
2. 使用 `shared-resources/templates/document-template.md` 作为骨架
3. 交叉引用使用相对路径（同模块内 `./`，跨模块 `../NN-<tech>/`）
4. 新文档须同步更新 `document-index.md` 与 `learning-progress.md`

### 模块重命名

1. 必须使用 `git mv`（保留文件历史），禁止 cp+rm
2. 全仓 `grep` 旧目录名，逐文件更新引用
3. 同步更新 `document-index.md`、`learning-progress.md`、各模块 README 自引用
4. 验证：`grep -rn "<旧目录名>" --include="*.md" .` 应无输出

### 重构归档

重构计划与日志写入 `refactor-archives/`：进行中的放 `pending/`，完成后移入 `completed/<模块名>/`，格式参照 `completed/01-go-backend/` 现有条目。

## 提交规范

- 前缀：`feat:`（新内容）、`refactor:`（结构调整）、`fix:`（修复）、`docs:`（文档修正）、`chore:`（杂项）
- 中文描述优先，与现有 git log 风格保持一致
- 大型整理按阶段分 commit（清理 → 重命名 → 引用更新 → 新文档），便于回滚
