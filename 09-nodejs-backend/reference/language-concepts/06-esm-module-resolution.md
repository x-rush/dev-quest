# ESM 与模块解析速查

> **文档简介**: package.json 的 `exports`/`imports` 字段、Node 的解析算法与 TypeScript 的解析策略速查——"import x from 'y' 如何落到一个真实文件"的全链路

> **目标读者**: 发布 npm 包、配置 monorepo 或排查模块解析报错的 Node 开发者

> **前置知识**: [模块系统与 ESM](../../basics/03-modules-esm.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#ESM` `#exports` `#imports` `#模块解析` `#moduleResolution` |
| **更新日期** | `2026年9月` |

</details>

## 1. 解析算法：标识符 → 文件

### 定义
Node 按说明符类型分派解析：内置模块直接命中；相对/绝对路径按文件系统解析（ESM 必须带扩展名）；裸说明符（bare specifier）沿目录树逐级向上找 `node_modules/<pkg>`，再读包的 `exports` 字段定位。

### 语法与示例

```ts
import fs from "node:fs";        // 1) 内置模块：直接命中（建议始终带 node: 前缀）
import { add } from "./add.js";  // 2) 相对路径：ESM 必须写全扩展名
import { Hono } from "hono";     // 3) 裸说明符：node_modules/hono → 读 exports 字段
```

### 陷阱
- ESM 不会自动补 `index.js` 与扩展名（CJS 才会）——`./utils` 报 `ERR_MODULE_NOT_FOUND`，写 `./utils.js`
- 解析以"最近的 package.json"为准：嵌套目录换了 `type` 字段，同名 `.js` 会解析成不同模块体系

## 2. exports 字段：包的公共 API

### 定义
`exports` 同时定义入口映射与按包名导入时的公共边界：列出的子路径外部可导入，未列出的路径一律拒绝（`ERR_PACKAGE_PATH_NOT_EXPORTED`）。新库可显式定义，存量库新增时要评估深层导入兼容性。

### 语法与示例

```json
{
  "name": "@quest/utils",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",   // ESM 消费者
      "require": "./dist/index.cjs"  // CJS 消费者
    },
    "./fmt": "./dist/fmt.js",        // 子路径：import "@quest/utils/fmt"
    "./internal/*": null             // 显式封箱：深层导入被拒绝
  }
}
```

```ts
import { who } from "@quest/utils";          // ✅ 命中 "." 主入口
import { fmt } from "@quest/utils/fmt";      // ✅ 命中 "./fmt" 子路径
import x from "@quest/utils/dist/index.js";  // ❌ ERR_PACKAGE_PATH_NOT_EXPORTED
```

条件键按声明顺序先到先得：`node-addons` → `node`/`import`/`require` → `default`。**`types` 必须放最前**，让类型条件优先匹配，避免其他条件先匹配后选到不合适的声明入口。

### 陷阱
- 条件顺序不是"按运行时挑最优"，而是**第一个匹配即胜出**——`node` 写在 `import` 前会让 ESM 消费者也拿到 node 条件产物
- 包内相对路径导入不受 `exports` 约束（仅外部消费者受限）
- 不写 `exports` 时包退回"全开放"（`main` + 目录直通），新包不建议

## 3. imports 字段：包内别名（Node 版 import maps）

### 定义
`imports` 定义以 `#` 开头的**包内部**子路径别名，仅本包代码可用，外部导入 `#xxx` 直接报错。应用项目同样可用（monorepo 内稳定引用，不受相对路径层级影响）。

### 语法与示例

```json
// 包内（node_modules/@quest/utils/package.json）
{
  "imports": {
    "#config": "./src/config.js",
    "#lib/*.js": "./src/lib/*.js"
  }
}
```

```ts
// 包内任何深度的文件都能稳定导入
import { config } from "#config";      // → ./src/config.js
import { env } from "#lib/env.js";     // → ./src/lib/env.js（* 通配）
```

### 陷阱
- `#` 别名只在定义它的那个 package.json 作用域内有效——跨包引用会 `ERR_PACKAGE_IMPORT_NOT_DEFINED`
- 别名键必须以 `#` 开头（与 npm scope 语法区分开）
- 模式别名 `#lib/*.js` 的 * 是子路径字符串替换，匹配内容可以包含斜杠和多层路径，两侧文字必须原样对应

## 4. TypeScript 解析策略：Node16+/NodeNext

### 定义
`tsconfig.json` 的 `"module": "node16"/"nodenext"`（配套 `"moduleResolution": "node16"/"nodenext"`）让 tsc 按 **Node 真实算法**解析：读 `exports` 的 `types` 条件、要求相对导入写全扩展名、以最近 package.json 的 `type` 判定模块格式。旧的 node/node10 解析策略（并非 bundler 策略）允许省略扩展名，产出的代码在 Node 下跑不起来。

### 语法与示例

```json
{
  "compilerOptions": {
    "module": "nodenext",
    "moduleResolution": "nodenext"
  }
}
```

```ts
// 源码写 .js 指向 .ts 源文件（编译后扩展名保持正确）
import { add } from "./add.js";   // 源文件是 add.ts
```

### 陷阱
- `module: nodenext` 下省略扩展名直接编译报错——这正是它"所见即所跑"的价值
- 三方包类型找不到时先查它的 `exports.types` 条件，再查本项目的 `moduleResolution`
- 不要把 `node file.ts` 当作跨版本的 TypeScript 运行方案。较新的 Node 可以在受限条件下做 TypeScript 类型擦除，较旧版本会拒绝 `.ts`；它也不替代 `tsc` 的完整类型检查。需要可移植部署时，先编译为 `.js`，再运行产物。

## 5. 高频报错速查

| 错误码 | 场景 | 修复 |
|--------|------|------|
| `ERR_MODULE_NOT_FOUND` | 相对导入缺扩展名/缺文件 | 补全 `./x.js` |
| `ERR_PACKAGE_PATH_NOT_EXPORTED` | 导入了 `exports` 未开放的子路径 | 走官方入口，或包自己补 exports |
| `ERR_PACKAGE_IMPORT_NOT_DEFINED` | 在作用域外使用 `#` 别名 | 别名仅限定义它的包内使用 |
| `ERR_INVALID_PACKAGE_TARGET` | 包的 exports 目标路径写错 | 锁旧版或向包提 issue |
| `ERR_UNSUPPORTED_DIR_IMPORT` | 导入目录（ESM 不补 index.js） | 写全 `./dir/index.js` |

### 可运行的解析边界实验

以下程序不依赖网络或已安装包：它在临时目录创建一个 ESM 包和一个消费者，再通过**包名**导入公开入口。`exports` 只开放 `.`，因此深层路径被拒绝；程序同时验证相对 `.mjs` 导入仍按文件路径工作。运行 `node esm-resolution-demo.mjs` 应输出两行固定结果。

<!-- terra-thirteenth-case: node-exports-resolution -->
```js
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const root = await mkdtemp(join(tmpdir(), "esm-resolution-"));
try {
  const packageDir = join(root, "node_modules", "@demo", "math");
  await mkdir(packageDir, { recursive: true });
  await writeFile(join(packageDir, "package.json"), JSON.stringify({
    name: "@demo/math", type: "module", exports: { ".": "./index.mjs" },
  }));
  await writeFile(join(packageDir, "index.mjs"), "export const add = (a, b) => a + b;\n");
  await writeFile(join(packageDir, "secret.mjs"), "export const secret = 1;\n");
  await writeFile(join(root, "relative.mjs"), "export const label = 'relative-ok';\n");
  await writeFile(join(root, "consumer.mjs"), [
    "import { add } from '@demo/math';",
    "import { label } from './relative.mjs';",
    "console.log(`sum=${add(2, 3)} ${label}`);",
    "try { await import('@demo/math/secret.mjs'); }",
    "catch (error) { console.log(`blocked=${error.code}`); }",
  ].join("\n"));
  await import(`${pathToFileURL(join(root, "consumer.mjs")).href}?case=1`);
} finally {
  await rm(root, { recursive: true, force: true });
}
```

---

<!-- full-library-explanation -->
## 类型检查通过之后还要运行构建产物

前置是 package.json、ESM 与 TypeScript 编译。导入路径在编辑器、编译器、打包器和 Node 中可能由不同规则解析。paths 别名让 TypeScript 找到类型，并不自动重写运行时 import；应用若直接运行 tsc 产物，就必须选择 Node 能理解的路径与包配置。Bundler 模式适合确实交给打包器处理的工程，不应为消除报错而随意切换。

包的 exports 定义公共入口，不是文件系统安全沙箱。条件对象按键顺序匹配，types 给类型工具，import/require 给对应加载方式；两种产物还需要与模块格式匹配的声明文件。发布双格式包时，ESM 与 CJS 入口若各自创建一份缓存或类定义，可能出现状态分裂与 instanceof 不一致，不能只验证两边都能 import。

练习：建立只有 index.js 与内部 helper.js 的小包，只导出主入口。按包名导入 helper 应得到未导出路径错误，包内相对导入仍可用。再分别用 ESM 和 CJS 消费构建后的发布目录，验证导出值、类型和运行行为。修改 type 字段后重新执行测试，确认 .mjs/.cjs 与 .js 的格式判定不会被编辑器的提示掩盖。

## 🔗 相关文档

- 📄 **[模块系统与 ESM](../../basics/03-modules-esm.md)** — ESM/CJS 差异与 `type` 字段的教程
- 📄 **[常见故障排除](../quick-references/02-troubleshooting.md)** — 模块类报错的症状→定位→修复
- 📄 **[现代 JS 语法速查](./01-js-modern-syntax.md)** — import 语法变体与元属性


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
