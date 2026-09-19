# 现代 JavaScript 语法速查

> **文档简介**: Node 后端高频使用的现代 JS/TS 语法条目——解构、展开、可选链、私有字段、迭代器等，按"定义→语法→示例→陷阱"组织

> **目标读者**: 需要快速确认语法细节或从旧版 JS 迁移的开发者

> **前置知识**: JavaScript 基础语法

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#解构` `#可选链` `#私有字段` `#语法速查` |
| **更新日期** | `2026年9月` |

</details>

## 1. 解构赋值

### 定义
从对象/数组中按模式提取值并绑定到变量。

### 语法与示例

```ts
// 对象解构 + 重命名 + 默认值
const { name, role = "member", age: userAge } = user;

// 嵌套解构
const { address: { city } } = profile;

// 数组解构 + 跳过
const [first, , third] = list;

// 函数参数解构（后端最常见形态）
function createUser({ name, email, role = "member" }: CreateUserInput) {}

// 循环解构
for (const [key, value] of Object.entries(config)) {}
```

### 陷阱
- 解构 `null`/`undefined` 直接抛 TypeError，需给默认值：`const { a } = maybeNull ?? {}`
- 默认值只对 `undefined` 生效，`null` 不会触发默认值

## 2. 展开运算符（...）

### 定义
把可迭代对象/对象展开到另一处，用于合并、拷贝与变参。

### 语法与示例

```ts
// 对象合并（后者覆盖前者）——浅拷贝
const merged = { ...defaults, ...options };

// 数组合去重
const ids = [...new Set([...idsA, ...idsB])];

// 剩余参数收集
function sum(...nums: number[]) { return nums.reduce((a, b) => a + b, 0); }

// 排除字段（删 key 的函数式写法）
const { password, ...safeUser } = user;
```

### 陷阱
- **浅拷贝**：嵌套对象仍共享引用，深结构需 `structuredClone(value)`（Node 17+ 全局可用）
- 将大型数组展开为函数实参（如 fn(...items)）可能触发参数数量限制；[...items] 创建数组属于不同场景，但同样要考虑内存

## 3. 可选链（?.）与空值合并（??）

### 定义
安全访问深层属性；仅在左侧为 null/undefined 时取右侧值。

### 语法与示例

```ts
const city = user?.address?.city;           // 链式安全访问
const val = config.timeout ?? 3000;          // 仅 null/undefined 用默认
const fn = handler?.();                      // 可选调用
const first = list?.[0];                     // 可选索引

// 组合：读环境变量
const dbUrl = process.env.DATABASE_URL ?? "postgres://localhost:5432/app";
```

### 陷阱
- 可选链在被检查对象为 null/undefined 时短路整段连续链；若未被可选检查的后续属性本身可能缺失，需在相应位置使用 ?.。括号会截断连续链，例如 (obj?.a).b 仍可能报错
- `??` 与 `||` 不同：`0`、`""`、`false` 是合法值，用 `||` 会被误覆盖

## 4. 私有字段（#field）

### 定义
类内部真正的私有成员（非约定下划线），外部无法访问。

### 语法与示例

```ts
class ConnectionPool {
  #conns: Conn[] = [];          // 私有字段
  static #maxSize = 20;         // 私有静态
  #drain() {}                   // 私有方法

  get size() { return this.#conns.length; }
}
```

### 陷阱
- `#` 字段是运行时强制的语言特性，与 TS `private` 关键字不同：`private` 仅类型检查可绕过，`#` 不可
- `#field in obj` 可用于判断实例是否来自本类（品牌检查）

## 5. 迭代器与生成器

### 定义
统一遍历协议；生成器函数惰性产出序列，适合分页拉取与流式构建。

### 语法与示例

```ts
// 生成器：惰性分页拉取 API 全量数据
async function* fetchAllPages<T>(firstPage: Page<T>): AsyncGenerator<T> {
  let page: Page<T> | undefined = firstPage;
  while (page) {
    yield* page.items;
    page = page.next ? await fetchPage(page.next) : undefined;
  }
}

for await (const item of fetchAllPages(await fetchPage(1))) {
  processItem(item);   // 内存中永远只有当前项
}
```

### 陷阱
- 生成器体内抛错会中断迭代，消费方需 try/catch
- `yield*` 委托与 `yield` 混用时注意返回值语义

## 6. 模板字符串与标签模板

### 语法与示例

```ts
// 多行 + 插值
const msg = `用户 ${user.name} 于 ${new Date().toISOString()} 登录`;

// 标签模板：库 API 常见形态（如 sql`` ）
const rows = await sql`SELECT * FROM tasks WHERE status = ${status}`;
// 参数自动转义，杜绝拼接 SQL 注入
```

### 陷阱
- 模板字符串直接拼用户输入进 SQL/HTML 是注入漏洞，必须走库的参数化机制

## 7. 其他高频条目

### 逻辑赋值运算符
```ts
config.retry ??= 3;      // 为 null/undefined 时赋值
obj.flag ||= true;       // 假值时赋值
```

### 数组与 Object 新方法
```ts
arr.at(-1);                                 // 末尾元素
arr.findLast(x => x.ok);                    // 反向查找
await Array.fromAsync(gen);                 // 异步迭代器转数组（Node 22+）
Object.groupBy(users, u => u.role);         // ES2024 分组
Object.entries(obj) / Object.fromEntries(pairs);
```

### Error cause 链（ES2022）
**定义**：构造 `Error` 时通过第二个参数挂上原始错误，形成"包装错误 → 根因"的因果链；跨层重抛时保留根因，日志不再丢堆栈起点。

```ts
try {
  await db.user.find(id);
} catch (err) {
  throw new Error("查询用户失败", { cause: err });  // 根因挂进 cause
}

// 逐层读取链
try {
  await load();
} catch (e) {
  console.log(e.message, "->", e.cause?.message);
}
```

**陷阱**：`cause` 不会出现在默认的错误字符串里——顶层日志必须显式序列化 cause（pino 的 `err` 序列化器需开启 `cause` 递归）；包装时若吞掉原错误不挂 cause，根因就永久丢失。

---

<!-- full-library-explanation -->
## 简写语法不会替你决定缺失值的含义

前置是对象、数组与函数。解构默认值只处理 undefined，?? 处理 null 和 undefined，|| 处理所有假值。选择哪一个取决于业务：重试次数允许 0 时用 || 会错误地改回默认次数；姓名空串应报错时，用 ?? 也不会自动验证它。可选链只避免特定的空值访问，不保证函数存在且可调用，也不会吞掉函数内部异常。

完整实验保存为 syntax.mjs，运行 node syntax.mjs。它将“未提供”和“明确为 0”分开，也验证浅拷贝的嵌套引用：

<!-- node-python-p1-final-case: node-modern-syntax-contracts -->
```js
const settings = { retries: 0, label: null };
const { label = 'untitled' } = settings;
const original = { tags: ['node'] };
const copy = { ...original };
copy.tags.push('js');

const report = [
  `fallback=${settings.retries || 3}/${settings.retries ?? 3}/${String(label)}`,
  `shared=${original.tags.join(',')}`,
];
if (report.join(';') !== 'fallback=3/0/null;shared=node,js') {
  throw new Error(`Unexpected syntax contract: ${report.join(';')}`);
}
console.log(`modern-syntax: ${report.join('; ')}`);
```

预期输出 `modern-syntax: fallback=3/0/null; shared=node,js`。`||` 将 0 当作假值，`??` 只替换 null/undefined；解构默认值只替换 undefined，所以 label 仍是 null。第二个字段说明展开只复制外层属性，嵌套数组仍共享。练习：改成 structuredClone 后，原数组应保留 node；再给对象加入函数，观察该克隆方法并非适用于所有对象。对象展开枚举自身可枚举属性，与数组展开所需的迭代协议是两种不同机制，不应混为“任意对象都能展开成数组”。

## 🔗 相关文档

- 📄 **[模块系统与 ESM](../../basics/03-modules-esm.md)** — import 语法与模块解析教程
- 📄 **[TypeScript 模式](./05-typescript-patterns.md)** — 类型层面的 Node 常用模式
- 📄 **[异步 API 全表](./02-async-api.md)** — 异步语法与 API 字典


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
