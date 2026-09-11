# 模块系统与 ESM

> **文档简介**: 理解 ESM 与 CommonJS 的差异、package.json 的 `exports` 字段以及 Node 的模块解析规则，这是读懂现代 Node 代码的基础

> **目标读者**: 需要 import/export 写规范、发布库或排查"Cannot use import statement outside a module"类报错的开发者

> **前置知识**: [环境搭建](./01-environment-setup.md)，对 `import`/`require` 有初步印象

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#ESM` `#CommonJS` `#模块解析` `#exports` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- 说清 ESM 与 CJS 的核心差异与互操作规则
- 用 `exports` / `imports` 字段设计包的公共 API
- 解释 Node 如何从 `import x from "y"` 找到真实文件
- 处理 `.js` / `.mjs` / `.cjs` 扩展名与 `type` 字段的关系

## 🔍 两套模块体系

### CommonJS（历史体系）

Node 早期方案，同步加载：

```js
// cjs/add.cjs
function add(a, b) { return a + b; }
module.exports = { add };

// cjs/main.cjs
const { add } = require("./add.cjs");
console.log(add(1, 2));
```

### ESM（现行标准）

JavaScript 官方标准，静态结构、异步加载、支持顶层 await：

```js
// esm/add.js
export function add(a, b) { return a + b; }
export default add;

// esm/main.js
import add, { add as plus } from "./add.js";
console.log(plus(1, 2));
```

### 关键差异速览

| 维度 | ESM | CommonJS |
|------|-----|----------|
| 加载时机 | 编译期静态分析（可 tree-shaking） | 运行时动态 require |
| 导出绑定 | 实时绑定（值变化可见） | 值拷贝 |
| 顶层 await | ✅ 支持 | ❌ 不支持 |
| `__dirname` | ❌ 需从 `import.meta.url` 推导 | ✅ 全局可用 |
| 条件加载 | 需用动态 `import()` | 可条件 require |
| 严格模式 | 始终启用 | 默认非严格 |

### 互操作规则（最常踩坑处）

```js
// ESM 中导入 CJS 包：default 即 module.exports
import _ from "lodash";                // ✅ CJS 包的整组导出挂在 default 上
import { map } from "lodash";          // ⚠️ 取决于该包是否提供命名导出（由 cjs-module-lexer 推断）

// CJS 中加载 ESM：只能动态 import
// old-plugin.cjs
async function load() {
  const { modern } = await import("./modern.mjs");
}
```

## 🛠️ 实践：`type` 字段与文件扩展名

Node 判断一段 `.js` 代码是 ESM 还是 CJS，依据如下：

| 条件 | 解析为 |
|------|--------|
| 最近 package.json 有 `"type": "module"` | ESM |
| 最近 package.json 有 `"type": "commonjs"`（或无 type） | CJS |
| 扩展名 `.mjs` | 永远 ESM |
| 扩展名 `.cjs` | 永远 CJS |

```bash
# 验证实验
mkdir module-lab && cd module-lab
pnpm init && pnpm pkg set type=module
echo 'export const who = "esm";' > lib.js
echo 'import { who } from "./lib.js"; console.log(who);' > main.js
node main.js   # 输出 esm
```

**验证方法**: 把 `type` 改回 `commonjs` 再运行，观察报错——这是理解解析规则的最好方式。

## 🛠️ 实践：`exports` 字段设计公共 API

`exports` 是现代包定义入口的标准方式，同时起到"封箱"作用——未列出的路径外部无法导入。

```json
{
  "name": "@quest/utils",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    },
    "./cli": "./dist/cli.js",
    "./internal/*": null
  }
}
```

条件键说明：

- `types`：TypeScript 消费者定位类型声明
- `import`：ESM 消费者使用
- `require`：CJS 消费者使用
- 匹配顺序先到先得：`node-addons` → `node` / `import` / `require` → `default`
- `"./internal/*": null`：显式禁止外部深层导入

内部子路径别名用 `imports` 字段（以 `#` 开头）：

```json
{
  "imports": {
    "#config": "./src/config.js",
    "#lib/*.js": "./src/lib/*.js"
  }
}
```

```js
// 任何位置都能稳定导入，不受相对路径层级影响
import { config } from "#config";
```

## 🔍 模块解析：从标识符到文件

`import x from "y"` 时 Node 按以下顺序查找：

1. **内置模块**：`node:fs`、`path` 等直接命中（建议始终加 `node:` 前缀）
2. **相对/绝对路径**：`./lib.js`——**ESM 必须写全扩展名**（不像 CJS 可省略）
3. **裸说明符**（bare specifier）：如 `hono`，沿当前目录逐级向上找 `node_modules/<pkg>`，读取其 `exports` 字段定位入口

目录索引行为差异：

```js
import { x } from "./utils/index.js";  // ✅ 必须写全
import { x } from "./utils";           // ❌ ESM 不再自动补 index.js
```

TypeScript 项目用 `.js` 后缀指向 `.ts` 源文件（编译期映射），或直接用 `#` 别名避开烦恼。

## 🎨 最佳实践

- ✅ **新项目一律 ESM**：`"type": "module"` + `.js` 全扩展名
- ✅ **内置模块加 `node:` 前缀**：区分来源且未来兼容性更好
- ✅ **发布库必写 `exports`**：显式控制 API 面，双格式（import/require）双构建
- ❌ **不要在 ESM 里用 `__dirname`**：改用 `import.meta.dirname`（Node 20.11+ 稳定）
- ❌ **不要在 ESM 文件里调用 `require`**：作用域中不存在，需用 `createRequire` 桥接

## ❓ 常见问题

### Q1: `ERR_MODULE_NOT_FOUND` 但文件明明存在？

**A**: 九成是缺扩展名。ESM 要求 `./utils.js` 而非 `./utils`；TypeScript 源码中写 `./utils.js`（指向编译目标）或 `.ts`（Node 原生运行时）。

### Q2: `require is not defined in ES module scope`？

**A**: 当前是 ESM 上下文。用 `await import("...")` 或 `import { createRequire } from "node:module"; const require = createRequire(import.meta.url);` 桥接。

## 🎯 练习与实践

### 练习一：解析规则实验

**任务要求**:
1. 按"`type` 字段验证实验"复现两种报错并解释原因
2. 把一个 `.js` 改名为 `.mjs`，观察在 `type: commonjs` 项目中仍可 ESM 运行

### 练习二：发布一个双格式迷你包

**挑战任务**:
- 用 `tsc` 分别构建 ESM 与 CJS 两个产物
- 写出含 `types`/`import`/`require` 条件的 `exports` 字段
- 在另一个项目中分别以两种方式导入验证

**提示**: `tsc` 单次构建只能输出一种模块格式，需要两次构建或用 tsup 等打包工具。

---

## 🔗 相关文档

- 📄 **[现代 JS 语法速查](../reference/language-concepts/01-js-modern-syntax.md)** — import 写法变体与元属性
- 📄 **[Node 核心模块 API](../reference/language-concepts/03-node-core-api.md)** — `module` 与 `process` 相关 API
- 📄 **[常见故障排除](../reference/quick-references/02-troubleshooting.md)** — ESM 兼容坑集中排查
