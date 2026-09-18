# JavaScript 核心语义（事件循环 / 闭包 / 原型链 / this / 可迭代协议）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `language-concepts`

## 📌 定义

五个支撑一切 JS/TS/React 代码的底层语义：**事件循环**（单线程下宏任务/微任务的调度顺序，决定 `Promise`、`setTimeout`、UI 更新的先后）、**闭包**（函数记住定义时词法作用域的能力，是 Hook 状态、回调、模块化的实现基础）、**原型链**（属性查找机制，`class` 只是它的语法糖）、**`this` 绑定**（四条规则决定函数内 `this` 指向谁）、**可迭代协议**（`for...of`、展开、解构背后的 `Symbol.iterator` 契约）。排查"为什么顺序不对""为什么 this 丢了""为什么旧值被读到"这类问题时，答案都在这里。

## 📖 语法/签名

### 事件循环执行模型

每轮循环：**执行完当前同步代码 → 清空全部微任务队列 → 取一个宏任务执行 → 重复**。微任务包括 `Promise.then/catch/finally`、`queueMicrotask`；宏任务包括 `setTimeout`/`setInterval`、I/O、UI 渲染、事件回调。Node 与浏览器的差别一句话：Node 有额外的 process.nextTick 队列与 timers/poll/check 等阶段；nextTick 与 Promise 的先后还受 CJS/ESM 顶层上下文影响。浏览器另有渲染机会，不应简化成每次任务后必定绘制。

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

实现 `[Symbol.iterator]` 的对象才能被 `for...of`、展开 `...`、数组解构消费。

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
a.__proto__ === A.prototype              // true —— 实例沿原型链找到方法
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
- ❌ **在类字段里给原型共享可变引用**：字段初始化写在实例上（`class A { items = [] }` 每个实例一份）；而写在方法内的默认参数或原型上手工赋值的对象会被所有实例共享。✅ 可变状态一律放实例字段或构造函数。
- ❌ **对普通对象用 `for...of`**：对象默认不实现 `Symbol.iterator`，`for...of {}` 直接抛 `TypeError: not iterable`。✅ 迭代对象用 `Object.keys/entries/values`（返回数组，天然可迭代），或给对象实现 `[Symbol.iterator]`。
- ❌ **混淆 nextTick 与微任务（Node）**：常见 CJS 顶层中 nextTick 先执行，但 ESM 顶层可不同；递归 nextTick 还可能饿死 I/O——这是 Node 服务端代码特有的坑。✅ 通用异步调度统一用 `queueMicrotask`/`setImmediate`，避免 `nextTick` 递归。

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
