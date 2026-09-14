# stdlib / Foundation 与系统框架低频地图

> **文档简介**: Swift 标准库与 Apple 系统框架的"按用途找框架"地图：每项一句话职责 + 官方文档链接；高频核心（String/Date/Codable 等）不在本篇，见 library-guides
>
> **目标读者**: 遇到"这该用哪个系统框架"选择问题的全体学习者（字典条目，可任意跳入）
>
> **前置知识**: 无；高频 Foundation 已收于 [../library-guides/01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#地图` `#系统框架` `#Foundation` `#索引` |
| **更新日期** | `2026年9月` |

## 📌 定义

本篇不展开 API，只回答"**这个用途该去哪个框架找**"：每项一行"一句话职责 + 官方文档链接"，需要细节时从链接进入官方文档。

---

## 1. 响应式：Combine 与它的边界

**[Combine](https://developer.apple.com/documentation/combine)** — 基于 Publisher/Subscriber 的响应式事件流框架。

**边界（SwiftUI 时代）**: UI 数据流主位已被 **Observation（`@Observable`）** 取代（对照表见 [04-swiftui-state-api.md §3](./04-swiftui-state-api.md)）；Combine 仍活跃于：旧代码维护（`ObservableObject`/`@Published`）、系统 publisher（如 `URLSession.dataTaskPublisher`、`NotificationCenter.publisher`）、声明式节流/合并操作符（`debounce`/`combineLatest`）。新 SwiftUI 项目默认不引入 Combine 模型层。

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
| [CloudKit](https://developer.apple.com/documentation/cloudkit) | 苹果云后端：结构化数据同步与订阅 | `CKContainer`、`NSPersistentCloudKitContainer`（Core Data/SwiftData 云同步入口） |
| [WidgetKit](https://developer.apple.com/documentation/widgetkit) | 桌面/锁屏小组件与时间线刷新 | `TimelineProvider`、`WidgetBundle`（iOS 14+） |
| [App Intents](https://developer.apple.com/documentation/appintents) | Siri/快捷指令/Spotlight 的可执行意图 | `AppIntent`、`AppShortcut`（iOS 16+） |
| [UserNotifications](https://developer.apple.com/documentation/usernotifications) | 本地与远程通知的调度与响应 | `UNUserNotificationCenter` |
| [CoreLocation](https://developer.apple.com/documentation/corelocation) | 定位、区域监听与地理编码 | `CLLocationManager`、`CLGeocoder` |
| [AVFoundation](https://developer.apple.com/documentation/avfoundation) | 音视频播放/录制/采集 | `AVPlayer`、`AVAudioSession` |
| [LocalAuthentication](https://developer.apple.com/documentation/localauthentication) | Face ID / Touch ID 生物认证 | `LAContext.evaluatePolicy` |
| [Security](https://developer.apple.com/documentation/security) | Keychain 安全存储与证书 | `SecItemAdd`、`SecItemCopyMatching` |
| [BackgroundTasks](https://developer.apple.com/documentation/backgroundtasks) | 后台刷新与处理任务调度 | `BGAppRefreshTask`（iOS 13+） |
| [ActivityKit](https://developer.apple.com/documentation/activitykit) | 实时活动（灵动岛/锁屏直播态） | `Activity.request`（iOS 16.1+） |
| [MapKit](https://developer.apple.com/documentation/mapkit) | 地图展示与地理数据 | SwiftUI `Map`（iOS 17 新 API） |
| [os](https://developer.apple.com/documentation/os) | 结构化日志与性能标记 | `Logger`（iOS 14+）、`Signposter` |

## 5. 标准库低频工具

| API | 一句话职责 |
|-----|-----------|
| `CommandLine.arguments` | 读取命令行启动参数（CLI/调试入口） |
| `ProcessInfo.processInfo` | 进程信息与环境变量（`environment`/`isiOSAppOnMac` 等运行判别） |
| `Mirror` | 运行时反射查看子结构（调试打印，勿用于业务逻辑） |
| `Result` | 成功/失败的显式包装值（错误处理见 [08-error-handling.md](./08-error-handling.md)） |

## ⚠️ 常见陷阱

- ❌ **新 SwiftUI 项目把模型层建在 Combine 上**：`ObservableObject` + `@Published` 与 Observation 双轨并存徒增心智负担
  ✅ 新模型一律 `@Observable`（对照迁移表见 [04-swiftui-state-api.md §3](./04-swiftui-state-api.md)）；只在节流/系统 publisher 场景借用 Combine。
- ❌ **用 `Timer` 做倒计时然后切后台失效**：Timer 依赖 RunLoop，后台被暂停
  ✅ UI 计时用 `Task` + `Task.sleep(for:)` 并响应生命周期；精确对时用 `Date` 差值而非累计次数。
- ❌ **Keychain 当 UserDefaults 用**：Keychain 无同步读写的"属性"语义，且写入类型受限
  ✅ 敏感小数据（token/密码）走 Keychain（Security 框架），普通偏好设置走 `UserDefaults`/`@AppStorage`。

## 🔗 相关条目

- 📄 **[01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md)** - 高频 Foundation 核心（String/Date/Codable）
- 📄 **[02-third-party-libs.md](../library-guides/02-third-party-libs.md)** - 第三方库选型与边界
- 📄 **[14-regex.md](./14-regex.md)** - 原生正则（文本处理深潜）
- 📄 **[04-swiftui-state-api.md](./04-swiftui-state-api.md)** - Observation 与 Combine 的取舍对照

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
