# Core Web Vitals：从症状定位到优化验证

先修：能区分服务器响应、资源下载、JavaScript 执行和浏览器绘制。先读[性能测试](../../testing/04-performance-testing.md)建立基线，再用本章解释测量结果。本章不预设所有页面都应使用同一种优化。

## 1. 三个指标对应三类体验

| 指标 | 用户感受 | 优先调查的证据 |
|---|---|---|
| LCP，最大内容绘制 | 主要内容何时显示 | LCP 元素、请求瀑布、服务器响应、渲染阻塞 |
| INP，交互到下一次绘制 | 点击或输入后多久看到反馈 | 输入排队、事件处理、后续渲染 |
| CLS，累积布局偏移 | 页面是否突然跳动 | 偏移区域、加载前后的布局、占位空间 |

FID 已退出当前核心指标集合。FCP、TTFB、TBT 可以辅助诊断，但不能与三个核心指标混成一套自创 SEO 权重。没有公开依据支持“LCP 占 SEO 40%”这样的断言。现行阈值与 p75 评估方法见 [Web Vitals 官方说明](https://web.dev/articles/vitals)。

## 2. LCP：先找到实际的大元素

在 DevTools Performance 中记录页面加载，查看 LCP 对应的元素。它可能是图片，也可能是大段文字；不能看到首页就默认优化 banner。

如果是图片，沿请求瀑布向前追问：HTML 来得晚吗？图片地址是否要等客户端脚本运行才出现？资源是否过大？资源已下载但元素仍被动画或样式隐藏吗？同一个 LCP 数字可能有不同原因。

```tsx
// app/page.tsx；先在 public 中放入真实的 hero.jpg
import Image from 'next/image';

export default function Page() {
  return (
    <main>
      <h1>旅行相册</h1>
      <Image
        src="/hero.jpg"
        alt="山间湖泊与远处的群山"
        width={1200}
        height={800}
        sizes="(max-width: 768px) 100vw, 800px"
        style={{ width: '100%', maxWidth: 800, height: 'auto' }}
        preload
      />
    </main>
  );
}
```

这张图假设已确认是首屏主要图片。width/height 提供固有比例，CSS 决定显示大小，sizes 告诉浏览器布局预计占用的宽度。检查 Network 中实际下载的候选图，不能只看 JSX 的 width。

Next.js 16 用 preload 表达预加载意图，priority 已弃用。不要把每张图都预加载；也不要把 preload、loading、fetchPriority 混在同一个示例里当作越多越好。具体组合约束见 [Image 属性](https://nextjs.org/docs/app/api-reference/components/image)。

## 3. INP：拆开一次交互的耗时

一次点击可能先等待前一个长任务结束，再运行处理函数，最后等待样式、布局和绘制。因此只给处理函数加 console.time 并不能覆盖完整交互响应。

常见处理方向：先减少重复计算，再缩小更新范围；重计算可考虑 Worker；大量 DOM 可考虑分页或虚拟列表。延后非必要工作时，需要确认延后后仍能及时完成，不能仅把卡顿移到下一次点击。

React 的 transition 可以让某些渲染更新以较低优先级处理，但不把同步 JavaScript 运算自动搬到后台。以下示意仍会阻塞：

```tsx
// 反例：expensiveCompute 是现有的同步重计算函数
startTransition(() => {
  const result = expensiveCompute();
  setResult(result);
});
```

`startTransition` 回调会立即调用。需要先定位 expensiveCompute 的成本，再选择算法、缓存、分块或 Worker。[React transition 限制](https://react.dev/reference/react/useTransition)

## 4. CLS：空间必须在内容到达前存在

```css
/* 广告、异步卡片等区域先保留合理空间 */
.recommendation-slot { min-height: 12rem; }
.cover { aspect-ratio: 3 / 2; width: 100%; object-fit: cover; }
```

min-height 并不保证零偏移：实际内容超过它时仍会扩展。预留过大空间也会损害布局。应根据真实内容尺寸设计骨架，并对窄屏、长标题和字体回退检查。

字体切换也可能改变文字宽度和换行。next/font 能帮助自托管和调整回退字体，但不能承诺彻底消除所有布局偏移。先限制不必要的字重与字符集，确认实际需要的中文字符未被错误排除。

## 5. 一个完整的诊断练习

建立只有标题、首屏图片、异步推荐列表的页面。第一轮保留图片尺寸，第二轮故意去掉原生 img 的尺寸，第三轮恢复尺寸；使用相同网络限速录制每轮。这里故意制造问题仅用于本地学习。

记录三件事：哪个元素移动、何时移动、是什么资源到达触发了移动。然后给列表输入框加入本地筛选，在不同数据量下录制输入过程。把“加载慢”和“交互慢”的证据分开，不用一个总分代替原因。

验收：提交修改前后的录制与指标、固定实验条件、指出具体瓶颈。若指标没有稳定改善，写出尚未验证的假设。不得填写未实际采集的结果。

自测：预加载所有图片能保证 LCP 更好吗？不能，会争抢资源。transition 能让一个同步循环并行执行吗？不能。CLS 为零能证明页面响应快吗？不能，它只反映布局稳定性。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
