# CLAUDE.md

本文件为 Claude Code 在此仓库中工作时提供指引。

## 项目定位

Dev Quest 是一个**个人学习路径仓库**（纯文档项目，无可运行代码），采用双轨制学习模式组织 10 个技术模块：

- **应用帝国矩阵（核心重点）**: `01-go-backend`、`02-nextjs-frontend`、`03-tanstack-stack`、`04-multiplatform-apps`、`05-kotlin-compose`、`06-swift-swiftui`
- **技术探索系列（零散时间）**: `07-php-mastery`、`08-java-revisited`、`09-nodejs-backend`、`10-python-discovery`

## 模块结构规范

每个模块遵循统一目录结构：

```
NN-<tech>/
├── README.md              # 模块入口与学习路径
├── basics/                # 基础入门（编号文档 01-xx.md）
├── advanced-topics/       # 高级主题（按专题分子目录）
├── knowledge-points/      # 知识点速查（按类别分子目录）
├── frameworks/            # 框架生态指南
├── projects/              # 实战项目
├── testing/               # 测试工程
└── deployment/            # 部署运维
```

01、02 模块已完成标准化重构；03-10 模块目前仅有 README 规划文档，内容分批补齐。

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
