# Node.js 24 开发环境搭建

## 先理解，再动手

Node 运行 JavaScript，包管理器安装依赖，TypeScript 工具提供类型检查或转换。运行 ts 文件与检查类型是不同能力。

**本节自测**：记录 node 版本、package.json 的 type 和启动脚本，运行一条日志。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

知道工程按 ESM 还是 CommonJS 解释，避免混用 require 与 import 后猜错误来源。

</details>

> **文档简介**: 从零搭建现代化 Node.js 24 后端开发环境，涵盖版本管理器（fnm/nvm）、pnpm、TypeScript 与 ESLint 的完整配置

> **目标读者**: 有其他语言后端经验、初次接触 Node.js 生态的开发者

> **前置知识**: 基本命令行操作，了解 Git 与包管理概念（如 Go modules、Maven 任一即可）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#环境搭建` `#Node24` `#fnm` `#pnpm` `#TypeScript` `#ESLint` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- 使用 fnm 或 nvm 安装并切换 Node.js 24 LTS
- 用 pnpm 初始化项目并理解 `package.json` 的关键字段
- 配置 TypeScript 以 ESM 模式运行 Node 后端
- 配置 ESLint 9 扁平配置进行代码质量检查
- 选择合适的编辑器插件与调试入口

## 🔍 核心概念

### 版本管理器：为什么不用官网安装包

Node.js 生态版本迭代快，不同项目可能锁定不同版本。版本管理器让你按项目切换 Node 版本，是当前社区的标准做法。

- **fnm**（Fast Node Manager）：Rust 编写，启动快，单一二进制，推荐首选
- **nvm**：老牌 Bash 脚本方案，生态文档最多，配置略繁琐
- 二者都通过读取 `.node-version` / `.nvmrc` 文件实现"进入目录自动切换"

截至 2026 年 9 月，**Node.js 24 处于活跃维护期（Active LTS）**；Node 22 已于 2025 年 10 月转入维护期（Maintenance LTS），仅接收安全修复。本模块统一以 **Node 24 LTS** 为基准，不再推荐新项目使用 Node 22。

## 🛠️ 实践步骤

### 步骤一：安装版本管理器与 Node 24

```bash
# macOS / Linux 安装 fnm（也可用 brew install fnm）
curl -fsSL https://fnm.vercel.app/install | bash

# 在 ~/.bashrc 或 ~/.zshrc 中追加初始化钩子（安装脚本通常已自动添加）
eval "$(fnm env --use-on-cd)"

# 安装并使用 Node 24 LTS
fnm install 24
fnm use 24
fnm default 24

# 验证
node -v   # v24.x.x
npm -v
```

nvm 等价操作：`nvm install 24 && nvm alias default 24`。

### 步骤二：安装 pnpm

pnpm 通过内容寻址存储 + 硬链接实现快速安装与严格依赖隔离（默认无法引用未声明的依赖）。

```bash
# 官方推荐：corepack（Node 内置，需先启用）
corepack enable pnpm
corepack use pnpm@latest   # 会把 packageManager 字段写入 package.json

# 或独立脚本安装
curl -fsSL https://get.pnpm.io/install.sh | sh

pnpm -v
```

### 步骤三：初始化项目

```bash
mkdir quest-api && cd quest-api
pnpm init
git init
```

编辑 `package.json`，后端项目推荐的最小骨架：

```json
{
  "name": "quest-api",
  "version": "0.1.0",
  "type": "module",
  "packageManager": "pnpm@10.0.0",
  "engines": {
    "node": ">=24"
  },
  "scripts": {
    "dev": "node --watch src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "lint": "eslint ."
  }
}
```

关键点：

- `"type": "module"`：启用原生 ESM，`.js` 文件按 ES 模块解析（详见 [03-modules-esm](./03-modules-esm.md)）
- `--watch`：Node 内置文件监听重启，开发期无需 nodemon
- `engines`：声明 Node 版本下限，配合 pnpm 校验

### 步骤四：配置 TypeScript

Node 24 原生支持运行 **TypeScript 类型剥离**（type stripping，默认开启）：`.ts` 文件可直接 `node src/server.ts` 运行，无需预编译——前提是只使用可被剥离的类型语法（不含 enum、namespace、参数属性等需要代码转换的语法）。

```bash
pnpm add -D typescript @types/node
pnpm exec tsc --init
```

推荐 `tsconfig.json`（面向 Node 24 的现代配置）：

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2023"],
    "types": ["node"],
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "verbatimModuleSyntax": true,
    "noUncheckedIndexedAccess": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

两种运行策略：开发期直接 `node src/server.ts`（类型剥离）；生产或需要 enum 等完整语法时用 `tsc && node dist/server.js` 预编译输出。

### 步骤五：配置 ESLint 9 扁平配置

```bash
pnpm add -D eslint @eslint/js typescript-eslint
```

创建 `eslint.config.mjs`（扁平配置，替代旧 `.eslintrc`）：

```js
import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    ignores: ["dist/**", "node_modules/**"],
  },
  {
    rules: {
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "no-console": "off", // 后端项目允许 console，生产建议换 pino
    },
  }
);
```

验证：`pnpm lint` 应无报错。

## 🎨 最佳实践

版本文件与 packageManager 字段记录工程约定，还需要开发工具和 CI 实际读取或执行这些约定；一个 major 版本号也不等于锁定所有补丁。安装后检查 Node、包管理器和 TypeScript 实际版本，依赖应在项目清单中可重建。

严格类型检查能更早发现不匹配，但不提供运行时输入验证。直接运行 TypeScript 时核对运行时支持的语法范围，不能把“可剥离类型”当完整编译器。内置模块采用 node: 前缀有助于识别来源，第三方依赖则由锁文件管理。

## ❓ 常见问题

### Q1: `corepack enable` 报权限错误？

**A**: Node 安装目录无写权限，用 `sudo` 或改用独立安装脚本。

### Q2: `pnpm install` 后找不到某个依赖的函数？

**A**: 幽灵依赖问题——引用了传递依赖。把该包显式 `pnpm add` 即可。

## 🎯 练习与实践

### 练习一：环境通关

**任务要求**:
1. 用 fnm 安装 Node 24，并生成 `.nvmrc`
2. 用 corepack 启用 pnpm 并初始化项目
3. 把 `node -v`、`pnpm -v`、`pnpm lint` 的输出贴进项目 README

### 练习二：lint 体检

**挑战任务**:
- 故意在代码里写一个未使用变量和一处 `==` 比较，观察 ESLint 报错并修复
- 给 ESLint 升级到 `recommendedTypeChecked` 配置，体会类型感知 lint 的价值

**提示**: 类型感知规则需要在配置里声明 `parserOptions.project: true`。

---

## 🔗 相关文档

- 📄 **[模块与包系统](./03-modules-esm.md)** — 理解 `type: module` 背后的模块解析规则
- 📄 **[第一个服务器](./02-first-server.md)** — 下一站：跑起你的第一个 HTTP 服务
- 📄 **[Node 一行式速查](../reference/quick-references/01-node-cheatsheet.md)** — 常用 CLI 命令速查
- 📄 **[常见故障排除](../reference/quick-references/02-troubleshooting.md)** — 环境问题排查手册


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
