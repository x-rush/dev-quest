# 开发工具链：pnpm、tsx/nodemon 与 ESLint + Prettier

## 先看框架承担哪部分职责

**Node 工具**：pnpm 管依赖，tsx 等工具运行 TypeScript 开发代码，类型检查器单独证明类型关系，格式化器只统一表达。

**最小练习与预期结果**：故意写一个能转译但类型错误的例子，比较开发运行与 tsc 结果；CI 同时执行必要的检查与行为测试。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 配置一套顺手的 Node.js 24 开发工作流——pnpm 包管理、tsx 热重载运行 TypeScript、ESLint 9 + Prettier 统一代码风格
>
> **目标读者**: 开始搭建个人/团队 Node 项目的初级后端开发者
>
> **前置知识**: [环境搭建](../basics/01-environment-setup.md) 中的 fnm 与 pnpm 安装

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#pnpm` `#tsx` `#eslint` `#prettier` `#dx` |
| **更新日期** | `2026年9月` |

</details>

CLI 命令的一行式速查见 [`../reference/quick-references/01-node-cheatsheet.md`](../reference/quick-references/01-node-cheatsheet.md)。

## 🎯 本节目标

- 用 pnpm 管理依赖与脚本
- 选择并配置合适的开发期热重载方案
- 建立 ESLint + Prettier 的统一校验链

## 1. pnpm：脚本即工作流

pnpm 默认内容寻址存储省磁盘、安装快、依赖结构严格（杜绝幽灵依赖）。核心是把常用动作固化到 `package.json` scripts：

```json
// package.json —— scripts 是项目的 CLI 门面
{
  "name": "todo-api",
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": {
    "dev": "tsx watch src/server.ts",        // 开发：热重载
    "build": "tsc",                          // 构建：输出 dist/
    "start": "node dist/server.js",          // 生产：跑编译产物
    "lint": "eslint .",
    "format": "prettier --write .",
    "typecheck": "tsc --noEmit",
    "check": "pnpm typecheck && pnpm lint",  // 提交前一键检查
    "db:migrate": "prisma migrate dev",
    "test": "vitest run"
  }
}
```

常用命令对照：

```bash
pnpm add hono               # 添加生产依赖
pnpm add -D vitest          # 添加开发依赖
pnpm up --latest            # 升级全部依赖
pnpm why <pkg>              # 追溯某个依赖为什么被安装
pnpm dlx <cli-tool>         # 免安装临时运行 CLI 工具
```

## 2. 开发热重载：tsx 优先，nodemon 兜底

**tsx（推荐）**：直接运行 TypeScript，零配置、启动快，内置 `watch` 模式：

```bash
pnpm add -D tsx
pnpm dev                    # 即 tsx watch src/server.ts
```

```jsonc
// tsconfig.json 关键项：Node 24 原生支持 ESM，模块策略选 nodenext
{
  "compilerOptions": {
    "target": "es2023",
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "outDir": "dist",
    "strict": true,
    "verbatimModuleSyntax": true // 强制显式 type 导入，利于编译器剔除类型
  },
  "include": ["src"]
}
```

**nodemon（兜底）**：适合"监控非 TS 产物"的场景（如需要监听 `prisma/schema.prisma` 或目录资源变化时联动命令）：

```json
// nodemon.json
{
  "watch": ["src", "prisma/schema.prisma"],
  "ext": "ts,prisma",
  "exec": "tsx src/server.ts"
}
```

> 二选一即可：纯 TS 项目用 `tsx watch`；需要联动多个外部动作（迁移、生成、构建）时再考虑 nodemon。

## 3. ESLint 9（扁平配置）+ Prettier

```bash
pnpm add -D eslint @eslint/js typescript-eslint prettier eslint-config-prettier
```

```javascript
// eslint.config.mjs —— ESLint 9 扁平配置
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  { ignores: ['dist', 'node_modules'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  prettier, // 放最后：关闭与 Prettier 冲突的格式类规则
  {
    rules: {
      '@typescript-eslint/no-floating-promises': 'error', // 后端最危险的坑：漏 await
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  },
);
```

```jsonc
// .prettierrc —— 团队统一格式
{
  "semi": true,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "all"
}
```

**分工原则**：ESLint 管质量（Bug 与反模式），Prettier 管格式（风格），`eslint-config-prettier` 消除两者重叠。可在编辑器保存时自动 format，在 CI 强制 `pnpm check`。

## 4. 调试补充

```bash
node --inspect dist/server.js     # 打开 Inspector，Chrome DevTools 连接
tsx watch --inspect src/server.ts # 开发期同样支持
```

VS Code 中用 `JavaScript Debug Terminal` 直接 `pnpm dev`，断点即可命中 TS 源码。

## ✅ 最佳实践与陷阱

先确认工具各负责哪件事：编译或类型检查验证静态契约，lint 检查配置规则，格式化统一文本。若多个工具修改相同格式，需协调配置并让本地与 CI 使用一致命令。

运行时与 TS 执行器依据维护政策、工程兼容性和构建需求选择，不以“一律禁用某工具”替代比较。engines 字段是否强制取决于安装器配置；用干净环境执行一次安装、检查和启动，才能确认版本约定真正生效。

## 🔗 相关文档

- 📄 [Node.js 24 开发环境搭建](../basics/01-environment-setup.md) — 工具链的前置安装
- 📖 [Node 一行式速查](../reference/quick-references/01-node-cheatsheet.md) — CLI 与脚本速查
- 📖 [常见故障排除](../reference/quick-references/02-troubleshooting.md) — 工具链疑难杂症
- 📄 [单元测试（Vitest）](../testing/01-unit-testing.md) — 工具链的下一站


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
