# 环境搭建 — Node/RN CLI/Expo 与三端工具链

## 先理解，再动手

先选择一个平台跑通工具链。JavaScript 依赖、Android/iOS 原生构建依赖与设备连接问题应分开排查。

**本节自测**：记录设备平台与运行方式，修改欢迎文案并重新加载。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

应在目标设备看到修改；浏览器预览成功不能代替原生平台验收。

</details>

> **文档简介**: 按 Android、iOS、OpenHarmony 三条独立工具链建立 React Native 环境；先选一个目标跑通，再为实际需求扩展另一平台
>
> **目标读者**: 有 React/TypeScript 基础、准备进入移动端开发的工程师
>
> **前置知识**: JavaScript/TypeScript 基础，了解 npm 包管理，最好有一门原生开发经验

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#环境搭建` `#Expo` `#Android Studio` `#Xcode` `#DevEco Studio` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 理解 RN CLI（bare workflow）与 Expo 两条开发路线的取舍
- ✅ 配置 Android Studio 并在模拟器/真机上运行调试
- ✅ 配置 Xcode + CocoaPods（需 macOS）并使用 iOS 模拟器
- ✅ 配置 DevEco Studio，为 RNOH（React Native for OpenHarmony）适配做准备
- ✅ 区分“开发服务器启动”“原生应用安装”“目标设备运行”三种证据，并为已选平台留下可复核记录

## 🧭 两条开发路线：Expo 还是 RN CLI

| 维度 | Expo（推荐起点） | RN CLI（bare） |
|------|-----------------|----------------|
| 心智模型 | 托管式，开箱即用 | 完全掌控 `android/`、`ios/` 原生工程 |
| 原生模块 | Expo SDK 与 Config Plugin 覆盖的能力可直接采用；任意原生库仍要核对集成方式 | 自己维护 Android/iOS 原生工程与依赖 |
| 构建 | 可用 EAS 云构建；本地 `npx expo run:android\|ios` 仍依赖对应原生工具链 | 本地 Gradle / Xcode 构建，或另行配置 CI |
| 鸿蒙 RNOH | 先确认目标 RNOH 版本、壳工程与生成策略兼容，不能假定所有 Expo 项目可直接接入 | 按目标 RNOH 发行版的示例工程集成 |

**建议**：学习阶段用 Expo 快速上手。Expo 的 `prebuild` 会按 app config 生成 Android/iOS 工程，适合采用持续原生生成（CNG）的项目；它不是“无缝迁移”保证。已经手工维护原生目录的工程，不应直接运行 `prebuild --clean`，否则手工修改可能被覆盖。是否接入 RNOH，应以该发行版的兼容矩阵与最小示例工程为准。

## 🛠️ 实践指南

### 步骤一：基础运行时（三端通用）

**目标**: 安装 Node.js、包管理器与 RN CLI 前置依赖

**操作指南**:

1. 安装项目需要的 Node.js 版本。新建 React Native 工程可先使用官方当前推荐版本；已有工程以 `package.json` 的 `engines`、锁文件和框架升级指南为准。不要把另一项目的 Node 版本抄过来。

```bash
# macOS（Homebrew；具体主版本按工程要求替换）
brew install node

# Windows（推荐用 nvm-windows 管理版本）
nvm install <项目要求的主版本>
nvm use <项目要求的主版本>
```

2. Android 目标再安装工程 Gradle/AGP 所要求的 JDK。先从 `android/gradle/wrapper/gradle-wrapper.properties`、Android Gradle Plugin 版本及构建输出确认兼容组合；JDK 的“能打印版本”不等于能编译该工程。

```bash
brew install --cask temurin@17   # macOS
```

3. 安装 Watchman（macOS/Linux，用于 Metro 文件监听，强烈推荐）

```bash
brew install watchman
```

**第一层证据**: `node -v` 可输出项目要求的版本；Android 项目再执行 `java -version`。记录命令实际解析到的路径（Windows 用 `where node` / `where java`，macOS/Linux 用 `which node` / `which java`）。这只证明运行时可调用，尚未证明原生构建可用。

### 步骤二：Android 工具链

**目标**: 配置 Android Studio、SDK 与 adb

**操作指南**:

1. 从官网安装 Android Studio，首次启动按默认勾选安装：
   - 工程要求的 Android SDK Platform（新工程可先安装官方当前稳定 API；已有工程以 `compileSdk` / 构建输出为准）
   - Android SDK Platform-Tools（含 `adb`）
   - Android Emulator + 最新系统镜像
2. 在 **Settings → Languages & Frameworks → Android SDK** 中确认以下组件已安装：
   - SDK Platforms: 工程所需 API 级别与系统镜像
   - SDK Tools: Platform-Tools、Build-Tools；只有报错或依赖要求时再安装 NDK（Side by side）和 CMake
3. 配置环境变量（macOS/Linux 写入 `~/.zshrc` 或 `~/.bashrc`）：

```bash
export ANDROID_HOME="$HOME/Library/Android/sdk" # macOS 示例；以 Android Studio 显示的 SDK Location 为准
export PATH="$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator"
```

4. 创建一台 AVD（模拟器），或开启手机的"开发者选项 → USB 调试"用真机。

**第二层证据**: 启动一个已下载系统镜像的 AVD 后，`adb devices` 显示其状态为 `device`；真机则需确认 USB 调试授权。空列表、`unauthorized`、`offline` 都不算通过。随后必须实际安装并启动一次原生应用，见“分层验收”。

### 步骤三：iOS 工具链（需 macOS）

**目标**: 安装 Xcode、命令行工具与 CocoaPods

**操作指南**:

1. 从 App Store 或 Apple Developer 下载页安装与项目依赖兼容的 Xcode；以 Xcode **当前实际版本**、项目 `ios/` 配置和框架官方升级说明为准，不在笔记中固定某个 Expo SDK 对应的 Xcode 小版本。
2. 安装 Command Line Tools：`Xcode → Settings → Locations`
3. 按工程的 iOS 依赖安装方式准备 CocoaPods。若仓库提供 `Gemfile`，优先让 Bundler 固定 CocoaPods 版本；没有时再选择团队规定的安装方式：

```bash
bundle install
bundle exec pod install
# 没有 Gemfile 且团队明确使用 Homebrew 时：brew install cocoapods
```

4. 打开一次模拟器确认运行正常：`Xcode → Open Developer Tool → Simulator`

**第二层证据**: `xcodebuild -version` 能输出版本；在实际工程的 `ios/` 目录按该工程流程完成 `bundle exec pod install`（若使用 Bundler）。仅能运行 `pod --version` 不能证明 Pods 或签名配置正确。

### 步骤四：鸿蒙工具链（DevEco Studio + RNOH 预备）

**目标**: 安装 DevEco Studio 并准备 HarmonyOS SDK

**操作指南**:

1. 从华为开发者官网安装与目标设备、目标 API 和 RNOH 发行版匹配的 DevEco Studio。产品版本、SDK API 和宿主机要求变化较快，安装前须同时核对 DevEco 文档与目标 RNOH 的发行说明。
2. 首次启动按向导安装 HarmonyOS SDK 与工具链（ArkTS 编译器、hvigor 构建系统）
3. 注册华为开发者账号，创建一个签名用的调试证书（DevEco 内置自动签名：**File → Project Structure → Signing Configs → Automatically generate signature**）
4. 创建一个空 Native 模板工程跑通模拟器/真机，确认 ArkTS 编译链正常
5. 记录 DevEco、SDK API、RNOH、React Native 与每个含原生代码依赖的版本。RNOH 包与 React Native、Harmony SDK 的具体对齐关系只能以目标发行版的映射表判断，不能从 API 号推导。

**第二层证据**: 从所选 RNOH 发行版的最小示例开始，在 DevEco 或该示例指定的 `hvigorw` 命令中构建并安装到一个模拟器或真机。`hvigorw --version` 只证明构建程序可启动；它不证明 RN 包注册、Metro 连通或设备运行正常。

**注意**：RNOH 适配要求 Node 版本与 RN 官方要求一致；DevEco Studio 本身有系统版本要求，安装前核对官方说明。

## 💻 快速验证

先选择下表中的**一个**目标完成第三层证据。三端不是一条命令，也不是每台开发机都能本地完成：iOS 本地构建需要 macOS；OpenHarmony 必须使用其匹配的 DevEco/RNOH 工具链。

| 层级 | 看到的结果 | 能证明什么 | 仍不能证明什么 |
|---|---|---|---|
| 开发服务器 | `npx expo start` 显示 Metro 地址 | JS 打包服务能启动 | 原生模块已编进应用、签名和设备兼容性 |
| Expo Go 预览 | Expo Go 打开默认页 | Expo Go 包含的运行时可以加载这段 JS | 任意自定义原生库或将来商店构建可用 |
| development build / 本地原生构建 | `npx expo run:android` 或 `npx expo run:ios` 编译、安装、启动 | 当前原生依赖与选定模拟器/设备能一起工作 | 另一平台、生产签名、权限和性能均已通过 |

创建最小 Expo 工程，先获得第一层或 Expo Go 预览证据：

```bash
npx create-expo-app@latest DevQuestDemo
cd DevQuestDemo
npx expo start
# Expo Go 扫码只用于快速 JS 预览；记录使用的设备与 Expo Go 版本
```

项目需要原生模块、原生配置或准备发版时，创建 development build 并做本地原生安装：

```bash
npx expo install expo-dev-client
npx expo run:android    # Android Studio + 已启动模拟器或 --device 真机
# macOS：npx expo run:ios   # Xcode + iOS Simulator 或 --device 真机
```

`run:*` 在缺少原生目录时会生成相应平台目录、编译、安装并启动开发服务器。新增/升级含原生代码的依赖、修改 app config 或升级 Expo SDK 后，要重新生成并重建；采用 CNG 的工程可用 `npx expo prebuild --clean` 后再构建。若原生目录由团队手工维护，先阅读项目说明，不能盲目执行该命令。鸿蒙端以选定版本的 RNOH 最小工程构建和设备启动为准，见 [RNOH 架构与鸿蒙适配](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

## 🎨 最佳实践

环境问题先核对实际执行的 Node、JDK、SDK 和构建插件版本，IDE 与终端可能使用不同路径。把项目采用的版本和检查命令写下来，再让新终端执行一次干净构建，验证文档是否足够复现。

JDK、Gradle、AGP 及原生依赖要按工程兼容表组合，不能把“某个最低版本以上”视为任意新版都兼容。模拟器适合快速迭代，涉及权限、相机、推送和性能的能力还要在目标真机验证；iOS 原生依赖按该工程的安装流程处理。

## ❓ 常见问题

### Q1: Windows 上能开发 iOS 吗？
**A**: 不能。Xcode 只在 macOS 运行，iOS 构建必须依赖 macOS（或 EAS Build 云端 macOS 机器）。Windows 用户可先完成 Android + 鸿蒙两端的开发。

### Q2: DevEco Studio 模拟器启动失败怎么办？
**A**: 检查系统虚拟化选项是否开启，在 **Device Manager** 中重新下载模拟器镜像；华为真机可改用 USB 连接直接调试。

### Q3: `npx expo start` 报 Metro 端口被占用？
**A**: 结束占用 8081 端口的进程，或用 `npx expo start --port 8082` 换端口。Linux/WSL 下注意 Windows 侧代理软件可能占用端口。

## 🎯 练习与实践

### 练习一：首个目标平台环境清单

**任务要求**:
1. 选择 Android、iOS 或 OpenHarmony 之一，并记录宿主 OS、Node、JDK（如适用）、IDE/SDK 与设备/模拟器版本。
2. 完成该平台的“第三层证据”：Android/iOS 为安装并启动 development build；OpenHarmony 为 RNOH 最小工程构建、安装和启动。
3. 修改一行欢迎文案，确认 JS 刷新生效；再记录一个失败案例及其定位层级（Metro、原生构建、安装或运行时权限）。
4. 其他平台写为“未验证”，直到拥有对应工具链和设备；不可用空命令输出替代。

**评估标准**: 笔记能给出一个真实的构建命令、安装目标、运行结果与失败案例；能解释为什么 `npx expo start` 或 `adb devices` 本身不构成原生应用验收。

### 练习二：跑通 Expo Demo

**任务要求**:
1. 用 `npx create-expo-app` 创建工程，并先在一个已选平台的 Expo Go 或模拟器中预览。
2. 修改模板首页的一行文案，确认 Metro 刷新；文件位置随模板变化，先查看项目目录，而不是假定必为 `app/(tabs)/index.tsx`。
3. 加入一个需要原生运行时的库后，创建 development build，在同一设备重新验证；写下“仅刷新失败、重建后成功”的原因。

**提示**: 真机预览需手机与电脑同一局域网；若网络隔离，用 `npx expo start --tunnel`。

---

## 🔗 相关文档

- 📄 **[创建第一个 App](./02-first-app.md)**: 环境就绪后的下一步，深入 Metro 与运行流程
- 📄 **[RN 核心 API 速查](../reference/language-concepts/01-rn-core-api.md)**: Platform、Dimensions 等运行时 API
- 📄 **[RNOH 架构与鸿蒙适配](../reference/language-concepts/05-harmonyos-rnoh-api.md)**: DevEco + RNOH 的版本匹配细则
- 📄 **[CLI 命令与调试速查](../reference/quick-references/01-cli-and-debug-cheatsheet.md)**: 常用命令一览
- 📄 **[故障排除](../reference/quick-references/02-troubleshooting.md)**: 环境类报错的对照表

> 💡 **学习建议**: 先把一个实际目标平台从构建到设备运行打通，再为第二平台重复同一套验收记录。版本组合、证书和原生插件会随项目变化；可复用的是检查顺序和证据，而不是一份永远不变的安装命令。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
