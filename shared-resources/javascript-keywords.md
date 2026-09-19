# JavaScript 关键词与语法入口

适用于 Next.js、TanStack、React Native 和 Node.js 的共同语言基础。前置知识只有变量、函数和条件判断；先读到能解释示例，再回到具体框架。TypeScript 额外的类型语法不应混入 JavaScript 关键词表。

## 先区分四种名字

`return` 是语法；`Array` 是语言内置对象；`fetch` 是运行环境提供的 API；`useState` 是 React 导出的函数。前三者即使在代码里都不需要手动导入，来源也不同。判断来源才能知道应该查哪个手册、能否在另一个环境运行。

关键词也不等于“任何位置都不能出现的文本”：`const item = { default: 1 }` 合法，`const default = 1` 不合法。属性名和变量绑定使用不同语法规则。当前规范的分类以 [ECMAScript 词法规则](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html#sec-keywords-and-reserved-words)为准；在线规范可能包含超出项目运行时的新增能力。

## 声明、作用域与函数

| 名称 | 必要解释 | 小例子或容易误解之处 |
|---|---|---|
| `let` | 声明块作用域、可重新赋值的绑定 | `let count = 0; count += 1` |
| `const` | 声明不能重新赋值的绑定 | 对象内部仍可修改；不是深度冻结 |
| `var` | 函数作用域的旧声明方式 | 声明会提升，赋值不会；新代码通常优先明确的块作用域 |
| `function` | 声明或创建函数 | 参数是局部绑定；函数是否返回值由执行路径决定 |
| `return` | 结束当前函数并返回值 | 换行可能触发自动分号插入；返回对象别把 `{` 放到独立下一行 |
| `class` | 定义类及其构造、实例和静态成员 | 类方法执行于严格模式；类不是 Java 类的逐字移植 |
| `extends` | 建立类继承 | 子类构造器使用 `this` 前通常要先调用 `super()` |
| `super` | 访问父类构造或方法 | `super()` 与 `super.method()` 作用不同 |
| `new` | 通过构造器创建实例 | 箭头函数不可用 `new` 调用 |
| `this` | 当前调用的接收者；箭头函数从外层捕获 | 普通方法被取出单独调用可能失去原接收者 |

`async`、`get`、`set`、`static` 在特定语法中有特殊意义，不要凭出现了这些英文单词就判断代码功能。`async function` 返回 Promise；getter/setter 是属性访问器；静态方法通过类访问而非实例访问。

## 分支、循环与异常

| 名称 | 解决的问题 | 边界 |
|---|---|---|
| `if` / `else` | 条件选择 | 条件会转成布尔值；空数组和空对象仍为真 |
| `switch` / `case` / `default` | 多分支选择 | 匹配后不自动结束；常需 `break`；也可显式 `return` |
| `for` | 重复执行 | 普通计数循环、`for…in`、`for…of` 是不同形式 |
| `in` | 判断属性是否存在；也出现在 `for…in` | 会涉及原型链；检查自有属性可用 `Object.hasOwn` |
| `of`（语境词） | `for…of` 遍历可迭代值 | 遍历数组得到元素；普通对象默认不可迭代 |
| `while` / `do` | 条件循环 | `do…while` 至少执行一次 |
| `break` / `continue` | 结束循环或开始下一次迭代 | `break` 也用于 switch；二者可使用标签 |
| `throw` | 抛出异常，沿调用链寻找处理者 | 推荐抛 `Error`，便于携带消息和堆栈 |
| `try` / `catch` / `finally` | 捕获异常与清理 | `finally` 中返回或抛出会覆盖原本结果，通常应避免 |
| `debugger` | 在调试器中设置停点 | 没有连接调试器时不能当作业务流程控制 |
| `with` | 旧的作用域扩展语句 | 严格模式禁止；学习旧代码时识别即可 |

## 运算、模块与异步

| 名称 | 含义 | 需要记住的区别 |
|---|---|---|
| `typeof` | 返回类型标签字符串 | `typeof null` 是 `"object"`；数组用 `Array.isArray` |
| `instanceof` | 通常检查原型链关系，可被定制 | 跨 realm 或原型被改变时不能作为所有数据的可靠校验 |
| `delete` | 尝试删除对象属性 | 不等于给变量赋 `undefined`；删除数组项会留下空位 |
| `void` | 求值后返回 `undefined` | 不取消表达式中的副作用 |
| `import` / `export` | 连接模块的导入与导出 | 动态 `import()` 返回 Promise；导出语句本身不是网络请求 |
| `await` | 暂停当前异步流程，等待 Promise 结算 | 不阻塞整个 JS 线程；顶层使用受模块与运行时支持限制 |
| `yield` | 生成器暂停并产出值 | 与 `await` 的协议不同；`function*` 返回迭代器 |
| `true` / `false` / `null` | 字面量 | `undefined` 是全局值名称，不能把它当作与 `null` 完全相同的语法分类 |

`enum` 为保留名称；严格模式还限制 `implements`、`interface`、`let`、`package`、`private`、`protected`、`public`、`static`、`yield` 等作为绑定名的使用，`await` 另受模块/异步语境限制。TypeScript 的 `interface`、`type`、`satisfies` 等有自己的规则；编译后类型信息通常不提供运行时校验。新语法如资源管理声明必须另外核对目标运行时，不因在线规范出现就默认为所有浏览器可用。

## 高频语法符号：不是关键词，也不是内置函数

下面几项经常出现在框架代码中。它们由 JavaScript 语法解析，不是要从某个包导入的 API；因此应和 `Array.map`、`fetch`、`useState` 分开记忆。

| 写法 | 读取方式 | 容易写错的边界 |
|---|---|---|
| `obj?.name`、`items?.[0]` | 左边为 `null`/`undefined` 时返回 `undefined`，否则继续读取/调用 | 只短路这条链；`obj?.missing.value` 仍可能因 `missing` 是 undefined 而报错，应写 `obj?.missing?.value` |
| `fn?.()` | 函数存在时调用 | 会吞掉“回调本应存在”的契约错误；关键回调应显式校验或让错误暴露 |
| `left ?? right` | 仅当左边是 `null` 或 `undefined` 时选右边 | 不把 `0`、`false`、`""` 当缺失；默认值场景通常比 `\|\|` 更合适。不能未加括号地和 `&&`/`\|\|` 混用 |
| `...items` | 展开可迭代值，或在对象字面量展开自有可枚举属性 | `[...array]`、`{...object}` 都是浅复制；嵌套对象仍共享。对象不能直接当可迭代数组展开 |
| `function f(...args) {}` | 剩余参数把多余实参收集为真实数组 | rest 必须在参数列表最后；它不同于旧函数的类数组 `arguments` |
| `(value) => value * 2` | 箭头函数使用词法 `this` | 没有自己的 `this`、`arguments` 或 `new.target`，不能当构造器；对象方法需要动态接收者时通常用普通方法 |
| `{ id, title: label = '未命名' } = item` | 解构读取属性并可改名/提供默认值 | 默认值只处理 `undefined`，不处理 `null`；`item` 本身可能为空时，先做输入校验或可选链 |

```js
const settings = { retries: 0, title: undefined, nested: { enabled: false } };

console.log(settings.retries ?? 3);       // 0：0 是有效值
console.log(settings.retries || 3);       // 3：|| 把 0 当假值
console.log(settings.title ?? '默认标题'); // 默认标题

const copy = { ...settings };
copy.nested.enabled = true;
console.log(settings.nested.enabled);     // true：对象展开不是深拷贝
```

当你想表达“字段可能缺失”时先选 `?.` / `??`；当你想表达“任何假值都走备用分支”时才选 `||`。这一区别会直接影响金额 `0`、开关 `false` 和空文本的业务含义。

## 完整小实验：看见绑定、遍历和错误边界

保存为 `keywords.mjs`，用 `node keywords.mjs` 运行。只用基础语言能力，不需要 npm 依赖。

<!-- verification-case: shared-js-keywords-binding-flow -->
```js
const tasks = [{ title: "read", done: false }];
tasks[0].done = true; // 修改对象允许；tasks = [] 则不允许

function titles(items) {
  const result = [];
  for (const item of items) {
    if (!item.done) continue;
    result.push(item.title);
  }
  return result;
}

console.log(titles(tasks).join(","));
try {
  const value = null;
  console.log(value.title);
} catch (error) {
  console.log(error instanceof TypeError);
} finally {
  console.log("finished");
}
```

预期输出依次是 `read`、`true`、`finished`。先预测再改动：把 done 改为 false，第一行应为空；把属性访问替换为 `value?.title`，不会进入 catch，但仍执行 finally。可选链只能处理空值访问，不能代替业务必填字段校验。

## 下一步

查[常用内置能力](javascript-builtins.md)，再进入 [JavaScript 核心语义](../09-nodejs-backend/reference/language-concepts/07-js-core-semantics.md)与 [TypeScript 类型参考](../02-nextjs-frontend/reference/language-concepts/03-typescript-types.md)。如果无法解释上面的三行输出，先不进入框架的缓存或状态管理。
