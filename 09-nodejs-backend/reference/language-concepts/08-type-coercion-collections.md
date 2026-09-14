# 类型转换、相等性与内置集合

> **文档简介**: 值语义的字典式速查——`===` 与 `Object.is` 差异、`==` 转换规则、ToNumber/ToString/ToBoolean 速查、Map/Set/WeakMap/WeakSet、JSON.stringify/parse、RegExp 与 Date 基础

> **目标读者**: 需要确认"这两个值相等吗""JSON 序列化后长什么样""这个键能不能用"的开发者

> **前置知识**: [JS 核心语义](./07-js-core-semantics.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#相等性` `#类型转换` `#Map` `#JSON` `#RegExp` |
| **更新日期** | `2026年9月` |

## 1. 相等性：`===` / `Object.is` / `==`

### 定义
三种相等语义精度递增：`==`（宽松，做类型转换）、`===`（严格，不做转换）、`Object.is`（同值，修正 NaN 与 ±0 特例）。

### 三者差异速查

| 比较 | `===` | `Object.is` |
|------|-------|-------------|
| `NaN` vs `NaN` | `false` | **`true`** |
| `+0` vs `-0` | **`true`** | `false` |
| 其余同类型值 | 值比较 | 值比较 |

`Object.is` 就是 `SameValue`；Map/Set 内部用的是 **SameValueZero**——与 `Object.is` 唯一区别是 ±0 视为同键。

### `==` 转换规则速查

| 场景 | 规则 | 实测结果 |
|------|------|---------|
| `null` 与 `undefined` | 互相相等且不与第三者相等 | `null == undefined` → `true` |
| `NaN` | 与任何值都不等 | `NaN == NaN` → `false` |
| number vs string | 字符串转数字 | `'1' == 1` → `true` |
| boolean vs 任意 | boolean 先转数字 | `true == 1` → `true` |
| object vs 原始值 | 对象做 ToPrimitive 再比 | `[] == 0`、`'' == 0` → `true` |

**结论**：业务代码一律 `===`；需要区分 NaN/±0（如缓存键、哨兵值）用 `Object.is`。

## 2. 类型转换三件套

### 定义
抽象操作 `ToNumber`/`ToString`/`ToBoolean` 是隐式转换的底层规则，显式写 `Number(x)`/`String(x)` 走同一套逻辑。

### ToNumber 实测速查

| 输入 | 结果 | 备注 |
|------|------|------|
| `''` / `'   '` | `0` | 空串是 0，最易踩坑 |
| `'12px'` | `NaN` | `parseInt('12px')` 才是 `12` |
| `null` | `0` | |
| `undefined` | `NaN` | null 与 undefined 不对称 |
| `[]` | `0` | 空数组 toString 得 `''` |
| `[5]` | `5` | 单元素数组 |
| `'0b11'` / `' 42 '` | `3` / `42` | 支持进制前缀与首尾空白 |

### ToString 实测速查

| 输入 | 结果 |
|------|------|
| `null` / `undefined` | `'null'` / `'undefined'` |
| `[1,2]` | `'1,2'`（join） |
| `{}` | `'[object Object]'` |
| `Symbol('s')` | **TypeError**（模板字符串里也会抛） |

### ToBoolean：唯一值得背的 falsy 八个
`false`、`0`、`-0`、`0n`、`''`、`null`、`undefined`、`NaN`。其余全为真——包括 `{} `、`[]`、`'0'`、`'false'`。

```ts
if (value) {}                          // 判空要显式：
if (value == null) {}                  // 同时覆盖 null 与 undefined
if (Array.isArray(arr) && arr.length) {}
```

## 3. Map / Set / WeakMap / WeakSet

### 定义
键值集合与去重集合，键相等采用 SameValueZero；Weak 系列持有键的弱引用，不阻止 GC。

### 语义速查（Node 24 实测）

```ts
const m = new Map();
m.set(NaN, "n");        m.get(NaN);          // "n"：NaN 可作键（SameValueZero）
m.set(-0, "neg");       m.get(0);            // "neg"：+0 与 -0 同键
new Set([1, "1", NaN, NaN, -0, 0]).size;     // 4：NaN 与 ±0 各去重一次

const wm = new WeakMap();
wm.set("str", 1);                            // TypeError：键必须是对象
const sym = Symbol("k");  wm.set(sym, 1);    // ✅ 未注册 Symbol 可作键
```

| 特性 | Map/Set | WeakMap/WeakSet |
|------|---------|-----------------|
| 键类型 | 任意值 | 仅对象（和未注册 Symbol） |
| 可迭代 | ✅ 按插入序 | ❌（不可枚举，因 GC 时机不确定） |
| `size` / `clear()` | ✅ | ❌ |
| GC 影响 | 强引用，键不回收 | 键的其他引用消失后条目可被回收 |

典型用途：WeakMap 做"附加到对象上的私有元数据"（随对象一起回收），Map 做缓存（注意自行用 LRU 防泄漏）。

## 4. JSON.stringify / parse

### 定义
JSON 是 JS 对象字面量的子集：序列化会**静默丢弃**部分值，理解丢弃规则是排错关键。

### 序列化规则速查（Node 24 实测）

```ts
JSON.stringify({ a: undefined, b: null });   // '{"b":null}'：undefined 属性被丢弃
JSON.stringify([undefined, 1]);              // '[null,1]'：数组中变 null
JSON.stringify({ d: new Date(0) });          // '{"d":"1970-01-01T00:00:00.000Z"}'：走 toJSON
JSON.stringify({ x: 1, y: 2 }, ["y"]);       // '{"y":2}'：白名单数组
JSON.stringify({ x: 1 }, (k, v) => k === "x" ? v * 2 : v);  // '{"x":2}'：replacer 函数
JSON.stringify({ x: 1 }, null, 2);           // 缩进 2 空格
JSON.parse('{"x":2}', (k, v) => typeof v === "number" ? v + 1 : v);  // { x: 3 }：reviver

JSON.stringify({ b: 1n });                   // TypeError：BigInt 不支持
const o = {}; o.self = o; JSON.stringify(o); // TypeError：循环引用
```

### 陷阱
- ❌ 直接 `JSON.stringify` 可能含循环引用的对象——上线即炸
- ✅ 需要安全序列化时捕获 TypeError，或用带循环保护的库（flatted 等）
- ❌ 把 `undefined` 字段当"会输出成 null"——对象属性里是**整个键消失**，字段校验器会报 required
- ✅ 想保留字段请显式 `null`
- `JSON.parse` 数字统一走 double，64 位整型 ID 先转字符串再序列化

## 5. RegExp 与 Date 基础

### RegExp

```ts
const re = /(?<year>\d{4})-(?<month>\d{2})/d;   // d：匹配位置索引
const r = re.exec("2026-09-14");
r.groups.year;          // "2026"
r.indices.groups.month; // [5, 7]

const g = /a/g;  g.lastIndex = 1;  g.exec("aaa")[0];  // "a"，exec 后 lastIndex=2
"foo".matchAll(/o/g);      // 必须带 g，否则 TypeError
/a.b/s.test("a\nb");       // s：dotAll，让 . 匹配换行
/o/y.exec("foo");          // y：粘性，只从 lastIndex 匹配（此处 null）
new RegExp("a\\d", "u");   // 字符串构造注意反斜杠双写
```

- `/g`、`/y` 的正则**有状态**（`lastIndex`），同一个实例复用于多处会互相干扰；需要复用时每次 `new` 或重置
- 拆分字符串优先 `matchAll` 而非反复 `exec`

### Date

```ts
new Date("2026-09-14T00:00:00Z").getTime();  // 1789344000000（毫秒时间戳）
new Date("nope").getTime();                  // NaN；字符串形式是 "Invalid Date"
Date.now();                                  // 当前毫秒时间戳，最快
d.toISOString();                             // 恒为 UTC 的 ISO 字符串
d.getFullYear();                             // 本地时区取值；getUTCFullYear() 才是 UTC
```

- 字符串解析除 ISO 8601 外**不保证跨引擎一致**，输入非 ISO 时先自行解析
- 只做加减比较用毫秒时间戳（`Date.now()`）；涉及时区展示用 `Intl.DateTimeFormat` 或 Temporal（提案中）

## 🔗 相关文档

- 📄 **[JS 核心语义](./07-js-core-semantics.md)** — 原型链、this 与闭包
- 📄 **[全局对象速查](./09-globals-reference.md)** — `structuredClone` 深拷贝与 Web 标准全局
- 📄 **[常见故障排除](../quick-references/02-troubleshooting.md)** — 类型相关报错排查
- 🌐 **[MDN: Equality comparisons and sameness](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Equality_comparisons_and_sameness)** — 相等性权威对比

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
