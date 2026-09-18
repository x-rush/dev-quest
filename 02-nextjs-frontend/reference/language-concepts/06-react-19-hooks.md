# React 19 关键 Hooks（use / useOptimistic / useActionState / useFormStatus）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `language-concepts`

## 📌 定义

React 19 围绕"异步 UI"补齐了四组 Hook，它们与 Next.js App Router 的 Server Actions 组合构成现代表单与数据变更的标准方案：

- **`use()`** —— 在渲染期间读取 Promise 或 Context 的值。与普通 Hook 不同，它可以在条件语句和循环中调用；配合 `<Suspense>` 时，组件会在 Promise resolve 前挂起。
- **`useOptimistic()`** —— 乐观更新：在异步操作（如 Server Action）完成前，先基于当前状态渲染"预期结果"，操作 settle 后自动回落到真实透传状态。
- **`useActionState()`** —— 以 Action 为中心管理表单状态：把"上一次提交的结果"作为状态保存，并暴露 `isPending` 提交中标记。
- **`useFormStatus()`** —— 读取**最近的父级 `<form>`** 的提交状态（`pending` / `data` / `method` / `action`），常用于让提交按钮独立成组件并显示 loading。

## 📖 语法/签名

以下为 React 19 系列常用签名摘要，精确重载以项目锁定类型包为准：

```ts
// react
function use<T>(usable: Usable<T>): T
// Usable<T> = Promise<T> | Context<T> 等可读取值

// react
function useOptimistic<State>(
  passthrough: State,
): [State, (action: State | ((pendingState: State) => State)) => void]

function useOptimistic<State, Action>(
  passthrough: State,
  reducer: (state: State, action: Action) => State,
): [State, (action: Action) => void]

// react —— 注意 action 的签名是 (state, payload)，不是事件处理器签名
function useActionState<State, Payload>(
  action: (state: Awaited<State>, payload: Payload) => State | Promise<State>,
  initialState: Awaited<State>,
  permalink?: string,
): [state: Awaited<State>, dispatch: (payload: Payload) => void, isPending: boolean]

// react-dom —— useFormStatus 的返回类型（判别联合）
function useFormStatus(): FormStatus

interface FormStatusPending {
  pending: true
  data: FormData
  method: string
  action: string | ((formData: FormData) => void | Promise<void>)
}
interface FormStatusNotPending {
  pending: false
  data: null
  method: null
  action: null
}
type FormStatus = FormStatusPending | FormStatusNotPending
```

## 💡 示例

### useActionState + useFormStatus：Server Action 表单（标准组合）

```tsx
// app/actions.ts
'use server'

export async function subscribeNewsletter(
  prevState: { ok: boolean; message: string },
  formData: FormData,
): Promise<{ ok: boolean; message: string }> {
  const email = String(formData.get('email') ?? '')
  if (!email.includes('@')) {
    return { ok: false, message: '邮箱格式不正确' }
  }
  await saveSubscriber(email) // 写库等真实副作用
  return { ok: true, message: '订阅成功' }
}
```

```tsx
// components/SubmitButton.tsx —— 必须是 <form> 的子组件
'use client'

import { useFormStatus } from 'react-dom'

export function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button type="submit" disabled={pending}>
      {pending ? '提交中…' : '订阅'}
    </button>
  )
}
```

```tsx
// components/NewsletterForm.tsx
'use client'

import { useActionState } from 'react'
import { subscribeNewsletter } from '@/app/actions'
import { SubmitButton } from './SubmitButton'

const initialState = { ok: false, message: '' }

export function NewsletterForm() {
  const [state, formAction] = useActionState(subscribeNewsletter, initialState)

  return (
    <form action={formAction}>
      <input type="email" name="email" required />
      <SubmitButton />
      {state.message && !state.ok && <p role="alert">{state.message}</p>}
    </form>
  )
}
```

### useOptimistic：乐观更新点赞列表

```tsx
'use client'

import { useOptimistic, useState, useTransition } from 'react'
import { likePost } from '@/app/actions'

interface Post {
  id: number
  title: string
  likes: number
}

export function PostList({ posts }: { posts: Post[] }) {
  const [snapshot, setSnapshot] = useState(posts)
  const [, startTransition] = useTransition()

  // 提交期间展示乐观状态；likePost 结束后自动回落到 setSnapshot 的真实值
  const [optimisticPosts, addOptimisticLike] = useOptimistic(
    snapshot,
    (state, postId: number) =>
      state.map((p) => (p.id === postId ? { ...p, likes: p.likes + 1 } : p)),
  )

  function handleLike(postId: number) {
    startTransition(async () => {
      addOptimisticLike(postId)            // 1. 立即渲染 +1
      const fresh = await likePost(postId) // 2. 真实提交
      startTransition(() => setSnapshot(fresh)) // await 后再次标记过渡更新
    })
  }

  return optimisticPosts.map((post) => (
    <article key={post.id}>
      <h3>{post.title}</h3>
      <button onClick={() => handleLike(post.id)}>👍 {post.likes}</button>
    </article>
  ))
}
```

### use：读取 Server Component 传入的 Promise / 条件读取 Context

```tsx
// app/posts/page.tsx —— Server Component
import { Suspense } from 'react'
import { PostFeed } from '@/components/PostFeed'
import { getPostList } from '@/lib/data' // 已用 "use cache" 缓存的异步函数

export default function PostsPage() {
  return (
    <Suspense fallback={<p>加载中…</p>}>
      <PostFeed postsPromise={getPostList()} />
    </Suspense>
  )
}
```

```tsx
// components/PostFeed.tsx
'use client'

import { use } from 'react'

type Post = { id: number; title: string };
export function PostFeed({ postsPromise }: { postsPromise: Promise<Post[]> }) {
  const posts = use(postsPromise) // resolve 前，组件在此挂起（由 Suspense 兜底）
  return <ul>{posts.map((p) => <li key={p.id}>{p.title}</li>)}</ul>
}
```

## ⚠️ 常见陷阱

- **`use()` 是唯一可以在条件/循环中调用的 Hook**，但依然只能在组件或自定义 Hook 内调用。
- 传给 `use()` 的 Promise 必须引用稳定：在客户端渲染体内直接 use(fetch(...)) 会每次渲染新建 Promise，导致无限挂起或重复请求。应传入 Server Component 里创建的 Promise，或 `'use cache'` 函数的返回值。
- `useOptimistic` 的乐观状态**无法自己落定**——异步操作结束后会自动回落到 `passthrough`。必须在操作完成后把服务端真实结果写入正式状态（如 `setSnapshot`），否则 UI 会"闪回"旧值。
- `useActionState` 的 `action` 第一个参数是**上一个 state**，第二个参数才是 `FormData`/payload；不要按事件处理器 `(event)` 的签名写。
- `useFormStatus` 读的是**最近的父级 `<form>`**：把它用在渲染 `<form>` 的组件本体或更上层的父组件中，永远读到 `pending: false`。正确的做法是把按钮/状态条抽成 `<form>` 的子组件。
- `useActionState` 第三参数 `permalink` 用于渐进增强下水合前提交的稳定目标 URL（跳转到稳定的permalink 页面再展示结果），常规表单不需要传。
- `useFormStatus` 从 `react-dom` 导入，而不是 `react`。

<!-- full-library-explanation -->
## 乐观状态要有成功、失败和并发三个出口

前置是 Promise、表单提交与正式状态。useOptimistic 只是临时展示层，服务端拒绝后需要恢复正式数据并向用户解释；它不替你保证幂等、权限或写入成功。若两次点赞并发返回完整列表，旧请求后返回可能覆盖新结果，应串行化、使用版本号拒绝旧响应，或通过框架的数据刷新机制重新获取权威状态。

示例 saveSubscriber、likePost 和 getPostList 是项目依赖，需要提供实际实现；邮箱 includes('@') 只演示状态反馈，不是完整验证。读取 FormData 时先确认 string，服务器仍需校验长度、格式和提交频率。useActionState 保存动作结果，但不自动执行这些业务规则。

**练习**：让提交延迟一秒并失败，预期 pending 期间按钮禁用、失败后恢复可提交并显示错误；让第二次操作先返回，验证旧响应不会覆盖新状态。将 useFormStatus 移到 form 外层，解释它读不到内层表单的原因。use 读取 Promise 的拒绝由错误边界处理，Suspense 负责等待，不能把二者当成同一种状态。

依据：[useActionState](https://react.dev/reference/react/useActionState)、[useOptimistic](https://react.dev/reference/react/useOptimistic)、[useTransition](https://react.dev/reference/react/useTransition)。

## 🔗 相关条目

- [React 语法速查表](./01-react-syntax-cheatsheet.md) —— 基础 Hooks 与 `use()` 速查
- [表单验证模式](../framework-patterns/06-form-validation-patterns.md)
- [错误与加载状态约定](../framework-patterns/11-error-loading-patterns.md)
- [数据仪表板项目](../../projects/03-dashboard-analytics.md) —— RSC 优先数据获取中的 Suspense/`use` 组合


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
