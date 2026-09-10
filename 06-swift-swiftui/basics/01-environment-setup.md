# 环境搭建 - Xcode 与 Swift 工具链

> **文档简介**: 搭建完整的 iOS 原生开发环境：安装 Xcode、配置 Swift 工具链、熟悉模拟器，并了解开发者账号体系
>
> **目标读者**: 有其他语言基础、首次接触 macOS/iOS 开发的学习者
>
> **前置知识**: 一台运行 macOS 的 Mac 电脑；了解基本编程概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Xcode` `#环境搭建` `#模拟器` `#开发者账号` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 安装并配置 Xcode 与 Command Line Tools
- ✅ 创建第一个 Xcode 项目并区分常见项目模板
- ✅ 使用 iOS 模拟器运行应用
- ✅ 理解开发者账号类型与签名机制的基本概念

## 🛠️ 第一步：安装 Xcode

### 1.1 检查系统要求

开发 iOS 18+ 应用需要：

- **macOS 版本**：Xcode 16.x 要求 macOS Sonoma 14.5 或更高（Xcode 26 要求 macOS Sequoia）
- **磁盘空间**：Xcode 本体约 12 GB，加上模拟器与组件缓存，建议预留 40 GB
- **Apple ID**：免费账号即可开发与真机调试，付费账号才能上架 App Store

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
swift --version   # 应输出 Apple Swift version 6.x
```

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

1. Xcode 左上角选择运行目标，如 **iPhone 16 Pro**
2. 按 `⌘R` 编译并运行
3. 首次启动模拟器较慢，属正常现象

### 3.2 常用模拟器技巧

```bash
# 命令行列出所有可用设备
xcrun simctl list devices available

# 截图模拟器屏幕
xcrun simctl io booted screenshot ~/Desktop/shot.png

# 清除某个模拟器的所有数据
xcrun simctl erase "iPhone 16 Pro"
```

模拟器窗口内的常用快捷键：

- `⌘S`：截屏（保存到桌面）
- `⌘⇧H`：模拟 Home 键
- `⌘R`（模拟器内）：屏幕旋转
- 菜单 **Device > Erase All Content and Settings**：恢复出厂状态

### 3.3 真机调试

模拟器无法覆盖摄像头、推送、传感器等硬件能力，真机调试步骤：

1. 用数据线连接 iPhone
2. iPhone 上信任该电脑
3. Xcode 中 **Settings > Accounts** 添加 Apple ID
4. 选择你的 iPhone 作为运行目标，`⌘R` 运行
5. 首次真机运行需在 iPhone **设置 > 通用 > VPN与设备管理** 中信任开发者证书

## 👤 第四步：理解开发者账号

| 账号类型 | 费用 | 能力 |
|----------|------|------|
| 免费（个人 Apple ID） | 0 | 模拟器开发 + 真机调试（签名 7 天过期，最多 3 台设备） |
| Apple Developer Program | $99/年 | 上架 App Store、TestFlight 分发、推送、CloudKit 高级能力 |
| Apple Developer Enterprise Program | $299/年 | 企业内部分发（不可上架） |

学习阶段使用免费账号完全够用；等到准备发布第一个项目（见 [08-first-project.md](./08-first-project.md)）再考虑付费账号。

> ⚠️ 免费账号的签名 7 天过期后应用会无法启动，重新运行一次即可续签。这是"为什么我的 App 突然打不开了"的高频问题。

## ✅ 最佳实践

- ✅ **推荐**：从 App Store 安装 Xcode，自动更新；从 developer.apple.com 下载的 .xip 适合锁定特定版本
- ✅ **推荐**：为每个项目使用独立的 Organization Identifier，避免后续 Bundle ID 冲突
- ✅ **推荐**：熟悉 `xcrun simctl`，它在 CI 与脚本化场景中不可替代
- ❌ **避免**：同时安装多个 Xcode 版本却不了解 `xcode-select` 切换机制
- ❌ **避免**：在学习初期就购买付费账号——模拟器 + 免费真机调试足以覆盖全部入门内容

## ❓ 常见问题

### Q1: `swift --version` 报错 "command not found"？

Command Line Tools 未安装或未指向 Xcode。执行 `xcode-select --install`，或检查 `xcode-select -p` 的输出路径是否正确。

### Q2: 真机运行报 "Signing certificate is invalid"？

在 Xcode **Settings > Accounts** 中选中账号点击 "Download Manual Profiles"，或删除钥匙串中的旧证书后重新运行项目让 Xcode 自动重建签名。

### Q3: 模拟器黑屏或卡死？

菜单 **Device > Restart** 重启模拟器；仍无效时执行 `xcrun simctl shutdown all` 后重新运行，或直接 Erase 设备数据。

## 🎯 练习与实践

### 练习一：基础练习

- [ ] 安装 Xcode 并确认 `swift --version` 输出 6.x 版本号
- [ ] 创建名为 `SwiftNotes` 的 SwiftUI 项目并成功运行在 iPhone 16 Pro 模拟器上
- [ ] 用 `xcrun simctl` 命令行截取一张模拟器屏幕截图

### 进阶挑战

- [ ] 连接真机并将项目运行在自己的 iPhone 上
- [ ] 在模拟器中打开深色模式（`⌘⇧A`），观察界面变化

---

## 相关文档

- 📄 [02-first-swiftui-app.md](./02-first-swiftui-app.md) — 在此环境上写下第一个 SwiftUI App
- 📄 [参考：Swift+SwiftUI 速查](../reference/quick-references/01-swift-swiftui-cheatsheet.md) — 常用命令与代码片段速查
- 📄 [参考：故障排除](../reference/quick-references/02-troubleshooting.md) — 签名、模拟器等环境问题汇总
