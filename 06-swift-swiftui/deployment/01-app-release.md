# 应用发布任务指南 — 签名、Archive 与 TestFlight

> **文档简介**: 从"本机能跑"到"别人能装"：理解苹果签名体系，完成 Archive 构建、分发到 TestFlight 让真实用户先行验证
>
> **目标读者**: 应用已通过本地验收、准备首次分发给测试者的学习者
>
> **前置知识**: [projects/04-production-ios-app.md](../projects/04-production-ios-app.md)（生产化改造完成）、有效的 Apple Developer 账号

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#代码签名` `#Archive` `#TestFlight` `#Profile` `#分发` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 本指南解决什么问题

签名是 iOS 发布的第一道墙：为什么真机调试要证书、上传要 Profile、装到别人手机还要重新签？先建立概念图，再按步骤操作，最后用 TestFlight 完成分发。

## 🔍 概念速览：签名三件套

| 概念 | 一句话解释 | 存放位置 |
|------|-----------|---------|
| 证书（Certificate） | 证明"你是注册开发者"的身份文件 | 钥匙串 + 开发者门户 |
| App ID | 应用的唯一身份证（Bundle ID） | 开发者门户 |
| 描述文件（Profile） | 证书 × App ID × 设备的"授权组合单" | Xcode 自动管理 |

**默认策略**：勾选 Xcode 的 **Automatically manage signing**，让 Xcode 代管以上三件；只有企业分发、手动续期等特殊场景才手动管理。

## 🛠️ 任务一：配置签名与版本号

1. Target → **Signing & Capabilities**：勾选 Automatically manage signing，选择 Team
2. 核对 `Bundle Identifier` 全局唯一（如 `com.yourname.habittracker`）
3. General → **Identity**：设置 `Version`（面向用户，如 1.0.0）与 `Build`（内部递增，如 3）
4. 需要系统能力（定位、推送）时在同一页添加 **Capabilities**，勿手改 entitlements 文件

**版本规则**：每次上传 App Store Connect，`Version+Build` 组合必须全新；只改代码不改 Build 号，上传会被拒。

## 🛠️ 任务二：Archive 构建

```text
1. 目标设备选 "Any iOS Device (arm64)"      ← 模拟器不能 Archive
2. Scheme 设为 Release                       ← Product → Scheme → Edit Scheme
3. Product → Archive                          ← 等待归档完成
4. Window → Organizer 查看产物
```

**Release 构建自检**（在 Archive 前跑一遍）：

- [ ] `#if DEBUG` 区块外的调试代码已清理
- [ ] 图标（1024×1024 App Store 图标）与启动画面齐备
- [ ] `Info.plist` 权限描述文案完整（用户看得懂的中文说明）
- [ ] 版本号递增、构建号递增

Archive 失败排查：签名冲突看 Organizer 报错详情；符号缺失多为 Bitcode/最低部署版本设置问题，见 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md)。

## 🛠️ 任务三：上传到 App Store Connect

Organizer → 选择归档 → **Distribute App**：

| 分发方式 | 用途 | 本文选择 |
|----------|------|---------|
| App Store Connect | 走 TestFlight / 商店上架 | ✅ 选这个 |
| TestFlight (Internal Only) | 快速内测 | 备选 |
| Ad Hoc | 指定设备名单分发 | 特殊场景 |
| Enterprise | 企业内部分发 | 需企业账号 |

选 **App Store Connect → Upload**，Xcode 完成签名打包并上传。上传成功后在 App Store Connect 的 TestFlight 页签可见处理中的构建（处理约 5-30 分钟）。

## 🛠️ 任务四：TestFlight 分发

### 内部测试（Internal，最多 100 人）

1. App Store Connect → 你的 App → **TestFlight** → 内部测试
2. 添加内部测试员（需是 App Store Connect 用户）
3. 测试员在 TestFlight App 中即可安装

### 外部测试（External，最多 10,000 人）

1. 创建外部测试组，添加测试员邮箱或公开邀请链接
2. **首次外部分发需要苹果 Beta 审核**（通常 1-2 天，比正式审核宽松）
3. 审核通过后，分享链接即可大规模收集反馈

### 收集反馈

- 测试员的**截图批注**自动回传 TestFlight 后台
- 崩溃报告在 TestFlight → 崩溃部分可见，符号化后可定位到代码行
- 崩溃与指标的自动化收集方案见 [03-ci-cd-observability.md](./03-ci-cd-observability.md)

## ✅ 最佳实践

将构建编号、源码提交、签名配置和产物关联保存，自动递增工具帮助避免重复编号，但要确认多个发布分支不会冲突。用可安装的 Release 产物走通核心流程，因为调试成功不能覆盖签名和优化构建差异。

测试组与分发链接按访问范围管理，明确测试数据环境和反馈渠道。先验证一名新测试者能安装并完成任务，再扩大发放范围。

## ❌ 避免陷阱

- ❌ 手动管理签名还同时开着自动管理——冲突后先全部清掉重新来
- ❌ 在 `Info.plist` 写英文模板权限描述——审核会以"说明不充分"拒掉
- ❌ 上传后才想起加权限描述——上传即固化，改文案要重新上传递增 Build

## ❓ 常见问题

**Q1: "No profiles for bundle ID were found"？** Xcode → Settings → Accounts → Download Manual Profiles，或关掉自动管理再开一次强制刷新。

**Q2: 上传后构建卡在 Processing？** 超过 1 小时看开发者门户邮箱，常见原因是缺失图标或 Info.plist 键缺失，处理失败会有邮件说明。

**Q3: 测试员说装不上？** 确认其用的是 TestFlight App 且系统版本 ≥ 最低部署版本；外部测试需审核通过后链接才生效。

## 🎯 练习

- [ ] 完成一次 Archive + 上传，把构建分发给自己的内部测试组
- [ ] 故意不写定位权限描述上传，观察处理结果并复盘（用测试 App）
- [ ] 写一个 Build 号自动递增的脚本（读现有最大值 +1 写回）

## 相关文档

- 📄 [02-app-store-release.md](./02-app-store-release.md) — 下一篇：App Store 正式上架流程
- 📄 [04-devtools.md](../frameworks/04-devtools.md) — Xcode 工具链（Organizer 与构建产物）
- 📄 [04-production-ios-app.md](../projects/04-production-ios-app.md) — 发布前的生产化检查清单
- 📄 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md) — 签名与上传报错速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
