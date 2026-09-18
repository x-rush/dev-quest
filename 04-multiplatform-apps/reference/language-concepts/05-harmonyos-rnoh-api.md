# RNOH 字典 — React Native for OpenHarmony 架构与适配

> **难度**: ⭐⭐ | **前置**: 已理解 RN 渲染链路与原生模块（[06-native-modules](../../basics/06-native-modules.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#鸿蒙` `#RNOH` `#ArkTS` `#DevEco Studio` `#HarmonyOS NEXT` |
| **更新日期** | `2026年9月` |

</details>

## RNOH 是什么

### 描述
React Native for OpenHarmony（RNOH）是华为/OpenHarmony 社区维护的 RN 适配层，让同一份 RN 业务代码运行在 HarmonyOS NEXT / OpenHarmony 设备上。代码托管于 Gitee 的 `openharmony-sig/ohos_react_native` 仓库，npm 侧以 `@react-native-ohos/react-native-harmony` 与 `@rnoh/react-native-openharmony` 两个包提供。

### 版本对齐（最重要的前置条件）

| 依赖/工具 | 对齐要求 |
|-----------|---------|
| `react-native-harmony` | 与工程 `react-native` 版本一一对应（查 RNOH 仓库版本映射表） |
| DevEco Studio + HarmonyOS SDK | 与 RNOH 发布说明标注的 API 版本匹配（API 12+） |
| 三方库 | 纯 JS 与原生依赖分别评估；原生库检查目标 RNOH 版本的适配实现 |

```bash
# 安装鸿蒙适配核心包（版本以 RNOH 发布页为准）
npm i @react-native-ohos/react-native-harmony
```

**陷阱**: 含未适配原生代码的社区库可能无法构建或运行；纯 JS 库不能一概而论；先查 RNOH 的三方库适配列表。

## 架构总览

```
┌────────────────────────────────────────────┐
│  JS 业务代码（可共享，平台能力另行适配）        │
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

**组件实现**：RN 的组件语义由 RNOH 适配到平台能力；不要推断 FlatList 必然映射成 WaterFlow/Grid。具体实现路径和支持范围须阅读目标版本文档与源码。

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

```arkts
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
鸿蒙原生模块用 ArkTS（基于 TypeScript 并带有自身约束及声明式 UI 能力）实现，通过 RNOH 的 TurboModule 机制暴露给 JS。

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
- ✅ 逐一检查带原生实现的依赖，采用经过目标版本验证的适配方案
- ✅ `module.json5` 声明了全部所需权限
- ✅ `appKey` 与 `AppRegistry.registerComponent` 名称一致
- ✅ 真机上 `hdc rport` 端口转发后 Metro 可连通
- ✅ 三端回归：深色模式、安全区、返回手势逐项验证

<!-- full-library-explanation -->
## 把“可共享”拆成可验证的四层

纯业务算法、React 组件、带原生依赖的库、系统服务要分别评估。纯 JS 工具库通常不需要特定命名空间的适配包；相机、数据库或支付库则可能包含平台实现。npm 包能安装，只证明依赖解析成功。

上文 RNApp 与 TurboModule 片段是架构示意，未提供可独立编译的壳工程。应从目标 RNOH 发行版的示例工程开始，保留它的 SDK、构建配置、注册方式，再逐步替换业务页面；不要直接把这些字段复制到任意最新 SDK。参考 [RNOH 官方仓库](https://gitee.com/openharmony-sig/ohos_react_native)的对应版本文档。

练习：建立能力表，记录“文本布局、网络请求、本地数据库、通知”在 Android/iOS/OpenHarmony 上的实现、版本、权限、验证设备和失败行为。先验证一个最小页面，再逐个加入依赖。验收：能够指出失败出在 JS 打包、原生链接、模块注册还是运行时权限，而不是只写“三端兼容”。

OpenHarmony 与面向具体商业设备的 HarmonyOS SDK/服务并非任意互换；平台识别值也要以选定适配版本实际返回为准，不要假设始终冒充 Android。

## 🔗 相关文档

- 📄 **[RN 核心 API 字典](./01-rn-core-api.md)**: `Platform.OS` 在鸿蒙的行为说明
- 📄 **[原生模块桥接教程](../../basics/06-native-modules.md)**: 三端原生模块的统一视角
- 📄 **[CLI 命令与调试速查](../quick-references/01-cli-and-debug-cheatsheet.md)**: hdc 常用命令
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)**: 鸿蒙白屏/版本冲突排查
- 📄 **[环境搭建教程](../../basics/01-environment-setup.md)**: DevEco Studio 安装步骤

*延伸: 华为开发者官网 HarmonyOS 文档 · RNOH 仓库（Gitee openharmony-sig/ohos_react_native）*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
