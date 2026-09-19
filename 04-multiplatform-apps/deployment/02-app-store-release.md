# 商店上架 — App Store 与 Google Play

> **文档简介**: 从构建产物到商店可售：TestFlight 与 Play 内测轨道的灰度策略、商店素材规范、审核避坑清单与正式发布流程
>
> **目标读者**: 已能用 EAS 产出构建包、准备完成首次上架或优化上架流程的开发者
>
> **前置知识**: 已完成 [EAS Build 构建流程](./01-eas-build.md)；有可用的开发者账号（Apple $99/年，Google 一次性 $25）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（deployment） |
| **难度** | ⭐⭐ |
| **标签** | `#AppStore` `#GooglePlay` `#上架` `#审核` `#灰度` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 学习目标

- ✅ 用 EAS Submit 自动提交构建到两大商店
- ✅ 设计 TestFlight / Play 测试轨道的灰度发布节奏
- ✅ 准备齐全的商店素材与隐私声明
- ✅ 掌握两大平台高频拒审原因与应对

## 📤 EAS Submit：一条命令提交

```bash
eas submit --platform ios --latest      # 上传最近一次构建到 App Store Connect
eas submit --platform android --latest  # 上传到 Play Console
```

首次运行会引导授权（App Store Connect API Key / Google 服务账号）；也可在 `eas.json` 的 `submit` 段配置实现 CI 全自动。

## 🍎 App Store 发布流程

### 1. TestFlight 内测

1. `eas submit` 后构建自动出现在 App Store Connect → TestFlight
2. 内部测试：邀请团队成员，即时生效（无审核）
3. 外部测试：最多 1 万人，需一次轻量 Beta 审核
4. 收集反馈后修复 → 重新 `eas build` + `eas submit`

### 2. 正式提审

在 App Store Connect 完成：

| 项目 | 要求 |
|------|------|
| 截图 | 6.9" 与 6.5" 两档必交，可用 Fastlane frameit 或第三方截图服务制作 |
| 隐私标签 | 数据收集问卷必须与实际一致，撒谎是下架级违规 |
| 权限文案 | Info.plist 用途字符串（Expo 走 app.json plugins）缺一不可 |
| 审核备注 | 有登录的后台测试账号必须提供，写在 App Review Information |

### 3. 高频拒审与应对

- **崩溃/首帧白屏**：审核用全新设备/系统版本，先在 TestFlight 真机全流程自测
- **权限说明不清**：定位/相机等文案写明"做什么"，不要写"用于改进服务"这类空话
- **诱导评分/隐藏功能**：热更新不得改变 App 审核时的核心行为（见 [OTA 更新](./03-ota-updates-observability.md)）
- **账号体系**：接了第三方登录就必须支持 Sign in with Apple

## 🤖 Google Play 发布流程

### 1. 测试轨道（由内到外）

```
内部测试（最多100人，即时）→ 封闭测试（邮件列表/社区，需审核）→ 开放测试 → 正式
```

新个人开发者账号需先完成 **12 名测试员封闭测试 14 天** 的政策要求才能申请正式发布，规划排期时要预留。

### 2. 正式发布要点

| 项目 | 要求 |
|------|------|
| 产物 | AAB 格式（EAS `buildType: app-bundle` 已产出），Play 侧动态分发 |
| 签名 | 启用 Play App Signing，upload keystore 由 EAS 托管 |
| 数据安全表单 | 与隐私政策一致，跨端声明要同步 |
| 内容分级问卷 | 如实填写，影响商店展示与地区可用性 |
| 目标受众 | 含儿童内容会触发额外家庭政策审核 |

### 3. 分阶段发布

Play Console 支持**按用户百分比放量**（1% → 10% → 50% → 100%），配合 Play Vitals 监控崩溃率随时暂停——这是 Android 端最重要的灰度手段。

## 📅 版本节奏建议

1. 双周一个版本窗口，冻结代码后只修 blocker
2. 版本号：`app.json` 的 `version` 给用户看，`versionCode`/`buildNumber` 交给 EAS `autoIncrement`
3. iOS 审核通常 24-48h，Android 新版数小时——**先发 Android 验证，再提 iOS**
4. 每个版本发布后 72h 内盯崩溃看板（见 [OTA 与可观测性](./03-ota-updates-observability.md)）

## ✅ 提交前演练与通过条件

每次候选版本在提交前保留一份可复查的发布记录，而不是只勾选页面：

| 演练 | 操作 | 期望结果 | 失败后先查 |
|------|------|------|------|
| 产物对应性 | 记录 Git 提交、EAS build ID、iOS buildNumber / Android versionCode 与提交的商店构建 | 四个标识能一一对应；不能把“最新构建”当作可追溯版本 | `eas build:list`、商店构建详情与 CI 产物 |
| 冷启动核心旅程 | 用全新模拟器和至少一台真机安装候选包，从未登录状态完成核心路径 | 没有白屏、崩溃、无法返回的登录或权限死路；每个权限只在相应功能触发时请求 | 环境变量、深链、权限声明、首次启动数据迁移 |
| 登录审核路径 | 若产品需要账号，使用专用测试账号和准备好的测试数据完成审核说明中的步骤 | 两个平台的审核说明、账号状态和实际路径一致；账号不过期且不需要人工开通 | App Review Information / Play 测试说明、后端白名单与角色权限 |
| 隐私一致性 | 逐项比对隐私表单、权限文案、网络抓包和本次新增 SDK | 声明与真实数据流一致；未声明的新上报或标识符即阻止提交 | SDK 更新记录、分析初始化、权限与隐私政策 |
| 灰度与回退 | 在内部／封闭轨道安装候选版本，准备暂停放量或回退到已知可用构建的步骤 | 能明确执行暂停或回退，且团队知道这不会撤销已经安装的客户端状态 | 商店发布状态、兼容性与服务端开关 |

将上述记录、截图和测试结论附在发布工单中。EAS Submit 命令成功只证明上传请求完成，不证明商店元数据、审核账号、隐私声明或真实设备体验已经通过。

## ✅ 最佳实践

提审前从未登录和全新安装状态走通核心旅程，再在内部测试渠道验证真机相关能力。把构建编号、源码提交、测试结果和提交记录关联起来，审核或崩溃问题才能定位到实际产物。

隐私说明应与权限、分析 SDK 和真实数据流一致，升级 SDK 后也要复核。审核时长和政策会变化，不用固定节假日经验作保证；OTA 可发布范围以平台规则及客户端兼容性为准，不能靠更新渠道绕开应有审核。

## ❓ 常见问题

**Q1: 鸿蒙端上架去哪里？**
A: 走华为 AppGallery，流程独立于 App Store/Play；RNOH 应用的适配与上架要点见 [RNOH 字典](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

**Q2: 被拒后怎么快速申诉？**
A: 在 Resolution Center 回复说明，附复现步骤与录屏；事实性误判申诉通过率不低，语气克制聚焦技术。

**Q3: 同一 App 能否双平台不同功能？**
A: 功能差异可以（平台特性），但付费解锁类必须用平台内购（iOS 3.1.1 条款），跨端充值"绕苹果"必被拒。

---

## 🔗 相关文档

- 📖 [故障排除](../reference/quick-references/02-troubleshooting.md) — 签名与白屏类上架杀手速查
- 📖 [原生与设备能力库指南](../reference/library-guides/02-native-and-device-libs.md) — 权限类能力与文案对照
- 📄 [EAS Build 构建流程](./01-eas-build.md) — 构建产物从哪来
- 🚀 [OTA 更新与可观测性](./03-ota-updates-observability.md) — 上架之后的更新与监控
- 🚀 [生产级移动应用](../projects/04-production-mobile-app.md) — 上架在完整发布闭环中的位置
- 📄 [RNOH 字典](../reference/language-concepts/05-harmonyos-rnoh-api.md) — 第三端华为市场发布参考


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
