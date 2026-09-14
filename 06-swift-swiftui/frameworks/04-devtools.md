# Xcode 工具链任务指南 — Preview、Instruments 与调试器

> **文档简介**: 面向任务的 Xcode 日常工具指南：用 Preview 即时预览界面、用 Instruments 定位性能问题、用 LLDB 调试器查状态找 bug
>
> **目标读者**: 刚配置好 Xcode 环境、需要在开发循环中高效排错与调优的学习者
>
> **前置知识**: [basics/01-environment-setup.md](../basics/01-environment-setup.md)（环境已就绪）、[basics/02-first-swiftui-app.md](../basics/02-first-swiftui-app.md)（跑通过第一个 App）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#Xcode` `#Preview` `#Instruments` `#LLDB` `#调试` |
| **更新日期** | `2026年9月` |

## 🎯 本指南解决什么问题

写 iOS 应用时 80% 的时间花在"改代码 → 看效果 → 查问题"循环上。本指南把循环里的三件武器按使用场景串起来，每个都给出最快上手路径。

## 🛠️ 任务一：用 Preview 告别"改一次跑一次"

### 1.1 基本用法

```swift
import SwiftUI

struct TagPicker: View {
    @State private var selected: Set<String> = []

    let tags = ["swift", "swiftui", "swiftdata"]

    var body: some View {
        HStack {
            ForEach(tags, id: \.self) { tag in
                Button(tag) {
                    if selected.contains(tag) {
                        selected.remove(tag)
                    } else {
                        selected.insert(tag)
                    }
                }
                .buttonStyle(.bordered)
                .tint(selected.contains(tag) ? .blue : .gray)
            }
        }
        .padding()
    }
}

#Preview {                                   // Xcode 15+：#Preview 宏即写即用
    TagPicker()
}

#Preview("深色模式") {                         // 可命名多个预览
    TagPicker()
        .preferredColorScheme(.dark)
}
```

### 1.2 让 Preview 可交互

Cmd+点击预览区或按播放键进入**交互模式**：点击、滚动、动画都能直接操作；SwiftData 页面用内存容器预填数据：

```swift
#Preview {
    CityListView()
        .modelContainer(for: City.self, isStoredInMemoryOnly: true)   // 内存库，不污染真机数据
}
```

**技巧**：改代码时保持预览开启（Cmd+Option+P 刷新）；预览崩溃看画布底部红色诊断条，多数是 `@Observable` 模型没在根部初始化。

## 🛠️ 任务二：用 LLDB 调试器查状态

### 2.1 断点与常用命令

打断点后运行到断点处，在 Debug Console（Cmd+Shift+Y）输入：

```text
p count            // print：打印表达式值（编译求值）
po viewModel       // print object：打印对象描述（调用 description/debugDescription）
frame variable     // 列出当前栈帧所有局部变量
expr count = 99    // 运行时改值，验证"如果是 99 会怎样"
bt                 // backtrace：打印调用栈，定位"谁调到这的"
```

### 2.2 SwiftUI 专属调试手段

| 手段 | 怎么用 | 查什么 |
|------|--------|--------|
| Self._printChanges() | 放进 `body` 第一行 | 视图为何被重算（打印依赖的属性名） |
| View Hierarchy Debugger | Debug 工具栏 ⓘ 图标 | 视图层级、约束、z 序 |
| 符号断点 | Breakpoint Navigator → Symbolic | 追踪 UIKit/SwiftUI 内部调用 |
| Environment 探针 | `@Environment(\.dismiss)` 打印 | 环境 vs 传参问题 |

```swift
var body: some View {
    let _ = Self._printChanges()      // 控制台输出 "TagPicker: @self, _selected"
    HStack { /* ... */ }
}
```

## 🛠️ 任务三：用 Instruments 定位性能问题

入口：Xcode → Product → Profile（Cmd+I），或直接在画布预览下方点 Performance 徽章（Xcode 16 起提供）。

| 场景 | 选哪个模板 | 看什么 |
|------|-----------|--------|
| 滚动卡顿 | SwiftUI View Body | 每个 body 求值次数与耗时 |
| 启动慢 | App Launch | 主线程冷启动时间线 |
| 内存暴涨 | Allocations / Leaks | 对象分配曲线、泄漏对象 |
| 界面掉帧 | Time Profiler | 主线程热点函数 |

**实操顺序**：先 Time Profiler 找热点函数 → 再用针对性模板（如 SwiftUI View Body）看该函数调用上下文 → 最后回代码修复。渲染优化的系统方法论见 [rendering-performance 专题](../advanced-topics/performance/01-rendering-performance.md)。

## ✅ 最佳实践

- ✅ 每个 UI 组件文件都留一个 `#Preview`，改动即时可见，减少全量编译
- ✅ 查"视图为什么刷新"优先 `Self._printChanges()`，比猜快得多
- ✅ 性能问题先测量（Instruments）再优化，禁止凭感觉

## ❌ 避免陷阱

- ❌ Preview 崩溃反复重启 Xcode——先看诊断信息，90% 是初始化阶段抛错
- ❌ 用 `print` 调试异步代码——打印顺序会骗人，用断点 + LLDB `po` 看真实时序
- ❌ 在 Release 构建里保留 `Self._printChanges()`——记得包 `#if DEBUG`

## ❓ 常见问题

**Q1: Preview 和模拟器结果不一致？** Preview 运行在独立的预览代理进程，设备特性（推送、定位）不可用，涉及系统能力时用模拟器验证。

**Q2: Instruments 里看到 body 求值上万次正常吗？** 长列表滚动时数千次正常；静止界面持续增长说明有循环刷新，见渲染专题排查清单。

**Q3: `po` 输出一堆 Metadata 看不懂？** 对 `@Observable` 类型自定义 `CustomDebugStringConvertible`，输出关键字段即可。

## 🎯 练习

- [ ] 给 TagPicker 加明暗两套 Preview，并进交互模式点击按钮
- [ ] 在任意视图中插入 `Self._printChanges()`，观察每次交互打印了什么
- [ ] 用 Time Profiler 录制滚动 30 秒，找出最耗时的 3 个函数

## 相关文档

- 📄 [01-swiftui-basics.md](./01-swiftui-basics.md) — SwiftUI 基础任务（配合 Preview 使用）
- 📄 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md) — 常见报错与故障排除字典
- 📄 [01-environment-setup.md](../basics/01-environment-setup.md) — 环境搭建教程
- 📄 [01-rendering-performance.md](../advanced-topics/performance/01-rendering-performance.md) — 渲染性能深度解释
