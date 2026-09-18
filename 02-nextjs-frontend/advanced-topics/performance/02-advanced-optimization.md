# 高级性能调优：资源生命周期、并发与缓存边界

先修：Effect 清理、Promise、组件渲染、HTTP 缓存。先完成[性能测试基线](../../testing/04-performance-testing.md)。本章讨论普通图片优化和代码分割之后仍存在的问题，不把复杂封装本身当作优化成果。

## 1. 内存增长什么时候才是泄漏

内存随数据量增长不一定是泄漏。泄漏的关键是：业务已不需要对象，但某条引用链仍让它无法释放。例如组件卸载后，window 事件监听器还引用组件闭包；重复进入页面又创建一套监听器。

比较相同操作前后的堆快照，重点查看多轮进入、退出后仍持续增长的对象及其保留路径。不要把浏览器总堆大小当成某一个 React 组件的内存占用，更不能根据一个任意阈值自动销毁仍在使用的对象。

```tsx
// app/components/viewport-width.tsx
'use client';

import { useEffect, useState } from 'react';

export function ViewportWidth() {
  const [width, setWidth] = useState<number | null>(null);

  useEffect(() => {
    const update = () => setWidth(window.innerWidth);
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);

  return <output>{width === null ? '测量中' : `${width}px`}</output>;
}
```

初始值不读取 window，因此可参与服务器预渲染。Effect 中创建监听、清理中移除同一个函数。开发模式的额外建立与清理可以暴露不对称代码；不要通过禁用检查掩盖问题。[Effect 生命周期](https://react.dev/reference/react/useEffect)

对定时器用 clearInterval，对 Observer 用 disconnect，对本次请求用 AbortController。资源应由创建它的作用域负责释放；不要在渲染阶段注册定时器或创建带副作用的资源。

## 2. 并行请求：减少瀑布，但保留依赖关系

```ts
// 通用 TypeScript 工具；T 的形状仍需调用方做运行时校验
async function readJson(url: string): Promise<unknown> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

export async function loadDashboard() {
  const [summary, alerts] = await Promise.all([
    readJson('https://example.com/api/summary'),
    readJson('https://example.com/api/alerts'),
  ]);
  return { summary, alerts };
}
```

example.com 是占位地址，运行前替换为自己的两个接口。本例表达两个请求相互独立，不能把示例当成有可用后端的完整应用。若 alerts 需要 summary 返回的账号 ID，就不能直接并行。

Promise.all 任何一项拒绝时整体拒绝，但不会自动取消其他请求。允许部分成功时可使用 allSettled 并分别显示失败状态。服务器组件的 Suspense 可以让独立区域分别显示结果；先 await 所有慢数据再创建边界，无法让这些已等待的工作提前流式展示。

## 3. 有界缓存：命中之外还要考虑什么

缓存设计至少回答：键包含哪些输入、结果允许旧多久、谁触发失效、最多占多少空间、多个实例是否共享。仅用一个永不清理的 Map 会把命中率问题变成内存问题。

```js
// cache-demo.mjs；Node.js 可直接运行的最小 LRU 演示
class LruCache {
  #items = new Map();
  constructor(capacity) {
    if (!Number.isInteger(capacity) || capacity < 1) {
      throw new RangeError('capacity must be a positive integer');
    }
    this.capacity = capacity;
  }
  get(key) {
    if (!this.#items.has(key)) return undefined;
    const value = this.#items.get(key);
    this.#items.delete(key);
    this.#items.set(key, value);
    return value;
  }
  set(key, value) {
    this.#items.delete(key);
    this.#items.set(key, value);
    if (this.#items.size > this.capacity) {
      this.#items.delete(this.#items.keys().next().value);
    }
  }
}

const cache = new LruCache(2);
cache.set('a', 1);
cache.set('b', 2);
cache.get('a');
cache.set('c', 3);
console.log(cache.get('b'), cache.get('a'), cache.get('c'));
// 预期：undefined 1 3
```

get 会把命中的键移到 Map 尾部，淘汰时删除最早的键。这里限制的是条目数量，不是字节数；没有 TTL、持久化、跨进程一致性，也没有区分“未命中”和“缓存值就是 undefined”。这是一段机制练习，不是替代 Next.js 缓存或 Redis 的生产库。

用户私有数据必须考虑账号与权限边界。公共缓存键遗漏用户身份可能串数据；键包含身份也不能替代每次操作的授权检查。写入后需要明确哪些页面和缓存数据应失效。

## 4. 列表、预取与批处理的取舍

| 方法 | 适用迹象 | 需要额外处理 |
|---|---|---|
| 分页 | 数据量大，用户通常只看少量记录 | 稳定排序、页间一致性、空页 |
| 虚拟列表 | 大量已加载记录导致 DOM 和渲染成本高 | 动态高度、焦点、键盘操作、滚动恢复 |
| 预取 | 下一步访问概率高且网络空闲 | 浪费流量、权限变化、缓存过期 |
| 请求批处理 | 大量小请求的固定开销明显 | 单项错误、顺序、取消、大小限制 |

不要根据缺乏兼容性保证的电池或网络 API 强制隐藏核心内容。可选能力需要特性检测与正常回退。批处理协议也必须由服务端实现；把多个请求拼成 multipart 并不会让任意服务器自动理解它们。

## 5. 练习、反馈与扩展

先运行 LRU 演示，再把容量改为 1，逐步预测每次 get 的值。随后给它增加 has 方法，解释为什么缓存 undefined 时仅靠 get 不够。验收包括重复写同键、访问改变淘汰顺序、非法容量三个用例。

在页面中挂载与卸载 ViewportWidth 十次，确认监听器不会随次数累积。再对两个独立请求比较串行与并行的瀑布图；两者都应在错误时显示明确反馈。

高级扩展可以研究 Worker、虚拟列表和分布式缓存，但先保留一份原始性能证据。选择方案时说明瓶颈、代价与验证方式，而不是罗列工具名。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
