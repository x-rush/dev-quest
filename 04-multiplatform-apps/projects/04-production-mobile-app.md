# 实战项目四 — 生产级移动应用（精通）

> **文档简介**: 把一个功能原型升级为可运营的生产级应用：分层架构、离线优先、错误边界、发布流水线与线上监控全链路，覆盖移动工程化的完整清单
>
> **目标读者**: 完成前三个项目、准备主导真实产品交付的高级开发者
>
> **前置知识**: 已完成 [聊天应用](./03-chat-app.md)；已了解 [EAS Build](../deployment/01-eas-build.md) 与 [测试工程](../testing/01-unit-testing.md) 概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（projects） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#生产级` `#架构` `#离线优先` `#监控` `#发布` |
| **更新日期** | 2026年9月 |

## 🎯 项目目标

- ✅ 建立按特性划分、依赖单向流动的工程结构
- ✅ 实现离线优先的数据层（本地为真相，网络为同步器）
- ✅ 建立错误边界 + 全局异常上报的兜底体系
- ✅ 打通"提交 → 测试 → 构建 → 灰度 → 监控"的发布闭环

## 🏗️ 工程结构：按特性划分

```text
src/
├── app/                    # 路由入口（Expo Router），只做装配
├── features/               # 业务特性，横向切分
│   ├── auth/               #   认证：screens/ components/ api/ store/
│   └── orders/             #   订单：同构四件套
├── shared/                 # 跨特性共享（ui/ hooks/ utils/）
├── services/               # 基础设施：api client、storage、analytics
└── types/                  # 全局类型
```

**依赖规则**：`app → features → shared → services`，单向流动；feature 之间禁止直接 import，需要共享的沉到 `shared/`。类型组织方式见 [TypeScript 类型模式](../reference/language-concepts/04-typescript-patterns.md)。

## 💾 离线优先数据层

生产级 App 的第一原则：**无网可用、有网同步**。

```ts
// services/api/client.ts —— 统一 API 客户端：超时/重试/错误归一化
const TIMEOUT_MS = 10_000;

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(path, {
      ...init,
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    });
    if (!res.ok) throw new ApiError(res.status, await res.text());
    return res.json() as Promise<T>;
  } finally {
    clearTimeout(timer);
  }
}
```

```ts
// services/api/outbox.ts —— 写操作离线队列：失败入队，恢复网络后重放
import { MMKV } from 'react-native-mmkv';
const outbox = new MMKV({ id: 'outbox' });

export function enqueue(method: string, path: string, body: unknown) {
  const list = JSON.parse(outbox.getString('ops') ?? '[]');
  list.push({ method, path, body, queuedAt: Date.now() }); // queuedAt 毫秒时间戳
  outbox.set('ops', JSON.stringify(list));
}

export async function flushOutbox() {
  const list = JSON.parse(outbox.getString('ops') ?? '[]');
  for (const op of list) {           // 顺序重放，保证写序
    await apiFetch(op.path, { method: op.method, body: JSON.stringify(op.body) });
  }
  outbox.delete('ops');
}
// 在 NetInfo 的 isConnected 回调中触发 flushOutbox（库选择见 reference/library-guides/02）
```

## 🛡️ 错误兜底体系

```tsx
// app/_layout.tsx —— 路由级错误边界 + 全局崩溃上报
import { Stack } from 'expo-router';
import { ErrorBoundary } from 'expo-router';          // 页面崩溃时显示恢复 UI 而非白屏
import * as Sentry from '@sentry/react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Sentry 包裹根组件：同时捕获 JS 崩溃与原生崩溃（初始化细节见 deployment/03）
export default Sentry.wrap(function RootLayout() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={new QueryClient({
        defaultOptions: { queries: { retry: 2 } },
      })}>
        <SafeAreaProvider>
          <Stack />
        </SafeAreaProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
});
```

**未捕获异常与 Promise 拒绝**由 Sentry 全局 handler 托管；本地开发另接 `LogBox.ignoreLogs` 白名单，避免噪音淹没真问题。

## 🚀 发布闭环清单

| 阶段 | 动作 | 工具与文档 |
|------|------|-----------|
| 提交前 | lint + 单测 + 组件测试全绿 | [单元测试](../testing/01-unit-testing.md)、[组件测试](../testing/02-component-testing.md) |
| CI | EAS Build 出 preview 包，Maestro 冒烟 | [E2E 测试](../testing/03-e2e-testing.md) |
| 构建 | production profile 构建 + 凭据托管 | [EAS Build 构建流程](../deployment/01-eas-build.md) |
| 上架 | TestFlight / 内部测试轨道灰度 | [商店上架](../deployment/02-app-store-release.md) |
| 热修 | OTA 推 JS 修复，原生问题走版本 | [OTA 与可观测性](../deployment/03-ota-updates-observability.md) |
| 运营 | 崩溃率 / 启动耗时 / ANR 看板 | Sentry + Play Vitals |

## ✅ 最佳实践

- ✅ **环境变量分级**：`EXPO_PUBLIC_` 前缀的进客户端（可被逆向读取），秘密一律留在服务端（见[安全实践](../advanced-topics/security/01-security-practices.md)）
- ✅ **灰度发布**：新版本先 5% 用户观察崩溃率，再全量；EAS Update 支持 rollout 百分比
- ✅ **崩溃率 < 0.5%、启动 < 2s** 作为版本准出红线，不达标回滚
- ✅ **每个 feature 自带测试**，集成进 CI 门禁，而非"最后统一补"
- ❌ **不要在客户端存长有效期 token**，用短期 access token + refresh 旋转
- ❌ **不要用 OTA 推"绕过审核"的行为变更**，违反商店政策风险极高

## ❓ 常见问题

**Q1: monorepo 里 EAS 构建怎么找依赖？**
A: `eas.json` 配置 `monorepo: true` 与正确的 `projectRoot`；pnpm workspace 需在安装回调里处理链接。

**Q2: 离线写操作与服务端冲突怎么办？**
A: 写操作携带客户端时间戳与版本号，服务端做 last-write-wins 或业务合并；关键业务改用乐观锁。

**Q3: 鸿蒙端如何纳入发布流水线？**
A: RNOH 构建/签名独立于 EAS，走 DevEco + 华为 AppGallery 流程，适配要点见 [RNOH 字典](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

---

## 🔗 相关文档

- 📖 [TypeScript 类型模式](../reference/language-concepts/04-typescript-patterns.md) — 分层架构下的类型组织
- 📖 [Expo 要点](../reference/framework-essentials/01-expo-essentials.md) — Config Plugins 与 EAS 机制
- 📖 [故障排除](../reference/quick-references/02-troubleshooting.md) — 生产事故排查手册
- 🎓 [Fabric/TurboModules/JSI 架构解析](../advanced-topics/architecture/01-new-architecture.md) — 技术选型的底层依据
- 🎓 [安全实践](../advanced-topics/security/01-security-practices.md) — 本文安全项的完整展开
- 🧪 [端到端测试](../testing/03-e2e-testing.md) — CI 冒烟测试配置
