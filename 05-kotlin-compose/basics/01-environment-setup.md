# 环境搭建 - Android Studio 与 Kotlin 开发环境

> **文档简介**: 从零搭建 Android + Jetpack Compose 开发环境：安装 Android Studio、配置 JDK 与 Android SDK、创建模拟器，并验证整条 Gradle 构建链路可用
>
> **目标读者**: 准备进入 Android 原生开发的初学者，以及从 Go、Web 等其他技术栈转来的开发者
>
> **前置知识**: 任意一门语言的编程基础；无需 Android 开发经验

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#环境搭建` `#Android-Studio` `#JDK` `#模拟器` `#Gradle` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 安装 Android Studio 并完成首次启动配置
- ✅ 理解 JDK、Android SDK、Gradle 三者在构建中的分工
- ✅ 创建并启动一台可用的模拟器（AVD）
- ✅ 用命令行工具验证 SDK 与设备状态
- ✅ 能独立解决环境搭建阶段的常见报错

## 📋 目录

- [工具链总览](#工具链总览)
- [安装 Android Studio](#安装-android-studio)
- [配置 Android SDK](#配置-android-sdk)
- [创建模拟器 AVD](#创建模拟器-avd)
- [验证开发环境](#验证开发环境)
- [常见问题](#常见问题)
- [练习与实践](#练习与实践)

---

## 🔧 工具链总览

Android 开发环境由四层工具组成，理解它们的分工能让你在报错时快速定位问题：

| 工具 | 角色 | 说明 |
|------|------|------|
| **Android Studio** | IDE | 基于 IntelliJ IDEA，内置模拟器管理、Layout Inspector、Profiler |
| **JDK** | 编译运行时 | Android Gradle Plugin 9.x 要求 **JDK 17+**；新版 Studio 已内置 JBR（JetBrains Runtime），通常无需另装 |
| **Android SDK** | 平台库 | 提供各 API 级别的 `android.jar`、构建工具（aapt2、d8）、平台工具（adb） |
| **Gradle** | 构建系统 | 通过 Android Gradle Plugin（AGP）驱动编译、打包、签名 |

> 💡 与 Go 的对照：`android.jar` 类似 Go 标准库，`adb` 类似设备管理工具，Gradle 扮演 `go build` 的角色——但配置复杂得多，值得花时间理解。

---

## 🖥️ 安装 Android Studio

1. 访问 [developer.android.com/studio](https://developer.android.com/studio) 下载最新稳定版（不要下载 Canary/预览版学习）。
2. 按操作系统安装：
   - **Windows**: 运行 `.exe` 安装器，勾选 Android Virtual Device 组件
   - **macOS**: 拖拽 `.dmg` 到 Applications（Apple Silicon 会自动安装 ARM 版）
   - **Linux**: 解压 `.tar.gz` 到 `/opt`，运行 `bin/studio.sh`
3. 首次启动进入 Setup Wizard，选择 **Standard** 安装类型，向导会自动下载：
   - 最新 Android SDK 平台
   - Platform-Tools（含 adb）
   - 模拟器与系统镜像

**验证方法**: 安装完成后打开 Studio，欢迎窗口左下角能看到版本号即成功。

---

## 📦 配置 Android SDK

### 通过 SDK Manager 管理

菜单路径：`Tools → SDK Manager`（或欢迎页 `More Actions → SDK Manager`）

| 标签页 | 用途 | 学习阶段建议 |
|--------|------|--------------|
| **SDK Platforms** | 各 Android 版本的平台库 | 勾选最新稳定 API 级别即可 |
| **SDK Tools** | 构建与调试工具 | 确保 Android SDK Build-Tools、Platform-Tools、Emulator 已勾选 |
| **SDK Update Sites** | 第三方仓库 | 初学阶段无需改动 |

### 记住 SDK 路径

SDK 默认安装位置（后续配置 CI 或命令行时会用到）：

```text
Windows: C:\Users\<用户名>\AppData\Local\Android\Sdk
macOS:   ~/Library/Android/sdk
Linux:   ~/Android/Sdk
```

> 💡 路径可随时在 `SDK Manager → Android SDK Location` 中查看，建议写入环境变量 `ANDROID_HOME`。

---

## 📱 创建模拟器 AVD

1. 打开 `Tools → Device Manager`，点击 **Create Virtual Device**。
2. 选择机型（学习用 **Pixel 8** 即可），点击 Next。
3. 选择系统镜像：
   - 优先选 **最新稳定 API 级别 + Google APIs**（非 Play Store 版，可 root 便于调试）
   - 镜像架构选 **x86_64**（Intel/AMD 通用，性能最好）
4. 点击 Next → Finish 完成创建。

### 启动与基本操作

- 点击设备列表右侧 ▶️ 启动；首次启动较慢（1-3 分钟），之后默认走 Quick Boot 快照
- 模拟器侧边栏可模拟旋转、指纹、网络断开、GPS 位置等
- `Cold Boot Now`（冷启动）可解决快照损坏导致的黑屏

> ⚠️ **WSL2 用户注意**: Windows 下的 WSL2 环境无法直接运行 GPU 加速的 Android 模拟器。可行方案：
> 1. 在 Windows 宿主机安装 Studio，WSL2 内通过 `adb connect` 连接宿主模拟器
> 2. 或直接使用物理设备：开启"开发者选项 → USB 调试"后用 `adb devices` 验证

---

## ✅ 验证开发环境

打开 Studio 内置终端（或系统终端），逐条验证：

```bash
# 1. 验证 adb（平台工具）——应列出已连接的设备/模拟器
adb devices

# 2. 验证 Java 版本——AGP 9.x 需要 17 及以上
java -version

# 3. 验证 sdkmanager（需先安装 cmdline-tools 组件）
sdkmanager --list | head -20
```

预期输出示例：

```text
List of devices attached
emulator-5554   device
```

三条命令都正常返回，说明 JDK、SDK、设备链路均已打通。

---

## ❓ 常见问题

### Q1: Gradle Sync 卡住或下载极慢？
**A**: Gradle 与依赖默认从境外服务器下载。在国内网络下可在项目 `settings.gradle.kts` 中配置镜像仓库（如阿里云 `maven.aliyun.com` 的 google/public 仓库），或为 Gradle 配置代理（`gradle.properties` 中 `systemProp.http.proxyHost` 等属性）。

### Q2: 报错 "Unsupported class file major version" 或 JDK 版本不符？
**A**: Studio 使用的 JDK 与 Gradle 期望的 JDK 不一致。在 `Settings → Build Tools → Gradle → Gradle JDK` 中选择内置的 JBR 17/21。

### Q3: 模拟器启动报 "HAXM/WHPX not installed"？
**A**: 硬件加速未启用。Windows 需在"启用或关闭 Windows 功能"中开启 Hyper-V 或虚拟机平台；Linux 需安装 KVM（`sudo apt install qemu-kvm` 并把用户加入 `kvm` 组）。

### Q4: 磁盘空间不足？
**A**: SDK + 模拟器镜像轻松占用 20GB+。删除未使用的系统镜像（SDK Manager）与旧版 Build-Tools 可释放大量空间。

---

## 🎯 练习与实践

### 基础练习
- [ ] 安装完成 Android Studio 并能打开欢迎窗口
- [ ] 记录你的 SDK 路径，并设置 `ANDROID_HOME` 环境变量
- [ ] 创建一台 Pixel 系列模拟器并成功启动到桌面
- [ ] 在终端运行 `adb devices`，看到模拟器处于 `device` 状态

### 进阶挑战
- [ ] 安装 cmdline-tools，用 `sdkmanager` 命令行安装一个额外的系统镜像
- [ ] 把模拟器语言切换为英文，熟悉开发者设置（如显示布局边界）
- [ ] 连接一台物理设备，观察 `adb devices` 中设备状态从 `unauthorized` 变为 `device` 的授权流程

---

## 🔗 相关文档

- 📄 **[第一个 Compose 应用](./02-first-compose-app.md)** - 环境就绪后，创建并运行你的第一个 Compose 项目
- 📄 **[第一个项目：笔记应用](./08-first-project.md)** - 综合运用本模块基础知识的实战项目
- 📖 **[Android Studio 下载页](https://developer.android.com/studio)** - 官方安装指南与系统要求
- 📖 **[Manage AVDs](https://developer.android.com/studio/run/managing-avds)** - 模拟器官方文档
