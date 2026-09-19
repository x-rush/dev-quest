# 原生模块桥接 — Android/iOS 实现与 TurboModules 概念

## 先理解，再动手

原生模块是 JavaScript 与平台能力之间的边界。参数、结果、线程与错误都要约定；不是把一个 JS 函数改名就能调用系统 API。

**本节自测**：先列出读取系统信息的输入、输出、平台可用性和失败方式。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

缺失原生实现或权限时有明确错误；普通 JS 刷新不会补出未编译的原生模块。

</details>

> **文档简介**: 手写一个 Android（Kotlin）与 iOS（Swift/ObjC）原生模块，理解 JSI 通信模型，并认识新架构下 TurboModules 与 Codegen 的角色
>
> **目标读者**: 已能完成常规页面开发、需要调用设备系统能力的开发者
>
> **前置知识**: 完成 [05-navigation](./05-navigation.md)，具备基本的 Kotlin/Swift 读码能力

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#原生模块` `#TurboModules` `#JSI` `#Kotlin` `#Swift` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 在 Android/iOS 各写一个可从 JS 调用的原生模块
- ✅ 解释旧架构 Bridge 与新架构 JSI/TurboModules 的差异
- ✅ 判断"造轮子"前是否已有现成三方库（优先复用）
- ✅ 理解 Codegen 从 TypeScript 规约生成原生骨架的流程

## 🔍 核心概念：JS 与原生如何通信

| 维度 | Legacy Native Module | Turbo Native Module / 新架构 |
|------|--------------|----------------------|
| 通信模型 | 基于旧 Bridge 的异步调用模型 | 通过 JSI 与 Codegen 接入；接口可声明同步或异步方法，但耗时工作仍必须由原生侧安排线程 |
| 注册与发现 | `ReactPackage` 返回模块实例 | 由生成规约、原生实现及包注册共同完成；是否按需创建由具体包实现决定 |
| 类型安全 | JS 与原生签名靠人工保持一致 | Codegen 从 TS/Flow 规约生成平台接口，仍需为输入、权限和运行失败建模 |
| 适用 | 维护已有遗留模块、理解兼容层 | 新建 RN 原生模块优先采用的方向；RN 0.82 起运行时完全采用新架构 |

**决策顺序**: 优先查社区库（React Native Directory）→ Expo SDK 能力 → 再自研原生模块。若项目已使用 Expo，优先评估 Expo Modules API：它用 Kotlin/Swift 定义模块，并通过 Expo Autolinking 接入；确有 C++ 互操作或需要直接控制 RN Codegen 时，再走 Turbo Native Module。鸿蒙端的自研走 RNOH 的 ArkTS TurboModule，见 [RNOH 架构](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

> **路径选择**：下节 Android/ObjC 代码展示的是 Legacy Native Module 的最小注册机制，目的是读懂既有项目，不是 Expo 主线的新模块模板。Expo 项目请从 [Expo Modules API 官方概览](https://docs.expo.dev/modules/overview/)开始；它会生成注册代码，且修改原生部分后仍需重建 development build。

## 💻 Android：Kotlin 原生模块

**目标**: 暴露一个 `getDeviceName()` 方法给 JS。

1. 创建模块类 `android/app/src/main/java/com/myfirstapp/DeviceModule.kt`：

```kotlin
package com.myfirstapp

import android.os.Build
import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod

class DeviceModule(reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    // JS 侧通过这个名字访问模块
    override fun getName() = "DeviceModule"

    @ReactMethod // 必须标注，否则不会暴露给 JS
    fun getDeviceName(promise: Promise) {
        try {
            val name = "${Build.MANUFACTURER} ${Build.MODEL}"
            promise.resolve(name)
        } catch (e: Exception) {
            promise.reject("DEVICE_ERROR", e.message)
        }
    }
}
```

2. 模块必须由一个 `ReactPackage` 提供。创建 `DevicePackage.kt`：

```kotlin
package com.myfirstapp

import com.facebook.react.ReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.uimanager.ViewManager

class DevicePackage : ReactPackage {
    override fun createNativeModules(context: ReactApplicationContext): List<NativeModule> =
        listOf(DeviceModule(context))

    override fun createViewManagers(context: ReactApplicationContext): List<ViewManager<*, *>> =
        emptyList()
}
```

3. 再在 `MainApplication.kt` 的 Package 列表中注册**包**，不要直接加入 `DeviceModule`：

```kotlin
import com.facebook.react.ReactPackage

override fun getPackages(): List<ReactPackage> =
    PackageList(this).packages.apply {
        add(DevicePackage())
    }
```

4. JS 侧调用：

```tsx
import { NativeModules } from 'react-native';

const { DeviceModule } = NativeModules;
DeviceModule.getDeviceName().then((name: string) => console.log(name));
```

## 💻 iOS：ObjC/Swift 原生模块

RN iOS 模块以 ObjC 文件承载（Swift 需桥接文件，初学建议先 ObjC）。新建 `ios/MyFirstApp/DeviceModule.mm`：

```objc
// DeviceModule.mm
#import <React/RCTBridgeModule.h>
#import <UIKit/UIKit.h>

@interface DeviceModule : NSObject <RCTBridgeModule>
@end

@implementation DeviceModule

RCT_EXPORT_MODULE(); // 不传名字时，模块名默认取类名（即 DeviceModule）

RCT_EXPORT_METHOD(getDeviceName:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)
{
  NSString *name = [NSString stringWithFormat:@"%@ %@",
                    [UIDevice currentDevice].model,
                    [[UIDevice currentDevice] name]];
  resolve(name);
}

@end
```

修改原生代码后需要重新编译安装（Metro 热更新只覆盖 JS 层）。如项目有 `Gemfile`，用它锁定 CocoaPods：

```bash
npm run android   # Android 重新构建
bundle exec pod install --project-directory=ios
npm run ios
```

## 💻 新架构：Codegen 规约 + TurboModule

新架构推荐"先写 TS 规约，由 Codegen 生成原生接口骨架"，保证三端签名一致：

```ts
// NativeDevice.ts（TurboModule 规约）
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  getDeviceName(): Promise<string>;
}

export default TurboModuleRegistry.getEnforcing<Spec>('DeviceModule');
```

在 `package.json` 中声明 `codegenConfig` 后，构建期 Codegen 会据此生成 C++/Kotlin/ObjC 接口，原生侧按生成接口实现模块。`getEnforcing` 表示“模块缺失就是配置或构建错误”，会抛出异常；如果功能是平台可选的，改用 `TurboModuleRegistry.get<Spec>()` 并在 JS 侧处理 `null`。不要把“TurboModule”直接等同于任意模块一定懒加载或一定更快。

完整的 Codegen 配置字段与目录约定见 [TS 类型模式](../reference/language-concepts/04-typescript-patterns.md)。

## 🎨 最佳实践

原生接口先声明输入、结果和失败形式，例如读取文件返回内容或“无权限”错误。Promise 描述异步结果，并不会自动把耗时原生计算移出 UI 线程；线程安排由原生实现及所用架构决定，应在各平台分别核对。

用一个 TypeScript 包装层统一参数和错误映射，页面只调用业务能力。修改原生代码通常需要重新编译客户端，JS 热更新不能替换已经编译的原生实现。验证成功、用户拒绝权限和组件离开后三种情况，确保资源能释放。

## ❓ 常见问题

### Q1: `undefined is not an object (evaluating NativeModules.X)`？
**A**: 模块没注册成功。Android 检查 Package 列表与 `getName()` 返回值；iOS 检查 `.mm` 文件是否在 Xcode target 内、模块名是否一致。

### Q2: 现在还必须手写这些胶水吗？
**A**: 新架构下多数场景由社区库覆盖。Expo 项目自研时优先评估 Expo Modules API；直接使用 RN 原生接口时，优先走 Codegen 规约路线。手写 Legacy Bridge 模块适合维护已有代码或学习其注册机制，不应与新模块教程混为同一条默认路径。

### Q3: 鸿蒙端怎么写等价模块？
**A**: RNOH 提供 ArkTS TurboModule 机制，在鸿蒙壳工程内实现并注册，JS 侧接口不变；细节见 [05-harmonyos-rnoh-api](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

## 🎯 练习与实践

### 练习一：三端设备信息模块

**任务要求**:
1. Android/iOS 分别实现 `getDeviceInfo(): Promise<{os, model, version}>`
2. JS 侧封装统一接口并在设置页展示
3. （鸿蒙真机可用者）用 ArkTS 补齐鸿蒙实现

**评估标准**: 三端返回字段结构一致，UI 无需感知平台。

### 练习二：Bridge → TurboModule 体验

**任务要求**:
1. 按 Codegen 规约改造练习一的模块
2. 观察构建产物中生成的原生接口文件

**提示**: RN 0.82 起应用运行时完全采用新架构；这不代表旧库接口会立即消失，兼容层和迁移状态仍要看目标 RN 版本与库的发布说明。把生成的接口文件、构建命令和实际安装的 development build 版本一起记录。

---

## 🔗 相关文档

- 📄 **[高级特性](./07-advanced-features.md)**: 下一课，Fabric 渲染与性能
- 📄 **[RNOH 架构与鸿蒙适配](../reference/language-concepts/05-harmonyos-rnoh-api.md)**: ArkTS TurboModule 与三端对齐
- 📄 **[原生与设备能力库指南](../reference/library-guides/02-native-and-device-libs.md)**: 先查现成库再自研
- 📄 **[TS 类型模式](../reference/language-concepts/04-typescript-patterns.md)**: Codegen 规约的类型写法

> 💡 **学习建议**: 原生模块是 RN 开发的"深水区"，先熟练调用三方库，把自研留到真正没有现成方案的时候——90% 的功能不该碰这一层。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
