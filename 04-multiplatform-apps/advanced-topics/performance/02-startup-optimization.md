# 启动优化 — 冷启动与首屏时间

> **文档简介**: 拆解 RN 应用的启动链路：从进程创建到用户可交互的每个阶段、对应瓶颈与优化手段，建立明确的启动指标，再根据目标设备和业务制定预算
>
> **目标读者**: 已完成功能开发、需要把启动体验做到生产级水准的开发者
>
> **前置知识**: 已读 [新架构解析](../architecture/01-new-architecture.md)；了解 [EAS Build](../../deployment/01-eas-build.md)（release 包产出）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 解释（advanced-topics） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#启动` `#Hermes` `#懒加载` `#TTI` `#性能` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 学习目标

- ✅ 画出启动时间线并定位自己应用的瓶颈段
- ✅ 兑现新架构红利：Hermes 字节码 + TurboModules 懒加载
- ✅ 用懒加载/延迟初始化压缩首屏 JS 成本
- ✅ 建立冷启动的本地测量与线上监控

## ⏱️ 启动时间线

```
[进程创建/原生初始化] ─▶ [JS 引擎启动] ─▶ [Bundle 加载执行] ─▶ [首屏渲染] ─▶ [可交互 TTI]
      需实测               需实测        需实测         ★           ★
```

**度量定义**：`TTI`（Time To Interactive）= 从点击图标到首屏可流畅响应用户输入。Android 快速测量：

```bash
adb shell am start -W com.example.app/.MainActivity
# 输出 TotalTime 即启动耗时初值；精确度量用 Sentry 或分段打点
```

## ⚙️ 阶段一：引擎与包体（收益最大）

### Hermes 字节码（Expo 默认开启）

Hermes 把 TS/JS **AOT 编译为字节码**随包分发：省去运行时解析 JS 文本、按需编译、内存占用更低。确认三件事：

1. `app.json` 未关闭 `jsEngine`（默认即 hermes）
2. 生产构建产物是 `.hbc` 字节码（构建日志可查），而非运行时解析
3. 内联 require 开启，模块按执行路径惰性求值

### TurboModules 懒加载

新架构下原生模块按需初始化（原理见 [架构解析](../architecture/01-new-architecture.md)）。工程侧要求：**不要在启动路径 import 从不立即使用的原生库**——`requireNativeModule` 的调用点即成本发生点。

## 📦 阶段二：压缩首屏 JS 成本

### 拆分首屏与懒加载

```tsx
// 反面教材：根布局同步 import 全部页面 → 首启就执行全 app 代码
import Home from '@/features/home';
import Admin from '@/features/admin';      // 用户 99% 不进后台，却先付了钱
import Charts from '@/features/charts';    // 图表库巨大

// 可选策略：延迟重组件求值；不要假设所有原生生产构建自动按路由拆包
import { lazy, Suspense } from 'react';
const Charts = lazy(() => import('@/features/charts'));

function Dashboard() {
  return (
    <Suspense fallback={<Spinner />}>
      <Charts />
    </Suspense>
  );
}
```

### 启动路径瘦身清单

| 动作 | 说明 |
|------|------|
| 依赖审计 | `npx expo-doctor` + 包体积分析，移除"全家桶"式依赖 |
| SDK 按需初始化 | 推送/统计/支付 SDK 延到首次使用场景，而非根布局 |
| Provider 精简 | QueryClient/主题/鉴权够用即可，勿堆 10 层 Provider |
| Splash 期预热 | `fallbackToCacheTimeout: 0` + 后台下载下一启生效的 OTA（见 [OTA](../../deployment/03-ota-updates-observability.md)） |
| 字体/图片延迟 | 非首屏资源延迟加载，首屏图片用 `expo-image` 占位渐显 |

```tsx
// 延迟初始化样板：把重 SDK 挪出启动路径
// （InteractionManager 已从 RN 0.87 核心移除，改用 requestIdleCallback）
import { useEffect } from 'react';

useEffect(() => {
  // 首屏空闲期再初始化非关键 SDK
  const id = requestIdleCallback(() => {
    initAnalytics();
    initPush();
  });
  return () => cancelIdleCallback(id);
}, []);
```

## 🖼️ 阶段三：首屏渲染提速

1. **骨架屏替代转圈**：布局占位（骨架组件 + FlashList 渲染，见 [列表性能模型](../../reference/language-concepts/12-list-performance-model.md)）比 spinner 感知更快
2. **首屏数据缓存优先**：TanStack Query 的 `staleTime`/持久化缓存让二次启动秒开（用法见 [天气应用](../../projects/02-weather-app.md)）
3. **首屏图片**：固定宽高防抖动 + 本地占位图；远程头图预加载
4. **避免首帧同步重计算**：列表初始渲染条数 `initialNumToRender` 压到 6-10

## 📊 建立度量闭环

| 阶段 | 工具 | 手段 |
|------|------|------|
| 开发期 | `adb shell am start -W` / Xcode Metrics | 每次优化前后记录基线 |
| 提交前 | release 包真机手测 | dev 包数据不可信（JS 执行慢数倍） |
| 线上 | Sentry Performance / Play Vitals | P50/P90 冷启动分布与版本对比 |

**练习预算示例**：可暂设目标设备的 P90 业务可用时间小于 2s，但它不是行业统一红线。先收集足够样本，再按耗时占比分配工作。

## ✅ 要点回顾

- ✅ **Hermes + TurboModules 是地基红利**，确认开启是第 0 步
- ✅ **首屏只付首屏的钱**：懒加载路由与重 SDK，启动路径零额外负担
- ✅ **二次启动秒开靠缓存**，首启骨架屏撑感知
- ❌ **不要在根布局同步 import 一切**，顶层求值的昂贵依赖可能进入关键路径，需检查构建和执行结果
- ❌ **不要用 dev 包做启动决策**，release 包 + 真机才有意义

## ❓ 常见问题

**Q1: 白屏时间过长怎么归因？**
A: 分段打点：原生 onCreate → JS bundle 执行完 → 首帧 commit，各自埋点对表；白屏长多在 bundle 执行段（回到阶段二）。首帧类异常见 [故障排除](../../reference/quick-references/02-troubleshooting.md)。

**Q2: `fallbackToCacheTimeout` 设大一点"等最新版"行吗？**
A: 这是新鲜度与启动等待的权衡；较长等待可能拖慢弱网启动。一般先以可用缓存启动，再按产品需求检查更新，并验证离线兜底。

**Q3: 鸿蒙端启动有专项差异吗？**
A: RNOH 的启动链路多一段 ArkTS 容器初始化，版本对齐影响显著，见 [RNOH 字典](../../reference/language-concepts/05-harmonyos-rnoh-api.md)。

---

<!-- full-library-explanation -->
## 区分首次显示与真正可用

首帧出现可能只是一张启动图。对待办应用，可把“列表和新增按钮可操作”作为可用点；对离线地图，可把“本地地图可拖动”作为可用点。指标定义必须写下来，否则减少启动图显示时间也可能只是把等待转移到白屏。

冷启动、后台恢复、安装后首次启动分别测量。Android `am start -W` 的结果用于活动启动观察，不是业务 TTI；已有进程未停止时也不能声称测到了冷启动。不得在生产用户设备上为测量清空数据。

练习：在同一测试机上各做五次冷启动与恢复，记录原生启动、JS 执行、首屏显示、业务可用四个点。先延后一个非必要 SDK，再重复。反馈：若首屏更快但首次点击支付卡顿，需要把成本转移也写入结论；若断网时永久停在 Splash，要先修失败路径。

`React.lazy` 延迟组件加载/求值与生产原生包是否真正拆分成多个可下载文件是不同问题。应查看 Metro/Expo 对目标平台和构建方式的支持，并检查产物，不能套用 Web 路由拆包经验。

## 🔗 相关文档

- 📖 [RN 核心 API 字典](../../reference/language-concepts/01-rn-core-api.md) — AppState 等启动相关 API
- 📖 [状态与数据请求库指南](../../reference/library-guides/01-state-and-data.md) — 启动缓存策略的实现
- 📄 [框架进阶](../../frameworks/02-react-native-advanced.md) — 新架构开发约束篇
- 📄 [天气应用实战](../../projects/02-weather-app.md) — staleTime 缓存秒开示例
- 🎓 [渲染性能](./01-rendering-performance.md) — 首屏渲染深水区
- 🎓 [新架构解析](../architecture/01-new-architecture.md) — 启动优化的原理底座


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
