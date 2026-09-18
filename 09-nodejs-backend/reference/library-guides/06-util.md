# node:util 工具集速查

> **文档简介**: `node:util` 的字典式速查——inspect 调试输出、promisify、parseArgs 命令行解析、styleText 终端着色、types 类型判定与 deprecate，用法在 Node 24 实测

> **目标读者**: 写 CLI 工具、调试输出、迁移回调式旧 API 的开发者

> **前置知识**: [内置模块导航表](./01-core-modules.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#util` `#inspect` `#parseArgs` `#styleText` `#promisify` |
| **更新日期** | `2026年9月` |

</details>

## 1. inspect：调试输出

### 定义
`util.inspect(value, options)` 把任意值格式化为可读字符串——`console.log` 内部就是它；选项可控制深度、长度与颜色。

```ts
import { inspect } from "node:util";

const deep = { a: { b: { c: { d: 1 } } } };
inspect(deep, { depth: 0 });           // "{ a: [Object] }"：截断层级
inspect(deep, { depth: null });        // null = 不限深度
inspect(bigArray, { maxArrayLength: 10 });  // 默认 100 项，超出显示 "... N more"
inspect(obj, { colors: true });        // TTY 下高亮
inspect(obj, { getters: true });       // 求值 getter 属性
```

- 打日志前怀疑"对象打印不全"，第一反应就是 `depth` 与 `maxArrayLength` 两个选项
- 想彻底展开写 JSON 看不出的循环结构时可以使用 inspect 或调试器，并限制输出规模

## 2. promisify：回调转 Promise

### 定义
把 Node 风格 `callback(err, value)` 回调函数包装成返回 Promise 的函数；被包装函数需遵循错误优先回调约定（或带 `util.promisify.custom` 符号）。

```ts
import { promisify } from "node:util";
import { execFile } from "node:child_process";

const pExecFile = promisify(execFile);
const { stdout } = await pExecFile("node", ["--version"]);

const sleep = promisify(setTimeout);   // 实测可用，resolve undefined
await sleep(500);

// 自定义 Promise 版：回调签名不规范时
const legacy = (a: number, cb: (err: null, v: number) => void) => cb(null, a * 2);
(legacy as any)[promisify.custom] = (a: number) => Promise.resolve(a * 2);
const pLegacy = promisify(legacy as any);
await pLegacy(21);   // 42
```

### 陷阱
- ❌ 对回调签名是 `(cb(value))`（无错误位）的旧函数直接 promisify——返回值会被误当作 error，可能错误拒绝或丢失结果
- ✅ 先读签名；多参数回调只保留第一个值，其余丢弃，需要多个返回值就自己包一层
- 现代 API（fs/promises、timers/promises）已有官方 Promise 版本，不必 promisify

## 3. parseArgs：CLI 参数解析

### 定义
`util.parseArgs({ options, args, strict, allowPositionals })` 解析命令行参数为 `{ values, positionals }`，零依赖写 CLI 的标准答案（Node 18.3+）。

```ts
import { parseArgs } from "node:util";

const { values, positionals } = parseArgs({
  args: process.argv.slice(2),
  options: {
    port: { type: "string", short: "p" },
    verbose: { type: "boolean", short: "v", default: false },
    out: { type: "string", multiple: true },  // --out a --out b 收集为数组
  },
  allowPositionals: true,      // 允许裸位置参数（默认 false，多了直接报错）
});
// args: ["--port", "3000", "-v", "extra.txt"]
values.port;       // "3000"
values.verbose;    // true
positionals;       // ["extra.txt"]
```

| 选项字段 | 类型 | 说明 |
|---------|------|------|
| `type` | `'string' \| 'boolean'` | 每个参数必须声明 |
| `short` | 单字符 | `-p` 短选项 |
| `default` | 随 type | 未提供时的值 |
| `multiple` | boolean | 可重复出现，收集为数组 |
| `strict` | boolean | 默认 true：未知参数直接抛错 |

### 陷阱
- ❌ 默认配置下出现位置参数——抛错退出，需要 `allowPositionals: true`
- ❌ 期待 `--port 3000` 解析出数字——type 只有 string/boolean，数值自己 `Number()` 转
- 复杂 CLI（子命令、自动补全提示）直接上 commander/yargs；parseArgs 定位是轻量脚本

## 4. styleText：终端着色

### 定义
`util.styleText(format, text, options)` 给字符串套 ANSI 颜色/样式，Node 20.12+ 内置，替代 chalk 的轻量场景（**注意：format 是第一个参数**）。

```ts
import { styleText } from "node:util";

styleText("red", "错误");                    // "\x1b[31m错误\x1b[39m"
styleText(["bold", "green"], "成功");        // 数组叠加样式
styleText("blue", url, { validateStream: false });  // 跳过 TTY 检测强制着色
```

| format 类别 | 取值 |
|------------|------|
| 颜色 | `red` `green` `yellow` `blue` `magenta` `cyan` `white` `gray`（前缀 `bg`/`fg` 指背景） |
| 修饰 | `bold` `dim` `italic` `underline` `strikethrough` |
| 特殊 | `reset` |

### 陷阱
- ❌ 输出被管道/重定向（非 TTY）时**默认不着色**——函数正常返回但无 ANSI 码，测试里"看不到颜色"不是 bug
- ✅ 只有明确需要验证 ANSI 序列时才传 validateStream:false；普通文件与机器输出通常应保持无颜色
- ❌ 参数顺序记反：是 `styleText(format, text)`，不是 `styleText(text, format)`——记反会抛 TypeError（实测）

## 5. types.isXxx 与 deprecate

### 定义
`util.types` 提供绕开 instanceof 的可靠类型判定（跨 realm、类数组陷阱都安全）；`util.deprecate` 包装函数标记弃用。

```ts
import { types, deprecate } from "node:util";

types.isDate(new Date());            // true
types.isPromise(new Promise(() => {}));  // true
types.isRegExp(/x/);                 // true
types.isMap(new Map());              // true
types.isNativeError(new Error());    // true（比 instanceof Error 可靠）

const oldFn = deprecate((x: number) => x, "改用 newFn()", "MYDEP001");
oldFn(1);    // 正常执行，并向 stderr 发出 DeprecationWarning
```

- `types.isNativeError(x)` 是"捕获后判断是不是错误对象"的最稳写法（跨 iframe/vm 场景）
- 自有库内弃用用 `deprecate(fn, msg, code)`；运行时警告可用 `process.emitWarning()` 直接发

<!-- full-library-explanation -->
## 调试表示、数据格式与回调契约不能混用

前置是函数、Promise 和命令行参数。inspect 面向调试者，它的输出不是稳定的 JSON 协议；开启 getters 或自定义 inspect 可能触发代码执行，记录不可信对象时要控制深度、长度和字段。将调试字符串重新 parse 来处理业务，会依赖随版本变化的展示格式。

promisify 默认期待最后一个参数是 error-first 回调。若旧函数使用 cb(value)，该 value 会被当作错误参数，而不是自动成为成功结果；对象方法还可能依赖 this，需要先绑定接收者。已有 Promise API 不需要再次包装，多个回调成功值要检查是否有自定义 promisify 实现，否则不能假定全部保留。

练习：用 parseArgs 解析 --port 3000 与 --port abc，它们都会得到字符串；下一步才做数值格式与范围验证。再为调用依赖 this.base 的旧对象方法分别使用直接 promisify 和绑定后 promisify，解释差异。测试 CLI 输出时默认不依赖 ANSI 颜色，面向机器的 JSON 输出与面向人的彩色提示应有明确出口。

## 🔗 相关文档

- 📄 **[全局对象速查](../language-concepts/09-globals-reference.md)** — console.dir 与 inspect 的关系
- 📄 **[node:child_process 子进程速查](./04-child-process.md)** — promisify(execFile) 的完整用法
- 📄 **[Node 一行式速查](../quick-references/01-node-cheatsheet.md)** — CLI 调试入口
- 🌐 **[Node.js 官方文档: util](https://nodejs.org/docs/latest/api/util.html)** — 全部工具函数权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
