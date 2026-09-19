# TanStack placeholderData API 验证

核对日期：2026-09-20。临时 Node 24.21.0 工程安装 `@tanstack/react-query` 5.90.20，直接导入 `keepPreviousData`。

验证结果：输入 `undefined` 返回 `undefined`；输入上一页对象时返回同一对象引用，输出 `PASS keepPreviousData identity contract`。这支持正文使用 `placeholderData: keepPreviousData` 的 API 名称与函数式语义。

范围不包括 React Provider、useQuery 观察者状态、请求、分页 UI 或浏览器渲染；这些仍须按正文练习在 React 工程中验收。
