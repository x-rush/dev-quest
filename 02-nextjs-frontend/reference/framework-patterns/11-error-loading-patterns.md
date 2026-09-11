# 错误与加载状态约定（error / loading / not-found）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（无难度门槛）
> **分类**: `framework-patterns`

## 📌 定义

App Router 用**约定文件**处理路由段的异常与等待状态：`error.tsx` 捕获渲染错误并提供恢复 UI，`loading.tsx` 在路由段挂起时自动包一层 Suspense 兜底，`not-found.tsx` 渲染 404 场景，`global-error.tsx` 兜底根布局级错误。它们以最近路由段为作用域自动生效，无需手动编排，是流式渲染（streaming）与错误边界（error boundary)的声明式封装。

## 📖 语法/签名

```tsx
// app/error.tsx —— 必须是客户端组件
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void; // 重试：重新渲染该路由段
}) {
  return (
    <div role="alert">
      <h2>出错了</h2>
      <button onClick={() => reset()}>重试</button>
    </div>
  );
}
```

```tsx
// app/loading.tsx —— 路由段加载兜底
export default function Loading() {
  return <p className="animate-pulse">加载中…</p>;
}

// app/not-found.tsx —— notFound() 触发的 404 UI
export default function NotFound() {
  return <h2>页面不存在</h2>;
}
```

触发方式：在服务端组件中调用 `notFound()` 抛出 404；`error.tsx` 由未捕获异常自动触发。

## 💡 示例

```tsx
// app/blog/[slug]/page.tsx —— 未找到文章时触发 404 约定
import { notFound } from 'next/navigation';

export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await getPost(slug);
  if (!post) notFound(); // 渲染最近的 not-found.tsx
  return <article>{post.title}</article>;
}
```

```tsx
// 全局兜底：app/global-error.tsx（替换根布局，需自带 <html>/<body>）
'use client'

export default function GlobalError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <html>
      <body>
        <h2>应用级错误</h2>
        <button onClick={() => reset()}>重试</button>
      </body>
    </html>
  );
}
```

## ⚠️ 常见陷阱

- `error.tsx` 必须标注 `'use client'`；服务端组件无法作为错误边界
- `error.tsx` 不捕获同层 `layout.tsx` 抛出的错误——需要覆盖布局错误时，把 `error.tsx` 放在父路由段或使用 `global-error.tsx`
- `global-error.tsx` 替换的是整个根布局，必须自含 `<html>` 与 `<body>`
- `loading.tsx` 的兜底范围是"整个路由段"；只想对慢数据加载需在组件树内自行使用 `<Suspense>`
- `notFound()` 抛出的是控制流信号，不要用 `try/catch` 包住它，否则会吞掉 404 行为
- 生产环境中 `error` 对象会被脱敏（移除敏感细节），详细原因需查服务端日志与 `digest`

## 🔗 相关条目

- [App Router 实战模式](./01-app-router-patterns.md)
- [服务端组件模式](./02-server-components-patterns.md)
- [异步请求 APIs](./09-async-request-apis.md)
