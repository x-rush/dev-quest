# 新架构术语字典 — Fabric、TurboModules、JSI、Codegen 与 Hermes

> **难度**: ⭐⭐ | **前置**: 建议先了解通信模型概念（[08-bridge-principles](./08-bridge-principles.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#新架构` `#Fabric` `#TurboModules` `#JSI` `#Codegen` `#Hermes` |
| **更新日期** | `2026年9月` |

## 📌 定义

新架构不是"更快的 Bridge"，而是 JS 与原生通信模型的更换：**JSI 提供同步直调的地基，Fabric 重构渲染器，TurboModules 重构原生模块，Codegen 保证两端类型一致，Hermes 是运行其上的默认 JS 引擎**。自 RN 0.82 起新架构是唯一架构（旧架构不可再启用），本模块基线 RN 0.87 下全部默认生效，无需任何开关。

术语关系一览：

```
        JS 业务代码（Hermes 引擎执行字节码）
                  │
                JSI  ←— C++ 地基：同步直调、无序列化、引擎无关
               ╱   ╲
       TurboModules     Fabric
       （原生模块体系）   （渲染器）
             ↑
          Codegen（TS 规格文件 → 原生接口，编译期校验）
```

## 📖 术语详解

### JSI（JavaScript Interface）— 一切的地基

- **定义**：用 C++ 实现的轻量 JS 引擎抽象层。原生代码通过"宿主对象（HostObject）"直接持有并暴露 JS 对象，反之 JS 也能持有原生对象——调用是直调
- **与旧架构对比**：Bridge 时代 JS 与原生互发**序列化后的 JSON 批量消息**、异步排队、无法同步取值；JSI 直调无序列化、可同步返回
- **与其他术语的关系**：Fabric 与 TurboModules 都构建在 JSI 之上；Hermes 等引擎经 JSI 对接，引擎可插拔

### Fabric — 渲染器

- **定义**：新渲染器。布局计算统一收进 C++（Yoga），JS 组件树与原生 Shadow Tree 通过**不可变快照**对齐，渲染提交可被高优先级交互打断（React 并发特性因此可用）
- **与旧渲染器（Paper）对比**：Paper 由 Java/ObjC 各自实现布局、经桥异步提交、不可中断；Fabric 在 C++ 层统一布局与视图拍平（View Flattening），三端行为一致
- **与其他术语的关系**：Fabric 的同步提交依赖 JSI；`startTransition`/Suspense 等并发特性只有在新渲染器上生效

### TurboModules — 原生模块体系

- **定义**：新架构的原生模块模型。JS 首次访问时才实例化对应原生模块（**懒加载**），方法调用经 JSI 直调、支持同步返回值
- **与旧架构对比**：旧 NativeModules 启动时**全量注册**所有模块、经桥异步调用、一切返回值只能回调
- **与其他术语的关系**：接口由 Codegen 从 TS 规格生成（类型安全）；Expo Modules API 构建于 TurboModule 之上并自动化了这一步

### Codegen — 类型脚手架

- **定义**：构建期工具，从 TS 规格文件（spec）生成 Android（Java/Kotlin）、iOS（ObjC++）原生接口代码，两端不匹配在**编译期**报错而非运行期静默失败
- **与旧架构对比**：旧桥接手写两端代码，类型不匹配要到运行时才暴露
- **与其他术语的关系**：服务 TurboModule 与 Fabric 组件；日常用 Expo Modules API 时通常感知不到它的存在

### Hermes — 默认 JS 引擎

- **定义**：为 RN 优化的 JS 引擎，启动前预编译为**字节码（AOT）**，带来启动耗时与内存优势。RN 0.84 起默认为 V1 版本引擎（见模块 README 技术基线）
- **与旧架构对比**：早期版本默认 JavaScriptCore（JSC），引擎与通信模型强耦合在旧实现里
- **与其他术语的关系**：JSI 的引擎无关性使 Hermes 可插拔；调试统一走 React Native DevTools（Flipper 已移除）

### 新架构默认化 — 版本时间线

| 节点 | 事实 |
|------|------|
| RN 0.76 | 新架构默认开启（可关） |
| RN 0.82（Expo SDK 55+） | 新架构成为**唯一架构**，旧架构不再可启用 |
| RN 0.84–0.85 | Legacy 组件陆续移除 |
| RN 0.87（本模块基线） | 无开关可关；库选型必须看"新架构适配"声明 |

## 💡 示例

```tsx
// NativeCounter.ts —— TurboModule 规格文件（Codegen 的输入）
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  getDeviceName(): Promise<string>;        // 异步方法
  multiply(a: number, b: number): number;  // 同步返回值——JSI 直调才有的能力
}

export default TurboModuleRegistry.get<Spec>('Counter');
```

```tsx
// JS 侧消费：懒加载在此刻才触发原生模块实例化
import Counter from './NativeCounter';

const six = Counter.multiply(2, 3); // 同步拿到结果，无回调
```

日常业务优先用 Expo Modules API（构建于 TurboModule 之上，Codegen 自动化），手写规格文件主要面向库作者。

## ⚠️ 常见陷阱

- ❌ **把新架构理解成"更快的桥"**，继续写"等一帧再量尺寸"类补丁——渲染时序已变，hack 全部失效
  ✅ 按"JS 执行 + 渲染提交"归因性能问题（见 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md)）
- ❌ **引入库不看新架构适配声明**——旧架构注册通道已移除，未适配库直接不可用
  ✅ 优先 Expo SDK 与声明支持新架构的库；选型优先级见 [原生与设备能力库指南](../library-guides/02-native-and-device-libs.md)
- ❌ **在动画节点上混挂内置 Animated 与 Reanimated 两套驱动**
  ✅ 按 [动画与手势库](../library-guides/04-animation-gesture-libs.md) 的边界小节二选一
- ❌ **性能归因还找"桥延迟"**——桥已不存在，瓶颈集中在 JS 线程长任务与渲染提交
  ✅ 重活移 UI 线程（Reanimated worklet）或原生侧；延迟非紧急更新用 `startTransition`

## 🔗 相关条目

- 📄 **[新架构解析（解释篇）](../../advanced-topics/architecture/01-new-architecture.md)** — 深入"为什么"：JSI/Fabric/TurboModules 的机制剖析，本文的上游入口
- 📄 **[桥接与原生通信原理](./08-bridge-principles.md)** — 新旧两代通信模型的对照详解
- 📄 **[RNOH 字典](./05-harmonyos-rnoh-api.md)** — 新架构在鸿蒙第三端的落地形态与版本对齐
- 📄 **[TypeScript 类型模式](./04-typescript-patterns.md)** — Codegen 规格文件的 TS 写法
- 📄 **[框架进阶](../../frameworks/02-react-native-advanced.md)** — 新架构下"怎么用"的任务式指南

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
