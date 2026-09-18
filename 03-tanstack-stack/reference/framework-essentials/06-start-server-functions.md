# Start Server Functions：createServerFn 全解

## 概述

TanStack Start 用 `createServerFn` 把"一段只在服务端跑的代码"声明成可直接 import 的函数：客户端调用它就是一次类型安全的 RPC，服务端调用它就是普通函数调用。本篇覆盖定义链式、校验、两端调用行为差异与序列化边界。路由侧的 loader 协作见 [Router 核心 API](../language-concepts/03-router-core-api.md)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#createServerFn` `#Start` `#RPC` `#前后端一体` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. 定义：method → validator → handler 链式

### 定义

`createServerFn` 返回一个 builder，按 `method → validator → handler` 链式组装：`method` 只允许 `'GET' | 'POST'`；`validator`（旧名 `inputValidator` 已弃用）接收 zod 等 schema 或普通函数，其**输出类型**成为 handler 内 `data` 的类型；`handler` 是真正在服务端执行的函数体。

### 语法

```ts
import { createServerFn } from '@tanstack/react-start'
import { z } from 'zod'

const getTodos = createServerFn({ method: 'GET' })
  .validator(z.object({ page: z.number().optional() }))
  .handler(async ({ data }) => {
    // data 是校验器的"输出"类型：{ page?: number }
    return { items: [`todo-${data.page ?? 1}`], page: data.page ?? 1 }
  })

const addTodo = createServerFn({ method: 'POST' })   // 写操作用 POST
  .validator(z.object({ title: z.string().min(1) }))
  .handler(async ({ data }) => ({ ok: true as const }))

// 无 validator：不传 data 也能调用（OptionalFetcher）
const healthCheck = createServerFn({ method: 'GET' }).handler(() => 'ok' as const)

// 函数式 validator（不引 zod 时）
const echoCount = createServerFn({ method: 'GET' })
  .validator((input: unknown) => (typeof input === 'number' ? input : 0))
  .handler(({ data }) => data * 2)
```

| 项 | 说明 |
|----|------|
| `method` | 仅 `'GET' \| 'POST'`：GET 语义取数，POST 语义写入 |
| `validator` | schema（zod 等）或 `(input: unknown) => T`；声明后调用端 `data` 必填（RequiredFetcher） |
| 无 `validator` | 调用端可不传 `data`（OptionalFetcher） |
| `handler` 上下文 | `{ data, serverFnMeta, context, method }`，最常用的是 `data` |

## 2. 调用端：客户端与服务端同一签名

### 定义

调用 server function 时传 `{ data }` 对象、拿到 `Promise`——组件里（事件回调、effect）与浏览器端代码、服务端代码的调用签名完全一致，类型随 validator/返回值自动流转。

### 语法与示例

```tsx
import { useQuery } from '@tanstack/react-query'

function TodoList() {
  const todoQuery = useQuery({
    queryKey: ['todos'],
    queryFn: () => getTodos({ data: { page: 1 } }),  // 有 validator：data 必填
  })
  if (todoQuery.isPending) return <p>加载中</p>
  if (todoQuery.isError) return <p>{todoQuery.error.message}</p>
  return <ul>{todoQuery.data.items.map((t) => <li key={t}>{t}</li>)}</ul>
}

async function clientFlow() {
  const health = await healthCheck()                       // 无 validator：不传 data
  const page1 = await getTodos({ data: { page: 1 } })      // 返回 Promise，await 取值
  const doubled = await echoCount({ data: 21 })
  const added = await addTodo({ data: { title: '写字典' } })
  return [health, page1.page, doubled, added.ok] as const
}
```

## 3. 服务端复用：loader 与 server function 之间

### 定义

server function 不是"只能从浏览器调"的端点：服务端代码（路由 loader、其他 server function 的 handler）里直接 `await` 它，走的是本地函数调用路径，签名不变。

### 示例

```tsx
const postRouteLoader = () => clientFlow()   // loader 里像普通异步函数一样调用

const nested = createServerFn({ method: 'GET' }).handler(async () => {
  const todos = await getTodos({ data: { page: 2 } })  // server fn 嵌套调用同签名
  return todos.items.length
})
```

## 4. 序列化边界：strict 选项

### 定义

server function 的输入输出默认受**可序列化约束**（跨网络传输的前提）：允许类型由框架序列化器决定。`strict: false` 只放宽 TypeScript 序列化检查，运行时仍须能正确传输。

### 示例

```ts
const timestamp = createServerFn({ method: 'GET' })
  .handler(() => ({ at: new Date(0).toISOString() })) // 显式字符串适合通用日期契约
```

## 5. 陷阱

- ❌ `method` 传 `'PUT'`/`'DELETE'`：类型直接报错——只允许 `GET`/`POST`，删除语义也用 POST 表达
- ❌ 仍用 `inputValidator`：已弃用，迁移到 `validator`
- ❌ 有 validator 却不传 `data`（`getTodos()`）：RequiredFetcher 类型报错；无 validator 的函数反过来传 `{ data }` 也不必要
- ❌ 把 validator 当"只校验不转换"：handler 里的 `data` 是 validator 的**输出**，zod 的 `.transform()` 结果会直接生效
- ❌ 把 strict:false 当成运行时序列化修复：它只放宽类型检查；自定义值仍需框架支持或显式转换
- ❌ 以为客户端调用是"魔法同构"：跨网络时是真实 HTTP 请求（GET/POST），入参出参都会过序列化
- ✅ server function 与 TanStack Query 组合：`queryFn: () => getTodos({ data })`，缓存与失效仍归 Query 管

## 相关文档

- 📄 **[Router 核心 API](../language-concepts/03-router-core-api.md)** - loader 中调用 server function
- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - queryFn 组合与缓存失效
- 📄 **[SSR 与预取](./04-prefetch-ssr.md)** - 服务端数据预取与 server function 的分工
- 📄 **[Router 基础教程](../../basics/05-router-fundamentals.md)** - loader 数据流入门
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - 一行式签名


<!-- full-library-explanation -->
## 一次函数调用跨越的真实边界

先修：Promise、HTTP、运行时校验。浏览器调用 server function 时实际通过网络进入服务端，TypeScript 类型不能阻止手工构造的请求。validator 应验证 unknown 或使用 schema；只写 `(data: Input) => data` 只是类型声明，不能检查内容。

服务端 handler 中仍需读取并验证会话、检查资源归属，再执行写入。客户端传来的 userId 不能成为授权依据。Query 负责缓存调用结果，Start 负责执行边界，两者不会替对方自动完成权限或失效。

strict:false 只放宽序列化的类型检查，不给运行时增加传输能力。框架序列化能力也不等于 JSON.stringify；不要用它来解释“只有 strict:false 才能返回 Date”。跨网络返回自定义类前应检查所用版本及其序列化适配。

**练习：** 把 echoCount 改为拒绝非有限数字，分别从页面传入 21、字符串与 NaN；合法值预期 42，其他输入应失败。再对写操作加入测试会话，确认直接调用同样受权限限制。参考[Server Functions](https://tanstack.com/start/latest/docs/framework/react/guide/server-functions)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
