# TypeScript 类型收窄与类型守卫

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `language-concepts`

## 📌 定义

**类型收窄（Narrowing）** 是 TypeScript 编译器基于控制流分析，把联合类型（`A | B | C`）在分支内自动缩小为更具体成员的机制——不需要额外类型转换，但仍需运行时检查，例如用 `if`/`switch` 做了"可判定"的检查，类型就跟着变窄。**类型守卫（Type Guard）** 是触发收窄的检查手段：语言内置的 `typeof`/`instanceof`/`in`/字面量相等，以及你自己编写的 `x is T` 守卫函数与 `asserts` 断言函数。收窄是 TypeScript 安全性的核心一环：它让"先判断、再使用"的代码获得精确类型，而不需要 `as` 强转。

## 📖 语法/签名

### 内置收窄手段

| 手段 | 形式 | 收窄效果 |
|------|------|----------|
| `typeof` | `typeof x === 'string'` | 原始类型联合按 JS 类型收窄 |
| `instanceof` | `x instanceof Err` | 类/构造函数实例收窄到该类 |
| `in` | `'fly' in a` | 按属性存在性收窄到含该属性的成员 |
| 字面量相等 | `x.kind === 'circle'` / `switch` | **判别联合**收窄，最常用 |
| 真值判断 | `if (x)` | 排除 `null`/`undefined`，但也会排除 `0`/`''`/`false` |
| 自定义守卫 | `function f(x): x is T` | 返回 true 的分支把参数收窄为 T |
| 断言函数 | `function f(x): asserts x is T` | 通过则收窄，不通过则抛错 |
| `never` 赋值 | `const _e: never = x` | 穷尽性检查：漏分支时编译报错 |

### 判别联合（tagged union）与守卫签名

```ts
// 判别联合：每个成员共享一个字面量类型属性（kind），类型各不相同
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'square'; size: number }

// 类型守卫函数：返回值写成 "x is T" 谓词
function isCircle(s: Shape): s is Extract<Shape, { kind: 'circle' }> {
  return s.kind === 'circle'
}

// 断言函数：返回值写成 "asserts x is T"，不满足时应抛错
function assertDefined<T>(v: T | undefined | null, msg = 'unexpected empty'): asserts v is T {
  if (v == null) throw new Error(msg)
}
```

## 💡 示例

### 判别联合 + `never` 穷尽检查

```ts
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'square'; size: number }
  | { kind: 'triangle'; base: number; height: number }

function area(s: Shape): number {
  switch (s.kind) {
    case 'circle':   return Math.PI * s.radius ** 2
    case 'square':   return s.size ** 2
    case 'triangle': return (s.base * s.height) / 2
    default: {
      const _exhaustive: never = s // 所有分支都处理后，此处 x 已是 never
      return _exhaustive
    }
  }
}
// 未来给 Shape 新增 { kind: 'rect' } 变体时，上面 default 分支立即编译报错
// （TS2322: 不能把新变体赋给 never），提醒你补分支
```

### 类型守卫函数（含 `filter` 场景）

```ts
type Event2 = { kind: 'circle'; payload: { radius: number } } | { kind: 'rect'; payload: null }

type CircleEvent = Extract<Event2, { kind: 'circle' }>

function isCircleEvent(e: Event2): e is CircleEvent {
  return e.kind === 'circle'
}

function handleAll(events: Event2[]) {
  // 原地判断：收窄后可直接访问 payload.radius
  for (const e of events) {
    if (isCircleEvent(e)) console.log(e.payload.radius)
  }
  // 过滤：类型谓词让 filter 返回收窄后的数组
  const circles: CircleEvent[] = events.filter(isCircleEvent)
}
```

### 断言函数：集中处理 `undefined`

```ts
function assertDefined<T>(v: T | undefined | null, msg = 'unexpected empty'): asserts v is T {
  if (v == null) throw new Error(msg)
}

function render(id: string | undefined) {
  assertDefined(id, '缺少 id')
  return id.toUpperCase() // 收窄为 string，无需 ! 或 as
}
```

### 解构判别联合（与 React Hooks 的关系）

```ts
// 06 篇 useFormStatus 的返回值就是判别联合：
// { pending: true; data: FormData } | { pending: false; data: null }
const { pending, data } = useFormStatus()
if (pending) {
  data?.append('k', 'v') // 判别量解构后，data 同步收窄
}
```

> **版本边界**：TS 4.4 支持条件别名分析；TS 4.6 扩展了对解构判别联合的控制流分析。const 解构以及未重新赋值的解构参数可以保留关联，不能泛化为任何可变变量或任意别名都能同步收窄。

## ⚠️ 常见陷阱

- ❌ **通过第二个引用访问，收窄失效**：`const alias = e; if (e.kind === 'circle') { alias.radius }` —— 收窄只绑定到被检查的引用 `e`，别名 `alias` 仍是完整联合（应在实际编译配置中验证）。✅ 始终用同一引用访问，或把收窄后的引用存入新变量：`if (e.kind === 'circle') { const c = e }`。
- ❌ **在参数位置解构非共有属性**：`function f({ kind, payload }: Shape)` —— `payload` 若不存在于所有变体，解构本身就报 TS2339（联合类型尚未收窄，无法解构其成员）。✅ 先判别、再在分支内解构：`function f(s: Shape) { if (s.kind === 'circle') { const { radius } = s; ... } }`。
- ❌ **把判别比较包进函数后期待收窄**：`const isA = () => e.t === 'a'; if (isA()) { e.x }` —— 编译器无法跨函数调用分析布尔值（闭包读取外部变量不等于参数类型谓词）。✅ 直接比较，或存为布尔别名：`const isA = e.t === 'a'`（TS 4.4+ 支持别名条件收窄）。
- ❌ **以为收窄能跨函数边界**：在 `if` 里调用 `assertDefined` 之外的自定义检查函数（显式声明返回普通 boolean）不会提供类型谓词；TS 5.5+ 能对满足条件的函数推断谓词。✅ 用 `x is T` 谓词签名声明守卫函数，或用 `asserts` 断言函数。
- ❌ **用真值收窄处理数值/字符串**：`if (x)` 会把 `0`、`''`、`false` 一并排除——`count !== 0` 的合法数据被当空值。✅ 用 `x != null` 或 `x !== undefined` 做"排除空值"的收窄。
- ❌ **忘记 `typeof null === 'object'`**：对 `unknown` 做 `typeof u === 'object'` 收窄后，`u` 仍可能是 `null`。✅ 标配写法：`if (typeof u === 'object' && u !== null)`。
- ❌ **穷尽检查漏掉 `default` 里的返回**：`never` 检查只有赋值给 `never` 类型变量（或 `s satisfies never`）才会触发；只在 `default` 里 `return 0` 则新变体会静默走到默认值。✅ default 中固定写 `const _e: never = s` 或 `s satisfies never`。

<!-- full-library-explanation -->
## 守卫函数本身也是需要验证的程序

前置是联合类型、unknown 与 JavaScript 条件判断。编译器信任你声明的 x is T，却不会证明函数逻辑真的识别了 T；写成 return true 也可能通过类型检查。外部 JSON 应从 unknown 开始，逐项检查对象非空、字段类型及业务范围，再进入有类型的内部代码。

```ts
type Product = { id: string; price: number };
function isProduct(value: unknown): value is Product {
  return typeof value === 'object' && value !== null
    && 'id' in value && typeof value.id === 'string'
    && 'price' in value && typeof value.price === 'number'
    && Number.isFinite(value.price) && value.price >= 0;
}
console.log(isProduct({ id: 'p1', price: 0 })); // true
console.log(isProduct({ id: 'p1', price: '0' })); // false
```

### 可直接提取的运行案例

下面的程序刻意只验证守卫的 JavaScript 行为；`value is Product` 的编译期收窄仍须由 TypeScript 编译器检查。

```js
function isProduct(value) {
  return typeof value === 'object' && value !== null
    && 'id' in value && typeof value.id === 'string'
    && 'price' in value && typeof value.price === 'number'
    && Number.isFinite(value.price) && value.price >= 0;
}

const actual = [
  isProduct({ id: 'p1', price: 0 }),
  isProduct({ id: 'p1', price: '0' }),
  isProduct(null),
  isProduct({ id: 'p1', price: NaN }),
  isProduct({ id: 'p1', price: -1 }),
];
const expected = [true, false, false, false, false];
if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error(JSON.stringify(actual));
console.log('Product guard runtime contracts passed');
```

**练习**：增加 null、空对象、NaN、负价格输入，预期全部 false。再给判别联合新增一种状态，确认 never 分支让遗漏的处理成为编译错误。穷尽性只约束已声明的联合，来自网络的未知 kind 仍要先验证；as Shape 不会制造运行时保障。

依据：[TypeScript 4.6 解构联合收窄](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-6.html)、[收窄](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)。本轮没有复现原文声称的各编译器版本测试，以下结论以机制与官方说明为依据。

## 🔗 相关条目

- [TypeScript 类型速查手册](./03-typescript-types.md) —— 联合类型、`Extract` 等工具类型与泛型基础
- [React 19 关键 Hooks](./06-react-19-hooks.md) —— `useFormStatus` 返回的 `FormStatus` 判别联合实例
- [现代 JavaScript 语法速查](./04-javascript-modern.md) —— `typeof`/`instanceof`/解构的 JS 基础语义
- 🌐 **[TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)** —— 官方收窄机制文档

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
