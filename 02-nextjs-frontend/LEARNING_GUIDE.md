# Next.js：理解地图与学习规划

> 前置：HTML/CSS、JavaScript 函数与数组；会基本 JSX、props、useState 和 Promise。不会 React 时先补这些概念，不直接从缓存策略开始。

## 先回答一个问题

**同一页面里，哪些工作在服务端执行，哪些交互必须在浏览器执行？**

React 用组件描述界面，Next.js 在其上组织路由、服务端执行与构建。先区分运行位置，再学习取数和缓存；否则容易把服务端秘密或浏览器专用 API 放错地方。

## 概念怎样连接

React 组件 → 文件路由与布局 → 服务端/客户端边界 → 数据读取 → 表单提交 → 状态与缓存 → 部署

| 概念 | 必要解释 |
|---|---|
| 路由与布局 | 路径决定显示哪一页，布局决定多页共享的外壳；文件夹存在不等于一定有可访问页面。 |
| 客户端边界 | 交互状态、事件处理和浏览器 API 需要客户端组件；不要因为有一个按钮就把整棵页面都变成客户端入口。 |
| 缓存 | 首先说明数据是否允许过期，再决定缓存和失效；缓存命中与组件重新渲染不是一回事。 |

## 从 0 到 1 的阅读顺序

以下按模块现有章节编号导航。章节中的“先理解，再动手”给出本节重点与自测；环境版本集中看[模块 README](README.md)。

1. [Next.js 16 开发环境搭建完整指南](basics/01-environment-setup.md)
2. [Next.js 16 第一个应用创建完整指南](basics/02-first-nextjs-app.md)
3. [Next.js 16 + TypeScript 7 集成配置完整指南](basics/03-typescript-integration.md)
4. [Next.js 16 布局和路由设计完整指南](basics/04-layouts-routing.md)
5. [Next.js 16 + Tailwind CSS 4 企业级样式开发完整指南](basics/05-styling-with-tailwind.md)
6. [Next.js 16 数据获取基础完整指南](basics/06-data-fetching-basics.md)
7. [Next.js 16 状态管理基础完整指南](basics/07-state-management.md)
8. [Next.js 16 第一个完整项目实战指南](basics/08-first-project.md)

## 三个阶段如何验收

1. 做主页和详情页，直接输入详情 URL 也能显示；说明哪部分布局复用。
2. 把一个服务端数据列表和一个客户端计数器放在同页，解释各自运行位置。
3. 提交一条数据后验证列表更新，再覆盖无数据、请求失败与无权限。

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

## 框架与高级主题怎么选

App Router 为主线；Tailwind 解决样式表达，TanStack Query 解决客户端远程状态，各自按需要引入。高级缓存、流式响应与性能优化放到能测量实际问题之后。

## 共用的 JavaScript 基础参考

[关键词与完整语法实验](../shared-resources/javascript-keywords.md)解释语言语法；[内置对象、方法与边界](../shared-resources/javascript-builtins.md)解释数组、字符串、对象、集合和 Promise。先区分语言、宿主 API 与框架函数，再查本模块特有内容。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### development-tools

- [Next.js 16 现代测试工具完整指南](reference/development-tools/01-testing-tools.md)
- [Next.js 16 现代样式工具完整指南](reference/development-tools/02-styling-tools.md)
- [Next.js 16 现代包管理器完整指南](reference/development-tools/03-package-managers.md)
- [Next.js 16 现代调试工具完整指南](reference/development-tools/04-debugging-tools.md)

### framework-patterns

- [Next.js 16 App Router 实战模式精要](reference/framework-patterns/01-app-router-patterns.md)
- [Next.js 16 服务端组件模式详解](reference/framework-patterns/02-server-components-patterns.md)
- [Next.js 16 客户端组件模式详解](reference/framework-patterns/03-client-components-patterns.md)
- [企业级数据获取模式详解](reference/framework-patterns/04-data-fetching-patterns.md)
- [企业级状态管理模式详解](reference/framework-patterns/05-state-management-patterns.md)
- [Next.js 16 企业级表单验证完整指南](reference/framework-patterns/06-form-validation-patterns.md)
- [Next.js 16 企业级认证流程完整指南](reference/framework-patterns/07-authentication-flows.md)
- [Cache Components 与 "use cache" 指令](reference/framework-patterns/08-caching-patterns.md)
- [异步请求 APIs（params / searchParams / cookies / headers）](reference/framework-patterns/09-async-request-apis.md)
- [网络代理模式（proxy.ts）](reference/framework-patterns/10-proxy-patterns.md)
- [错误与加载状态约定（error / loading / not-found）](reference/framework-patterns/11-error-loading-patterns.md)
- [Metadata API 与 next/script](reference/framework-patterns/12-metadata-and-script.md)
- [路由段配置（Route Segment Config）](reference/framework-patterns/13-route-segment-config.md)
- [环境变量（.env 加载顺序 / NEXT_PUBLIC_ 内联 / 类型声明）](reference/framework-patterns/14-env-vars.md)

### language-concepts

- [React 语法速查表](reference/language-concepts/01-react-syntax-cheatsheet.md)
- [Next.js API 参考手册](reference/language-concepts/02-nextjs-api-reference.md)
- [TypeScript 类型速查手册](reference/language-concepts/03-typescript-types.md)
- [现代 JavaScript 语法速查手册](reference/language-concepts/04-javascript-modern.md)
- [CSS-in-JS 和现代样式模式速查手册](reference/language-concepts/05-css-patterns.md)
- [React 19 关键 Hooks（use / useOptimistic / useActionState / useFormStatus）](reference/language-concepts/06-react-19-hooks.md)
- [TypeScript 类型收窄与类型守卫](reference/language-concepts/07-type-narrowing-guards.md)
- [TypeScript 枚举、环境声明与模块系统](reference/language-concepts/08-ts-declarations-modules.md)
- [JavaScript 核心语义（事件循环 / 闭包 / 原型链 / this / 可迭代协议）](reference/language-concepts/09-js-core-semantics.md)
- [Web 平台 API 速查（fetch / URL / FormData / Storage / Blob / structuredClone / BroadcastChannel）](reference/language-concepts/10-web-platform-apis.md)

### library-guides

- [02 模块生态依赖地图（按用途分组的第三方库导览）](reference/library-guides/03-ecosystem-map.md)

### performance-optimization

- [Next.js 16 渲染性能优化完整指南](reference/performance-optimization/01-rendering-optimization.md)
- [Next.js 16 打包优化完全指南](reference/performance-optimization/02-bundle-optimization.md)
- [图片与字体优化（next/image / next/font）](reference/performance-optimization/03-image-font-optimization.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
