# 生态集成 — Expo Router、EAS 与常用库选型

> **文档简介**: 把 RN 应用接入主流生态：用 Expo Router 组织文件式路由，用 EAS 完成构建与更新链路，按决策表选型 Zustand/MMKV 等高频库并正确安装配置
>
> **目标读者**: 已掌握 RN 基础开发、准备搭建真实项目骨架的开发者
>
> **前置知识**: 已完成 [React Native 框架入门](./01-react-native-basics.md)，了解 npm 依赖管理

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐⭐ |
| **标签** | `#ExpoRouter` `#EAS` `#Zustand` `#MMKV` `#生态` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 用 Expo Router 建立文件路由 + 类型安全的导航结构
- ✅ 理解 EAS 三件套（Build/Submit/Update）在整个交付链路中的位置
- ✅ 按选型决策表落地状态管理与本地存储方案
- ✅ 识别哪些库需要原生编译、哪些是纯 JS

## 🧭 Expo Router：文件即路由

Expo Router API 速查见 [Expo 要点](../reference/framework-essentials/01-expo-essentials.md)；SDK 56 前 expo-router 基于 React Navigation 构建（SDK 56 起已 fork 内置），React Navigation 直接用法见 [导航基础教程](../basics/05-navigation.md)。

```
app/
├── _layout.tsx          # 根布局：全局 Provider 挂载点
├── index.tsx            # 首页（/）
├── (tabs)/              # 括号分组：不出现在 URL 中
│   ├── _layout.tsx      # 底部标签导航
│   ├── home.tsx         # /home
│   └── profile.tsx      # /profile
└── detail/[id].tsx      # 动态路由 /detail/:id
```

```tsx
// app/_layout.tsx —— 全局 Provider 统一挂载，路由组件保持纯净
import { Stack } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <Stack screenOptions={{ headerShown: false }} />
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
```

```tsx
// app/detail/[id].tsx —— 类型安全地读取动态参数
import { useLocalSearchParams } from 'expo-router';
import { Text } from 'react-native';

export default function Detail() {
  // params 类型来自泛型标注，无需手写 ParamList
  const { id } = useLocalSearchParams<{ id: string }>();
  return <Text>详情页：{id}</Text>;
}
```

## ☁️ EAS：构建/提交/热更新三件套

| 服务 | 作用 | 深入指南 |
|------|------|---------|
| **EAS Build** | 云端构建 ipa/aab，免配本地原生工具链 | [EAS Build 构建流程](../deployment/01-eas-build.md) |
| **EAS Submit** | 直推 App Store Connect / Play Console | [商店上架](../deployment/02-app-store-release.md) |
| **EAS Update** | 推送 JS/资源热更新，绕过商店审核 | [OTA 更新与可观测性](../deployment/03-ota-updates-observability.md) |

```bash
npm install -g eas-cli
eas login            # 登录 Expo 账号
eas build:configure  # 生成 eas.json（development/preview/production 三 profile）
```

## 📦 常用库选型与安装

状态与数据请求库的完整对比见 [状态与数据请求库指南](../reference/library-guides/01-state-and-data.md)，设备能力库见 [原生与设备能力库指南](../reference/library-guides/02-native-and-device-libs.md)。

```bash
# 状态管理：Zustand（轻量、无 Provider、选择器订阅）
npm install zustand

# 本地存储：MMKV（同步读写，比 AsyncStorage 快一个量级）
npm install react-native-mmkv

# Expo 设备能力：一次性装齐，无需手动 link
npx expo install expo-image expo-secure-store expo-haptics expo-location
# 注意：Expo 生态包优先用 expo install（版本与 SDK 对齐），而非 npm install
```

```ts
// zustand store：几行定义一个全局状态
import { create } from 'zustand';

type CartStore = {
  count: number;
  add: () => void;
};

export const useCart = create<CartStore>((set) => ({
  count: 0,
  add: () => set((s) => ({ count: s.count + 1 })),
}));

// 组件内用选择器订阅 —— 只有 count 变化才重渲染本组件
function CartBadge() {
  const count = useCart((s) => s.count);
  return <Text>{count}</Text>;
}
```

```ts
// MMKV：同步 API 直接读写，适合高频小数据（设置项、缓存）
import { createMMKV } from 'react-native-mmkv';

export const storage = createMMKV();        // 实例全局唯一即可
storage.set('theme', 'dark');
const theme = storage.getString('theme');   // 同步返回，无 await
```

**MMKV 与 SecureStore 分工**：MMKV 明文存储、追求速度；token/密码必须走 `expo-secure-store`（Keychain/Keystore 加密），安全细则见 [安全实践](../advanced-topics/security/01-security-practices.md)。

## ✅ 最佳实践

- ✅ **Expo 包优先 `npx expo install`**，保证与 SDK 版本对齐，避免原生依赖冲突
- ✅ **区分纯 JS 库与含原生代码的库**，后者升级需重新 `eas build`，无法走 OTA
- ✅ **Zustand 选择器订阅**（`useCart((s) => s.count)`），不要解构整个 store
- ❌ **不要同时引入两套路由方案**（Expo Router 与裸 React Navigation），二选一
- ❌ **不要用 MMKV 存敏感数据**，它不提供加密

## ❓ 常见问题

**Q1: `expo install` 和 `npm install` 有什么区别？**
A: expo install 会查询当前 SDK 的兼容版本表安装精确版本；npm 装最新版可能引入原生不兼容代码导致构建失败。

**Q2: 装了新库后真机白屏？**
A: 含原生代码的库需要重新构建 dev client（`npx expo run:android` 或 `eas build --profile development`），不能只刷新 Metro。排错思路见[故障排除](../reference/quick-references/02-troubleshooting.md)。

**Q3: 项目能从 RN CLI 迁到 Expo Router 吗？**
A: 可以，Expo SDK 覆盖绝大多数原生需求；先在分支上按 app/ 目录约定重排页面，再逐个迁移导航调用。

---

## 🔗 相关文档

- 📖 [Expo 要点 — Router、EAS 与 expo-modules](../reference/framework-essentials/01-expo-essentials.md) — 本文涉及的 API 完整速查
- 📖 [状态与数据请求库指南](../reference/library-guides/01-state-and-data.md) — Zustand/Redux/TanStack Query 全量对比
- 📖 [CLI 命令与调试速查表](../reference/quick-references/01-cli-and-debug-cheatsheet.md) — eas/expo 命令行全集
- 📄 [导航基础 — React Navigation](../basics/05-navigation.md) — Expo Router 的底层模型
- 🚀 [EAS Build 构建流程](../deployment/01-eas-build.md) — 生态集成在交付端的延伸
- 🚀 [生产级移动应用](../projects/04-production-mobile-app.md) — 本文档选型的综合落地
