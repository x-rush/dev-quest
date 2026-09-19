# JavaScript 内置能力：从输入到结果

本页用于浏览器前端、React Native 和 Node.js 共用的基础查阅。前置知识：变量、函数、数组、对象；术语不熟先看[关键词入口](javascript-keywords.md)。范围是高频标准能力及其重要边界，并非所有标准对象每个方法的逐项手册。

## 数据清洗的完整例子

保存为 `builtins.mjs`，执行 `node builtins.mjs`。预期输出是 `2,7,10`、`19`、`false`、`true`、`true`，各占一行。

```js
const raw = ["7", "2", "bad", "10", "2"];
const numbers = raw.map(Number).filter(Number.isFinite);
const unique = [...new Set(numbers)].sort((a, b) => a - b);
console.log(unique.join(","));
console.log(unique.reduce((sum, item) => sum + item, 0));
console.log(Number.isNaN("bad"));
console.log(Number.isNaN(Number("bad")));
console.log(Object.hasOwn({ title: "read" }, "title"));
```

逐步解释：`map` 对每一项转换；不合法数字转成 NaN，`filter` 再按有限数条件保留。`Set` 去重；展开成数组后才能调用数组排序。显式比较器使排序按数值进行。`reduce` 的初始值 0 让空数组也有定义明确的总和。这个例子接受 `"" → 0`；表单中若空串意味着“未填写”，必须在转换前检查，不能把技术转换当成业务校验。

## 转换和数值判断

| 能力 | 输入与结果 | 易错边界 |
|---|---|---|
| `Number(value)` | 转数值；失败常得到 NaN | 空串/空白字符串转 0；不是“只接受数字文本”的验证器 |
| `String(value)` | 转字符串 | 对象一般不自动转 JSON |
| `Boolean(value)` | 按真假规则转布尔 | `"false"`、`[]`、`{}` 都为 true |
| `BigInt(value)` | 创建任意精度整数 | 不能与 Number 随意混算；JSON 默认不能直接序列化 BigInt |
| `Number.isFinite` / `Number.isNaN` | 不先转换输入的数值判断 | `Number.isNaN("bad")` 为 false；全局 `isNaN` 会先转换 |
| `Number.isInteger` / `isSafeInteger` | 整数与安全整数检查 | 是整数不代表超大值仍能精确区分相邻整数 |
| `parseInt(text, radix)` | 按基数解析可用整数前缀 | `parseInt("12px", 10)` 得到 12，不能验证整个字符串 |
| `parseFloat(text)` | 解析可用小数前缀 | 同样不是严格整串校验 |
| `Math.floor` / `ceil` / `trunc` / `round` | 向下/向上/截断/就近取整 | 负数时 floor 与 trunc 不同；金钱规则应显式设计 |
| `Math.min` / `max` / `abs` / `pow` | 极值、绝对值、幂 | 极大数组不要无限展开为函数实参；`Math.random` 不用于密码学 |

## 数组：先问是否修改原数组

| 任务 | 方法 | 结果与副作用 |
|---|---|---|
| 变换每项 | `map` | 新数组；回调必须返回值；不等待 async 回调完成 |
| 保留部分 | `filter` | 新数组；内部对象仍可与原数组共享 |
| 找一个 | `find` / `findIndex` | 未找到分别为 undefined / -1 |
| 判断包含或条件 | `includes` / `some` / `every` | every 对空数组为 true，some 对空数组为 false |
| 汇总 | `reduce` | 初始值影响结果类型与空数组行为 |
| 取区间 | `slice(start, end)` | 不含 end；浅复制，不修改原数组 |
| 替换区间 | `splice(start, count, ...items)` | 修改原数组，返回被删除项 |
| 排序 | `sort(compare)` | 修改原数组；默认按字符串顺序 |
| 反转 | `reverse` | 修改原数组；需保留原值时先复制或核对复制版方法支持情况 |
| 增删端点 | `push` / `pop` / `unshift` / `shift` | 修改原数组；返回值不都相同，push 返回新长度 |
| 展平/展平映射 | `flat` / `flatMap` | 生成新数组；flatMap 只展平一层 |
| 创建/识别 | `Array.from` / `Array.isArray` | 支持由可迭代或类数组创建；typeof 数组只得到 object |

当 UI 状态要求不可变更新时，不能直接对原 state 调用 sort/splice；复制外层数组也不等于复制了其中的对象。方法契约见 [ECMAScript 数组规范](https://tc39.es/ecma262/multipage/indexed-collections.html)。

## 字符串与结构化数据

| 能力 | 用处 | 注意 |
|---|---|---|
| `trim`、`toLowerCase`、`toUpperCase` | 清理空白、大小写转换 | 返回新字符串；不自动满足特定语言的文本比较需求 |
| `includes`、`startsWith`、`endsWith` | 子串或前后缀判断 | 默认区分大小写 |
| `slice`、`split`、`join` | 截取、拆分、拼合 | 字符串 length 是 UTF-16 码元数，不能总当用户看到的字符数 |
| `replace`、`replaceAll` | 替换文本 | replace 的字符串模式只替换第一处；正则旗标影响行为 |
| `RegExp.test`、`String.match` | 模式匹配 | 带 g/y 的 RegExp 有 lastIndex 状态，重复 test 可能变结果 |
| `Object.keys/values/entries` | 枚举自有可枚举字符串键相关内容 | 不含所有继承键，也不等于包含 Symbol 键 |
| `Object.fromEntries` | 键值对组成对象 | 重复键后者覆盖；输入不是任意 JSON |
| `Object.hasOwn` | 判断自有属性 | 属性值是 undefined 仍可能存在 |
| `Object.assign` / 对象展开 | 浅层合并 | 后写覆盖；内部对象仍共享 |
| `Object.freeze` | 阻止对象本层变更 | 不递归冻结所有嵌套对象 |
| `JSON.parse/stringify` | JSON 文本与 JS 值转换 | parse 可抛异常；JSON 不是完整 JS 对象存档协议 |

JSON 序列化会受 undefined、函数、循环引用、日期和 BigInt 影响；因此 `JSON.parse(JSON.stringify(x))` 不应被描述为适合所有对象的深拷贝。宿主提供的 `structuredClone` 也有可克隆类型范围，不能克隆任意函数或类行为。字符串与 JSON 的正式契约分别见 [文本处理](https://tc39.es/ecma262/multipage/text-processing.html)与 [JSON](https://tc39.es/ecma262/multipage/structured-data.html#sec-json-object)。

## 集合、异步与异常

`Map` 存任意键的键值关系，使用 get/set/has/delete；`Set` 存唯一值。二者对对象比较使用身份：两个内容相同的新对象仍是两个键或元素。WeakMap/WeakSet 适合与对象生命周期关联的元数据，不提供普通集合那样的可枚举清单。详见[键控集合规范](https://tc39.es/ecma262/multipage/keyed-collections.html)。

| Promise 能力 | 成功结果 | 失败与取消 |
|---|---|---|
| `Promise.resolve/reject` | 创建或接纳指定结算状态 | 创建 rejected Promise 后仍要处理它 |
| `then/catch/finally` | 返回新的 Promise | finally 主要清理；它抛错会改变最终结果 |
| `Promise.all` | 按输入顺序收集成功值 | 任一失败则整体拒绝；其他工作不自动取消 |
| `Promise.allSettled` | 每项都返回状态记录 | 用于需要知道全部结果的场景 |
| `Promise.race` | 最先结算项决定结果 | “超时获胜”不代表底层请求已取消 |
| `Promise.any` | 第一个成功值 | 全失败时拒绝为 AggregateError |

`async` 创建 Promise 语义，不使 CPU 密集计算自动并行。Error/TypeError/RangeError/SyntaxError 用于表达不同失败；捕获后应决定恢复、转换或传播，避免只打印后返回假的成功。详见 [Promise 规范](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-promise-objects)。

## 还需知道名字与边界的能力

Date 表示时间点，Intl 处理语言地区相关的显示；Symbol 可作为独特属性键，Reflect/Proxy 用于对象元操作；ArrayBuffer、TypedArray、DataView 处理二进制，SharedArrayBuffer/Atomics 涉及共享内存；WeakRef/FinalizationRegistry 不适合保证及时业务清理。它们不是所有初学练习都需要的工具，遇到实际需求再展开。

全局名称完整入口见 [ECMAScript 全局对象](https://tc39.es/ecma262/multipage/global-object.html)。DOM、fetch、URL、定时器、console、structuredClone 的可用性还要查宿主；Node 内置模块另看 [Node 标准能力](../09-nodejs-backend/reference/library-guides/01-core-modules.md)。

## 练习与验收

表单“数值”先定义文本契约，再转换。下面示例只接受可选负号、整数部分和可选小数部分的 ASCII 十进制文本；它刻意拒绝空白、`Infinity`、科学计数法、千分位和半截输入。若产品需要其中任何一种，应修改契约并新增相应测试，不能只换成 `parseFloat`。

```js
function parseFiniteDecimal(text) {
  const normalized = text.trim();
  if (!/^-?(?:\d+|\d+\.\d+)$/.test(normalized)) return null;

  const value = Number(normalized);
  return Number.isFinite(value) ? value : null;
}

const raw = ["", "  ", "-2", "2.5", "8x", "8", "1e3", "1,000"];
const accepted = raw
  .map(parseFiniteDecimal)
  .filter((value) => value !== null)
  .sort((left, right) => left - right);

console.log(accepted.join(","));
console.log(accepted.reduce((sum, value) => sum + value, 0));
console.log(raw.join("|")); // 原始输入没有被修改
```

预期输出依次为 `-2,2.5,8`、`8.5` 和 `|  |-2|2.5|8x|8|1e3|1,000`。再把 `parseFiniteDecimal` 替换为 `parseInt(text, 10)`，解释为什么 `8x` 会错误混入。最后输入空数组，应输出空结果和总和 0，而不是抛异常。
