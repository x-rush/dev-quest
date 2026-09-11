# 桥接与原生通信原理 — Bridge、JSI 与 TurboModules

> **难度**: ⭐⭐ | **前置**: 读过[原生模块桥接教程](../../basics/06-native-modules.md)更佳，非必需

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#JSI` `#Bridge` `#TurboModules` `#通信原理` |
| **更新日期** | `2026年9月` |

## 📌 定义

JS 与原生（Kotlin/Swift/ObjC/ArkTS）分属两个运行时，必须有一条通信通道。RN 历史上有两代模型，**本文按概念描述，不绑定具体版本号**：

- **Bridge（旧架构）**：异步消息队列。JS 与原生互发**序列化后的 JSON 批量消息**，双方互不知道对方存在，无法同步取值，原生模块启动时全量注册
- **JSI（新架构地基）**：用 C++ 实现的 JS 引擎抽象层。原生代码可以**直接持有 JS 对象引用**（宿主对象），反之 JS 也能持有原生对象——调用是直调，可同步、无序列化、引擎无关
- **TurboModules**：建立在 JSI 之上的原生模块体系——按需懒加载 + 从 TS 规约（Codegen）生成类型安全的接口

**一句话**：Bridge 是"寄信"（批量、异步、复制数据），JSI 是"打电话"（直连、可同步、共享引用）。

## 📖 语法/签名

```ts
// JS 侧访问原生模块的三种形态（由底层通道决定行为）
import { NativeModules } from 'react-native';            // 旧式全量注册访问（维护遗留代码用）
import { TurboModuleRegistry } from 'react-native';      // 按需懒加载 + Codegen 类型
import { requireNativeModule } from 'expo-modules-core'; // Expo Modules API（构建于 JSI 之上）

// TurboModule 规约：Codegen 依据此接口生成两端胶水代码
export interface Spec extends TurboModule {
  getDeviceName(): Promise<string>;        // 异步：Promise
  isFeatureEnabledSync(): boolean;         // 同步：JSI 直调（慎用）
}
export default TurboModuleRegistry.getEnforcing<Spec>('Device');
```

## 💡 示例

```tsx
// 同步 vs 异步的体感差异：同步方法可直接参与渲染计算
const spec = TurboModuleRegistry.getEnforcing<Spec>('Device');

// 异步（Promise）——默认形态，不阻塞 JS 线程
const name = await spec.getDeviceName();

// 同步（JSI 直调）——无桥延迟，但会阻塞 JS 线程直到返回
const enabled = spec.isFeatureEnabledSync();
```

## ⚠️ 常见陷阱

- **以为"桥没了 = JS 不再阻塞"**：JSI 消除的是序列化与队列，JS 线程仍是单线程；重活应移到原生线程或 UI 线程
- **滥用同步方法**：同步调用会卡住 JS 线程，只应用于轻量取值（如测量、开关位）；涉及 IO 一律异步
- **原生方法默认不在主线程**：更新 UI 需切回主线程（Android 主线程 Handler / iOS 主队列）
- **手写两端接口不对齐**：走 Codegen/Expo Modules 声明式路线，让类型从规约单向生成
- **把 JSI 当"更快的 Bridge"**：它是通信模型的更换（共享引用 vs 复制数据），不是同一模型的加速版

## 🔗 相关条目

- 📄 [原生模块桥接教程](../../basics/06-native-modules.md) — 手写模块的完整操作
- 📄 [新架构解析](../../advanced-topics/architecture/01-new-architecture.md) — Fabric/TurboModules 的架构级展开
- 📄 [RNOH 鸿蒙适配字典](./05-harmonyos-rnoh-api.md) — 第三端的等价通道（ArkTS TurboModule）
- 📄 [原生与设备能力库指南](../library-guides/02-native-and-device-libs.md) — "先找库再自研"的选型清单

*延伸: React Native 官方文档 "The New Architecture" 系列页*
