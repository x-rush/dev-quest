# Expo 要点 — Router、EAS 与 expo-modules

> **难度**: ⭐ | **前置**: 已用 Expo 创建过工程（[02-first-app](../../basics/02-first-app.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Expo` `#expo-router` `#EAS` `#Config Plugins` |
| **更新日期** | `2026年9月` |

## expo-router — 文件路由

### 描述
Expo 官方的文件系统路由（基于 React Navigation），`app/` 目录结构即路由结构，新版 Expo 模板默认使用。

### 语法和示例
```
app/
├── _layout.tsx        # 根布局（Stack 或 Tabs 容器）
├── index.tsx          # / 首页
├── todo/
│   ├── _layout.tsx    # /todo 分组布局
│   ├── index.tsx      # /todo
│   └── [id].tsx       # /todo/:id 动态路由
└── +not-found.tsx     # 404
```

```tsx
// app/todo/[id].tsx —— 动态参数
import { useLocalSearchParams, Stack } from 'expo-router';

export default function TodoDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <Stack.Screen options={{ title: `详情 ${id}` }} />;
}
```

```tsx
// 编程式跳转
import { router } from 'expo-router';
router.push({ pathname: '/todo/[id]', params: { id: '42' } });
router.back();
```

### 陷阱
- 文件名即路由，大小写敏感；`_layout.tsx` 不产生路由
- 动态路由文件夹用 `[id]` 命名，误用圆括号 `(group)` 会变成纯分组不进 URL

## EAS — 构建与提交

### 描述
Expo Application Services：云端构建（EAS Build）、商店提交（EAS Submit）、热更新（EAS Update）三件套。

### 语法和示例
```bash
npm install -g eas-cli
eas login
eas build:configure          # 生成 eas.json

# 构建（--profile 对应 eas.json 中 profiles）
eas build --platform android --profile preview   # APK 供内测
eas build --platform all --profile production    # 商店包（aab/ipa）

# 提交商店
eas submit --platform ios --latest
```

```json
// eas.json 常用配置
{
  "build": {
    "preview": { "android": { "buildType": "apk" } },
    "production": { "autoIncrement": true }
  }
}
```

### 陷阱
- EAS 构建需 Expo 账号 + 项目所有者权限；免费额度按月计
- iOS 证书/描述文件由 EAS 托管管理，本地已有证书冲突时先清理 keychain 配置

## expo-modules 与系统能力

### 描述
Expo SDK 的能力层。覆盖绝大多数常用设备能力，优先于社区原生库使用。

### 常用模块速查

| 模块 | 能力 |
|------|------|
| `expo-secure-store` | 加密键值存储（存 token） |
| `expo-camera` / `expo-image-picker` | 相机/相册 |
| `expo-notifications` | 推送通知 |
| `expo-location` | 定位 |
| `expo-sensors` | 传感器 |
| `expo-file-system` | 文件读写 |
| `expo-local-authentication` | 指纹/面容 |
| `expo-image` | 高性能图片组件（替换 RN Image） |

### 语法和示例
```tsx
import * as SecureStore from 'expo-secure-store';

await SecureStore.setItemAsync('token', 'xxx');
const token = await SecureStore.getItemAsync('token');
```

## app.json / app.config.ts — 工程配置

```json
{
  "expo": {
    "name": "TodoLedger",
    "slug": "tod-ledger",
    "scheme": "todledger",
    "ios": { "bundleIdentifier": "com.example.todledger" },
    "android": { "package": "com.example.todledger" },
    "plugins": ["expo-router", ["expo-camera", { "cameraPermission": "扫码需要相机" }]]
  }
}
```

### Config Plugins
**描述**: 以声明式插件修改原生工程（AndroidManifest/Info.plist 等），替代手工编辑自动生成文件。

```ts
// app.config.ts 自定义插件（示意）
const withMyConfig = (config) => {
  config.ios.infoPlist.NSAppTransportSecurity = { NSAllowsArbitraryLoads: false };
  return config;
};
```

### 陷阱
- 原生目录是 prebuild 的产物，手工改动会被下次 prebuild 覆盖；平台配置一律走 plugins
- `scheme` 决定深链协议，改后需重新 prebuild

## Expo vs bare 决策表

| 场景 | 建议 |
|------|------|
| 新项目、常规 App | Expo + CNG（Continuous Native Generation） |
| 需要大量自研原生模块 | prebuild 转 bare，保留 Expo SDK |
| 主目标含鸿蒙 RNOH | 鸿蒙侧按 bare 流程接入（RNOH 不走 Expo 托管构建） |

## 🔗 相关文档

- 📄 **[React Navigation API 速查](./02-navigation-essentials.md)**: expo-router 的底层依赖
- 📄 **[RNOH 架构](../language-concepts/05-harmonyos-rnoh-api.md)**: 鸿蒙接入的 bare 流程
- 📄 **[原生与设备能力库指南](../library-guides/02-native-and-device-libs.md)**: Expo 模块之外的补充选型
- 📄 **[综合练习教程](../../basics/08-first-project.md)**: 在项目中使用 Expo 全家桶

*延伸: Expo 官方文档 docs.expo.dev · EAS 定价页*
