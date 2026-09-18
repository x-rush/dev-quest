# 错误与加载状态约定（error / loading / not-found）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
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

触发方式：在服务端组件中调用 notFound() 触发未找到控制流；实际 HTTP 状态还受是否已开始流式响应影响；`error.tsx` 由未捕获异常自动触发。

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
- loading.tsx 包裹该段 page 与下层内容，不包同层 layout；只想对慢数据加载需在组件树内自行使用 `<Suspense>`
- `notFound()` 抛出的是控制流信号，不要用 `try/catch` 包住它，否则会吞掉 404 行为
- 生产环境中 `error` 对象会被脱敏（移除敏感细节），详细原因需查服务端日志与 `digest`

## 模式不变量

- **异常兜底的覆盖范围由其作用域层级决定**：错误边界只捕获"作用域之内"的失败，同层布局抛出的错误不在同层兜底范围内，需要覆盖时把边界上移一层（对照 `error.tsx` 不捕获同层 `layout.tsx` 错误、`global-error.tsx` 兜根）。
- **恢复 UI 必须运行在交互语境**：提供重试能力的兜底组件必然是客户端组件——恢复是交互行为，服务端组件无法充当错误边界（对照 `error.tsx` / `global-error.tsx` 必须 `'use client'`）。
- **等待与失败是段级声明而非手动编排**：加载与错误的兜底以最近路由段为单位自动生效；需要比段更细的粒度时，在组件树内显式声明更小的边界（对照 `loading.tsx` 整段兜底 vs 自行 `<Suspense>`）。
- **控制流信号不得被异常处理吞掉**：以异常形式传递的导航信号（404）不能被 try/catch 拦截，否则其语义被破坏（对照 `notFound()` 不要 try/catch 的陷阱）。
- **用户可见的错误与可诊断的错误分离**：生产环境向用户呈现脱敏后的错误对象，完整定位依据只存在于服务端日志与摘要标识中（对照 `error` 脱敏 + `digest` 的陷阱条目）。

<!-- full-library-explanation -->
## 为等待、业务拒绝和程序失败安排不同反馈

前置是 Promise、Suspense 和 React 错误边界。加载状态表示结果尚未就绪，不意味着失败；输入错误、余额不足等可预期拒绝适合返回结构化结果；意外异常由错误边界兜底并记录诊断信息。事件处理器里的异常不会自动被普通渲染边界捕获，需要在动作路径处理。

reset 尝试重新渲染边界内容，不能保证清除数据缓存、重启服务器或撤销已发生的写入。提交超时后的“重试”必须考虑幂等，不能重复扣款。服务端错误在生产会隐藏细节，使用 digest 与服务端日志关联，不应把数据库连接字符串打印给用户。

**练习**：分别模拟两秒等待、不存在的文章和数据库异常，预期出现加载、缺失和错误三种 UI。让同层 layout 抛错，确认需要父层边界；让按钮事件抛错，确认不能依赖 error.tsx 自动展示。流式响应已经发出状态头后，not-found UI 可能伴随 HTTP 200，非流式才返回 404，应同时检查页面与网络状态。

依据：[错误处理](https://nextjs.org/docs/app/getting-started/error-handling)、[not-found](https://nextjs.org/docs/app/api-reference/file-conventions/not-found)。

## 🔗 相关条目

- [App Router 实战模式](./01-app-router-patterns.md)
- [服务端组件模式](./02-server-components-patterns.md)
- [异步请求 APIs](./09-async-request-apis.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
