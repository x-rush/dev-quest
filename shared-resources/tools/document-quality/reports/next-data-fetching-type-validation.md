# Next 数据获取解析边界验证

**验证日期**：2026-09-20  
**正文来源**：`02-nextjs-frontend/basics/06-data-fetching-basics.md` 第 101–169 行。  
**范围**：`readJson`、`parsePosts`、`parseUsers`、单请求和并行请求的类型关系。

## 环境与命令

在 WSL 原生文件系统中，使用 Node `v24.7.0`、锁定的 `typescript@5.9.3` 与严格模式执行：

```bash
./node_modules/.bin/tsc --strict --noEmit --target ES2022 --lib ES2022,DOM /tmp/dev-quest-data-fetching.ts
```

结果：`PASS_DATA_FETCHING_TYPES`。

验证临时文件只额外声明了 Next.js 对 `RequestInit` 的 `next.revalidate` 扩展；该声明用于让独立 TypeScript 知道框架 API，未改变正文行为。

## 本次确认的教学契约

- 非 2xx 响应抛出 HTTP 错误，不能被伪装为空数组。
- 网络或 JSON 失败由调用方、`error.tsx` 或其他明确错误边界处理。
- JSON 先作为 `unknown` 读取，再验证文章和作者需要的字段；TypeScript 断言不作为运行时校验。
- 并行读取中的两个响应都检查 HTTP 状态与数据形状，作者缺失以 `null` 表达。

## 不覆盖的内容

这是一项正文片段的严格类型检查，不运行完整 Next.js 构建、真实网络请求、缓存、路由、`error.tsx` 或浏览器页面。
