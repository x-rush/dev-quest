# JS 核心语义：原型链、this、闭包与生成器

> **文档简介**: JavaScript 运行时核心语义的字典式速查——原型链与 class 语法糖、this 绑定四规则、闭包与作用域、可迭代协议，每条断言均可在 Node 24 中复现

> **目标读者**: 从其他语言转入 JS 的开发者，或需要确认某条语义精确行为的开发者

> **前置知识**: [现代 JS 语法速查](./01-js-modern-syntax.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#原型链` `#this` `#闭包` `#私有字段` `#生成器` |
| **更新日期** | `2026年9月` |

</details>

## 1. 原型链与 class

### 定义
`class` 的实例方法建立在原型链上，类本身也是函数；但它不只是可随意替换的“语法糖”。类体有严格模式、暂时性死区、私有字段和必须经 `new` 调用等独立语义。实例属性查找仍会沿原型链逐级上溯。

### 实测要点（Node 24）

```ts
class A {
  greet() { return "hi" }        // 挂在 A.prototype 上
  static tag = "A";              // 挂在 A 构造函数本身
  #secret = 42;                  // 私有字段：不在原型链上
}
typeof A;                                    // "function"
Object.getOwnPropertyNames(A.prototype);     // ["constructor", "greet"]
new A().greet === A.prototype.greet;         // true（方法共享，不在实例上）
```

### 继承的双链结构

```ts
class B extends A {
  constructor() { super(); }             // 必须先 super() 才能碰 this
  greet() { return super.greet() + "!"; }
}
Object.getPrototypeOf(B.prototype) === A.prototype;  // true：实例方法链
Object.getPrototypeOf(B) === A;                      // true：静态成员链
new B() instanceof A;                                // true：instanceof 沿链判断
```

继承同时建立**两条**原型链：实例方法链（`B.prototype → A.prototype`）与静态成员链（`B → A`）。这是 `class` 比 ES5 手写寄生组合继承省心的地方。

### 私有字段 `#`

```ts
class Card {
  #cvv;
  constructor(cvv) { this.#cvv = cvv; }
  hasSecret(o) { return #cvv in o; }     // 私有名 in 检查（必须写在类体内）
}
```

- `#` 字段是**编译期按类绑定**的，不是字符串键：`"#cvv" in obj` 为 `false`，`obj["#cvv"]` 拿不到
- 类体外部写 `obj.#cvv` 直接 **SyntaxError**（语法层禁止，不是运行时 TypeError）
- 真正的存在性检查要用 `#cvv in obj`，且只能写在同一个类体内

## 2. this 绑定四规则

### 定义
`this` 在**函数调用时**决定，不取决于定义位置（箭头函数除外，它继承定义处词法 `this`）。

### 四规则速查（按优先级从高到低）

| 规则 | 触发方式 | this 指向 |
|------|---------|-----------|
| `new` 绑定 | `new Fn()` | 新构造的实例 |
| 显式绑定 | `fn.call/apply/bind` | 指定对象（`call(null)` 在严格模式下为 `null`） |
| 隐式绑定 | `obj.fn()` | 点号前的 `obj` |
| 默认绑定 | `fn()` 独立调用 | 严格模式 `undefined`；非严格 `globalThis` |

箭头函数**跳过**以上全部规则，沿用定义处的词法 `this`（`.call/.bind` 都改不动）。

### 示例

```ts
function f() { return this; }
const obj = { f };

f();            // undefined（ESM 自动采用严格模式；TS 还取决于输出格式与编译配置）
obj.f();        // obj
f.call(obj);    // obj
new (function P() { this.ok = true; })().ok;  // true

const o = {
  x: 1,
  m() { const get = () => this.x; return get(); },
};
o.m();          // 1：箭头函数捕获定义处 this
```

### 陷阱
- ❌ `const m = obj.m; m()`——取出方法后独立调用，隐式绑定丢失，`this` 变 `undefined`，容易在回调中踩中
- ✅ 传回调前先绑定：`obj.m.bind(obj)`、箭头包装 `() => obj.m()`，或类字段写法 `m = () => {}`
- ❌ 想给箭头函数"换 this"再调 `.call(other)`——静默无效
- ✅ 需要动态 `this` 就用普通函数；需要固定 `this` 就用箭头函数

## 3. 闭包与作用域

### 定义
闭包是函数与其定义时词法作用域的组合：内层函数保有对外层变量的引用，即使外层已返回。

### `let/const` 块级作用域 vs `var` 函数作用域

```ts
// 经典循环陷阱：var 只有一个绑定，循环结束时全部回调读到 3
const out1 = [];
for (var i = 0; i < 3; i++) out1.push(() => i);
out1.map((fn) => fn());          // [3, 3, 3]

// let 每轮循环创建新绑定
const out2 = [];
for (let j = 0; j < 3; j++) out2.push(() => j);
out2.map((fn) => fn());          // [0, 1, 2]
```

### 示例：闭包做私有状态

```ts
function createCounter() {
  let count = 0;                       // 只能通过闭包访问
  return { inc: () => ++count, get: () => count };
}
const c = createCounter();
c.inc(); c.inc();
c.get();     // 2；外部无法直接改 count
```

### 陷阱
- ❌ 循环里给异步回调传 `var` 循环变量，回调执行时读到的是循环结束后的值
- ✅ 改 `let`（每轮新绑定），或用 IIFE `(i => ...)(i)` 捕获快照
- ❌ `let` 在声明前访问——TDZ（暂时性死区）直接 ReferenceError，`var` 则是 `undefined`（更隐蔽）
- ✅ 闭包引用大对象会阻止 GC 回收，长生命周期监听器/定时器里只捕获必要数据

## 4. 可迭代协议与生成器

### 定义
对象实现 `[Symbol.iterator]()`（返回带 `next()` 的迭代器）即可被 `for...of`、展开运算符、解构消费；`function*` 生成器是"写起来最省事的迭代器工厂"，`yield*` 可委托子生成器。

```ts
function* ids() { yield 1; yield* [2, 3]; }   // yield* 委托内层可迭代
[...ids()];        // [1, 2, 3]
for (const v of ids()) {}                     // for...of 消费
```

<!-- node-python-seventh-case: node-keyword-binding-contracts -->
```js
import assert from 'node:assert/strict';

class Parent {
  constructor(value) { this.value = value; }
  read() { return this.value; }
}
class Child extends Parent {
  read() { return `${super.read()}!`; }
}

const callbacks = [];
for (let index = 0; index < 3; index++) callbacks.push(() => index);
assert.deepEqual(callbacks.map((callback) => callback()), [0, 1, 2]);
assert.equal(new Child('ok').read(), 'ok!');
assert.throws(() => Child(), TypeError);
console.log('keyword-binding: class extends super; let loop bindings; new required');
```

这段完整 ESM 程序同时运行 `class`、`extends`、`super`、`let`、`for` 与 `new` 的关键语义。它只验证这里列出的绑定和构造约束；私有字段、静态初始化块和跨模块的解析错误仍需在各自的最小程序中检验。

与事件循环的配合见 [异步 API 全表](./02-async-api.md)（异步迭代 `for await...of`）。

<!-- full-library-explanation -->
## 共享方法、独立状态与回调接收者

前置是对象、函数和赋值。类实例通常共享 prototype 上的方法，但实例字段各自存放；箭头类字段为每个实例创建一个函数，并捕获该实例的 this。它能解决回调丢失接收者的问题，也有分配与继承行为差异。class 仍建立在原型机制上，但严格模式、私有字段与构造调用规则不能简化为和普通函数完全等价。

下面的完整 ESM 实验保存为 semantics.mjs：

```js
const counter = {
  value: 1,
  read() { return this.value; },
};
const bound = counter.read.bind(counter);
counter.value = 2;
console.log(bound());
const callbacks = [];
for (let i = 0; i < 3; i++) callbacks.push(() => i);
console.log(callbacks.map(fn => fn()).join(','));
```

输出 2 和 0,1,2。bind 固定接收者，不是冻结对象的值；闭包保留变量绑定，也不是自动快照。练习：将 let 换成 var，输出应为 3,3,3；把 read 脱离对象直接调用，ESM 严格模式下 this 为 undefined。调试时先写出实际调用表达式，再判断 this，不能只看函数最初定义在哪个对象里。

## 🔗 相关文档

- 📄 **[现代 JS 语法速查](./01-js-modern-syntax.md)** — 解构、可选链、空值合并等语法层细节
- 📄 **[类型转换与集合语义](./08-type-coercion-collections.md)** — 相等性与内置集合行为
- 📄 **[异步编程教程](../../basics/04-async-promises.md)** — 闭包在异步流程中的应用
- 🌐 **[MDN: Inheritance and the prototype chain](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Inheritance_and_the_prototype_chain)** — 原型链权威讲解

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
