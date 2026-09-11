# 环境搭建 — Node/RN CLI/Expo 与三端工具链

> **文档简介**: 一次配置好 React Native 三端（Android + iOS + 鸿蒙 HarmonyOS）开发所需的全部环境，包括 Node、RN CLI、Expo、Android Studio、Xcode 与 DevEco Studio
>
> **目标读者**: 有 React/TypeScript 基础、准备进入移动端开发的工程师
>
> **前置知识**: JavaScript/TypeScript 基础，了解 npm 包管理，最好有一门原生开发经验

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#环境搭建` `#Expo` `#Android Studio` `#Xcode` `#DevEco Studio` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 理解 RN CLI（bare workflow）与 Expo 两条开发路线的取舍
- ✅ 配置 Android Studio 并在模拟器/真机上运行调试
- ✅ 配置 Xcode + CocoaPods（需 macOS）并使用 iOS 模拟器
- ✅ 配置 DevEco Studio，为 RNOH（React Native for OpenHarmony）适配做准备
- ✅ 用一条命令验证三端环境是否就绪

## 🧭 两条开发路线：Expo 还是 RN CLI

| 维度 | Expo（推荐起点） | RN CLI（bare） |
|------|-----------------|----------------|
| 心智模型 | 托管式，开箱即用 | 完全掌控 `android/`、`ios/` 原生工程 |
| 原生模块 | 大部分场景用 Expo SDK + Config Plugins 覆盖 | 任意三方原生库 |
| 构建 | EAS Build 云端构建，也支持 `npx expo prebuild` 弹出原生目录 | 本地 Gradle / Xcode 构建 |
| 鸿蒙 RNOH | 需 prebuild 出原生工程后按 bare 流程接入 | 直接接入 |

**建议**：学习阶段用 Expo 快速上手；需要深度原生集成（含 RNOH）时，Expo 的 `prebuild` 可以无缝过渡到 bare 工程形态，两条路线并不对立。

## 🛠️ 实践指南

### 步骤一：基础运行时（三端通用）

**目标**: 安装 Node.js、包管理器与 RN CLI 前置依赖

**操作指南**:

1. 安装 Node.js LTS（RN 0.87 要求 Node 22+，Expo SDK 57 最低 22.13，推荐 22 LTS）

```bash
# macOS（Homebrew）
brew install node@22

# Windows（推荐用 nvm-windows 管理版本）
nvm install 22
nvm use 22
```

2. 安装 JDK 17（Android 构建必需；RN 0.87 的 AGP 9 + Kotlin 2.0+ 基准下 JDK 17 满足）

```bash
brew install --cask temurin@17   # macOS
```

3. 安装 Watchman（macOS/Linux，用于 Metro 文件监听，强烈推荐）

```bash
brew install watchman
```

**验证方法**: `node -v`、`java -version` 均能输出版本号即通过。

### 步骤二：Android 工具链

**目标**: 配置 Android Studio、SDK 与 adb

**操作指南**:

1. 从官网安装 Android Studio，首次启动按默认勾选安装：
   - Android SDK Platform（现行 RN/Expo 基准为 compileSdk 36，安装最新稳定 API 级别即可）
   - Android SDK Platform-Tools（含 `adb`）
   - Android Emulator + 最新系统镜像
2. 在 **Settings → Languages & Frameworks → Android SDK** 中确认以下组件已安装：
   - SDK Platforms: 最新稳定 API 级别
   - SDK Tools: NDK（Side by side）、CMake、Android SDK Build-Tools
3. 配置环境变量（macOS/Linux 写入 `~/.zshrc` 或 `~/.bashrc`）：

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/emulator
```

4. 创建一台 AVD（模拟器），或开启手机的"开发者选项 → USB 调试"用真机。

**验证方法**: `adb devices` 能看到模拟器或真机列表。

### 步骤三：iOS 工具链（需 macOS）

**目标**: 安装 Xcode、命令行工具与 CocoaPods

**操作指南**:

1. 从 App Store 安装 Xcode（Expo SDK 57 要求 Xcode 26.4+，建议最新稳定版）
2. 安装 Command Line Tools：`Xcode → Settings → Locations`
3. 安装 CocoaPods（RN iOS 依赖管理）：

```bash
sudo gem install cocoapods
# 或使用 Homebrew: brew install cocoapods
```

4. 打开一次模拟器确认运行正常：`Xcode → Open Developer Tool → Simulator`

**验证方法**: `xcodebuild -version` 与 `pod --version` 均能输出版本号。

### 步骤四：鸿蒙工具链（DevEco Studio + RNOH 预备）

**目标**: 安装 DevEco Studio 并准备 HarmonyOS SDK

**操作指南**:

1. 从华为开发者官网下载并安装 DevEco Studio（当前支持 HarmonyOS NEXT / API 12+）
2. 首次启动按向导安装 HarmonyOS SDK 与工具链（ArkTS 编译器、hvigor 构建系统）
3. 注册华为开发者账号，创建一个签名用的调试证书（DevEco 内置自动签名：**File → Project Structure → Signing Configs → Automatically generate signature**）
4. 创建一个空 Native 模板工程跑通模拟器/真机，确认 ArkTS 编译链正常
5. 记录 API 版本号——接入 RNOH 时，`react-native-harmony` 包版本需与 DevEco SDK API 版本匹配

**验证方法**: DevEco 内置终端 `hvigorw --version` 可执行，模拟器能运行空工程。

**注意**：RNOH 适配要求 Node 版本与 RN 官方要求一致；DevEco Studio 本身有系统版本要求，安装前核对官方说明。

## 💻 快速验证

创建一个最小 Expo 工程验证 Node + 模拟器链路：

```bash
npx create-expo-app@latest DevQuestDemo
cd DevQuestDemo
npx expo start
# 终端按 a 启动 Android 模拟器；按 i 启动 iOS 模拟器
# 或用 Expo Go 扫码在真机预览
```

若模拟器中能看到默认欢迎页，说明 Android/iOS 工具链已就绪。鸿蒙端的环境验证在接入 RNOH 后进行（见 [RNOH 架构与鸿蒙适配](../reference/language-concepts/05-harmonyos-rnoh-api.md)）。

## 🎨 最佳实践

### ✅ 推荐做法
- **用 nvm 类工具管理 Node 版本**，避免全局版本漂移导致构建突然失败
- **Android 环境变量写进 shell 配置文件**并 `source` 一次，IDE 与终端共用
- **三端 SDK 版本记录在项目 README**，新成员可按文档复现环境

### ❌ 避免陷阱
- **JDK 版本不匹配**: 现行 RN 工具链（AGP 9）需要 JDK 17+，装错大版本会出现莫名其妙的构建异常
- **只在模拟器上验证**: 真机（尤其华为鸿蒙真机）与模拟器行为差异大，环境搭好后尽早连真机
- **跳过 CocoaPods**: bare 工程 iOS 侧漏跑 `pod install` 会出现头文件找不到的编译错误

## ❓ 常见问题

### Q1: Windows 上能开发 iOS 吗？
**A**: 不能。Xcode 只在 macOS 运行，iOS 构建必须依赖 macOS（或 EAS Build 云端 macOS 机器）。Windows 用户可先完成 Android + 鸿蒙两端的开发。

### Q2: DevEco Studio 模拟器启动失败怎么办？
**A**: 检查系统虚拟化选项是否开启，在 **Device Manager** 中重新下载模拟器镜像；华为真机可改用 USB 连接直接调试。

### Q3: `npx expo start` 报 Metro 端口被占用？
**A**: 结束占用 8081 端口的进程，或用 `npx expo start --port 8082` 换端口。Linux/WSL 下注意 Windows 侧代理软件可能占用端口。

## 🎯 练习与实践

### 练习一：三端环境清单自查

**任务要求**:
1. 依次执行 `node -v`、`adb devices`、`xcrun simctl list devices`（macOS）、`hvigorw --version`（DevEco 终端）
2. 把每条命令的输出记录到个人笔记
3. 对失败项按本文档对应步骤重新排查

**评估标准**: 三端各自的验证命令都能成功输出。

### 练习二：跑通 Expo Demo

**任务要求**:
1. 用 `npx create-expo-app` 创建工程并在 Android 真机上预览
2. 修改 `App.tsx` 中的一行文案并体验 Metro 热更新

**提示**: 真机预览需手机与电脑同一局域网；若网络隔离，用 `npx expo start --tunnel`。

---

## 🔗 相关文档

- 📄 **[创建第一个 App](./02-first-app.md)**: 环境就绪后的下一步，深入 Metro 与运行流程
- 📄 **[RN 核心 API 速查](../reference/language-concepts/01-rn-core-api.md)**: Platform、Dimensions 等运行时 API
- 📄 **[RNOH 架构与鸿蒙适配](../reference/language-concepts/05-harmonyos-rnoh-api.md)**: DevEco + RNOH 的版本匹配细则
- 📄 **[CLI 命令与调试速查](../reference/quick-references/01-cli-and-debug-cheatsheet.md)**: 常用命令一览
- 📄 **[故障排除](../reference/quick-references/02-troubleshooting.md)**: 环境类报错的对照表

> 💡 **学习建议**: 环境搭建是三端开发中"一次性成本最高"的环节，值得花半天时间把三端全部打通并记录踩坑日志——之后每个新项目都能直接复用这套配置。
