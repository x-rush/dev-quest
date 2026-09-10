# RNOH 字典 — React Native for OpenHarmony 架构与适配

> **难度**: ⭐⭐ | **前置**: 已理解 RN 渲染链路与原生模块（[06-native-modules](../../basics/06-native-modules.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#鸿蒙` `#RNOH` `#ArkTS` `#DevEco Studio` `#HarmonyOS NEXT` |
| **更新日期** | `2026年9月` |

## RNOH 是什么

### 描述
React Native for OpenHarmony（RNOH）是华为/OpenHarmony 社区维护的 RN 适配层，让同一份 RN 业务代码运行在 HarmonyOS NEXT / OpenHarmony 设备上。代码托管于 Gitee 的 `openharmony-sig/ohos_react_native` 仓库，npm 侧以 `@react-native-ohos/react-native-harmony` 与 `@rnoh/react-native-openharmony` 两个包提供。

### 版本对齐（最重要的前置条件）

| 依赖/工具 | 对齐要求 |
|-----------|---------|
| `react-native-harmony` | 与工程 `react-native` 版本一一对应（查 RNOH 仓库版本映射表） |
| DevEco Studio + HarmonyOS SDK | 与 RNOH 发布说明标注的 API 版本匹配（API 12+） |
| 三方库 | 必须使用 `@react-native-oh-tpl/` 或 `@react-native-ohos/` 下的 harmony 适配版 |

```bash
# 安装鸿蒙适配核心包（版本以 RNOH 发布页为准）
npm i @react-native-ohos/react-native-harmony
```

**陷阱**: 直接把社区库装最新版（未经 harmony 适配）在鸿蒙真机必然报错；先查 RNOH 的三方库适配列表。

## 架构总览

```
┌────────────────────────────────────────────┐
│  JS 业务代码（与 Android/iOS 完全共享）        │
├────────────────────────────────────────────┤
│  Hermes 引擎（JS Bundle → 字节码执行）        │
├────────────────────────────────────────────┤
│  RNOH C++ 核心：RNInstance（JS 引擎/任务调度） │
├────────────────────────────────────────────┤
│  ArkTS 层：RNSurface → ArkUINode 映射        │
├────────────────────────────────────────────┤
│  ArkUI 渲染引擎 + 鸿蒙系统能力                │
└────────────────────────────────────────────┘
```

**组件映射关系**: `View → Stack/Column`、`Text → Text`、`Image → Image`、`ScrollView → Scroll`、`FlatList → WaterFlow/Grid`（视配置）。Fabric 渲染下组件树由 C++ 管线提交给 ArkTS 挂载到 ArkUI。

## 壳工程结构（harmony/）

```
harmony/
├── entry/src/main/ets/
│   ├── pages/Index.ets          # 鸿蒙入口页，内嵌 RNApp
│   ├── RNPackagesFactory.ets    # 注册 RN Package（含鸿蒙原生模块）
│   └── ability/EntryAbility.ets
├── entry/src/main/module.json5  # 权限、want 配置（鸿蒙侧"manifest"）
├── hvigorfile.ts                # hvigor 构建脚本
└── build-profile.json5          # 签名与 SDK 版本配置
```

### Index.ets 最小骨架（示意）

```ts
// entry/src/main/ets/pages/Index.ets
import { RNApp } from '@rnoh/react-native-openharmony';

@Entry
@Component
struct Index {
  build() {
    RNApp({
      rnInstanceConfig: {
        enableNDKText: true,
        enableCArchitecture: true,   // 新架构（Fabric/JSI）开关
      },
      appKey: 'MyFirstApp',          // 与 AppRegistry 注册名一致
      initialProps: {},
      onConfigurationUpdated: () => {},
    })
  }
}
```

## 工具链命令对照

| 场景 | Android/iOS | 鸿蒙 |
|------|------------|------|
| 设备列表 | `adb devices` | `hdc list targets` |
| 安装应用 | `adb install xx.apk` | `hdc install xx.hap` |
| 日志 | `adb logcat` | `hdc hilog` |
| 端口转发（连 Metro） | `adb reverse tcp:8081` | `hdc rport tcp:8081 tcp:8081` |
| 构建 | Gradle / Xcode | DevEco 或 `hvigorw assembleHap` |
| 签名 | keystore / 证书 | AGC 证书 + profile（DevEco 可自动签名） |

## ArkTS 混合开发要点

### 描述
鸿蒙原生模块用 ArkTS（TS 超集 + 声明式 UI）实现，通过 RNOH 的 TurboModule 机制暴露给 JS。

### 语法和示例

```ts
// 鸿蒙侧：ArkTS TurboModule 实现（示意）
import { RNPackage, TurboModule, TurboModuleFactory } from '@rnoh/react-native-openharmony/ts';
import type { TurboModuleContext } from '@rnoh/react-native-openharmony/ts';

class DeviceModule extends TurboModule {
  getDeviceName(): Promise<string> {
    return new Promise((resolve) => {
      // 调用鸿蒙系统 API（@ohos.deviceInfo 等）
      resolve('HarmonyOS Device');
    });
  }
}

class DeviceModuleFactory extends TurboModuleFactory {
  createModule(name: string) {
    return name === 'DeviceModule' ? new DeviceModule(this.ctx) : null;
  }
}

export class MyRNPackages extends RNPackage {
  createTurboModuleFactory(ctx: TurboModuleContext) {
    return new DeviceModuleFactory(ctx);
  }
}
```

```tsx
// JS 侧：接口与 Android/iOS 完全一致，无需感知平台
import { NativeModules } from 'react-native';
NativeModules.DeviceModule.getDeviceName().then(console.log);
```

### 陷阱
- ArkTS 是 TS 的受限子集：禁用 `any`、禁运行时动态修改对象结构，不能把通用 TS 代码直接搬过来
- 鸿蒙系统 API 以 `@ohos.*` 命名空间导入，与 Android/iOS SDK 完全不同，能力对照需单独维护

## 鸿蒙特有能力对照

| 能力 | Android | iOS | 鸿蒙 |
|------|---------|-----|------|
| 推送 | FCM/厂商通道 | APNs | 华为 Push Kit（HMS） |
| 支付 | Google Pay | Apple Pay | 华为 IAP Kit |
| 权限声明 | AndroidManifest | Info.plist | module.json5 `requestPermissions` |
| 页面路由 | Activity | ViewController | `want` / ArkUI 页面栈 |
| 包格式 | APK/AAB | IPA | HAP/App Pack |

## 适配检查清单

- ✅ `react-native-harmony` 版本与 RN 版本对齐（查 RNOH 版本映射表）
- ✅ 三方库全部替换为 `@react-native-ohos`/`@react-native-oh-tpl` 适配版
- ✅ `module.json5` 声明了全部所需权限
- ✅ `appKey` 与 `AppRegistry.registerComponent` 名称一致
- ✅ 真机上 `hdc rport` 端口转发后 Metro 可连通
- ✅ 三端回归：深色模式、安全区、返回手势逐项验证

## 🔗 相关文档

- 📄 **[RN 核心 API 字典](./01-rn-core-api.md)**: `Platform.OS` 在鸿蒙的行为说明
- 📄 **[原生模块桥接教程](../../basics/06-native-modules.md)**: 三端原生模块的统一视角
- 📄 **[CLI 命令与调试速查](../quick-references/01-cli-and-debug-cheatsheet.md)**: hdc 常用命令
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)**: 鸿蒙白屏/版本冲突排查
- 📄 **[环境搭建教程](../../basics/01-environment-setup.md)**: DevEco Studio 安装步骤

*延伸: 华为开发者官网 HarmonyOS 文档 · RNOH 仓库（Gitee openharmony-sig/ohos_react_native）*
