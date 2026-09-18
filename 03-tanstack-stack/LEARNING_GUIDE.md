# TanStack：理解地图与学习规划

> 前置：React 组件、Hooks、数组变换、Promise 和 fetch；能区分请求失败与 HTTP 非成功状态。

## 先回答一个问题

**服务器数据会变化，页面怎样知道显示的是哪一份结果？**

TanStack 是一组可组合的库。Query 管请求结果，Table 管表格行为，Router 管地址与导航，Form 管输入与校验。先分清各自状态归属，再组合；它们并不是一个必须一次装齐的框架。

## 概念怎样连接

服务端数据与本地输入 → queryKey → 加载/成功/失败 → mutation 与失效 → 表格 → 路由参数 → 表单

| 概念 | 必要解释 |
|---|---|
| queryKey | 是结果的身份。不同用户或不同筛选条件需要不同键，否则两份请求可能共用错误结果。 |
| staleTime 与 gcTime | 前者讨论数据多久算新鲜，后者讨论无人使用的缓存保留多久；不是一条从新鲜走到删除的必经流水线。 |
| Headless | 库给出状态与操作，你负责按钮、表头、样式和可访问性；没有默认界面不等于没有行为。 |

## 从 0 到 1 的阅读顺序

以下按模块现有章节编号导航。章节中的“先理解，再动手”给出本节重点与自测；环境版本集中看[模块 README](README.md)。

1. [环境搭建与项目初始化](basics/01-environment-setup.md)
2. [Headless 设计哲学](basics/02-headless-philosophy.md)
3. [Query 基础：useQuery 与 useMutation](basics/03-query-fundamentals.md)
4. [Table 基础：列模型与数据行](basics/04-table-fundamentals.md)
5. [Router 基础：路由树、文件式路由与导航](basics/05-router-fundamentals.md)
6. [Form 基础：useForm 与字段绑定](basics/06-form-fundamentals.md)
7. [Query 高级特性：乐观更新、无限查询与失效策略](basics/07-advanced-features.md)
8. [第一个项目：城市天气数据面板](basics/08-first-project.md)

## 三个阶段如何验收

1. 只接 Query，列出加载、失败、空列表和有数据四种界面。
2. 创建后让对应列表失效；若用模拟服务，明确它是否真的保存写入。
3. 加入筛选后让筛选值同时进入 queryKey 和请求参数；来回切换不能串数据。

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

## 框架与高级主题怎么选

先掌握 Query 再按场景选 Table、Router、Form。Next.js 已管理路由时不为了“全家桶”再引入一套路由。框架升级前核对版本与迁移文档。

## 共用的 JavaScript 基础参考

[关键词与完整语法实验](../shared-resources/javascript-keywords.md)解释语言语法；[内置对象、方法与边界](../shared-resources/javascript-builtins.md)解释数组、字符串、对象、集合和 Promise。先区分语言、宿主 API 与框架函数，再查本模块特有内容。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [Query 框架要点：缓存键、staleTime/gcTime、失效与重试](reference/framework-essentials/01-query-essentials.md)
- [Router 框架要点：守卫、预加载、嵌套布局与 SSR 集成](reference/framework-essentials/02-router-essentials.md)
- [QueryClient 全局配置：defaultOptions 与网络模式](reference/framework-essentials/03-queryclient-config.md)
- [预取与 SSR 水合：prefetch、dehydrate 与流式预取](reference/framework-essentials/04-prefetch-ssr.md)
- [Mutation 状态与副作用：useMutationState 与 MutationCache](reference/framework-essentials/05-mutation-state.md)
- [Start Server Functions：createServerFn 全解](reference/framework-essentials/06-start-server-functions.md)

### language-concepts

- [Query 核心 API](reference/language-concepts/01-query-core-api.md)
- [Table 核心 API](reference/language-concepts/02-table-core-api.md)
- [Router 核心 API](reference/language-concepts/03-router-core-api.md)
- [Form 核心 API](reference/language-concepts/04-form-core-api.md)
- [TypeScript 模式](reference/language-concepts/05-typescript-patterns.md)
- [乐观更新：onMutate 快照与回滚](reference/language-concepts/06-optimistic-update.md)
- [无限查询：useInfiniteQuery 与游标分页](reference/language-concepts/07-infinite-query.md)
- [占位数据：placeholderData 与 isPlaceholderData](reference/language-concepts/08-placeholder-data.md)
- [Suspense 查询：useSuspenseQuery 与数据保证](reference/language-concepts/09-suspense-query.md)
- [网络模式与离线支持：networkMode](reference/language-concepts/10-network-mode.md)
- [URL 搜索参数状态：validateSearch 与类型化 search](reference/language-concepts/11-search-params.md)
- [useQueries：并行与动态查询列表](reference/language-concepts/12-use-queries.md)
- [useIsFetching / useIsMutating / useMutationState：全局加载指示器](reference/language-concepts/13-use-is-fetching-use-is-mutating.md)
- [缓存持久化：PersistQueryClientProvider 与按条目持久化](reference/language-concepts/14-query-persistence.md)
- [条件与依赖查询：enabled 与 skipToken](reference/language-concepts/15-enabled-conditional-queries.md)
- [渲染优化：select、notifyOnChangeProps 与 structuralSharing](reference/language-concepts/16-render-optimization.md)
- [FlexRender：Table 渲染入口与单元格上下文](reference/language-concepts/17-flexrender.md)
- [受控状态：state 切片与 OnChangeFn 回调](reference/language-concepts/18-controlled-state.md)
- [Outlet 与路由组件：notFoundComponent / errorComponent / pendingComponent](reference/language-concepts/19-outlet-and-route-components.md)
- [useMatch / useMatches / router.invalidate：匹配读取与刷新重校验](reference/language-concepts/20-use-match-hooks.md)
- [useField 与 createFormHook：字段复用与表单工厂](reference/language-concepts/21-usefield-and-createformhook.md)

### library-guides

- [生态集成：官方周边库指南](reference/library-guides/01-ecosystem-integrations.md)
- [相关库搭配：Zustand、Jotai、Axios、GraphQL Request](reference/library-guides/02-related-libs.md)

### quick-references

- [五库语法速查表](reference/quick-references/01-syntax-cheatsheet.md)
- [故障排除：常见错误与排查路径](reference/quick-references/02-troubleshooting.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
