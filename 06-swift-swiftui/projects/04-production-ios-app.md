# 实战项目四：生产级 iOS 应用

> **文档简介**: 把"能跑的 App"升级为"能上线的 App"：架构分层、错误处理、无障碍、配置管理、发布前清单，一份可对照执行的生产化改造指南
>
> **目标读者**: 完成三个实战项目、准备把作品推向 App Store 的中高级学习者
>
> **前置知识**: [projects/03-habit-tracker.md](./03-habit-tracker.md)、[architecture/01-app-architecture.md](../advanced-topics/architecture/01-app-architecture.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南（实战项目） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#生产化` `#架构分层` `#错误处理` `#无障碍` `#发布清单` |
| **更新日期** | `2026年9月` |

## 🎯 本项目解决什么问题

Demo 与产品的差距不在功能多少，而在**失败路径的处理质量**：网络会断、输入会错、用户会开最大字体、版本会迭代。本指南以一个"习惯追踪器"为改造底座，逐层补齐生产化缺口。

## 🛠️ 第一步：目录分层（功能优先的包结构）

```text
HabitTracker/
├── App/                    # 入口与根装配：App struct、容器注入、路由表
├── Features/               # 按功能竖切，每个功能内聚
│   ├── Today/              #   TodayView + TodayViewModel
│   ├── HabitDetail/        #   详情 + 图表 + 编辑
│   └── Settings/
├── Core/
│   ├── Models/             # @Model 实体 + 业务扩展（无 UI 依赖）
│   ├── Services/           # 网络层、定位层（协议抽象，见下）
│   └── DesignSystem/       # 颜色、字体、通用组件
└── Support/                # 常量、工具、本地化文件
```

**原则**：`Core/` 不 import SwiftUI（模型可测试、可复用到 Widget）；`Features/` 之间不互相 import（防耦合，靠路由跳转）。

## 🛠️ 第二步：依赖协议化（可测可换）

```swift
// Core/Services/WeatherService.swift —— 协议是分界线
protocol WeatherServicing: Sendable {
    func fetch(latitude: Double, longitude: Double) async throws -> WeatherSnapshot
}

struct LiveWeatherService: WeatherServicing {          // 生产实现
    func fetch(latitude: Double, longitude: Double) async throws -> WeatherSnapshot {
        // URLSession 真实请求……
        WeatherSnapshot(temperatureC: 21, conditionCode: "cloud.sun")
    }
}

// 环境注入：运行时给实现，测试时给 Mock
struct LiveWeatherServiceKey: EnvironmentKey {
    static let defaultValue: any WeatherServicing = LiveWeatherService()
}

extension EnvironmentValues {
    var weatherService: any WeatherServicing {
        get { self[LiveWeatherServiceKey.self] }
        set { self[LiveWeatherServiceKey.self] = newValue }
    }
}

// 视图内读取，测试中替换成 Mock 即可（见 testing/01-unit-testing.md）
@Environment(\.weatherService) private var weatherService
```

## 🛠️ 第三步：错误处理从"弹窗"升级为"状态机"

```swift
enum AppError: Error, LocalizedError {
    case offline
    case unauthorized(permission: String)
    case server(statusCode: Int)

    var errorDescription: String? {        // 用户能看懂的话术，不是异常堆栈
        switch self {
        case .offline:                     "网络不可用，请检查连接后重试"
        case .unauthorized(let p):         "需要「\(p)」权限，请到设置中开启"
        case .server(let code):            "服务暂时不可用（\(code)），稍后再试"
        }
    }
}

// 视图侧：统一错误横幅组件，任何页面复用
struct ErrorBanner: View {
    let error: AppError
    let retry: () -> Void

    var body: some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(.yellow)
            Text(error.localizedDescription)
                .font(.footnote)
            Spacer()
            Button("重试", action: retry)
                .buttonStyle(.bordered)
                .controlSize(.small)
        }
        .padding(12)
        .background(.red.opacity(0.1), in: .rect(cornerRadius: 10))
    }
}
```

**规则**：`URLError` 等底层错误在服务层翻译为 `AppError`；视图层永远只见 `AppError`；"取消"不算错误。

## 🛠️ 第四步：无障碍与适配（审核与口碑的分水岭）

```swift
struct CheckButton: View {
    let habit: Habit

    var body: some View {
        Button {
            habit.toggleCheckIn()
            UIAccessibility.post(notification: .announcement,
                                 argument: "\(habit.name)已打卡")   // VoiceOver 播报结果
        } label: {
            Image(systemName: habit.isChecked() ? "checkmark.circle.fill" : "circle")
        }
        .accessibilityLabel(habit.isChecked() ? "\(habit.name)，已完成" : "完成\(habit.name)")
        .accessibilityAddTraits(habit.isChecked() ? .isSelected : [])
    }
}
```

**发布前必查清单**：

- [ ] Dynamic Type 最大档不破版（用 XL 预览一遍）
- [ ] 所有可点元素有 `accessibilityLabel`，纯图标按钮不许留空
- [ ] 深色模式全页面走查（Color 资源语义化，不硬编码 hex）
- [ ] 中英文案全部走本地化文件（`String(localized:)`）
- [ ] 空状态、加载态、错误态三态齐备

## 🛠️ 第五步：配置与环境分离

```swift
enum AppConfig {
    static let apiBaseURL = URL(string: {
        #if DEBUG
        return "https://api.dev.example.com"
        #else
        return "https://api.example.com"
        #endif
    }())!

    static let isLogEnabled: Bool = {
        #if DEBUG
        return true
        #else
        return false
        #endif
    }()
}
```

Release 构建验证：`Product → Scheme → Edit Scheme → Run → Release`，确认无 `print` 残留、无测试数据开关。签名与 Archive 的完整操作见 [01-app-release.md](../deployment/01-app-release.md)。

## ✅ 生产化验收标准

- [ ] 飞行模式下每个网络页面都有明确反馈与重试，不白屏不闪退
- [ ] VoiceOver 能完成核心流程（打卡 → 看图表 → 删除习惯）
- [ ] 代码中没有硬编码的域名、密钥、开关（全部收敛到 `AppConfig`）
- [ ] 核心业务逻辑（streak、打卡切换）有单元测试覆盖
- [ ] 崩溃率与关键指标有监控（Xcode Cloud + MetricKit，见 [03-ci-cd-observability.md](../deployment/03-ci-cd-observability.md)）

## ❌ 常见问题

**Q1: 要不要上第三方依赖？** 默认零依赖起步（系统框架够用）；确需引入时用 SPM 并锁版本，评估清单见 [02-third-party-libs.md](../reference/library-guides/02-third-party-libs.md)。

**Q2: 测试代码放哪？** 业务测试放独立 Target；Preview 示例数据放 `#if DEBUG` 包裹的 `SampleData.swift`。

**Q3: 老代码没有分层怎么办？** 不必一步到位，按"新代码分层 + 顺手重构"节奏推进，架构演进策略见 [01-app-architecture.md](../advanced-topics/architecture/01-app-architecture.md)。

## 🎯 进阶挑战

- [ ] 为 `streak` 补齐边界测试（跨月、闰年、时区变更）
- [ ] 实现启动崩溃兜底：捕获异常后下次启动给用户友好恢复页
- [ ] 接入 Widget：今日完成度桌面小组件（复用 `Core/` 模型）

## 相关文档

- 📄 [01-unit-testing.md](../testing/01-unit-testing.md) — Swift Testing 单元测试
- 📄 [01-app-release.md](../deployment/01-app-release.md) — 签名、Archive 与 TestFlight
- 📄 [01-app-architecture.md](../advanced-topics/architecture/01-app-architecture.md) — 架构模式深度解释
- 📄 [01-security-practices.md](../advanced-topics/security/01-security-practices.md) — 安全实践（密钥、Keychain）
