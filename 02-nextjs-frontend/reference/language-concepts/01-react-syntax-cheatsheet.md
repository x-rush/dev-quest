# React 语法速查表

> **文档简介**: React 19核心语法和Hooks快速参考，提供日常开发中最常用的React语法模式
>
> **目标读者**: 有React基础的开发者，需要快速查阅React语法的开发者
>
> **前置知识**: JavaScript ES6+基础、React基础概念
>
> **预计时长**: 15-30分钟

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `reference` |
| **难度** | ⭐⭐⭐ |
| **标签** | `#react19` `#hooks` `#syntax` `#jsx` `#cheatsheet` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

---

## ⚛️ 组件语法

### 函数组件定义
```tsx
// 基础函数组件
function MyComponent() {
  return <div>Hello World</div>
}

// 箭头函数组件
const MyComponent = () => <div>Hello World</div>

// 带props的组件
interface Props {
  name: string
  age?: number
}

function UserCard({ name, age }: Props) {
  return (
    <div>
      <h2>{name}</h2>
      {age != null && <p>Age: {age}</p>}
    </div>
  )
}
```

### 组件导出
```tsx
// 命名导出
export const Button = () => <button>Click</button>

// 默认导出
export default function App() {
  return <div>App</div>
}
```

---

## 🪝 React Hooks

### useState - 状态管理
```tsx
import { useState } from 'react'

// 基础用法
const [count, setCount] = useState(0)

// 对象状态
interface User {
  name: string
  email: string
}
const [user, setUser] = useState<User>({ name: '', email: '' })

// 函数式更新
const increment = () => setCount(prev => prev + 1)

// 延迟初始化
const [data, setData] = useState(() => expensiveComputation())
```

### useEffect - 副作用处理
```tsx
import { useEffect } from 'react'

// 基础用法
useEffect(() => {
  console.log('组件挂载')
}, []) // 每次挂载建立副作用；开发 StrictMode 还会额外执行建立/清理检查

// 依赖项监听
useEffect(() => {
  document.title = `Count: ${count}`
}, [count])

// 清理函数
useEffect(() => {
  const timer = setInterval(() => console.log('tick'), 1000)
  return () => clearInterval(timer) // 清理副作用
}, [])
```

### useContext - 上下文使用
```tsx
import { createContext, useContext } from 'react'

// 创建上下文
const ThemeContext = createContext<'light' | 'dark'>('light')

// 提供者组件
function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  return (
    <ThemeContext.Provider value={theme}>
      <MainComponent />
    </ThemeContext.Provider>
  )
}

// 消费者Hook
function MainComponent() {
  const theme = useContext(ThemeContext)
  return <div className={theme}>Content</div>
}
```

### useReducer - 复杂状态管理
```tsx
import { useReducer } from 'react'

// 定义状态类型
type State = { count: number }

// 定义action类型
type Action = { type: 'increment' } | { type: 'decrement' } | { type: 'reset' }

// Reducer函数
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 }
    case 'decrement': return { count: state.count - 1 }
    case 'reset': return { count: 0 }
    default: return state
  }
}

// 使用reducer
const [state, dispatch] = useReducer(reducer, { count: 0 })

// 派发action
dispatch({ type: 'increment' })
```

### useMemo - 性能优化
```tsx
import { useMemo } from 'react'

// 缓存计算结果
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b)
}, [a, b])

// 缓存对象
const memoizedObject = useMemo(() => ({
  name,
  age,
  email: `${name.toLowerCase()}@example.com`
}), [name, age])
```

### useCallback - 函数缓存
```tsx
import { useCallback } from 'react'

// 缓存事件处理函数
const handleClick = useCallback((id: number) => {
  onItemClick(id)
}, [onItemClick])

// 缓存异步函数
const fetchData = useCallback(async () => {
  const result = await api.getData()
  setData(result)
}, [])
```

### useRef - 引用操作
```tsx
import { useRef, useEffect } from 'react'

// DOM引用
const inputRef = useRef<HTMLInputElement>(null)

useEffect(() => {
  inputRef.current?.focus()
}, [])

// 通用引用
const timerRef = useRef<NodeJS.Timeout>()

useEffect(() => {
  timerRef.current = setTimeout(() => console.log('done'), 1000)
  return () => clearTimeout(timerRef.current!)
}, [])
```

### 其余 Hooks 补遗（并发 / 外部存储 / 指令式 / 工具）

> 签名摘自 `@types/react@19.3`。React 19 四个异步 Hooks（`use` / `useOptimistic` / `useActionState` / `useFormStatus`）详见 **[React 19 关键 Hooks](./06-react-19-hooks.md)**。

#### useTransition - 非阻塞过渡更新
```tsx
const [isPending, startTransition] = useTransition()
// isPending: boolean - 过渡更新进行中
// startTransition(cb) - 把 cb 内的 setState 标记为低优先级"过渡"，可被紧急更新打断

function SearchBox() {
  const [query, setQuery] = useState('')
  const [list, setList] = useState<Item[]>([])
  const [isPending, startTransition] = useTransition()

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    setQuery(e.target.value)              // 紧急更新：输入框立即响应
    startTransition(() => {
      setList(filterList(e.target.value)) // 列表状态更新标记为过渡；filterList 本身仍同步执行，昂贵计算仍可能阻塞
    })
  }
  return (
    <>
      <input value={query} onChange={onChange} />
      {isPending && <span>筛选中…</span>}
      <List items={list} />
    </>
  )
}
```

#### useDeferredValue - 值的延迟副本
```tsx
function useDeferredValue<T>(value: T, initialValue?: T): T
// React 19 新增第二参 initialValue：首次渲染用初值，避免首帧就被慢计算阻塞

function Results({ query }: { query: string }) {
  const deferredQuery = useDeferredValue(query, '')
  // query（急）与 deferredQuery（缓）会得到两个渲染优先级，React 自动让 urgent 先行
  return <List query={deferredQuery} />
}
// 场景：没有把 setState 包进自己代码的机会时（props 来自父组件），代替 useTransition
```

#### useId - SSR 安全的稳定唯一 ID
```tsx
function useId(): string

function Field() {
  const id = useId()
  return (
    <>
      <label htmlFor={id}>邮箱</label>
      <input id={id} type="email" />
    </>
  )
}
// 服务端与客户端渲染出相同 ID（水合一致）；Math.random()/自增计数器会导致 SSR 不匹配
```

#### useSyncExternalStore - 订阅外部存储（React 提供的外部存储订阅协议）
```tsx
function useSyncExternalStore<Snapshot>(
  subscribe: (onStoreChange: () => void) => () => void, // 订阅并返回取消订阅函数
  getSnapshot: () => Snapshot,                           // 读取当前快照
  getServerSnapshot?: () => Snapshot,                    // 服务端渲染用的快照
): Snapshot

function useOnlineStatus() {
  return useSyncExternalStore(
    (onChange) => {
      window.addEventListener('online', onChange)
      window.addEventListener('offline', onChange)
      return () => {
        window.removeEventListener('online', onChange)
        window.removeEventListener('offline', onChange)
      }
    },
    () => navigator.onLine, // 原始值天然引用稳定
    () => true,             // 服务端快照（避免水合不匹配）
  )
}
```

> ⚠️ **getSnapshot 一致性陷阱**：React 会反复调用 `getSnapshot` 比对结果——在 store 真正变化前它必须返回**同一个引用**。若每次返回新对象/新数组（如 `() => ({ online: navigator.onLine })` 或 `() => store.items.slice()`），快照永远"变了"，触发无限重渲染。✅ 快照必须缓存在 store 内部，只在 store 真正变更时更新引用。

#### useLayoutEffect - DOM 提交后、浏览器绘制前同步执行
```tsx
function useLayoutEffect(effect: EffectCallback, deps?: DependencyList): void
// 时机：DOM 变更 → useLayoutEffect（同步）→ 浏览器绘制；useEffect 通常在绘制后运行，但交互触发时可能在绘制前，不能作为严格时序保证

function Tooltip({ target }: { target: HTMLElement }) {
  const ref = useRef<HTMLDivElement>(null)
  useLayoutEffect(() => {
    const rect = target.getBoundingClientRect() // 绘制前测量并定位，用户看不到跳动
    if (ref.current) ref.current.style.top = `${rect.bottom + 8}px`
  }, [target])
  return <div ref={ref}>提示</div>
}
// 场景：测量布局并同步修改样式（tooltip 定位、虚拟列表测量）
// 陷阱：SSR 下不执行并告警——Next.js 中默认首选 useEffect，仅测量/定位类需求用本 Hook
```

#### useImperativeHandle - 自定义 ref 暴露的接口
```tsx
function useImperativeHandle<T, R extends T>(
  ref: Ref<T> | undefined,
  init: () => R,
  deps?: DependencyList,
): void

interface TextInputHandle { focus(): void; clear(): void }

const TextInput = forwardRef<TextInputHandle>(function TextInput(_props, ref) {
  const inputRef = useRef<HTMLInputElement>(null)
  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current?.focus(),
    clear: () => { if (inputRef.current) inputRef.current.value = '' },
  }), [])
  return <input ref={inputRef} />
})
// 父组件只能调 focus()/clear()，拿不到整个 DOM —— 暴露受控 API 而非内部实现
// React 19：函数组件可直接把 ref 作为 prop 接收，不再必须包 forwardRef
```

#### useInsertionEffect - CSS-in-JS 注入专用（库作者用）
```tsx
function useInsertionEffect(effect: EffectCallback, deps?: DependencyList): void
// 在布局 Effect 前插入样式；不要依赖 DOM 是否已更新，此时不是渲染函数体

useInsertionEffect(() => {
  injectRule('.btn-primary', 'background: blue') // styled-components 等库的内部行为示意
}, [])
// 业务代码几乎用不到：数据请求/订阅用 useEffect，测量定位用 useLayoutEffect
```

#### useDebugValue - DevTools 中显示自定义 Hook 标签
```tsx
function useDebugValue<T>(value: T, format?: (value: T) => any): void

function useWindowSize() {
  const [w] = useState(() => (typeof window !== 'undefined' ? window.innerWidth : 0))
  useDebugValue(w, (width) => `${width}px`) // DevTools 显示 "WindowSize: 1920px"
  return w
}
// 用于调试显示，不应承载业务逻辑；format 只在 DevTools 打开时才被调用
```

### 自定义Hook
```tsx
// 自定义Hook规则：以use开头
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue)

  const increment = useCallback(() => {
    setCount(prev => prev + 1)
  }, [])

  const decrement = useCallback(() => {
    setCount(prev => prev - 1)
  }, [])

  const reset = useCallback(() => {
    setCount(initialValue)
  }, [initialValue])

  return { count, increment, decrement, reset }
}

// 使用自定义Hook
function Counter() {
  const { count, increment, decrement, reset } = useCounter(10)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
      <button onClick={reset}>Reset</button>
    </div>
  )
}
```

---

## 🎨 JSX 语法

### 基础JSX
```tsx
// 元素渲染
const element = <h1>Hello, world!</h1>

// 属性设置
const button = <button type="button" disabled={false}>Click me</button>

// 自定义属性
const div = <div data-testid="custom-id">Content</div>
```

### 表达式插值
```tsx
const name = 'John'
const age = 25
const isLoggedIn = true

// 文本插值
const greeting = <h1>Hello, {name}!</h1>

// 属性插值
const className = `user-${isLoggedIn ? 'active' : 'inactive'}`
const element = <div className={className}>User</div>

// 条件渲染
const message = isLoggedIn ? <p>Welcome back!</p> : <p>Please login</p>

// 复杂表达式
const user = (
  <div>
    <h2>{name}</h2>
    <p>Age: {age}</p>
    <p>Status: {isLoggedIn ? 'Active' : 'Inactive'}</p>
  </div>
)
```

### 列表渲染
```tsx
const users = [
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' },
  { id: 3, name: 'Charlie' }
]

// 基础列表
const userList = (
  <ul>
    {users.map(user => (
      <li key={user.id}>{user.name}</li>
    ))}
  </ul>
)

// 条件列表渲染
const activeUsers = users.filter(user => user.isActive)
const activeUserList = (
  <ul>
    {activeUsers.map(user => (
      <li key={user.id}>{user.name}</li>
    ))}
  </ul>
)
```

### 事件处理
```tsx
// 事件处理函数
function handleClick() {
  console.log('Button clicked')
}

// 带参数的事件处理
function handleDelete(id: number) {
  console.log(`Delete item ${id}`)
}

// 事件对象
function handleSubmit(event: React.FormEvent) {
  event.preventDefault()
  console.log('Form submitted')
}

// JSX中使用
<button onClick={handleClick}>Click</button>
<button onClick={() => handleDelete(item.id)}>Delete</button>
<form onSubmit={handleSubmit}>
  <button type="submit">Submit</button>
</form>
```

### 样式处理
```tsx
// 内联样式
const style = {
  color: 'red',
  fontSize: '16px',
  backgroundColor: '#f0f0f0'
}
const element = <div style={style}>Styled content</div>

// CSS类名
const className = 'container active'
const element = <div className={className}>Content</div>

// 条件样式
const isError = true
const element = <div className={isError ? 'error' : 'success'}>Message</div>

// CSS Modules (假设有styles.module.css)
import styles from './styles.module.css'
const element = <div className={styles.container}>Content</div>
```

### Fragment
```tsx
import { Fragment } from 'react'

// 使用Fragment避免额外DOM元素
function List() {
  return (
    <Fragment>
      <li>Item 1</li>
      <li>Item 2</li>
      <li>Item 3</li>
    </Fragment>
  )
}

// 简写语法
function List() {
  return (
    <>
      <li>Item 1</li>
      <li>Item 2</li>
      <li>Item 3</li>
    </>
  )
}
```

---

## 🔄 React 19 新特性

### use() Hook
```tsx
import { use } from 'react'

// 读取Promise
function DataComponent({ promise }: { promise: Promise<string> }) {
  const data = use(promise)
  return <div>Data: {data}</div>
}

// 读取Context
function ThemeComponent() {
  const theme = use(ThemeContext)
  return <div className={theme}>Content</div>
}
```

> 📖 **React 19 异步 Hook 速查**：`use` / `useOptimistic` / `useActionState` / `useFormStatus` 的完整签名、示例与陷阱见 **[React 19 关键 Hooks](./06-react-19-hooks.md)**。

### Server Components 语法
```tsx
// 服务器组件（默认导出）
async function ServerComponent() {
  const data = await fetchData()
  return <div>{data}</div>
}

// 客户端组件标记
'use client'

function ClientComponent() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

### Actions
```tsx
// 表单Action
async function updateName(formData: FormData) {
  'use server'
  const name = formData.get('name') as string
  await updateUser(name)
}

function NameForm() {
  return (
    <form action={updateName}>
      <input name="name" />
      <button type="submit">Update</button>
    </form>
  )
}
```

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[Next.js API 参考](./02-nextjs-api-reference.md)**: 深入了解Next.js框架API和路由系统
- 📄 **[TypeScript类型速查](./03-typescript-types.md)**: 学习React组件的类型定义和泛型使用
- 📄 **[现代JavaScript语法](./04-javascript-modern.md)**: 掌握React开发所需的ES6+语法
- 📄 **[CSS模式速查](./05-css-patterns.md)**: 学习React组件的样式和CSS-in-JS模式

### 参考章节
- 📖 **[本模块其他章节]**: [framework-patterns/客户端组件模式](../framework-patterns/03-client-components-patterns.md)中的组件状态管理部分
- 📖 **[其他模块相关内容]**: [basics/第一个Next.js应用](../../basics/02-first-nextjs-app.md)中的React基础部分

---

## 📝 总结

### 核心要点回顾
1. **函数组件语法**: 现代React开发的核心模式，支持TypeScript类型系统
2. **React Hooks**: useState、useEffect、useContext等核心Hook的使用
3. **React 19新特性**: use() Hook、Server Components、Actions等
4. **JSX语法**: 组件声明、条件渲染、列表处理等核心语法
5. **性能优化**: useMemo、useCallback、React.memo等优化技巧

### 学习成果检查
- [ ] 是否掌握了React函数组件的定义和使用？
- [ ] 是否理解了核心Hooks的作用和使用场景？
- [ ] 是否了解了React 19的新特性和改进？
- [ ] 是否能够使用TypeScript定义组件Props？
- [ ] 是否具备了React组件性能优化的基础知识？

---

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

---

## 🔗 外部资源

### 官方文档
- 📖 **[React 19 官方文档](https://react.dev/)**: 最新React完整文档
- 📖 **[React Hooks 参考](https://react.dev/reference/react)**: 所有Hooks的详细说明
- 📖 **[JSX 深入理解](https://react.dev/learn/writing-markup-with-jsx)**: JSX语法完整指南

### 快速参考
**Hook 使用规则**:
1. **只在函数顶层调用Hook** - 不要在循环、条件或嵌套函数中调用
2. **只在React函数中调用Hook** - 在React函数组件或自定义Hook中调用

**常用Hook清单**:
- `useState()` - 组件状态管理
- `useEffect()` - 副作用处理
- `useContext()` - 上下文消费
- `useReducer()` - 复杂状态管理
- `useCallback()` - 函数缓存优化
- `useMemo()` - 值缓存优化
- `useRef()` - 引用操作
- `useTransition()` - 非阻塞过渡更新（并发）
- `useDeferredValue()` - 值的延迟副本（并发）
- `useId()` - SSR 安全的稳定唯一 ID
- `useSyncExternalStore()` - 订阅外部存储（SSR 安全）
- `useLayoutEffect()` - DOM 提交后、绘制前同步副作用
- `useImperativeHandle()` - 自定义 ref 暴露的接口
- `useInsertionEffect()` - css-in-js 注入专用（库作者用）
- `useDebugValue()` - DevTools 自定义 Hook 标签
- `use()` - 读取Promise/Context (React 19)
- `useActionState()` - 表单Action状态管理 (React 19)
- `useOptimistic()` - 乐观更新 (React 19)
- `useFormStatus()` - 表单提交状态（react-dom, React 19）

**性能优化要点**:
- 使用`useMemo`缓存计算结果
- 使用`useCallback`缓存函数引用
- 合理使用`React.memo`包装组件
- 避免在render中创建新对象/函数

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2026年9月
**版本**: v1.0.0

<!-- full-library-explanation -->
## 渲染、事件与 Effect 分别承担什么

前置是闭包、不可变更新和函数调用。渲染根据当前 props/state 计算 UI，应保持纯粹；点击提交属于事件；订阅外部系统属于 Effect。setState 更新的是下一次渲染的状态，本次函数中的变量仍是这次渲染的快照。连续递增应使用 prev => prev + 1，不能假定调用后 count 立即改变。

Hook 必须在组件或自定义 Hook 的合法位置调用，速查中顶层展示的 useState/useEffect 是组件体片段，不能放到模块顶层执行。useMemo/useCallback 是性能工具，缓存可能被 React 丢弃，不能拿它们保证业务只执行一次。列表 key 应来自数据身份，useId 用于无障碍关联而不是生成列表键。

**练习**：在一次点击中连续调用三次 setCount(count + 1)，观察只增加 1；改用三次函数更新，应增加 3。开启 StrictMode 检查订阅是否出现重复连接，修复方式是成对清理而不是关闭检查。再给 age 传 0，确认条件渲染显示年龄而不是意外渲染一个裸 0。

依据：[状态快照](https://react.dev/learn/state-as-a-snapshot)、[Effect](https://react.dev/reference/react/useEffect)、[Insertion Effect](https://react.dev/reference/react/useInsertionEffect)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
