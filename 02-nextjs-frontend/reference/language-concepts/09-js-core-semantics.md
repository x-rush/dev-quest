# JavaScript 核心语义（事件循环 / 闭包 / 原型链 / this / 可迭代协议）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `language-concepts`

## 📌 定义

五个支撑一切 JS/TS/React 代码的底层语义：**事件循环**（单线程下宏任务/微任务的调度顺序，决定 `Promise`、`setTimeout`、UI 更新的先后）、**闭包**（函数记住定义时词法作用域的能力，是 Hook 状态、回调、模块化的实现基础）、**原型链**（属性查找机制，`class` 只是它的语法糖）、**`this` 绑定**（四条规则决定函数内 `this` 指向谁）、**可迭代协议**（`for...of`、展开、解构背后的 `Symbol.iterator` 契约）。排查"为什么顺序不对""为什么 this 丢了""为什么旧值被读到"这类问题时，答案都在这里。

## 📖 语法/签名

### 事件循环执行模型

同步调用先完成当前执行栈；宿主在微任务检查点处理 Promise 回调、`queueMicrotask` 等排队工作。浏览器有任务队列、微任务检查点和渲染机会，**UI 渲染不是一个可以简单列入“宏任务队列”的普通回调**，任务之后也不一定立即绘制。持续追加微任务会延迟其他任务和渲染。Node 另有 process.nextTick 队列与 timers/poll/check 等阶段；nextTick 与 Promise 的顺序还受 CJS/ESM 顶层上下文影响。这个模型用于解释调度关系，不能据此推断不同 I/O 来源的通用执行顺序。依据：[HTML 事件循环处理模型](https://html.spec.whatwg.org/multipage/webappapis.html#event-loop-processing-model)。

### this 绑定四条规则（优先级从高到低）

| 优先级 | 规则 | 形式 | `this` 指向 |
|--------|------|------|------------|
| 1 | `new` 绑定 | `new Fn()` | 新创建的实例 |
| 2 | 显式绑定 | `fn.call/apply/bind(obj)` | 指定的 `obj` |
| 3 | 隐式绑定 | `obj.fn()` | 调用者 `obj` |
| 4 | 默认绑定 | `fn()` | 严格模式 `undefined`，非严格全局对象 |

箭头函数没有自己的 `this`：沿词法作用域取外层的，四条规则对它一律不适用。

### 可迭代协议

```ts
interface Iterable {
  [Symbol.iterator](): Iterator
}
interface Iterator {
  next(): { value: unknown; done: boolean }
}
```

同步 `for...of`、数组/实参展开和数组解构要求可迭代协议；对象展开 `{ ...obj }` 枚举自身可枚举属性，不要求 `[Symbol.iterator]`。上表接口用于展示形状，正式 TypeScript 程序应使用标准库已有的泛型 `Iterable<T>` / `Iterator<T>`，避免同名重声明。

## 💡 示例

### 事件循环顺序（本机 Node 24 实测输出）

```js
console.log('1 sync')
setTimeout(() => console.log('4 setTimeout (macro)'), 0)
Promise.resolve().then(() => console.log('3 promise.then (micro)'))
queueMicrotask(() => console.log('3.5 queueMicrotask (micro)'))
console.log('2 sync end')

// 实际输出：1 sync → 2 sync end → 3 promise.then → 3.5 queueMicrotask → 4 setTimeout
// 同步代码先全部跑完；微任务按入队顺序在宏任务前全部清空
```

### 闭包：函数记住定义处的作用域

```js
function makeCounter() {
  let count = 0            // 被内部函数引用，存活期延长到闭包存活期
  return () => ++count
}
const next = makeCounter()
next(); next()
console.log(next())        // 3 —— count 没有被重置，闭包持有同一个绑定
```

### 原型链与 class：class 是原型的语法糖

```js
class A { greet() { return 'hi' } }
const a = new A()

Object.getOwnPropertyNames(A.prototype)  // ['constructor', 'greet'] —— 方法在原型上
Object.getOwnPropertyNames(a)            // [] —— 实例自身没有方法
Object.getPrototypeOf(a) === A.prototype // true —— 使用标准反射 API 查看原型
```

属性查找顺序：实例自身 → 构造函数 `prototype` → 父类 `prototype` → … → `null`。

### this 绑定四条（本机 Node 24 实测）

```js
function show() { return this?.v }
const obj = { v: 'implicit', show }

show()                       // undefined（默认绑定，模块/严格模式）
obj.show()                   // 'implicit'（隐式绑定：看调用者）
show.call({ v: 'call' })     // 'call'（显式绑定）
show.bind({ v: 'bind' })()   // 'bind'（显式绑定，永久固定）

const arrow = { v: 'outer', get: () => this?.v }
arrow.get()                  // undefined —— 箭头函数不适用以上规则，this 来自词法外层
```

### 自定义可迭代对象

```js
const range = {
  [Symbol.iterator]() {
    let i = 0
    return { next: () => (i < 3 ? { value: i++, done: false } : { value: undefined, done: true }) }
  },
}
;[...range]        // [0, 1, 2] —— for...of / 展开都走同一协议
```

## ⚠️ 常见陷阱

- ❌ **用微任务做无限/长链轮询**：`Promise.then` 链的微任务在**宏任务之前**清空——纯微任务自循环会让 `setTimeout`、UI 渲染、I/O 回调永远插不进来（浏览器表现为页面卡死）。✅ 轮询/重试用 `setTimeout`/`setInterval`（宏任务）让出事件循环。
- ❌ **以为 `setTimeout(fn, 0)` 是"立即执行"**：它只是把回调排入宏任务，最短也要等同步代码与全部微任务结束，且浏览器嵌套 5 层后被钳制到 ≥4ms。✅ 需要"当前代码后、渲染前"执行用 `queueMicrotask`/`Promise.then`，需要"下一帧"用 `requestAnimationFrame`。
- ❌ **提取 class 方法后丢失 this**：`const g = obj.greet; g()` 只剩默认绑定，`this` 变 `undefined`（React 类组件回调、事件监听丢 this 的根源）。✅ 传参时绑定：`onClick={() => obj.greet()}` 或 `greet = () => {...}` 箭头字段。
- ❌ **以为闭包捕获"值"**：闭包捕获的是**变量绑定**（引用）——循环里 `var i` + 回调读到最终值，多个闭包共享同一个 `let` 变量。✅ 每次迭代要独立快照时用 `let`（块级作用域逐次创建绑定）或在循环体内立即捕获 `const snapshot = i`。
- ❌ **把 JavaScript 默认参数误认为共享对象**：`function f(items = []) {}` 的数组在需要默认值的每次调用时创建。实例字段 `items = []` 也在每次实例初始化时创建。真正共享的是显式引用的外部对象，例如 `const shared = []; function f(items = shared) {}`，或者手工赋在原型上的数组。✅ 用对象创建位置判断生命周期，再用两个实例/两次调用检验。
- ❌ **对普通对象用 `for...of`**：对象默认不实现 `Symbol.iterator`，`for...of {}` 直接抛 `TypeError: not iterable`。✅ 迭代对象用 `Object.keys/entries/values`（返回数组，天然可迭代），或给对象实现 `[Symbol.iterator]`。
- ❌ **混淆 nextTick 与微任务（Node）**：常见 CJS 顶层中 nextTick 先执行，但 ESM 顶层可不同；递归 nextTick 还可能饿死 I/O。✅ 按用途选择：`queueMicrotask` 用于当前同步工作结束后的微任务；Node `setImmediate` 用于其 check 阶段，不是浏览器标准 API，也不与微任务等价。

## 可运行实验：绑定与对象究竟何时创建

以下完整程序均保存为 `.mjs` 文件、用 Node 24 执行。ESM 明确采用严格模式，避免浏览器普通脚本和 CommonJS 顶层 this 的差异。每个围栏独立运行，不需要拼接前文片段。

### 默认参数、实例字段与原型方法

保存为 `object-lifetimes.mjs`，预期五行：`true,false`、`true`、`true`、`1,0`、`1,0`。

<!-- foundation-case: object-lifetimes -->
```js
class Basket {
  items = [];
  add(item) { this.items.push(item); }
}
const a = new Basket();
const b = new Basket();
a.add('book');
console.log([Object.hasOwn(a, 'items'), Object.hasOwn(a, 'add')].join(','));
console.log(Object.getPrototypeOf(a) === Basket.prototype);
console.log(a.add === b.add);
console.log([a.items.length, b.items.length].join(','));
function append(item, items = []) {
  if (item !== undefined) items.push(item);
  return items;
}
const first = append('book');
const second = append();
console.log([first.length, second.length].join(','));
```

同一个原型方法可以供两个实例使用，方法中的 this 区分接收者；两个实例的 items 数组并未共享。默认参数的数组也在两次调用时分别创建。类基于原型机制，但还规定严格模式、私有字段和初始化顺序，不能把所有 class 行为都用“语法糖”一词代替解释。

### 闭包持有绑定，箭头函数持有外层 this

保存为 `bindings.mjs`，预期五行：`2`、`0,1,2`、`7`、`undefined`、`8`。

<!-- foundation-case: bindings -->
```js
let value = 1;
const read = () => value;
value = 2;
console.log(read());
const readers = [];
for (let i = 0; i < 3; i++) readers.push(() => i);
console.log(readers.map((fn) => fn()).join(','));
const model = {
  value: 7,
  read() { return this?.value; },
  makeReader() { return () => this.value; },
};
console.log(model.read());
const detached = model.read;
console.log(detached());
const arrow = model.makeReader();
model.value = 8;
console.log(arrow.call({ value: 99 }));
```

最后一行仍使用 model：箭头函数固定的是外层 this 关系，value 属性本身仍能变化。练习：将循环 let 改成 var，解释为什么变成 `3,3,3`；再给 detached 绑定 model，确认结果恢复。

### 生成器消费后不会自动重置

保存为 `iteration.mjs`，预期三行：`0,1,2`、空行、`a:1,b:2`。

<!-- foundation-case: iteration -->
```js
function* range(end) {
  for (let i = 0; i < end; i++) yield i;
}
const iterator = range(3);
console.log([...iterator].join(','));
console.log([...iterator].join(','));
const record = { a: 1, b: 2 };
console.log(Object.entries(record).map(([key, value]) => `${key}:${value}`).join(','));
```

生成器对象既是迭代器也是可迭代对象；重新调用 range 才会创建新状态。普通对象用 Object.entries 变成键值对数组。异步数据来源另有 `Symbol.asyncIterator` 与 `for await...of`，同步迭代协议不会替你等待网络。

语言语义依据：[ECMAScript 函数与类](https://tc39.es/ecma262/multipage/ecmascript-language-functions-and-classes.html)、[迭代协议](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-iteration)。

## 🔗 相关条目

- [现代 JavaScript 语法速查](./04-javascript-modern.md) —— ES6+ 解构、展开、模块语法层
- [Web 平台 API 速查](./10-web-platform-apis.md) —— 事件循环之上的 `fetch`/定时器/存储
- [React 19 关键 Hooks](./06-react-19-hooks.md) —— 闭包陈旧值与 Hook 状态的关系
- [类型收窄与类型守卫](./07-type-narrowing-guards.md) —— `typeof`/`instanceof` 的类型层镜像
- 🌐 **[MDN: Event Loop](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Event_loop)** —— 官方事件循环模型

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
