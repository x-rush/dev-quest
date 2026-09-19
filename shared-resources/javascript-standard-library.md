# JavaScript 标准库：核心对象、宿主能力与选型边界

本页是 Next.js、TanStack、React Native 与 Node.js 共用的 JavaScript 标准库入口。先读[关键词](javascript-keywords.md)理解语法，再读[内置能力](javascript-builtins.md)掌握高频转换、数组和 Promise；本页回答“某个对象属于 ECMAScript、浏览器、Node 还是移动端宿主，以及什么时候该用它”。

“标准库”在 JavaScript 中有两层含义：ECMAScript 定义的 `Array`、`Map`、`Promise`、`Date`、`Intl`、`JSON` 等对象在合规运行时中可用；`fetch`、`URL`、`localStorage`、`setTimeout`、DOM、文件系统和原生桥接由宿主提供，名字相同也可能能力不同。写跨端代码时先确认运行时，不要只因编辑器补全就假定 API 存在。

## 先按问题选对象

| 问题 | 首选能力 | 不要误用成 |
|---|---|---|
| 变换、筛选、聚合一组值 | `Array.prototype.map/filter/reduce` | 对有副作用或异步并发任务盲目 `forEach(async ...)` |
| 用稳定键查找数据 | `Map` | 把任意键都塞进普通对象并忽略原型/键转换 |
| 记录唯一成员 | `Set` | 用数组 `includes` 在大量去重场景反复线性查找 |
| 处理时间点 | `Date` 的时间戳或 `Temporal`（若目标运行时支持） | 把本地显示字符串当作可交换的时间协议 |
| 本地化显示数字、日期、货币 | `Intl.NumberFormat/DateTimeFormat` | 手工拼接语言、货币和时区格式 |
| 解析或生成 JSON 协议 | `JSON.parse/stringify` | 把 JSON 当成任意 JavaScript 对象的深拷贝方案 |
| 取消支持 AbortSignal 的工作 | `AbortController` | 仅用 `Promise.race` 宣称已经停止底层请求 |
| 处理二进制 | `ArrayBuffer`、TypedArray、`DataView` | 以 UTF-16 字符串保存任意字节 |

## ECMAScript 集合与数据对象

### Array、Map、Set

`Array` 保留顺序，适合列表展示；`Map` 按键保存值，适合缓存、索引和对象键；`Set` 只保留唯一值。`Map`/`Set` 对对象使用引用身份：两个字段相同但分别创建的对象不是同一个键。

<!-- verification-case: shared-js-standard-library-map-set -->
```js
const first = { id: "a" };
const sameShape = { id: "a" };
const index = new Map([[first, "saved"]]);

console.log(index.get(first));     // saved
console.log(index.get(sameShape)); // undefined

const ids = new Set(["a", "a", "b"]);
console.log([...ids].join(","));  // a,b
```

在 Node 运行此完整片段时，预期输出依次是 `saved`、`undefined`、`a,b`。它只验证 ECMAScript `Map`/`Set` 的身份和去重语义，不证明浏览器缓存、React 状态或跨端存储行为。

若业务身份来自 API，应优先使用稳定字符串或数字 ID 作为键。把整个响应对象作为键会在每次重新获取后失去命中。`WeakMap` 与 `WeakSet` 只能用对象键且不可枚举，适合给对象附加不控制其生命周期的元数据；它们不适合构建需要列出全部成员的业务缓存。

### Object、Reflect 与 Proxy

普通对象适合固定字段的记录；`Object.keys`、`values`、`entries` 只枚举自有、可枚举的字符串键。读取未知键前使用 `Object.hasOwn(value, key)`，避免把继承属性误当作输入字段。对象展开和 `Object.assign` 都是浅复制，嵌套对象仍共享。

`Reflect` 和 `Proxy` 用于元编程，例如框架的拦截、表单追踪或兼容层。它们会使调用路径难追踪，也可能破坏优化和类型推断；普通应用状态优先用显式函数和数据结构。不要用 `Proxy` 绕过只读、权限或输入校验。

## 文本、时间、国际化与 JSON

### String、RegExp 与 Unicode

字符串不可变，`replace` 返回新值。用户看到的“一个字符”不总等于 `string.length` 的一个 UTF-16 码元；涉及截断、光标或用户名长度时，应按产品规则处理 Unicode 分段，而不是直接切片。带 `g` 或 `y` 标记的 `RegExp` 会维护 `lastIndex`，复用同一个实例连续 `test` 可能得到不同结果。

正则适合格式筛选，不替代业务规则。例如邮箱正则不能证明地址存在；密码格式检查不能替代服务端哈希和速率限制。

### Date 与 Intl

`Date` 的可靠交换值是时间戳或带时区的 ISO 约定。日期字符串的解析有格式和时区陷阱；由服务端规定输入格式，客户端只做展示和明确转换。`Intl.DateTimeFormat`、`Intl.NumberFormat`、`Intl.Collator` 根据语言和时区格式化值；相同时间点在不同用户设置下显示不同是正常结果。

```js
const instant = new Date("2026-09-20T08:00:00.000Z");
const formatter = new Intl.DateTimeFormat("zh-CN", {
  dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Shanghai",
});
console.log(formatter.format(instant));
```

上例只验证显示指定时区，不是日期业务规则。预约、账期、重复事件和跨时区截止时间需要另行定义时区、日历和边界包含关系。

### JSON 与 structuredClone

`JSON.parse` 可能抛错，且得到的字段仍是不可信输入；先检查形状与范围。`JSON.stringify` 会忽略或改变 `undefined`、函数、Symbol、循环引用、`BigInt` 与部分对象语义。`structuredClone` 覆盖更多数据类型，但也不能克隆函数、DOM 节点或任意类行为。选择复制方式前先写出需要保留什么，而不是寻找一个“万能深拷贝”。

## 异步与取消

`Promise.all` 适合“全部成功才继续”；`allSettled` 用于汇总每项结果；`any` 寻找首个成功；`race` 只选择先结算者。它们不会自动取消尚在进行的网络、定时器或 I/O。

```js
async function loadProfile(id, signal) {
  const response = await fetch(`/api/profiles/${encodeURIComponent(id)}`, { signal });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

const controller = new AbortController();
const task = loadProfile("42", controller.signal);
controller.abort();
await task.catch((error) => console.log(error.name)); // AbortError（支持 AbortSignal 的 fetch）
```

取消是接口契约：只有下游接受 `signal` 才可能停止工作；调用方还要决定如何忽略已过期结果。前端请求竞态见 Next.js 和 TanStack 的数据获取文章，Node 资源取消见 Node 模块的异步章节。

## 宿主能力地图

| 能力 | 浏览器 / Next.js 客户端 | Next.js 服务端 / Node | React Native | 使用前检查 |
|---|---|---|---|---|
| `fetch`、`URL`、`AbortController` | 通常可用 | 以目标 Node/框架版本为准 | 以目标 RN/Expo 版本为准 | 超时、取消、凭据与缓存语义 |
| DOM、`window`、`document` | 仅浏览器 | 不可直接使用 | 不可直接使用 | 是否在客户端组件、是否有 SSR 保护 |
| `localStorage` | 浏览器存储 | 不可直接使用 | 不是浏览器 API | 隐私、配额、同步读取与替代存储 |
| 文件系统、子进程 | 通常不可用 | Node `node:*` 模块 | 通过平台/Expo API | 权限、路径、打包与平台差异 |
| 定时器 | 可用但可能被页面生命周期限制 | 可用但会影响进程退出 | 受应用生命周期限制 | 清理、后台行为与测试时钟 |

宿主地图只给方向，不承诺每个版本都有同一实现。练习工程应在目标平台运行并记录版本；平台 API 与权限模型另看各模块的标准库或框架参考。

## 练习与验收

为一个“最近搜索”功能选择数据结构：用 `Map` 按稳定 ID 保存结果、用数组保存显示顺序、用 `AbortController` 取消过期请求、用 `Intl` 显示时间。验收时做以下输入：同一 ID 重复返回、两个不同对象但同一 ID、慢请求晚于新请求返回、存储 JSON 损坏、切换语言或时区。记录每种输入的界面或函数结果，并说明哪些能力属于 ECMAScript、哪些依赖宿主。

本页不把上述示例视为已在浏览器、Node 和移动设备全部运行的证据；运行时覆盖以各模块的具名验证报告为准。ECMAScript 对象的权威定义见 [ECMA-262](https://tc39.es/ecma262/)，宿主 API 以目标平台官方文档和实际构建结果为准。
