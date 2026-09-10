# 相关库搭配：Zustand、Jotai、Axios、GraphQL Request

## 概述

TanStack 各库职责清晰但不垄断：Query 管"服务端状态"，客户端状态、请求层、Schema 层仍需其他库配合。本篇给出主流组合的分工边界与最小示例。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Zustand` `#Jotai` `#Axios` `#GraphQL` `#技术选型` |
| **更新日期** | `2026年9月` |

---

## 1. Zustand：与 Query 的分工

### 定义

Zustand 管**客户端状态**（UI 状态、本地偏好），Query 管**服务端状态**（接口数据）。边界清晰后二者互不替代。

### 分工对照

| 数据 | 归属 | 示例 |
|------|------|------|
| 接口返回、会过期 | Query | 列表、详情、统计 |
| 纯 UI 偏好 | Zustand | 侧边栏折叠、主题 |
| 跨页面会话状态 | Zustand | 草稿、多步表单的中间态 |

### 示例

```ts
import { create } from 'zustand'

// Zustand：只放客户端状态
const useUiStore = create<{ sidebarOpen: boolean; toggle: () => void }>((set) => ({
  sidebarOpen: true,
  toggle: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}))

// 登录态也是客户端状态（token 来自接口，但"当前用户会话"是本地事实）
const useAuthStore = create<{ token: string | null; login: (t: string) => void }>(
  (set) => ({
    token: null,
    login: (token) => {
      set({ token })
      queryClient.clear() // 会话切换时清空服务端缓存
    },
  }),
)
```

### 陷阱

- 把接口响应 setState 进 Zustand = 自建缓存系统，失去 staleTime/失效等全部能力
- 反向错误：把弹窗开关放进 Query 缓存，Devtools 里全是 UI 噪音

## 2. Jotai：原子化客户端状态

### 定义

Jotai 以 atom 为单位做细粒度状态，与 Query 组合时可用社区包 `jotai-tanstack-query` 把查询包装成 atom。

### 示例

```ts
import { atomWithQuery } from 'jotai-tanstack-query'

const userAtom = atomWithQuery((get) => ({
  queryKey: ['user', get(userIdAtom)],
  queryFn: ({ queryKey: [, id] }) => fetchUser(id as string),
}))

// 组件中 useAtomValue(userAtom) —— Query 能力 + atom 组合性
```

### 陷阱

- `atomWithQuery` 会把 key 藏进 atom，Devtools 里的 key 需要与键工厂对齐，否则失效时对不上
- 团队同时用 Zustand 与 Jotai 是常见反模式——二选一

## 3. Axios：作为 queryFn 的请求层

### 定义

Axios 不与 Query 竞争——它是 queryFn 背后的 HTTP 客户端，负责拦截器、baseURL、类型化实例。

### 示例

```ts
// api/http.ts：集中配置请求层
import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  timeout: 10_000,
})

http.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${getAccessToken()}`
  return config
})

// 拦截器统一抛 Error（401 跳登录等全局逻辑放这里）
http.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(new Error(err.response?.data?.message ?? '请求失败')),
)

// queryFn 只做取数与解析
const fetchUsers = async (): Promise<User[]> => {
  const { data } = await http.get<User[]>('/users')
  return data
}
```

### 陷阱

- Axios 错误对象不是 `Error` 实例，Query 的 `error` 分支要适配（或像上例在拦截器统一转换）
- 取消（AbortSignal）需要手动接到 Axios 配置，否则 `cancelQueries` 无法取消 Axios 请求

## 4. GraphQL Request：queryFn 中的 GraphQL 客户端

### 定义

轻量 GraphQL 客户端（`graphql-request`）放 queryFn 里执行查询，服务端状态仍归 Query 管。

### 示例

```ts
import { GraphQLClient, gql } from 'graphql-request'

const client = new GraphQLClient('https://api.example.com/graphql', {
  headers: () => ({ authorization: `Bearer ${getAccessToken()}` }),
})

const POSTS_QUERY = gql`
  query Posts($page: Int!) {
    posts(page: $page) {
      id
      title
    }
  }
`

const fetchPosts = async (page: number): Promise<Post[]> => {
  const { posts } = await client.request(POSTS_QUERY, { page })
  return posts
}

useQuery({
  queryKey: queryKeys.posts.list({ page }),
  queryFn: () => fetchPosts(page),
})
```

### 陷阱

- 不需要缓存/订阅的简单场景，`graphql-request` + Query 足够；需要规范化缓存与订阅时再上 Apollo/urql
- GraphQL 错误在 `errors` 数组里而非 HTTP 状态码，queryFn 里要显式抛出

## 5. 选型速记

| 需求 | 推荐 |
|------|------|
| 服务端数据缓存 | TanStack Query（唯一答案） |
| 简单客户端状态 | Zustand |
| 复杂依赖图、细粒度更新 | Jotai |
| HTTP 请求层 | 原生 fetch / Axios / ky |
| GraphQL | graphql-request（轻）/ urql（重） |
| SWR vs Query | 小项目 SWR 够用；需要 mutation/乐观更新/离线则 Query |

## 相关文档

- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - 请求层的宿主 API
- 📄 **[Query 框架要点](../framework-essentials/01-query-essentials.md)** - 与请求层配合的缓存语义
- 📄 **[TypeScript 模式](../language-concepts/05-typescript-patterns.md)** - zod 推断与判别联合
