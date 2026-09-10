# 新架构解析 — Fabric、TurboModules 与 JSI

> **文档简介**: 深入 React Native 新架构的三大支柱：JSI 如何取代 Bridge、Fabric 渲染器的 C++ 共享树、TurboModules 的懒加载机制，理解"为什么"才能写出正确的性能代码
>
> **目标读者**: 已有完整 RN 开发经验、希望理解底层机制与做技术决策的资深开发者
>
> **前置知识**: 已完成 [框架进阶](../../frameworks/02-react-native-advanced.md)；建议先读 [原生模块桥接](../../basics/06-native-modules.md) 建立感性认识

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 解释（advanced-topics） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#JSI` `#Fabric` `#TurboModules` `#架构` `#Hermes` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 画出新旧架构的通信模型并解释差异
- ✅ 解释 JSI "宿主对象"如何实现 JS 与原生的同步直调
- ✅ 理解 Fabric 双树（Shadow Tree）渲染机制
- ✅ 据此对第三方库选型、性能问题归因做出正确判断

## 🧩 全景：为什么要有新架构

旧架构（0.68 前）的核心瓶颈是 **JSON 消息桥**：

```
旧架构：JS ──(异步 JSON 序列化)──▶ Bridge 队列 ──▶ Native
         （跨语言全靠序列化，批量异步，无法同步取值）
```

三大痛点：序列化开销（大列表布局抖动）、异步独占（`measure` 必须回调）、模块全量注册（启动时把 200 个原生模块全初始化）。新架构用三个组件逐一解决：

```
新架构：JS(Hermes) ⇄ JSI 直调 ⇄ C++ 层 ⇄ { TurboModules | Fabric }
         （类型安全、可同步、按需初始化）
```

## 🔌 JSI：一切的地基

**JSI（JavaScript Interface）** 是用 C++ 写的轻量 JS 引擎抽象层，让原生代码能"看见并持有" JS 对象，反之亦然。

```cpp
// 概念示意（非完整代码）：宿主对象 = 原生侧暴露给 JS 的对象
class NativeMath : public jsi::HostObject {
  jsi::Value get(jsi::Runtime& rt, const jsi::PropNameID& name) override {
    if (name.utf8(rt) == "sqrt") {
      // 返回一个可直接被 JS 调用的函数 —— 无序列化、无队列
      return jsi::Function::createFromHostFunction(
        rt, name, 1,
        [](jsi::Runtime& rt, const jsi::Value&, const jsi::Value* args, size_t) {
          return jsi::Value(std::sqrt(args[0].asNumber())); // 同步返回！
        });
    }
    return jsi::Value::undefined();
  }
};
```

**JSI 的三重意义**：
1. **引擎无关**：Hermes/JSC/V8 皆可对接（Hermes 默认引擎，AOT 字节码带来启动与内存优势）
2. **同步调用成为可能**：测量、手势、布局读取不再需要"回调地狱"
3. **类型安全**：C++ 层强类型直调，序列化错误类 bug 从根上消失

**鸿蒙侧注**：RNOH 在新架构下同样基于 JSI 模型对接 ArkTS 侧，实现细节与版本对齐见 [RNOH 字典](../../reference/language-concepts/05-harmonyos-rnoh-api.md)。

## 🎨 Fabric：渲染器重构

**核心思想**：布局计算（C++）与绘制（各平台）解耦，JS 树与原生 Shadow Tree 通过不可变快照对齐。

```
JS 组件树            C++ Shadow Tree            平台视图树
   │  (Yoga 同步计算布局)   │                        │
   ├─▶ commit A ──────────▶ 快照 A ───────────────▶ 挂载 A
   ├─▶ commit B（JS 中断）   快照 B ───────────────▶ 挂载 B
   └─▶ commit C ──────────▶ 快照 C ───────────────▶ 挂载 C
```

**与旧渲染器（Paper）的关键差异**：

| 维度 | Paper（旧） | Fabric（新） |
|------|------------|-------------|
| 布局计算 | Java/ObjC 各自实现 | 统一 C++ + Yoga，三端一致 |
| 通信 | 异步批量经桥 | 同步直调 + 优先级提交 |
| 可中断 | 不支持 | 支持（React 并发特性可用） |
| 视图拍平 | 平台各自实现 | C++ 统一 View Flattening |

**开发侧收益**：`startTransition`/Suspense 生效、渲染提交可被高优交互打断；代价是渲染时序更敏感——"等一帧"类 hack 全部失效，这也解释了 [渲染性能](../performance/01-rendering-performance.md) 中的优化手法。

## 📦 TurboModules：按需原生

**旧 NativeModules**：启动时全量注册 + 桥上异步调用。**TurboModule** 的三个变化：

1. **懒加载**：JS 首次 `requireNativeModule` 时才实例化原生模块（200 个模块中只用 5 个 → 启动只付 5 个的钱）
2. **Codegen 类型安全**：从 TS 规格文件生成原生接口，编译期校验两端一致
3. **JSI 直调**：方法调用不再排队，支持同步返回值

对开发流程的影响已在 [框架进阶](../../frameworks/02-react-native-advanced.md) 展开：优先 Expo Modules API（它构建于 TurboModule 之上并自动化了 Codegen），手写规格文件留给库作者。

## 🗺️ 迁移与决策要点

- **RN 0.76+ 默认启用新架构**，旧架构已进入移除通道——新项目无需决策，存量项目规划好适配窗口
- **库选型看适配状态**：`RCTBridge` 时代 API 的库不再维护即弃用；优先 Expo SDK 与声明支持新架构的库
- **性能归因升级**：桥延迟类问题消失后，瓶颈集中在 JS 执行与渲染提交，分析工具见 [渲染性能](../performance/01-rendering-performance.md)
- **启动收益立现**：TurboModules 懒加载 + Hermes 字节码是启动优化两大杠杆（详见 [启动优化](../performance/02-startup-optimization.md)）

## ✅ 要点回顾

- ✅ **JSI 是地基**，同步/类型安全/引擎无关三性质派生出其余一切
- ✅ **Fabric 把布局收进 C++**，三端一致 + 可中断渲染，React 并发特性因此可用
- ✅ **TurboModules 把启动成本改为按需付费**，第三方库未适配即技术债
- ❌ **不要再写"等一帧/桥延迟"时代的补丁代码**，假设已失效
- ❌ **不要把新架构理解成"更快的桥"**，它是通信模型的更换，不是量变

## ❓ 常见问题

**Q1: 新架构下 JS 与原生完全同步了吗？**
A: 调用通道同步了，但 JS 线程仍是单线程；长任务阻塞照旧，重活移 UI 线程（Reanimated）或原生。

**Q2: 混用旧架构库会怎样？**
A: 新架构提供兼容层（interop layer），多数旧库可用但有性能与稳定性折损；核心链路库必须适配。

**Q3: 如何验证应用真的跑在新架构？**
A: `npx react-native config` 检查 `newArchEnabled`；运行时看 LogBox 提示与库的 Fabric 分支加载日志。

---

## 🔗 相关文档

- 📖 [RNOH 字典 — 鸿蒙适配](../../reference/language-concepts/05-harmonyos-rnoh-api.md) — 新架构在第三端的落地形态
- 📖 [TypeScript 类型模式](../../reference/language-concepts/04-typescript-patterns.md) — Codegen 规格文件的 TS 写法
- 📄 [框架进阶 — 新架构、原生模块与动画](../../frameworks/02-react-native-advanced.md) — 本文的"怎么用"篇
- 📄 [原生模块桥接](../../basics/06-native-modules.md) — 手写模块的感性入口
- 🎓 [渲染性能](../performance/01-rendering-performance.md) — Fabric 渲染管线上的优化实践
- 🎓 [启动优化](../performance/02-startup-optimization.md) — TurboModules/Hermes 的启动红利兑现
