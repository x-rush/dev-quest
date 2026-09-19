# 预取与 SSR 水合：何时取数、传递什么

先修：QueryClient、queryKey、服务器渲染。预取把请求提前；脱水提取可传递的缓存状态；水合把状态放入浏览器缓存。它们不会自动保证数据永不过期，也不会自动把任意 Promise 流式传给浏览器。

## API 的职责

| API | 适合用途 | 关键边界 |
|---|---|---|
| prefetchQuery | 提前准备可能访问的数据 | 返回 Promise<void>，查询失败通常不向调用方抛出 |
| fetchQuery | 必须获得符合新鲜度要求的数据 | 返回数据，失败抛出 |
| ensureQueryData | 确保缓存中有数据可用 | 已有数据默认直接返回，即使过期；revalidateIfStale 可安排后台刷新 |
| dehydrate | 提取缓存状态 | 默认包含成功查询；不是通用 JSON 序列化器 |
| hydrate / HydrationBoundary | 恢复缓存状态 | 不能替代 Provider 或服务端请求隔离 |

## 缓存传递实验：在练习环境中执行并验收

在已安装 @tanstack/react-query 的项目中，保存为 hydration-demo.mjs 并用 Node.js 执行。它演示缓存机制，不启动 React SSR 服务器。

验收要求：在自己的练习环境运行以下程序，记录 Node.js 与依赖版本，确认输出为“你好”。历史 Web 检查报告未逐用例绑定本页来源，因此本页当前没有命名的文件级运行证据；以下输出是学习者需要核对的预期结果，也不能证明 React SSR、Next.js 构建或实际浏览器水合已经通过。

```js
import { QueryClient, dehydrate, hydrate } from '@tanstack/react-query';

const server = new QueryClient();
await server.prefetchQuery({
  queryKey: ['greeting'],
  queryFn: async () => ({ text: '你好' }),
});
const payload = JSON.stringify(dehydrate(server));
const browser = new QueryClient();
hydrate(browser, JSON.parse(payload));
console.log(browser.getQueryData(['greeting']).text);
server.clear();
browser.clear();
// 预期：你好
```

这里数据只有普通对象与字符串，所以 JSON 往返可保留结构。Date、BigInt、自定义类型以及安全嵌入 HTML 的问题需由框架序列化层处理，不能把任意 JSON 字符串直接拼进 script 标签。

## 在真实应用中放置这些步骤

服务端为每次请求创建 client，预取页面需要的数据，过滤不应发送给浏览器的字段，再由框架传递脱水状态。浏览器复用稳定 client，在 QueryClientProvider 内使用 HydrationBoundary 包裹读取这些数据的组件。

Next.js App Router 通常在服务器组件预取；TanStack Router/Start 通常在路由与其 Query 集成中组织预取。不能把一个导出的 loader 函数当作两个框架都自动识别的统一文件约定。

两端必须使用相同键和兼容数据结构。水合后是否立即后台重取，取决于 dataUpdatedAt、staleTime 和触发条件；设置 staleTime 不能弥补两端键不同。

## 非阻塞预取与流式传输

`void client.prefetchQuery(...)` 只是“不等待这个 Promise”。紧接着调用默认 dehydrate 时，尚未成功的查询通常不会包含在结果中。要流式传输 pending 查询，需要支持该能力的框架集成、脱水选项和序列化流程；普通 JSON.stringify 不能完成它。

先实现 await 关键查询的版本，再按[官方高级 SSR 指南](https://tanstack.com/query/latest/docs/framework/react/guides/advanced-ssr)扩展。不要靠删除 await 就宣称首屏与慢数据自动流式水合。

## 练习与验收

运行上述实验，把浏览器查询键改为另一个值，预期 getQueryData 返回 undefined；再恢复键并验证。随后让预取函数抛错，检查默认脱水内容，解释为什么不存在成功数据。

在真实页面中记录服务器请求数和浏览器请求数，并设置合适 staleTime。验收不是“没有任何浏览器请求”，而是能解释每次请求的原因，并确认未把另一用户或无关页面的数据一起传出。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
