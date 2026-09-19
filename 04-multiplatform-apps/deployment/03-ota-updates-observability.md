# OTA 更新与可观测性 — EAS Update、Sentry 与崩溃治理

> **文档简介**: 上架之后的运营生命线：用 EAS Update 秒级推送 JS 修复，用 Sentry/Crashlytics 建立崩溃与性能监控体系，形成"发布 → 监控 → 热修"的运营闭环
>
> **目标读者**: 已完成首次上架、关注线上质量与快速响应的开发者
>
> **前置知识**: 已完成 [商店上架](./02-app-store-release.md)；了解 [EAS Build 构建流程](./01-eas-build.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（deployment） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#OTA` `#EASUpdate` `#Sentry` `#崩溃监控` `#可观测性` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 学习目标

- ✅ 集成 expo-updates 并理解 OTA 的能力边界
- ✅ 用 EAS Update 推送热修复，并掌握回滚手段
- ✅ 接入 Sentry 建立 JS + 原生双端崩溃监控
- ✅ 定义崩溃率/启动耗时等质量红线并建立告警

## 📡 OTA 更新原理与边界

**原理**：RN 应用 = 原生壳 + JS/资源包。`expo-updates` 在启动时检查服务器上是否有新 bundle，有则后台下载、下次启动生效——**不用经过商店审核**。

**能力边界（必须牢记）**：

| 变更类型 | 能否 OTA |
|----------|---------|
| JS 代码 / 组件逻辑 / 样式 | ✅ 可以 |
| 图片等静态资源 | ✅ 可以 |
| 新增/升级含原生代码的库 | ❌ 必须商店发版 |
| app.json 原生配置（权限/插件） | ❌ 必须商店发版 |
| RN 版本 / Hermes 配置 | ❌ 必须商店发版 |

## 🛠️ expo-updates 集成

```bash
npx expo install expo-updates
```

```json
// app.json —— EAS Update 会自动填充 url；runtimeVersion 是安全阀
{
  "expo": {
    "updates": {
      "fallbackToCacheTimeout": 0   // 启动不等更新，后台静默下载，下一启生效
    },
    "runtimeVersion": {
      "policy": "appVersion"        // 原生变了必须换 runtime，policy 自动隔离新旧 JS
    }
  }
}
```

**runtimeVersion 是安全阀**：JS 与原生必须匹配。`appVersion` 策略保证每个商店版本只接受为它编译的更新包，杜绝"新 JS 配旧原生"的崩溃。

```bash
# 推送热修
eas update --branch production -m "修复支付页空态崩溃"
# 按渠道灰度：先推 preview 分支验证，再推 production
```

```tsx
// 紧急热修的即时生效模式：仅修复场景使用，勿日常开启
import * as Updates from 'expo-updates';

useEffect(() => {
  Updates.checkForUpdateAsync().then((r) => {
    if (r.isAvailable) Updates.reloadAsync(); // 立即重载，牺牲一次启动时延
  });
}, []);
```

**回滚**：EAS 后台可把分支指向切回上一组发布（revert）；最坏情况引导用户等商店版。发布前用演练分支验证回滚流程。

## 📊 Sentry：崩溃与性能监控

```bash
npx expo install @sentry/react-native
```

```ts
// 入口文件最顶部 —— 尽早初始化
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN, // 通过 EAS env 注入
  tracesSampleRate: 0.2,                   // 性能采样 20%，按量调整
  enableNative: true,                      // 原生崩溃也归集到同一 issue
});
```

**三层监控面**：

| 层 | 数据源 | 看什么 |
|----|--------|--------|
| 崩溃 | Sentry Issues | 崩溃率、影响用户数、堆栈聚合（JS + Native 同屏） |
| 性能 | Sentry Performance | 冷启动耗时、慢请求、页面渲染时长 |
| 商店 | Play Vitals / Xcode Organizer | ANR 率、电量、第三方视角崩溃 |

**Crashlytics 与 Sentry 的取舍**：两者都需要验证原生符号文件、source map、隐私字段、告警路由和费用模型。已有 Firebase 或 Sentry 组织账号时，优先比较复用现有告警与访问控制的成本；新项目用一个最小发布包制造可控 JS 与原生错误，确认事件能正确归属到发布版本后再决定。配置插件可减少部分上传步骤，但不能替代产物级验证。

## 🚨 质量红线与告警

1. **崩溃率**：会话崩溃率 > 0.5% 触发告警（Sentry Alert → Slack/邮件）
2. **启动耗时**：P90 冷启动 > 3s 立项优化（方法论见 [启动优化](../advanced-topics/performance/02-startup-optimization.md)）
3. **OTA 健康度**：新 update 推送后 2h 内崩溃率不升才继续放量
4. **发布检查单**：每次发版后 72h 为重点观察期，值班人明确

## ✅ 最佳实践

OTA 能更新什么取决于新 JS/资源是否兼容已安装的原生运行时；加入新的原生模块通常需要新客户端。runtimeVersion 用来表达这个兼容边界，不只是一个随意填写的版本标签。

先向受控群体验证启动、关键操作和恢复路径，观察窗口按风险和用户量决定，不能固定等待 24 小时就算安全。记录更新 ID 与客户端构建的对应关系；应用重载前处理未保存输入，准备停止分发或发布修复更新的流程。

## ❓ 常见问题

**Q1: OTA 更新后用户多久生效？**
A: 默认下次启动生效（fallbackToCacheTimeout: 0）；即时模式用 `reloadAsync` 但体验代价大，慎用。

**Q2: Sentry 里 iOS 崩溃没有符号化？**
A: 确认 dSYM 上传任务在构建插件里启用（`@sentry/react-native` 的 config plugin 默认处理）；缺符号堆栈可在后台手动补传。

**Q3: 鸿蒙端崩溃监控怎么办？**
A: RNOH 接入 Sentry 需要社区适配层，成熟度低于双端；过渡期用华为 AppGallery Connect 的质量分析，细节见 [RNOH 字典](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

---

## 🔗 相关文档

- 📖 [Expo 要点 — Router、EAS 与 expo-modules](../reference/framework-essentials/01-expo-essentials.md) — EAS Update 机制速查
- 📖 [CLI 命令与调试速查表](../reference/quick-references/01-cli-and-debug-cheatsheet.md) — updates 相关命令
- 📄 [EAS Build 构建流程](./01-eas-build.md) — OTA 更新包的构建基础
- 📄 [商店上架](./02-app-store-release.md) — 与 OTA 互补的商店通道
- 🎓 [启动优化](../advanced-topics/performance/02-startup-optimization.md) — 启动红线指标的优化方法
- 🎓 [安全实践](../advanced-topics/security/01-security-practices.md) — OTA 通道的安全约束


<!-- acceptance-exercise -->
## 练习与验收：验证更新兼容与失败恢复

准备两个测试安装包，使用不同 runtimeVersion，在测试 channel 发布只匹配其中一个运行时的 JS 更新。预期兼容包按配置获取更新，不兼容包不会把无法运行的 bundle 当作有效更新。再让更新请求断网，旧版核心页面仍可打开。验收记录包版本、update ID、运行时和冷启动结果；修改原生依赖时重新构建，不能以 JS 更新替代原生二进制。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
