# TanStack 无限查询 v5 API 验证

核对日期：2026-09-20。使用 Node 24.21.0、TypeScript 5.9.3 和 `@tanstack/react-query` 5.90.20，为正文的无限查询选项构造 `UseInfiniteQueryOptions` 并执行严格类型检查。

`queryKey`、异步 `queryFn` 的 `pageParam`、`initialPageParam: 0`、返回 `number | null` 的 `getNextPageParam` 与 `maxPages: 10` 均通过 `tsc --strict --noEmit`。输出：`PASS useInfiniteQuery v5 options type check`。

这只覆盖 v5 选项的类型契约；不覆盖 React Provider、页面渲染、真实游标 HTTP 请求或并发追加行为。
