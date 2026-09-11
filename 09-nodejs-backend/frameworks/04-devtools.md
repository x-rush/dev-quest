# 开发工具链：pnpm、tsx/nodemon 与 ESLint + Prettier

> **文档简介**: 配置一套顺手的 Node.js 24 开发工作流——pnpm 包管理、tsx 热重载运行 TypeScript、ESLint 9 + Prettier 统一代码风格
>
> **目标读者**: 开始搭建个人/团队 Node 项目的初级后端开发者
>
> **前置知识**: [环境搭建](../basics/01-environment-setup.md) 中的 fnm 与 pnpm 安装

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#pnpm` `#tsx` `#eslint` `#prettier` `#dx` |
| **更新日期** | `2026年9月` |

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

- ✅ 把 `check`（typecheck + lint）挂到 CI，本地依赖编辑器集成
- ✅ `engines.node` 锁定 24 LTS（当前 Active LTS；22 已进入 Maintenance，新项目不要选），配合 `.npmrc` 的 `engine-strict=true`
- ❌ 用 `ts-node`——维护停滞且慢，新项目一律 tsx
- ❌ ESLint 与 Prettier 各自管理格式导致互相打架——加 `eslint-config-prettier`

## 🔗 相关文档

- 📄 [Node.js 24 开发环境搭建](../basics/01-environment-setup.md) — 工具链的前置安装
- 📖 [Node 一行式速查](../reference/quick-references/01-node-cheatsheet.md) — CLI 与脚本速查
- 📖 [常见故障排除](../reference/quick-references/02-troubleshooting.md) — 工具链疑难杂症
- 📄 [单元测试（Vitest）](../testing/01-unit-testing.md) — 工具链的下一站
