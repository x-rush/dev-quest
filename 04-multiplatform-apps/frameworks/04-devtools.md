# 开发工具链 — Expo Devtools、调试与性能工具

> **文档简介**: 配置一套高效的移动端调试环境：Expo 开发服务器与 Devtools、Flipper 退役后的替代方案（React Native DevTools）、网络检查、日志与性能剖析
>
> **目标读者**: 正在进行日常功能开发、需要快速定位 UI/网络/性能问题的开发者
>
> **前置知识**: 已完成 [第一个 App](../basics/02-first-app.md)，理解 Metro 与 dev client 的关系

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐ |
| **标签** | `#调试` `#DevTools` `#Flipper` `#性能分析` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 熟练使用 Expo 开发服务器与 dev client 的调试入口
- ✅ 用 React Native DevTools 完成 Elements/Console/Network/Profiler 全套检查
- ✅ 了解 Flipper 为何退役及功能对应替代
- ✅ 建立真机日志与崩溃的快速排查流程

## 🚀 Expo 开发环境

```bash
npx expo start              # 启动 Metro + Expo Devtools（默认按 i/a 自动装模拟器）
npx expo start --dev-client # 配合自定义 dev client 使用（装了三方原生库的标配）
npx expo start --clear      # Metro 缓存异常时的清缓存启动
```

**dev client 与 Expo Go 的分工**：Expo Go 只能加载 SDK 内置的纯 JS 模块；一旦安装了 MMKV 等自带原生代码的依赖，必须构建自己的 dev client（`npx expo run:ios` / `npx expo run:android`），之后 `--dev-client` 启动即可连真机。命令全集见 [CLI 速查表](../reference/quick-references/01-cli-and-debug-cheatsheet.md)。

## 🧰 React Native DevTools：Flipper 的官方替代

**Flipper 为什么退役**：Meta 已停止维护 Flipper，新架构（Fabric/TurboModules）下其插件体系不再兼容；RN 官方转向 **React Native DevTools**——基于 Chrome DevTools 协议的调试器，随 Hermes 引擎内建，无需额外安装。

| Flipper 旧能力 | 现在用什么 |
|----------------|-----------|
| Layout 检查器 | React Native DevTools → Elements 面板 |
| Network 插件 | DevTools → Network 面板（Hermes 内建） |
| Crash 日志 | `adb logcat` / Xcode 日志 + Sentry（见 [可观测性](../deployment/03-ota-updates-observability.md)） |
| Hermes Debugger | 同一个 DevTools（按 `j` 打开） |
| Redux 检查 | Reactotron 或 zustand devtools 中间件 |

```bash
# 调试入口（Metro 运行中）：
#   j  —— 打开 React Native DevTools（Debugger）
#   r  —— 重新加载 bundle
#   m  —— 切换开发菜单（真机上摇一摇等效）

# 真机日志
adb logcat -s ReactNativeJS           # Android：只看 JS console 输出
xcrun simctl spawn booted log stream  # iOS 模拟器系统日志
```

## 🔍 五大高频调试场景

```tsx
// 1. 渲染次数排查：为什么这个组件一直在重渲染？
//    DevTools → Profiler 面板录制交互，查看 commit 次数与耗时
//    常见元凶：父组件内联对象 props、未 memo 的回调

// 2. 网络调试：DevTools → Network 面板可直接看 fetch/XHR
//    注意：原生层请求（原生 SDK 发出的）不会出现在这里

// 3. 断点与 source map：DevTools Console 中直接打断点，
//    Hermes 自动上传 source map，TS 源码可读

// 4. 状态可视化：zustand 挂 devtools
import { devtools } from 'zustand/middleware';

export const useStore = create(
  devtools((set) => ({ count: 0 }), { name: 'AppStore' })
);

// 5. 元素定位：DevTools Elements 面板点选组件 → 高亮真实布局，
//    右侧可直接改样式验证（与浏览器 DevTools 操作一致）
```

## 📊 性能工具分层

| 层级 | 工具 | 用途 |
|------|------|------|
| JS 帧率 | DevTools → Profiler | 组件渲染耗时、重渲染定位 |
| UI 帧率 | 开发菜单 → Show Perf Monitor | 实时 FPS 叠加层 |
| 启动耗时 | `adb shell am start -W <包名>` | Android 冷启动 Time To Interactive 初测 |
| 原生剖析 | Android Studio Profiler / Xcode Instruments | CPU/内存/电量深查 |
| 线上性能 | Sentry Performance | 真实用户帧率与启动分布（见 [可观测性](../deployment/03-ota-updates-observability.md)） |

深挖原理见 [渲染性能](../advanced-topics/performance/01-rendering-performance.md) 与 [启动优化](../advanced-topics/performance/02-startup-optimization.md)。

## ✅ 最佳实践

- ✅ **团队统一 dev client**，把调试依赖（Reactotron、自定义菜单）打进客户端，避免"我机器上能跑"
- ✅ **崩溃先看 `adb logcat -s ReactNativeJS`**，再进 DevTools 复现，最后查 Sentry 聚合
- ✅ **Profiler 用"录制交互"而非盯实时曲线**，数据可复现可对比
- ❌ **不要在生产包里留 `console.log`**，用 babel 插件在构建时剥离
- ❌ **不要用 `debugger` 硬断点代替 DevTools 断点**，前者在 release 包会直接抛错

## ❓ 常见问题

**Q1: 按 j 打开 DevTools 无反应？**
A: 确认使用 Hermes 引擎（Expo 默认开启）；JSC 引擎不支持内建 DevTools。

**Q2: DevTools Network 面板看不到请求？**
A: 只能拦截 JS 层 fetch/XHR；原生 SDK 的请求用 Charles/mitmproxy 做代理抓包。

**Q3: 鸿蒙端怎么调试？**
A: RNOH 提供 DevEco Studio 联调与 hdc 日志，命令差异见 [CLI 速查表](../reference/quick-references/01-cli-and-debug-cheatsheet.md) 与 [RNOH 字典](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

---

## 🔗 相关文档

- 📖 [CLI 命令与调试速查表](../reference/quick-references/01-cli-and-debug-cheatsheet.md) — 本文所有命令的完整清单
- 📖 [故障排除 — 常见错误与解法](../reference/quick-references/02-troubleshooting.md) — 白屏/红屏/依赖冲突速查
- 📖 [Expo 要点](../reference/framework-essentials/01-expo-essentials.md) — dev client 与 Config Plugins 机制
- 📄 [第一个 App — 创建、Metro 与三端运行](../basics/02-first-app.md) — Metro 启动链路入门
- 🎓 [渲染性能](../advanced-topics/performance/01-rendering-performance.md) — Profiler 数据的优化方法论
- 🚀 [OTA 更新与可观测性](../deployment/03-ota-updates-observability.md) — 线上崩溃监控方案
