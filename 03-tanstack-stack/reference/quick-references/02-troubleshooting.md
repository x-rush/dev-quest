# 故障排除：常见错误与排查路径

## 概述

收录 TanStack 五库的高频故障：症状 → 原因 → 解决。遇到"明明照文档写的却不工作"时先查此表，再回到对应核心 API 字典。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#排查` `#无限重渲染` `#缓存键` `#水合不匹配` |
| **更新日期** | `2026年9月` |

---

## 1. useQuery 无限重新请求

### 症状

Network 面板请求循环发出；Devtools 中该查询反复进入 fetching。

### 原因与解决

| 原因 | 判断方式 | 解决 |
|------|---------|------|
| key 含不稳定引用（内联对象/数组/new Date()） | key 每次渲染都变 | 把变量提为 useMemo/组件外常量再进 key |
| queryFn 每次返回新对象且 select 再造引用 | Devtools 数据一直"更新" | 派生逻辑用 useMemo 包住或移出 select |
| 手动在渲染期调用 setQueryData/refetch | 渲染函数里出现副作用调用 | 移入事件回调或 useEffect |

```tsx
// ❌ 内联对象每次渲染都是新 key
useQuery({ queryKey: ['todos', { page, sort }], queryFn })

// ✅ 稳定化后再用
const filters = useMemo(() => ({ page, sort }), [page, sort])
useQuery({ queryKey: ['todos', filters], queryFn })
```

## 2. 缓存键错配：失效不生效 / 读到旧数据

### 症状

mutation 成功后 `invalidateQueries` 跑了，但列表没刷新；或 Devtools 出现两条相似 key。

### 原因与解决

- **类型不一致**：写入时 `id` 是 number，失效时传了 string——`['todo', 3]` 与 `['todo', '3']` 是两条缓存。统一经键工厂产出
- **作用域写错**：想失效 `['todos', 'list', {...}]` 却只失效了 `['todos', 'detail', 3]`——用前缀 `['todos']` 兜底再收窄
- **refetchType 误用**：目标查询未挂载时默认不重取（`'active'`），需要立即取用 `refetchType: 'all'`

## 3. SSR 水合不匹配（Hydration mismatch）

### 症状

Next.js/Start 控制台报 hydration mismatch；首屏内容闪变。

### 原因与解决

- **QueryClient 单例跨请求**：A 请求的缓存渲染进 B 的 HTML。解决：`useState(() => new QueryClient())` 或每请求工厂
- **服务端/客户端渲染内容依赖时间或随机数**：如 `dataUpdatedAt` 格式化、`Math.random`。解决：这些片段用客户端标志延迟渲染
- **服务端 prefetch 的 key 与客户端不一致**：水合后立刻重新请求且内容跳变。解决：两端共用键工厂

```tsx
// 标准模式
function Layout() {
  const [queryClient] = useState(() => new QueryClient()) // 每组件树一份
  return <QueryClientProvider client={queryClient}>…</QueryClientProvider>
}
```

## 4. Table 渲染空白

### 症状

`<table>` 出现但无行/无表头；或控制台 "Maximum update depth exceeded"。

### 原因与解决

- 忘传 `getCoreRowModel: getCoreRowModel()`——行模型必须显式接通
- `data` 初始为 `undefined` 直接传入——用 `data ?? []`，并在加载态分支提前 return
- 表头渲染了 `header.isPlaceholder === true` 的占位（分组表头）——按 `flexRender` 前置判空
- `columns`/`data` 在组件体内每次渲染重建新引用 → 行模型重算死循环——提为模块常量或 `useMemo`

## 5. Router 类型报错 / 运行时 404

### 症状

`<Link to>` 报"不存在该路径"；新路由文件不生效。

### 原因与解决

- `routeTree.gen.ts` 未重新生成：保存路由文件触发插件，或重启 dev server
- 文件命名错误：`posts.$postId.tsx` 写成了 `posts.postId.tsx`（`$` 是参数前缀）
- 忘记 `declare module` 全局注册 router 类型，Link 退化宽泛类型
- params 传了 number：Router 要求 string，`String(id)` 转换

## 6. Form 校验不触发

### 症状

输入错误值没提示；提交时也没拦截。

### 原因与解决

- 校验器挂在 `onBlur` 但用户没失焦就点了提交——补 `onSubmit` 校验兜底
- 函数校验器返回了 `null` 而不是 `undefined`——返回 `undefined` 才表示通过
- Standard Schema 的错误对象渲染成 `[object Object]`——取 `errors[i].message`
- 字段 `name` 与 `defaultValues` 键名不一致导致错误挂不上

## 7. mutation 后列表不更新

### 症状

写接口成功，界面还是旧数据。

### 原因与解决

- `onSuccess` 里忘了 `invalidateQueries`——Query 不自动感知写操作
- 失效的 key 与读查询的 key 不同源——全部经键工厂
- 乐观更新 `onMutate` 忘了 `await cancelQueries`——进行中的旧请求完成后覆盖了你的预测值

## 8. gcTime 相关闪现

### 症状

切页回来数据闪一下"加载中"；或数据永远陈旧。

### 原因与解决

- `gcTime: 0`（或全局误设）导致卸载即清缓存——保留默认 5 分钟或显式设大
- `staleTime: 0` + `refetchOnWindowFocus` 三连击导致切窗口必请求——按业务设 staleTime
- 想切页即秒开又要新数据：`staleTime` 大一点 + `placeholderData: keepPreviousData`

## 9. Devtools 看不到查询

### 症状

面板空白或缺条目。

### 原因与解决

- `<ReactQueryDevtools />` 放在了 Provider 外——移进 `QueryClientProvider` 内
- 查询在 Provider 树外调用（多 QueryClient 项目）——确认 `useQuery` 组件在正确 Provider 下
- 生产构建不含 Devtools——属正常行为

## 相关文档

- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - 状态与缓存语义
- 📄 **[缓存键、staleTime 与失效策略](../framework-essentials/01-query-essentials.md)** - 键与失效规则
- 📄 **[Table 核心 API](../language-concepts/02-table-core-api.md)** - 行模型与状态
- 📄 **[Router 核心 API](../language-concepts/03-router-core-api.md)** - 路由树与类型注册
