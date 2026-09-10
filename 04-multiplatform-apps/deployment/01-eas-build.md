# EAS Build — 云端构建流程

> **文档简介**: 用 EAS Build 告别本地配环境：构建 profile 设计、凭据托管、环境变量注入与构建变体产出，打通从源码到可分发安装包的标准链路
>
> **目标读者**: 需要产出可安装/可上架包（ipa/aab）并希望构建流程可复现的开发者
>
> **前置知识**: 已完成 [环境搭建](../basics/01-environment-setup.md)；已了解 Expo 生态（见 [生态集成](../frameworks/03-ecosystem-integration.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（deployment） |
| **难度** | ⭐⭐ |
| **标签** | `#EAS` `#构建` `#签名` `#环境变量` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 初始化 EAS 并设计 development/preview/production 三套 profile
- ✅ 理解凭据托管（keystore 与证书）的原理与恢复方式
- ✅ 用 EAS 环境变量区分 dev/staging/prod 配置
- ✅ 产出对应安装物：开发用 dev client、内测用 apk、上架用 aab/ipa

## 🚀 初始化

```bash
npm install -g eas-cli
eas login
eas build:configure   # 生成 eas.json，并把 projectId 写入 app.json
```

## 📋 eas.json：三套 profile

```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "development": {
      "developmentClient": true,       // 产出 dev client：连 Metro 热更新
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "preview": {
      "distribution": "internal",      // 内测包：完整 release 行为 + 可直装
      "android": { "buildType": "apk" },
      "env": { "EXPO_PUBLIC_API_URL": "https://staging.example.com" }  // 合成示例域名
    },
    "production": {
      "autoIncrement": true,           // versionCode/buildNumber 自动递增
      "android": { "buildType": "app-bundle" },  // 上架 Google Play 必须 aab
      "env": { "EXPO_PUBLIC_API_URL": "https://api.example.com" }
    }
  },
  "submit": { "production": {} }
}
```

```bash
# 常用构建命令
eas build --profile development --platform android   # 日常联调包
eas build --profile preview --platform all           # 内测双端包
eas build --profile production --platform ios        # 上架包
eas build:list                                       # 查看历史构建
```

## 🔐 凭据托管

| 凭据 | Android | iOS |
|------|---------|-----|
| 签名材料 | upload keystore | 分发证书 + provisioning profile |
| 托管方式 | `eas credentials` 管理，云端加密保存 | 同左；可在 App Store Connect 自动生成 |
| 本地恢复 | `eas credentials` → 同步到本地 | 同左 |

**实践要点**：
- 首次构建选 "Generate new keystore"，EAS 生成并托管；**务必备份**（`eas credentials` 可导出）
- 已有旧项目可用 `eas credentials` 上传现有 keystore，保证升级签名一致
- iOS 证书续期由 EAS 自动处理，手动模式仅特殊团队流程需要

## 🌍 环境变量体系

```bash
# 服务端定义（不入库，安全性最高，推荐）
eas env:create --name EXPO_PUBLIC_API_URL --value https://api.example.com --environment production
```

```ts
// 客户端读取：EXPO_PUBLIC_ 前缀的变量会被内联进 JS 包
export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:3000';
```

**安全红线**：所有 `EXPO_PUBLIC_` 变量都会打包进客户端、可被逆向读取——秘密（密钥/证书/token 类）一律放服务端或 EAS 服务端变量，见 [安全实践](../advanced-topics/security/01-security-practices.md)。

## ⚙️ 构建排错速查

| 症状 | 原因与处理 |
|------|-----------|
| 依赖冲突构建失败 | 本地先 `npx expo-doctor` 预检；坚持用 `expo install` 锁版本 |
| iOS 构建卡在 pod install | 检查自定义 pod 是否指定了不兼容架构 |
| 超出免费并发 | 队列等待属正常；团队可升级 plan |
| 构建缓存失效 | `eas.json` 的 `cache.key` 配合 lock 文件 hash |

更多环境问题见 [故障排除](../reference/quick-references/02-troubleshooting.md)。

## ✅ 最佳实践

- ✅ **三 profile 铁律**：development 连 Metro、preview 装真机、production 走商店，禁止混用
- ✅ **`appVersionSource: "remote"`**，让 EAS 管版本号，配合 `autoIncrement` 杜绝手改遗漏
- ✅ **把 `eas build` 接进 CI**，构建产物链接自动回帖到 PR
- ❌ **不要把 keystore 提交进 git**，用 EAS 托管或本地安全存储
- ❌ **不要在 preview profile 里放生产密钥**，内测包也会落到测试者设备

## ❓ 常见问题

**Q1: 没有付费 Apple 开发者账号能构建 iOS 吗？**
A: 能出模拟器构建（`ios.simulator: true`）；真机分发与上架需要付费账号（$99/年）。

**Q2: 本地构建和 EAS 构建产物有差异吗？**
A: EAS 是受控的标准环境，可复现性更好；本地构建需自备 macOS/Xcode 且易受本地缓存影响。调试技巧见 [开发工具链](../frameworks/04-devtools.md)。

**Q3: monorepo 怎么配？**
A: `eas.json` 顶层加 `monorepo: true`，并在 package.json 指定 `projectRoot`；pnpm workspace 注意 lock 文件路径。

---

## 🔗 相关文档

- 📖 [Expo 要点 — Router、EAS 与 expo-modules](../reference/framework-essentials/01-expo-essentials.md) — EAS 机制速查
- 📖 [CLI 命令与调试速查表](../reference/quick-references/01-cli-and-debug-cheatsheet.md) — eas-cli 命令全集
- 📄 [环境搭建](../basics/01-environment-setup.md) — 本地工具链（EAS 的对照组）
- 🚀 [商店上架](./02-app-store-release.md) — 构建产物的下一步去向
- 🚀 [OTA 更新与可观测性](./03-ota-updates-observability.md) — 与构建互补的热更新通道
- 🚀 [生产级移动应用](../projects/04-production-mobile-app.md) — 构建纳入发布闭环的完整视图
