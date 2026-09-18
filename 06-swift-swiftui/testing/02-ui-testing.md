# UI 测试任务指南 — XCUITest

> **文档简介**: 用 XCUITest 以用户视角驱动真实界面：定位元素、模拟交互、验证页面流转，为核心用户旅程建立回归防线
>
> **目标读者**: 已有单元测试基础、要验证端到端交互流程的中级学习者
>
> **前置知识**: [01-unit-testing.md](./01-unit-testing.md)（测试框架已就绪）、[projects/01-notes-app.md](../projects/01-notes-app.md)（有可测的界面流程）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#XCUITest` `#UI测试` `#可访问性` `#用户旅程` `#回归` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 本指南解决什么问题

单元测试保证"逻辑对"，UI 测试保证"用户操作路径通"：按钮真的能点、页面真的会跳、输入真的会保存。原则先立住——**UI 测试测旅程，不测像素**，只覆盖核心路径（登录、下单、打卡），数量少而稳定。

## 🛠️ 任务一：新建 UI 测试 Target 并跑通冒烟测试

File → New → Target → **UI Testing Bundle**。注意 UI 测试运行在独立进程，通过无障碍树驱动 App，`@testable import` 在这里不可用。

```swift
import XCTest

final class NotesAppUITests: XCTestCase {

    override func setUp() {
        continueAfterFailure = false        // 第一步失败就停，后面的断言无意义
    }

    @MainActor
    func testLaunchShowsNoteList() {
        let app = XCUIApplication()
        app.launch()

        XCTAssertTrue(app.navigationBars["我的笔记"].waitForExistence(timeout: 5))
    }
}
```

## 🛠️ 任务二：核心旅程测试（新建 → 保存 → 可见）

```swift
@MainActor
func testCreateNoteEndToEnd() {
    let app = XCUIApplication()
    app.launch()

    // 1. 点击右上加号（SwiftUI toolbar 按钮可通过 label 定位）
    app.buttons["plus"].firstMatch.tap()
    // 或者：给按钮加 .accessibilityIdentifier("addNote") 后用
    // app.buttons["addNote"].tap()

    // 2. 表单输入
    let titleField = app.textFields["标题"]
    XCTAssertTrue(titleField.waitForExistence(timeout: 3))
    titleField.tap()
    titleField.typeText("UITest 笔记")

    let contentField = app.textViews.firstMatch
    contentField.tap()
    contentField.typeText("由 UI 测试创建")

    // 3. 保存并验证列表出现新条目
    app.buttons["保存"].tap()

    let newRow = app.staticTexts["UITest 笔记"]
    XCTAssertTrue(newRow.waitForExistence(timeout: 3), "保存后列表应出现新笔记")
}
```

## 🛠️ 任务三：让 SwiftUI 元素"可被找到"

XCUITest 靠**无障碍树**定位，两个习惯要养成本文写作时贯穿：

```swift
// 1. 业务关键控件显式给 identifier（不随文案改动而失效）
Button {
    showingEditor = true
} label: {
    Image(systemName: "plus")
}
.accessibilityIdentifier("addNote")       // 测试用 app.buttons["addNote"]

// 2. 自定义组件合成一个无障碍元素，避免内部子视图被逐个遍历
struct CheckButton: View {
    let habit: Habit

    var body: some View {
        Button { habit.toggleCheckIn() } label: {
            HStack {
                Image(systemName: habit.icon)
                Text(habit.name)
                Image(systemName: habit.isChecked() ? "checkmark.circle.fill" : "circle")
            }
        }
        .accessibilityElement(children: .combine)      // 合并为一整个可点元素
        .accessibilityIdentifier("check-\(habit.name)")
    }
}
```

**元素定位速查**：

| 场景 | API | 说明 |
|------|-----|------|
| 按钮按标识 | `app.buttons["addNote"]` | 首选，最稳定 |
| 文本按内容 | `app.staticTexts["UITest 笔记"]` | 验证展示结果 |
| 等待出现 | `element.waitForExistence(timeout:)` | 异步界面必用，勿直接断言 |
| 滚动到可见 | `element.swipeUp()` 循环 | 长列表先滚再点 |
| 断言存在性 | `element.exists` | 即时快照，异步场景别单独用 |

## 🛠️ 任务四：测试隔离与状态清理

UI 测试共享真实磁盘数据，第二条运行可能被第一条污染。用启动参数注入测试模式：

```swift
// 测试里：launchArguments 传给 App
app.launchArguments += ["-UITEST"]
app.launch()

// App 启动处（App/RootAssembly.swift）：
@main
struct NotesApp: App {
    let container: ModelContainer = {
        if ProcessInfo.processInfo.arguments.contains("-UITEST") {
            // 测试模式：内存库 + 固定种子数据，每条测试都从干净状态开始
            let config = ModelConfiguration(isStoredInMemoryOnly: true)
            return try! ModelContainer(for: Note.self, configurations: config)
        }
        return try! ModelContainer(for: Note.self)
    }()

    var body: some Scene {
        WindowGroup { NoteListView() }
            .modelContainer(container)
    }
}
```

## ✅ 最佳实践

UI 测试优先覆盖发布后代价高的旅程，数量由风险与维护能力决定，不设“两位数以内”的硬上限。定位使用稳定的标识或可理解语义，文案变化不应让与文字无关的用例全部失效。

等待目标元素出现或状态达到预期，而不是固定 sleep；元素出现也可能尚未可操作，需检查相应条件。保存失败截图与应用日志，另外验证焦点、动态字体和读屏，不把可定位等同于可访问。

## ❌ 避免陷阱

- ❌ 用 XCUITest 断言样式与布局——那是 Preview 与设计走查的职责
- ❌ 测试之间共享状态不清理——用 launchArguments 的内存库或专门测试账号
- ❌ 在 CI 上依赖弹窗位置点系统权限弹窗——用 `addUIInterruptionMonitor` 或测试启动参数绕过

## ❓ 常见问题

**Q1: 元素明明在屏幕上却查不到？** 它可能被 `accessibilityHidden(true)` 隐藏，或被 `.accessibilityElement(children: .ignore)` 吞掉；用 Xcode 的无障碍检查器（Accessibility Inspector）核对树结构。

**Q2: SwiftUI 的 `TextField` 找不到？** SwiftUI 输入框映射为 `textFields` 或 `textViews`（多行）按 label 定位；带 placeholder 优先用 placeholder 文案。

**Q3: 测试在本机能过、CI 失败？** 多为时序与语言环境差异：统一启动参数 `-AppleLanguages (zh-Hans)`，所有断言前加 `waitForExistence`。

## 🎯 练习

- [ ] 给"新建笔记 → 保存 → 搜索到它"写一条完整旅程测试
- [ ] 故意把保存按钮文案从"保存"改为"确定"，验证 identifier 定位不受影响
- [ ] 实现 `-UITEST` 启动参数 + 内存库，让两条测试连续运行互不污染

## 相关文档

- 📄 [03-integration-testing.md](./03-integration-testing.md) — 下一篇：集成测试（数据层 + 服务层）
- 📄 [01-unit-testing.md](./01-unit-testing.md) — 单元测试（逻辑层保障）
- 📄 [01-notes-app.md](../projects/01-notes-app.md) — 被测界面出处
- 📄 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md) — 测试报错速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
