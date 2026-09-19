# 环境搭建 - Xcode 与 Swift 工具链

## 先理解，再动手

Xcode 包含平台 SDK、编译与签名工具。模拟器运行、真机签名和商店发布是不同阶段。

**本节自测**：创建 SwiftUI 模板，选定模拟器运行并修改首页文本。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

记录运行目标和系统版本；通过构建不代表签名与真机发布都已完成。

</details>

> **文档简介**: 搭建完整的 iOS 原生开发环境：安装 Xcode、配置 Swift 工具链、熟悉模拟器，并了解开发者账号体系
>
> **目标读者**: 有其他语言基础、首次接触 macOS/iOS 开发的学习者
>
> **前置知识**: 一台运行 macOS 的 Mac 电脑；了解基本编程概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Xcode` `#环境搭建` `#模拟器` `#开发者账号` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 安装并配置 Xcode 与 Command Line Tools
- ✅ 创建第一个 Xcode 项目并区分常见项目模板
- ✅ 使用 iOS 模拟器运行应用
- ✅ 理解开发者账号类型与签名机制的基本概念

## 🛠️ 第一步：安装 Xcode

### 1.1 检查系统要求

开发 iOS 应用前，先在 [Apple 的 Xcode 系统要求](https://developer.apple.com/xcode/system-requirements)中核对当前 Xcode 与 macOS 的组合；课程不以一个未锁定的小版本作为永远正确的基线。写作时的 Xcode 26.2 需要 macOS Sequoia 15.6 或更高，并包含 Swift 6.2.3；你的工程应记录实际 Xcode、SDK、Swift language mode 与 deployment target。

- **磁盘空间**：Xcode、平台组件、模拟器与派生数据会持续增长。安装前查看磁盘余量；为首次安装与一个模拟器保留足够空间，遇到下载失败先检查空间而不是反复重装。
- **Apple Account / Team**：模拟器不需要签名。要在个人设备安装应用，在 Xcode 的 Apple Accounts 登录 Apple Account，并在 Signing & Capabilities 中选择 Personal Team 或已加入的开发团队。App Store、TestFlight、受限能力和分发需要相应的 Apple Developer Program 资格。

### 1.2 通过 App Store 安装（推荐）

1. 打开 **App Store**，搜索 "Xcode"
2. 点击"获取"并等待下载完成（体积大，建议有线网络）
3. 首次启动 Xcode 时会提示安装附加组件，输入管理员密码确认

### 1.3 安装 Command Line Tools

即使不写命令行程序，很多工具（git、swiftc、simctl）也依赖它：

```bash
# 方式一：独立安装
xcode-select --install

# 方式二：Xcode 已装好后直接切换路径
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer

# 验证安装
xcode-select -p
swift --version   # 记录输出；它应与当前 xcode-select 指向的开发者目录一致
```

> 💡 如果只做命令行/服务端开发，或需要在多个 Swift 版本之间切换，可以用 swiftly 独立管理 Swift 工具链（见 swift.org/install）。iOS 开发仍以 Xcode 内置工具链为主。

## 🚀 第二步：创建第一个项目

### 2.1 选择模板

启动 Xcode → **File > New > Project**（快捷键 `⇧⌘N`）→ 选择 **iOS > App**：

| 选项 | 推荐值 | 说明 |
|------|--------|------|
| Product Name | `SwiftNotes` | 应用名 |
| Team | 你的 Apple ID | 真机调试需要 |
| Organization Identifier | `com.yourname` | 反向域名格式 |
| Interface | **SwiftUI** | 本模块全程使用 SwiftUI |
| Language | **Swift** | Swift 6.x |
| Storage | **None**（或 Swift） | 后续项目会选 SwiftData |

> 💡 Interface 一定选 SwiftUI。选择 Storyboard 的模板属于旧式 UIKit 工作流，与本模块学习路径不符。

### 2.2 认识项目结构

```
SwiftNotes/
├── SwiftNotesApp.swift      # App 入口（@main）
├── ContentView.swift        # 默认根视图
├── Assets.xcassets          # 图片、颜色、App 图标资源
└── SwiftNotes.entitlements  # 能力声明文件（按需生成）
SwiftNotes.xcodeproj         # 项目配置文件（Targets、签名、构建设置）
```

## 📱 第三步：使用模拟器

### 3.1 运行应用

1. Xcode 左上角先选择当前 scheme，再选一个已安装、且系统版本不低于项目 deployment target 的模拟器；不要把某个手机型号名称当作必然存在。
2. 按 `⌘R` 编译并运行，并在活动区记录 Build succeeded 或首个错误。
3. 首次启动模拟器较慢，属正常现象

### 3.2 常用模拟器技巧

```bash
# 命令行列出所有可用设备
xcrun simctl list devices available

# 截图模拟器屏幕
xcrun simctl io booted screenshot ~/Desktop/shot.png

# 清除某个模拟器的所有数据
xcrun simctl erase "iPhone 17 Pro"
```

模拟器窗口内的常用快捷键：

- `⌘S`：截屏（保存到桌面）
- `⌘⇧H`：模拟 Home 键
- `⌘R`（模拟器内）：屏幕旋转
- 菜单 **Device > Erase All Content and Settings**：恢复出厂状态

### 3.3 真机调试

模拟器能验证基础 UI、导航与很多系统行为，但不能完整复制真实设备的性能和硬件能力。摄像头、推送、传感器、后台限制、发布构建等需要真机或相应服务验收。真机调试步骤：

1. 用数据线连接 iPhone
2. iPhone 上信任该电脑
3. Xcode 中 **Settings > Accounts** 添加 Apple ID
4. 选择你的 iPhone 作为运行目标，`⌘R` 运行
5. 保持 Xcode 的 **Automatically manage signing** 开启；Xcode 会注册设备并创建开发 provisioning profile。若系统提示，按设备上的开发者模式或信任流程完成授权；界面路径会随 iOS 版本变化，以设备提示为准。

## 👤 第四步：理解开发者账号

| 账号类型 | 费用 | 能力 |
|----------|------|------|
| Personal Team（免费 Apple Account） | 0 | 个人设备安装与调试；App ID、设备和已安装 App 均有小额度限制，provisioning profile 约 7 天后需重新构建/安装 |
| Apple Developer Program | 以所在地区当前价格为准 | App Store Connect、TestFlight、分发与更多服务；费用、可用能力和地区条件以 Apple 当前计划页为准 |
| Apple Developer Enterprise Program | 面向符合资格的组织 | 仅用于受控内部员工分发，不能替代 App Store 发布 |

学习阶段使用免费账号完全够用；等到准备发布第一个项目（见 [08-first-project.md](./08-first-project.md)）再考虑付费账号。

> ⚠️ 免费账号的签名 7 天过期后应用会无法启动，重新运行一次即可续签。这是"为什么我的 App 突然打不开了"的高频问题。

## ✅ 最佳实践

先确认项目实际使用哪个 Xcode 和命令行工具路径，再创建并运行一个最小应用；多版本并存时把所选版本记录在工程说明和 CI 中。自动更新方便个人试学，团队复现构建则需要明确升级时机。

Organization Identifier 可以由多个项目共用，完整 Bundle Identifier 才用于区分应用。模拟器足以开始界面学习，真机和开发者计划需求由具体能力与分发方式决定，不预先承诺免费配置能覆盖所有功能。

## ❓ 常见问题

### Q1: `swift --version` 报错 "command not found"？

Command Line Tools 未安装或未指向 Xcode。执行 `xcode-select --install`，或检查 `xcode-select -p` 的输出路径是否正确。

### Q2: 真机运行报 "Signing certificate is invalid"？

在 Xcode **Settings > Accounts** 中选中账号点击 "Download Manual Profiles"，或删除钥匙串中的旧证书后重新运行项目让 Xcode 自动重建签名。

### Q3: 模拟器黑屏或卡死？

菜单 **Device > Restart** 重启模拟器；仍无效时执行 `xcrun simctl shutdown all` 后重新运行，或直接 Erase 设备数据。

## 🎯 练习与实践

### 练习一：基础练习

- [ ] 安装 Xcode，记录 `xcodebuild -version`、`xcode-select -p` 与 `swift --version`
- [ ] 创建名为 `SwiftNotes` 的 SwiftUI 项目，选择已安装且满足 deployment target 的模拟器，构建并运行模板页
- [ ] 修改首页文本，停止后再次运行，确认正在运行的是刚修改的 target
- [ ] 用 `xcrun simctl` 截取 booted 模拟器屏幕截图；若没有 booted 设备，先记录“未验证”而不是伪造成功

### 进阶挑战

- [ ] 连接真机并将项目运行在自己的 iPhone 上
- [ ] 在模拟器中打开深色模式（`⌘⇧A`），观察界面变化

---

## 相关文档

- 📄 [02-first-swiftui-app.md](./02-first-swiftui-app.md) — 在此环境上写下第一个 SwiftUI App
- 📄 [参考：Swift+SwiftUI 速查](../reference/quick-references/01-swift-swiftui-cheatsheet.md) — 常用命令与代码片段速查
- 📄 [参考：故障排除](../reference/quick-references/02-troubleshooting.md) — 签名、模拟器等环境问题汇总


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
