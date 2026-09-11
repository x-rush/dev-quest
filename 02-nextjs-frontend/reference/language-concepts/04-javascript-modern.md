# 现代 JavaScript 语法速查手册

> **文档简介**: ES6+ 现代 JavaScript 语法快速参考，涵盖日常开发中常用的新特性和最佳实践
>
> **目标读者**: JavaScript开发者，需要快速查阅现代JS语法的开发者
>
> **前置知识**: JavaScript基础语法、编程基础概念
>
> **预计时长**: 20-35分钟

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `reference` |
| **难度** | ⭐⭐⭐ (3/5星) |
| **标签** | `#es6` `#modern-javascript` `#async-programming` `#destructuring` `#cheatsheet` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

---

## 🔤 变量声明和作用域

### let 和 const
```javascript
// const - 常量声明（推荐优先使用）
const API_URL = 'https://api.example.com'
const config = { timeout: 5000 }

// 引用类型可以修改内容，但不能重新赋值
const user = { name: 'John', age: 30 }
user.age = 31 // ✅ 允许
// user = { name: 'Jane' } // ❌ 错误：不能重新赋值

// let - 块级作用域变量
let counter = 0
if (true) {
  let blockScoped = 'local'
  counter = 1
}
// console.log(blockScoped) // ❌ 错误：块级作用域

// 避免使用 var（函数作用域，变量提升）
function oldStyle() {
  if (true) {
    var functionScoped = 'old'
  }
  console.log(functionScoped) // ✅ 可以访问
}
```

### 暂时性死区 (Temporal Dead Zone)
```javascript
// 在声明前访问变量会报错
{
  // console.log(myVar) // ❌ ReferenceError: Cannot access 'myVar' before initialization
  let myVar = 'value'
}

// 与 var 的对比
{
  console.log(hoistedVar) // ✅ undefined（变量提升）
  var hoistedVar = 'value'
}
```

---

## 🎯 箭头函数

### 基础语法
```javascript
// 传统函数
function add(a, b) {
  return a + b
}

// 箭头函数
const addArrow = (a, b) => a + b

// 多行函数体
const multiply = (a, b) => {
  const result = a * b
  return result
}

// 单参数可以省略括号
const double = x => x * 2

// 无参数需要括号
const getRandom = () => Math.random()
```

### this 绑定规则
```javascript
// 箭头函数没有自己的 this，继承外层作用域
const person = {
  name: 'John',
  traditionalMethod: function() {
    console.log(this.name) // ✅ 'John'

    setTimeout(function() {
      console.log(this.name) // ❌ undefined（全局对象或严格模式报错）
    }, 100)

    setTimeout(() => {
      console.log(this.name) // ✅ 'John'（继承外层 this）
    }, 200)
  },

  arrowMethod: () => {
    console.log(this.name) // ❌ undefined（箭头函数作为方法时，this 指向全局）
  }
}

// 正确的方法定义方式
const person = {
  name: 'John',
  greet() {
    console.log(`Hello, ${this.name}!`)
  },

  initTimer() {
    this.timer = setInterval(() => {
      console.log(`${this.name} is still here`)
    }, 1000)
  }
}
```

---

## 🔄 解构赋值

### 对象解构
```javascript
// 基础对象解构
const user = {
  id: 1,
  name: 'John',
  email: 'john@example.com',
  address: {
    city: 'New York',
    country: 'USA'
  }
}

// 基础解构
const { name, email } = user
console.log(name, email) // 'John', 'john@example.com'

// 重命名变量
const { name: userName, email: userEmail } = user

// 默认值
const { age = 25, name: fullName = 'Anonymous' } = user

// 嵌套解构
const { address: { city, country } } = user

// 函数参数解构
function displayUser({ name, email, age = 25 }) {
  console.log(`${name} (${age}) - ${email}`)
}
displayUser(user)

// 剩余属性解构
const { id, ...userInfo } = user
console.log(userInfo) // { name: 'John', email: '...', address: {...} }
```

### 数组解构
```javascript
// 基础数组解构
const colors = ['red', 'green', 'blue', 'yellow']
const [first, second, third] = colors
console.log(first, second, third) // 'red', 'green', 'blue'

// 跳过元素
const [primary, , tertiary] = colors
console.log(primary, tertiary) // 'red', 'blue'

// 默认值
const [x, y, z = 'default'] = ['a', 'b']
console.log(x, y, z) // 'a', 'b', 'default'

// 剩余元素
const [main, ...others] = colors
console.log(main, others) // 'red', ['green', 'blue', 'yellow']

// 函数返回值解构
function getUserInfo() {
  return ['John', 30, 'john@example.com']
}
const [name, age, email] = getUserInfo()

// 交换变量（无需临时变量）
let a = 1, b = 2
[a, b] = [b, a]
console.log(a, b) // 2, 1
```

### 函数参数解构
```javascript
// 对象参数解构
function createUser({ name, age = 25, role = 'user' }) {
  return { name, age, role, createdAt: new Date() }
}

const user = createUser({ name: 'Alice', age: 28 })
console.log(user) // { name: 'Alice', age: 28, role: 'user', createdAt: ... }

// 数组参数解构
function processCoordinates([x, y, z = 0]) {
  return { x, y, z, distance: Math.sqrt(x*x + y*y + z*z) }
}

const coords = processCoordinates([3, 4])
console.log(coords) // { x: 3, y: 4, z: 0, distance: 5 }
```

---

## 🚀 异步编程

### Promise 基础
```javascript
// 创建 Promise
const fetchData = () => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const success = Math.random() > 0.3
      if (success) {
        resolve({ data: 'Success!', timestamp: Date.now() })
      } else {
        reject(new Error('Network error'))
      }
    }, 1000)
  })
}

// 使用 Promise
fetchData()
  .then(result => {
    console.log('Success:', result)
    return result.data
  })
  .then(data => {
    console.log('Data:', data)
  })
  .catch(error => {
    console.error('Error:', error.message)
  })
  .finally(() => {
    console.log('Operation completed')
  })

// Promise 静态方法
Promise.resolve('Immediate success')
  .then(data => console.log(data))

Promise.reject(new Error('Immediate error'))
  .catch(error => console.error(error.message))

// Promise.all - 等待所有 Promise 完成
const promises = [
  fetch('/api/users'),
  fetch('/api/posts'),
  fetch('/api/comments')
]

Promise.all(promises)
  .then(responses => {
    console.log('All requests completed')
    return Promise.all(responses.map(r => r.json()))
  })
  .then(data => {
    const [users, posts, comments] = data
    console.log('Data loaded:', { users, posts, comments })
  })

// Promise.race - 返回第一个完成的 Promise
const timeout = new Promise((_, reject) =>
  setTimeout(() => reject(new Error('Timeout')), 5000)
)

Promise.race([fetchData(), timeout])
  .then(result => console.log('First completed:', result))
  .catch(error => console.error('First error:', error.message))
```

### async/await
```javascript
// async 函数声明
async function fetchUserData(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const user = await response.json()
    return user
  } catch (error) {
    console.error('Failed to fetch user:', error)
    throw error // 重新抛出错误
  }
}

// async 箭头函数
const fetchUserPosts = async (userId) => {
  const response = await fetch(`/api/users/${userId}/posts`)
  return response.json()
}

// 并行执行异步操作
async function loadUserProfile(userId) {
  try {
    // 并行执行多个异步操作
    const [user, posts, comments] = await Promise.all([
      fetchUserData(userId),
      fetchUserPosts(userId),
      fetch(`/api/users/${userId}/comments`).then(r => r.json())
    ])

    return {
      user,
      posts,
      comments,
      loadedAt: new Date()
    }
  } catch (error) {
    console.error('Failed to load profile:', error)
    return null
  }
}

// 使用 async/await
async function main() {
  const profile = await loadUserProfile(123)
  if (profile) {
    console.log('Profile loaded:', profile.user.name)
    console.log('Posts count:', profile.posts.length)
  }
}

// 错误处理模式
async function safeAsyncOperation(operation) {
  try {
    return await operation()
  } catch (error) {
    console.error('Operation failed:', error)
    return null
  }
}

// 使用示例
const result = await safeAsyncOperation(() => fetchData())
```

### 异步迭代器
```javascript
// 异步生成器函数
async function* fetchPosts(userId, limit = 10) {
  let page = 1
  let hasMore = true

  while (hasMore && page <= limit) {
    const response = await fetch(`/api/users/${userId}/posts?page=${page}`)
    const posts = await response.json()

    if (posts.length === 0) {
      hasMore = false
    } else {
      for (const post of posts) {
        yield post
      }
      page++
    }
  }
}

// 使用异步迭代器
async function displayUserPosts(userId) {
  for await (const post of fetchPosts(userId)) {
    console.log(`Post: ${post.title}`)
    console.log(`Content: ${post.content}`)
    console.log('---')
  }
}

// 使用 for...of 循环和 Promise
async function processBatch(items, batchSize = 5) {
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize)
    const results = await Promise.all(
      batch.map(item => processItem(item))
    )
    console.log(`Processed batch ${Math.floor(i/batchSize) + 1}:`, results)
  }
}
```

---

## 🛠️ 对象和数组方法

### 对象方法
```javascript
// 对象属性简写
const name = 'John'
const age = 30

const user = { name, age } // 等同于 { name: name, age: age }

// 对象方法简写
const person = {
  name: 'John',
  greet() {
    return `Hello, I'm ${this.name}`
  },

  // 计算属性名
  [`get${name.toUpperCase()}Info`]() {
    return `${this.name} is ${this.age} years old`
  }
}

console.log(person.greet())
console.log(person.getJOHNInfo())

// Object.assign - 对象合并
const target = { a: 1, b: 2 }
const source1 = { b: 3, c: 4 }
const source2 = { d: 5 }

const merged = Object.assign(target, source1, source2)
console.log(merged) // { a: 1, b: 3, c: 4, d: 5 }

// 展开运算符合并对象
const mergedWithSpread = { ...target, ...source1, ...source2 }
console.log(mergedWithSpread) // { a: 1, b: 2, c: 4, d: 5 }

// Object.keys, Object.values, Object.entries
const user = { id: 1, name: 'John', age: 30 }

const keys = Object.keys(user) // ['id', 'name', 'age']
const values = Object.values(user) // [1, 'John', 30]
const entries = Object.entries(user) // [['id', 1], ['name', 'John'], ['age', 30]]

// 遍历对象
Object.entries(user).forEach(([key, value]) => {
  console.log(`${key}: ${value}`)
})

// Object.fromEntries - 从条目创建对象
const entriesArray = [['name', 'Alice'], ['age', 25], ['city', 'NYC']]
const userFromEntries = Object.fromEntries(entriesArray)
console.log(userFromEntries) // { name: 'Alice', age: 25, city: 'NYC' }

// 可选链操作符 (?.)
const user = {
  name: 'John',
  address: {
    street: '123 Main St',
    city: 'New York'
  }
}

const city = user?.address?.city // 'New York'
const country = user?.address?.country // undefined
const phone = user?.contact?.phone // undefined

// 空值合并操作符 (??)
const settings = {
  theme: null,
  language: '',
  notifications: false,
  maxItems: 0
}

const theme = settings.theme ?? 'default' // 'default'
const language = settings.language ?? 'en' // '' (空字符串不是 null 或 undefined)
const notifications = settings.notifications ?? true // false
const maxItems = settings.maxItems ?? 10 // 0
```

### 数组方法
```javascript
// map - 转换数组
const numbers = [1, 2, 3, 4, 5]
const doubled = numbers.map(n => n * 2) // [2, 4, 6, 8, 10]

const users = [
  { id: 1, name: 'John', age: 30 },
  { id: 2, name: 'Jane', age: 25 },
  { id: 3, name: 'Bob', age: 35 }
]
const userNames = users.map(user => user.name) // ['John', 'Jane', 'Bob']

// filter - 过滤数组
const adults = users.filter(user => user.age >= 18)
const evenNumbers = numbers.filter(n => n % 2 === 0)

// reduce - 累计操作
const sum = numbers.reduce((total, n) => total + n, 0) // 15
const max = numbers.reduce((max, n) => n > max ? n : max, -Infinity)

const usersByName = users.reduce((acc, user) => {
  acc[user.name] = user
  return acc
}, {})

// find 和 findIndex
const john = users.find(user => user.name === 'John')
const janeIndex = users.findIndex(user => user.name === 'Jane')

// some 和 every
const hasAdults = users.some(user => user.age >= 18) // true
const allAdults = users.every(user => user.age >= 18) // false

// 展开运算符复制和合并数组
const numbersCopy = [...numbers]
const combined = [...numbers, 6, 7, 8]
const mergedArrays = [...[1, 2], ...[3, 4], ...[5, 6]]

// includes - 检查元素是否存在
const hasFive = numbers.includes(5) // true
const hasTen = numbers.includes(10) // false

// flat 和 flatMap (ES2019)
const nested = [1, [2, 3], [4, [5, 6]]]
const flat1 = nested.flat() // [1, 2, 3, 4, [5, 6]]
const flat2 = nested.flat(2) // [1, 2, 3, 4, 5, 6]

const sentences = ['Hello world', 'How are you', 'Nice to meet you']
const words = sentences.flatMap(sentence => sentence.split(' '))
// ['Hello', 'world', 'How', 'are', 'you', 'Nice', 'to', 'meet', 'you']

// Array.from - 从类数组创建数组
const nodeList = document.querySelectorAll('div')
const divs = Array.from(nodeList)

const range = Array.from({ length: 5 }, (_, i) => i + 1) // [1, 2, 3, 4, 5]

// Array.of - 创建数组
const arrayOf = Array.of(1, 2, 3) // [1, 2, 3]
const arrayConstructor = new Array(1, 2, 3) // [1, 2, 3]
const singleElement = new Array(5) // [empty × 5]
const singleElementOf = Array.of(5) // [5]
```

---

## 🎨 模板字符串和字符串方法

### 模板字符串
```javascript
// 基础模板字符串
const name = 'John'
const age = 30
const message = `Hello, my name is ${name} and I'm ${age} years old`

// 多行字符串
const html = `
  <div class="user">
    <h2>${name}</h2>
    <p>Age: ${age}</p>
  </div>
`

// 表达式计算
const price = 19.99
const quantity = 3
const total = `Total: $${(price * quantity).toFixed(2)}`

// 函数调用
const formatDate = (date) => date.toLocaleDateString()
const message = `Today is ${formatDate(new Date())}`

// 嵌套模板字符串
const user = {
  name: 'John',
  details: {
    email: 'john@example.com',
    phone: '123-456-7890'
  }
}

const userInfo = `
  User: ${user.name}
  Contact: ${user.details.email} / ${user.details.phone}
`

// 标签模板字符串
function highlight(strings, ...values) {
  return strings.reduce((result, string, i) => {
    const value = values[i] ? `<mark>${values[i]}</mark>` : ''
    return result + string + value
  }, '')
}

const highlighted = highlight`Name: ${name}, Age: ${age}`
// 结果: "Name: <mark>John</mark>, Age: <mark>30</mark>"
```

### 字符串方法
```javascript
// includes, startsWith, endsWith
const text = 'Hello, world!'

console.log(text.includes('world')) // true
console.log(text.includes('World')) // false

console.log(text.startsWith('Hello')) // true
console.log(text.endsWith('!')) // true

// repeat
const dash = '-'.repeat(10) // '----------'
const chorus = 'La '.repeat(3) + 'Land' // 'La La La Land'

// padStart 和 padEnd (ES2017)
const number = '42'
const padded = number.padStart(6, '0') // '000042'
const paddedEnd = number.padEnd(6, '0') // '420000'

const name = 'John'
const centered = name.padStart(10, ' ').padEnd(20, ' ')
// '    John      '

// trimStart 和 trimEnd (ES2019)
const spaced = '   Hello, world!   '
console.log(spaced.trimStart()) // 'Hello, world!   '
console.log(spaced.trimEnd()) // '   Hello, world!'
console.log(spaced.trim()) // 'Hello, world!'

// 字符串转数组
const str = 'Hello world'
const chars = [...str] // ['H', 'e', 'l', 'l', 'o', ' ', 'w', 'o', 'r', 'l', 'd']
const words = str.split(' ') // ['Hello', 'world']

// 数组转字符串
const arr = ['Hello', 'world']
const joined = arr.join(' ') // 'Hello world'
const joinedWithComma = arr.join(', ') // 'Hello, world'
```

---

## 🔧 函数进阶

### 默认参数
```javascript
// 基础默认参数
function greet(name = 'Guest', message = 'Hello') {
  return `${message}, ${name}!`
}

console.log(greet()) // 'Hello, Guest!'
console.log(greet('John')) // 'Hello, John!'
console.log(greet('Jane', 'Hi')) // 'Hi, Jane!'

// 对象默认参数
function createUser(options = {}) {
  const {
    name = 'Anonymous',
    age = 25,
    role = 'user',
    settings = {}
  } = options

  return { name, age, role, settings, createdAt: new Date() }
}

const user = createUser({ name: 'Alice', age: 30 })
console.log(user) // { name: 'Alice', age: 30, role: 'user', settings: {}, createdAt: ... }

// 函数作为默认参数
function createLogger(prefix = () => new Date().toISOString()) {
  return {
    log: (message) => console.log(`${prefix()}: ${message}`)
  }
}

const logger = createLogger()
logger.log('Hello') // "2023-01-01T12:00:00.000Z: Hello"
```

### 剩余参数和参数解构
```javascript
// 剩余参数
function sum(...numbers) {
  return numbers.reduce((total, n) => total + n, 0)
}

console.log(sum(1, 2, 3, 4, 5)) // 15

function join(separator, ...strings) {
  return strings.join(separator)
}

console.log(join(', ', 'apple', 'banana', 'cherry')) // 'apple, banana, cherry'

// 参数解构
function processUser({ name, age, address: { city } }) {
  return `${name} (${age}) from ${city}`
}

const user = {
  name: 'John',
  age: 30,
  address: {
    street: '123 Main St',
    city: 'New York'
  }
}

console.log(processUser(user)) // 'John (30) from New York'

// 混合使用
function configure({ timeout = 5000, retries = 3 }, ...endpoints) {
  return { timeout, retries, endpoints }
}

const config = configure(
  { timeout: 10000 },
  'https://api1.example.com',
  'https://api2.example.com'
)
```

### 函数属性和方法
```javascript
// 函数作为对象
function createCounter(initial = 0) {
  function counter() {
    return ++counter.count
  }

  counter.count = initial
  counter.reset = function() {
    counter.count = initial
  }

  counter.increment = function(by = 1) {
    counter.count += by
    return counter.count
  }

  return counter
}

const myCounter = createCounter(10)
console.log(myCounter()) // 11
console.log(myCounter.increment(5)) // 16
myCounter.reset()
console.log(myCounter()) // 11

// 函数组合
const compose = (...fns) => (value) =>
  fns.reduceRight((acc, fn) => fn(acc), value)

const add = x => x + 1
const multiply = x => x * 2
const toString = x => `Result: ${x}`

const composed = compose(toString, multiply, add)
console.log(composed(5)) // "Result: 12" ((5 + 1) * 2 = 12)
```

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[TypeScript 类型速查](./03-typescript-types.md)**: JavaScript的超集TypeScript类型系统
- 📄 **[React 语法速查](./01-react-syntax-cheatsheet.md)**: React组件中的现代JavaScript应用
- 📄 **[Next.js API 参考](./02-nextjs-api-reference.md)**: Next.js中的JavaScript API使用
- 📄 **[CSS 模式速查](./05-css-patterns.md)**: JavaScript操作CSS的现代化方法

### 参考章节
- 📖 **[数据获取模式](../framework-patterns/04-data-fetching-patterns.md)**: 异步JavaScript在数据获取中的应用
- 📖 **[状态管理模式](../framework-patterns/05-state-management-patterns.md)**: JavaScript对象在状态管理中的使用
- 📖 **[认证流程](../framework-patterns/07-authentication-flows.md)**: 异步JavaScript在用户认证中的应用
- 📖 **[环境配置](../../basics/01-environment-setup.md)**: 现代JavaScript开发环境搭建
- 📖 **[数据获取基础](../../basics/06-data-fetching-basics.md)**: JavaScript异步编程的实际应用
- 📖 **[状态管理基础](../../basics/07-state-management.md)**: JavaScript对象和数组操作实战

## 📝 总结

### 核心要点回顾
1. **现代变量声明**: 掌握了let和const的使用，理解了块级作用域和暂时性死区概念
2. **箭头函数**: 学会了箭头函数的语法和this绑定规则，避免了传统函数的常见陷阱
3. **解构赋值**: 熟练运用对象和数组解构，编写更简洁、可读性更强的代码
4. **异步编程**: 掌握了Promise、async/await的使用，能够处理复杂的异步操作流程
5. **现代方法**: 学会了数组和对象的现代方法，提高了代码编写效率和可维护性

### 学习成果检查
- [ ] 是否理解了let/const与var的区别和使用场景？
- [ ] 是否能够正确使用箭头函数和处理this绑定问题？
- [ ] 是否能够熟练运用解构赋值简化代码？
- [ ] 是否掌握了Promise和async/await异步编程模式？
- [ ] 是否能够使用现代JavaScript方法处理数据操作？

## 🤝 贡献与反馈

### 内容改进
如果你发现本文档有改进空间，欢迎：
- 🐛 **报告问题**: 在Issues中提出具体问题
- 💡 **建议改进**: 提出修改建议和补充内容
- 📝 **参与贡献**: 提交PR完善文档内容

### 学习反馈
分享你的学习体验：
- ✅ **有用内容**: 哪些部分对你最有帮助
- ❓ **疑问点**: 哪些内容需要进一步澄清
- 🎯 **建议**: 希望增加什么内容

## 🔗 外部资源

### 官方文档
- 📖 **[MDN JavaScript 指南](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)**: 完整JavaScript官方文档
- 📖 **[ES6 特性详解](https://es6-features.org/)**: ES6+ 特性详细介绍和示例
- 📖 **[JavaScript.info](https://javascript.info/)**: 现代JavaScript深度教程

### 快速参考

### 变量声明
- `const` - 常量声明（推荐优先使用）
- `let` - 块级作用域变量
- 避免 `var` - 函数作用域，变量提升

### 函数语法
- `() => {}` - 箭头函数
- `function name() {}` - 传统函数
- `async function() {}` - 异步函数

### 解构赋值
- `{ prop } = obj` - 对象解构
- `[a, b] = arr` - 数组解构
- `{ prop: newName } = obj` - 重命名解构

### 异步编程
- `new Promise()` - 创建Promise
- `async/await` - 异步函数
- `Promise.all()` - 并行执行
- `Promise.race()` - 竞争执行

### 数组方法
- `map()` - 转换数组
- `filter()` - 过滤数组
- `reduce()` - 累计操作
- `find()` - 查找元素
- `some()/every()` - 条件检查

### 对象操作
- 展开运算符 `{...obj}` - 对象合并
- `Object.keys/values/entries` - 对象遍历
- 可选链 `obj?.prop` - 安全属性访问
- 空值合并 `??` - 默认值处理

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0