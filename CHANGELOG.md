# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式。

## [2.2.0] - 2026-09-10

### Added
- 标准体系升级为 Diátaxis 双轴框架：内容四象限（教程/操作指南/字典/解释）+ 三级难度标记（⭐/⭐⭐/⭐⭐⭐）
- `knowledge-points/` 全局更名为 `reference/`（模块知识字典，单一事实来源）
- 补齐 03-10 模块知识库内容约 300 篇：basics/ 教程 8 篇、reference/ 字典 11 篇、frameworks/projects/testing/deployment 工程域指南、advanced-topics 高级主题
- 03-10 模块 README 重写为四象限导览 + 入门/进阶/精通三路径视图

### Changed
- `document-index.md` 03-10 章节从"规划中"占位更新为实际文档目录索引（v3.0.0）
- `learning-progress.md` 为 02-10 模块补充模块入口链接并修正过时技术基线（Node 22/Express 5 等）
- 模块结构指南重写为 v2.0.0（双轴设计原则、README 三路径视图格式、结构适配原则）

### Fixed
- 全仓 Markdown 相对链接校验（3269 条真实链接，0 断链）：修复 document-index/cross-reference-system 的层级错误、02 模块指向旧仓库结构的 61 处死链、learning-progress 与各 README 的陈旧文件名引用

## [2.1.0] - 2026-09-10

### Added
- 新增 `03-tanstack-stack` 模块规划（TanStack Query/Table/Router/Form/Start）
- 新增根级工程文档：`CLAUDE.md`、`CONTRIBUTING.md`、`CHANGELOG.md`、`LICENSE`（MIT）

### Changed
- 模块布局重组为双轨制 10 模块：核心矩阵 01-06 + 技术探索系列 07-10
- `05-kotlin-compose`、`06-swift-swiftui` 聚焦 Kotlin Jetpack Compose 与 Swift SwiftUI 官方原生开发
- 根 README 目录结构树重写，与 01/02 模块实际结构对齐
- `document-index.md`、`learning-progress.md` 按实际文件全量重写
- `refactor-archives/README.md` 对齐实际归档结构，补充 02 模块归档条目

### Removed
- 移除 `03-taro-miniprogram` 模块（Taro 框架已不再活跃维护）
- 移除 `10-nuxtjs-exploration`、`11-sveltekit-journey` 模块（调整兴趣技术栈范围）
- 删除根级空目录 `development-tools/`、`framework-patterns/`、`performance-optimization/`

### Fixed
- 修复 `02-nextjs-frontend/{deployment,projects,testing}` 目录权限（700 → 755）
- 修复根 README 中指向不存在文件的 `shared-resources/` 链接
- 修复 `01-go-backend/README.md` 跨模块引用路径
- 清理全部文档中的 Taro 引用与旧模块编号残留

## [2.0.0] - 2025-10

### Added
- 建立 `shared-resources/` 标准体系：模块结构指南、开发标准、文档规范、交叉引用系统
- 建立重构归档系统（`refactor-archives/`）
- 完成 `02-nextjs-frontend` 模块现代化重构（App Router、React 19、Next.js 15）

### Changed
- 移除所有学习路线文档中的固定时间规划，改为灵活学习模式
- `01-go-backend` 模块内容对齐修复

## [1.0.0] - 2025-10-24

### Added
- 初始提交：dev-quest 学习路线图
- 完成 `01-go-backend` 模块重构（basics/frameworks/projects/testing/deployment 标准结构）
- 创建技术探索系列模块，建立双轨制学习体系

[2.1.0]: https://github.com/x_rush/dev-quest/compare/2.0.0...2.1.0
[2.0.0]: https://github.com/x_rush/dev-quest/compare/1.0.0...2.0.0
[1.0.0]: https://github.com/x_rush/dev-quest/releases/tag/1.0.0
