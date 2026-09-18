# 渲染优化：服务器、客户端与等待边界

先修：React props/state、Promise、App Router 的 Server/Client Components。性能优化应从[可重复测量](../../testing/04-performance-testing.md)开始。本页回答“这项工作在哪里执行、为什么会重复、用户在等待什么”。

## 1. 一次页面访问的工作

服务器读取数据并生成响应；浏览器解析 HTML、下载样式与脚本，再执行客户端代码。Server Component 的代码不作为该组件的客户端 JavaScript 发送，但其输出与传给客户端的数据仍可能传到浏览器。因此不能把服务器组件当成可随意返回秘密数据的地方。

Client Component 在首次访问时也可以参与服务器预渲染。`'use client'` 表示客户端模块边界，不能据此在渲染中直接访问 window。把交互边界缩小到按钮、筛选器等需要状态的区域，能减少进入客户端依赖图的代码。[服务器与客户端组件](https://nextjs.org/docs/app/getting-started/server-and-client-components)

## 2. Suspense 让独立区域分别等待

下面是可放入 App Router 的机制演示。延迟用来模拟慢任务，生产代码应替换为真实数据读取；不代表性能基准。

```tsx
// app/page.tsx
import { Suspense } from 'react';

async function Recommendations() {
  await new Promise<void>((resolve) => setTimeout(resolve, 1000));
  return <ul><li>先学习组件边界</li><li>再学习缓存失效</li></ul>;
}

export default function Page() {
  return (
    <main>
      <h1>学习主页</h1>
      <Suspense fallback={<p>正在准备推荐……</p>}>
        <Recommendations />
      </Suspense>
    </main>
  );
}
```

外层内容可以先准备好，内部慢区域由 fallback 占位。但这个固定内容可能在生产构建期间被预渲染，发布后不一定每次访问都等待一秒。练习时观察开发模式边界行为，同时用生产构建输出确认实际路由策略。代理缓冲、浏览器缓冲也会影响肉眼看到的流式效果。

## 3. 什么时候减少重复渲染

先用 React Profiler 找到耗时组件。频繁渲染不必然慢；创建少量元素通常比维护复杂缓存更便宜。

| 工具 | 保存什么 | 不能解决什么 |
|---|---|---|
| memo | 在 props 未变化时跳过部分组件重渲染 | 组件自身 state/context 更新 |
| useMemo | 依赖未变化时复用计算结果 | 第一次计算、错误依赖、原地突变 |
| useCallback | 依赖未变化时复用函数引用 | 自动减少函数执行成本 |
| useDeferredValue | 让较慢区域使用延后的值 | 自动节流网络请求或提高算法速度 |

依赖项使用对象引用比较时，每次新建 `{filter}` 都可能使缓存失效。不要为保持引用而遗漏真实依赖，否则结果会过期。启用 React Compiler 的项目应结合其实际编译结果判断是否还需要手工缓存，不能机械给每个组件加 memo。[useMemo 的使用边界](https://react.dev/reference/react/useMemo)

## 4. 动态加载要落在确实可延后的功能上

```tsx
// app/components/help-panel.tsx
'use client';
import dynamic from 'next/dynamic';
import { useState } from 'react';

const Help = dynamic(() => import('./help-content'), {
  loading: () => <p>正在加载帮助……</p>,
});

export default function HelpPanel() {
  const [open, setOpen] = useState(false);
  return <>
    <button onClick={() => setOpen((value) => !value)}>切换帮助</button>
    {open && <Help />}
  </>;
}
```

```tsx
// app/components/help-content.tsx
export default function Help() {
  return <aside>选择主题后，先运行最小示例，再做练习。</aside>;
}
```

例子演示模块边界，内容很小，实际未必值得拆分。真正的大编辑器、图表等可结合网络请求确认是否减少初始下载。不要把首屏主要内容一律设为 ssr: false；它会改变预渲染行为，并可能推迟可见内容。[懒加载指南](https://nextjs.org/docs/app/guides/lazy-loading)

## 5. 缓存与渲染分别判断

缓存避免重复获取或计算，流式渲染改变等待内容的展示方式，客户端查询缓存负责另一套数据生命周期。三者不能用一个“开启缓存”开关概括。

使用 Cache Components 时先明确项目已开启相关配置。cacheLife 的命名配置同时包含 stale/revalidate/expire 语义，`hours` 不能简单解释成“所有缓存恰好一小时”。写入后按数据依赖失效，而不是公开一个允许任何人提交任意 tag/path 的重验证接口。详见本模块的[缓存参考](../language-concepts/02-nextjs-api-reference.md)。

## 6. 练习与判断

在页面加入一个计数器和独立帮助面板。记录点击计数器时哪些组件执行，再将状态移动到最小需要范围，比较结果。随后把帮助内容替换成真实大依赖，观察打开前后的脚本请求。

验收：能说明服务器执行、首次浏览器加载、客户端导航各自发生什么；保留一次修改前后的测量；按钮与内容在错误和加载状态下仍可使用。

自测：Suspense 会自动缓存请求吗？不会。useMemo 能避免初次重计算吗？不能。把秘密字段传给 Client Component，但 JSX 不显示它，安全吗？不安全，应在服务器返回数据前删除不需要的字段。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
