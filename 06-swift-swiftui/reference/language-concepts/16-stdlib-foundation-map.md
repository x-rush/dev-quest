# stdlib / Foundation 与系统框架低频地图

> **文档简介**: Swift 标准库与 Apple 系统框架的"按用途找框架"地图：每项一句话职责 + 官方文档链接；高频核心（String/Date/Codable 等）不在本篇，见 library-guides
>
> **目标读者**: 遇到"这该用哪个系统框架"选择问题的全体学习者（字典条目，可任意跳入）
>
> **前置知识**: 无；高频 Foundation 已收于 [../library-guides/01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#地图` `#系统框架` `#Foundation` `#索引` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

本篇不展开 API，只回答"**这个用途该去哪个框架找**"：每项一行"一句话职责 + 官方文档链接"，需要细节时从链接进入官方文档。

---

## 1. 响应式：Combine 与它的边界

**[Combine](https://developer.apple.com/documentation/combine)** — 基于 Publisher/Subscriber 的响应式事件流框架。

**边界（SwiftUI 时代）**: UI 数据流主位已被 **Observation（`@Observable`）** 取代（对照表见 [04-swiftui-state-api.md §3](./04-swiftui-state-api.md)）；Combine 仍活跃于：旧代码维护（`ObservableObject`/`@Published`）、系统 publisher（如 `URLSession.dataTaskPublisher`、`NotificationCenter.publisher`）、声明式节流/合并操作符（`debounce`/`combineLatest`）。部署目标支持 Observation 时可优先考虑它；既有 Publisher 管线及旧系统支持仍可能需要 Combine。

## 2. 图形与渲染

| 框架 | 一句话职责 |
|------|-----------|
| [CoreGraphics](https://developer.apple.com/documentation/coregraphics) | 2D 绘制与基础几何类型（`CGPoint`/`CGSize`/`CGRect`/`CGPath`/`CGColor`）——SwiftUI 的 `Shape`/`Canvas` 坐标体系地基 |
| [CoreAnimation](https://developer.apple.com/documentation/quartzcore) | 图层树渲染与动画（`CALayer`）——SwiftUI/UIKit 界面的底层合成器 |
| [CoreImage](https://developer.apple.com/documentation/coreimage) | 图像处理滤镜管线（`CIFilter`，美颜/调色/风格化） |
| [Metal](https://developer.apple.com/documentation/metal) | 直接 GPU 编程（自定义渲染/计算管线，普通 app 很少直接用） |

## 3. 时间与通知

| API | 一句话职责 |
|-----|-----------|
| [Timer](https://developer.apple.com/documentation/foundation/timer) | RunLoop 驱动的重复定时器（**必须在有 RunLoop 的线程**）；并发时代一次性延迟首选 `Task.sleep(for:)` |
| [NotificationCenter](https://developer.apple.com/documentation/foundation/notificationcenter) | 进程内同步广播总线（`post`/`addObserver`）；配合 `.publisher(for:)`（Combine）或 async `notifications` 序列使用 |
| [Calendar](https://developer.apple.com/documentation/foundation/calendar) | 日期组件运算与历法（已收于 library-guides/01 §2） |

## 4. 系统能力框架

| 框架 | 一句话职责 | 代表 API |
|------|-----------|----------|
| [StoreKit 2](https://developer.apple.com/documentation/storekit) | 内购：商品、购买、订阅与交易收据 | `Product.products(for:)`、`Transaction.currentEntitlements`（iOS 15+） |
| [CloudKit](https://developer.apple.com/documentation/cloudkit) | 苹果云后端：结构化数据同步与订阅 | `CKContainer`、`NSPersistentCloudKitContainer`（Core Data 同步）；SwiftData 则通过自身 ModelConfiguration 配置 |
| [WidgetKit](https://developer.apple.com/documentation/widgetkit) | 桌面/锁屏小组件与时间线刷新 | `TimelineProvider`、`WidgetBundle`（iOS 14+） |
| [App Intents](https://developer.apple.com/documentation/appintents) | Siri/快捷指令/Spotlight 的可执行意图 | `AppIntent`、`AppShortcut`（iOS 16+） |
| [UserNotifications](https://developer.apple.com/documentation/usernotifications) | 本地与远程通知的调度与响应 | `UNUserNotificationCenter` |
| [CoreLocation](https://developer.apple.com/documentation/corelocation) | 定位、区域监听与地理编码 | `CLLocationManager`、`CLGeocoder` |
| [AVFoundation](https://developer.apple.com/documentation/avfoundation) | 音视频播放/录制/采集 | `AVPlayer`、`AVAudioSession` |
| [LocalAuthentication](https://developer.apple.com/documentation/localauthentication) | Face ID / Touch ID 生物认证 | `LAContext.evaluatePolicy` |
| [Security](https://developer.apple.com/documentation/security) | Keychain 安全存储与证书 | `SecItemAdd`、`SecItemCopyMatching` |
| [BackgroundTasks](https://developer.apple.com/documentation/backgroundtasks) | 后台刷新与处理任务调度 | `BGAppRefreshTask`（iOS 13+） |
| [ActivityKit](https://developer.apple.com/documentation/activitykit) | 实时活动（灵动岛/锁屏直播态） | `Activity.request`（iOS 16.1+） |
| [MapKit](https://developer.apple.com/documentation/mapkit) | 地图展示与地理数据 | SwiftUI `Map`（iOS 14+；iOS 17 起 MapContentBuilder 新 API 并弃用旧 init） |
| [os](https://developer.apple.com/documentation/os) | 结构化日志与性能标记 | `Logger`（iOS 14+）、`OSSignposter` |

## 5. 标准库与 Foundation 辅助工具

| API | 一句话职责 |
|-----|-----------|
| `CommandLine.arguments` | 读取命令行启动参数（CLI/调试入口） |
| `ProcessInfo.processInfo` | Foundation 的进程信息与环境变量（`environment`/`isiOSAppOnMac` 等运行判别） |
| `Mirror` | 运行时反射查看子结构（调试打印，勿用于业务逻辑） |
| `Result` | 成功/失败的显式包装值（错误处理见 [08-error-handling.md](./08-error-handling.md)） |

## ⚠️ 常见陷阱

- ❌ **新 SwiftUI 项目把模型层建在 Combine 上**：`ObservableObject` + `@Published` 与 Observation 双轨并存徒增心智负担
  ✅ 先核对最低系统版本，再决定是否采用 `@Observable`（对照迁移表见 [04-swiftui-state-api.md §3](./04-swiftui-state-api.md)）；只在节流/系统 publisher 场景借用 Combine。
- ❌ **用 `Timer` 做倒计时然后切后台失效**：Timer 依赖 RunLoop，后台被暂停
  ✅ 保存截止时刻，回到前台重新计算 Date 差值；Task.sleep 同样不能绕过系统挂起限制。
- ❌ **Keychain 当 UserDefaults 用**：Keychain 无同步读写的"属性"语义，且写入类型受限
  ✅ 敏感小数据（token/密码）走 Keychain（Security 框架），普通偏好设置走 `UserDefaults`/`@AppStorage`。

<!-- full-library-explanation -->
## 怎样用这张地图完成一个功能

以“到时提醒”为例：Date 保存截止时刻，Calendar 处理用户的时区与历法，前台 UI 根据当前时刻重新计算差值，UserNotifications 请求授权后提交通知。Timer 或 Task.sleep 只能协助前台刷新，不能保证应用挂起时仍执行。通知被拒绝时仍保留任务本身，并明确显示“尚未开启提醒”。

系统能力的选型要回答三件事：最低系统版本是否支持；是否需要权限、entitlement 或设备能力；失败时如何降级。例如 LocalAuthentication 验证的是本机用户，不自动登录远端账号；CloudKit 同步不是对所有服务器的通用数据库客户端；BackgroundTasks 由系统决定调度时机，不能充当每分钟准时运行的 cron。

练习：给笔记应用添加提醒，写下允许通知、拒绝通知、跨时区、退出再启动四种结果。验收不以“调用 API 未报错”为准，而以任务仍可查看、截止时刻正确、权限状态可理解为准。随后用 Logger 记录操作类型与错误类别，避免记录笔记正文、token 和定位精确坐标。

## 🔗 相关条目

- 📄 **[01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md)** - 高频 Foundation 核心（String/Date/Codable）
- 📄 **[02-third-party-libs.md](../library-guides/02-third-party-libs.md)** - 第三方库选型与边界
- 📄 **[14-regex.md](./14-regex.md)** - 原生正则（文本处理深潜）
- 📄 **[04-swiftui-state-api.md](./04-swiftui-state-api.md)** - Observation 与 Combine 的取舍对照

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
