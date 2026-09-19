# 布局系统 - Stack、Spacer 与滚动容器

## 先理解，再动手

Stack 排列内容，Spacer 消耗可用空间。布局是父子协商尺寸，固定 frame 与内容自身大小可能产生冲突。

**本节自测**：用短标题和很长标题测试带尾部按钮的 HStack。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

长标题不遮挡按钮，动态字体也可读；先修约束再加任意固定宽度。

</details>

> **文档简介**: 掌握 SwiftUI 布局的三步协商算法与核心容器：VStack/HStack/ZStack、Spacer 与 flexible frame、List 与 ScrollView，能搭出适配任意屏幕的界面
>
> **目标读者**: 已掌握状态管理、开始搭建完整界面的学习者
>
> **前置知识**: [04-views-state.md](./04-views-state.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#布局` `#VStack` `#HStack` `#List` `#ScrollView` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 解释 SwiftUI"父级提议 → 子级自报 → 父级放置"的三步布局协商
- ✅ 用 Stack + Spacer + frame 实现常见对齐与填充策略
- ✅ 在 List 与 ScrollView 之间正确选型
- ✅ 构建适配 iPhone 横竖屏与 iPad 的自适应界面

## 🔍 一、布局协商三步曲

理解一次布局计算时，可以沿以下步骤追踪；不能据此断言每一帧都会重算每个视图：

1. **父级提议尺寸**：父视图给子视图一个建议尺寸（可能很宽松或固定）
2. **子级自报尺寸**：子视图依据自身内容与 modifier 决定自己的尺寸并返回
3. **父级放置**：父视图把子视图放进容器坐标系的某个位置

理解它的两个推论：

- `Text` 的默认尺寸由**内容**决定；`Image(systemName:)` 同理
- `.background(Color.red)` 在前面视图所占区域后绘制背景，并不自动增加文字的布局尺寸；要覆盖更大区域先提供相应 frame 或容器

```swift
// 观察协商：Text 只占内容宽，红色背景不会铺满
Text("内容决定宽度")
    .background(Color.red)

// 让 frame 接管尺寸后，背景才铺满指定区域
Text("撑满宽度")
    .frame(maxWidth: .infinity)
    .background(Color.red)
```

## 🔍 二、Stack 家族

```swift
VStack(alignment: .leading, spacing: 12) {   // 垂直：默认居中对齐
    Text("标题").font(.title)
    Text("副标题").foregroundStyle(.secondary)
}

HStack(spacing: 8) {                          // 水平
    Image(systemName: "star.fill")
    Text("收藏")
}

ZStack {                                      // 深度叠加：后写的在上层
    Rectangle().fill(.blue.gradient)
    Text("封面文字").font(.largeTitle)
}
```

| 参数 | 作用 | 默认值 |
|------|------|--------|
| `alignment` | 次轴对齐（VStack 的水平方向） | `.center` |
| `spacing` | 子视图间距 | nil 时由系统按上下文选择，不承诺固定 8pt |

**布局优先级**：默认值为 0。较高优先级让视图在空间不足时相对更晚收缩，在有额外空间时相对更早伸展；不能理解为从高到低优先压缩。它也不保证文字永不截断，仍需检查可用宽高。

```swift
HStack {
    Text("固定不动的长标题")
        .layoutPriority(1)                 // 优先保我
    Text("可被压缩的次要说明文字可以多行")
}
```

## 🔍 三、Spacer 与 flexible frame

### Spacer：吃掉弹性空间

```swift
HStack {
    Text("左")
    Spacer()                // 尽可能撑开，把右视图推到末尾
    Text("右")
}
```

- Spacer 在容器主轴上扩展以占据可用空间；多个 Spacer 或其他弹性视图可能共同分配空间
- `Spacer(minLength: 20)` 可设下限
- 未显式指定 minLength 时由系统决定最小长度，不存在“独占一行必然是 8pt”的规则。只想左对齐时可用 `.frame(maxWidth: .infinity, alignment: .leading)`，无需制造额外空白视图

### frame：显式尺寸协商

```swift
// 固定尺寸
Color.blue.frame(width: 100, height: 50)

// 弹性尺寸：min/max 参与协商，alignment 决定内容在框内位置
Text("弹性")
    .frame(maxWidth: .infinity, maxHeight: .infinity)
    .background(.yellow)

// 常用技巧：内容限宽居中（iPad 上不至于拉太宽）
VStack { /* 表单内容 */ }
    .frame(maxWidth: 480)
    .frame(maxWidth: .infinity)
```

`frame(maxWidth: .infinity)` 的语义是"我愿意无限扩张"，而不是"我必须是全宽"——空间由父级分配。

## 🔍 四、滚动容器：ScrollView 与 List

### ScrollView：自由滚动

以下是容器结构片段，依赖调用者提供 articles 与 ArticleCard；完整屏幕见后面的练习。

```swift
ScrollView {
    VStack(alignment: .leading, spacing: 16) {
        ForEach(articles) { article in
            ArticleCard(article: article)
        }
    }
    .padding()
}
.scrollBounceBehavior(.basedOnSize)   // 内容不满一屏时禁用回弹
```

### List：语义化列表

```swift
List {
    Section("进行中") {
        ForEach(activeTasks) { task in
            TaskRow(task: task)
        }
    }
    Section("已完成") {
        ForEach(doneTasks) { task in
            TaskRow(task: task)
                .swipeActions(edge: .trailing) {
                    Button("删除", role: .destructive) {
                        delete(task)
                    }
                }
        }
    }
}
.listStyle(.insetGrouped)
```

### 选型对照

| 能力 | List | ScrollView + LazyVStack |
|------|------|------------------------|
| 惰性加载 | ✅ 自动 | 用 `LazyVStack` 才有 |
| 分组/表头 | ✅ Section 原生 | 手写 |
| 滑动操作/编辑/多选 | ✅ 内建 | 手写 |
| 完全自定义行布局 | 一般 | ✅ 自由 |
| 混排（图表+列表） | 受限 | ✅ |

> **Lazy vs 非 Lazy**：普通 Stack 不提供按滚动可见需求延迟创建子视图的能力；Lazy 容器按需要创建，系统可提前准备视图，不能断言只有屏幕内项目才存在。是否改用 Lazy 应结合内容规模和测量结果，不能据此假定 List 只保留固定数量的行。

## ✅ 最佳实践

布局从内容需求推导容器：垂直表单需要文本换行与键盘避让，平行操作需要横向空间分配，大量数据需要滚动和适当的延迟构建。不要只在一个固定设备尺寸下用 padding 凑位置。

fixedSize 与 frame 会改变父子尺寸协商，可能帮助内容按理想尺寸展示，也可能让内容超出可用范围，不能统一解释成必然截断。验收至少包括大字体、窄屏和横屏；限宽数值从内容可读性选择，而非固定 480。

## ❓ 常见问题

### Q1: Text 在 HStack 里显示"一行被截成…"而不是换行？

先检查是否设置了 lineLimit 或固定高度。`.lineLimit(2)` 允许最多两行，并不保证完整展示任意长文字；`.fixedSize(horizontal: false, vertical: true)` 保持理想的垂直尺寸，同时仍接受水平约束，可能让内容高于父容器。关键文本可提高 layoutPriority，但仍需用窄屏和大字体验收。

### Q2: ZStack 里两个视图为什么重叠错位？

ZStack 用 `alignment` 统一对齐所有子视图（默认 `.center`）。想让文字贴底部：`ZStack(alignment: .bottom) { … }`。

### Q3: ScrollView 内容不满一屏也想让底部按钮固定住？

不要把按钮放 ScrollView 里，用 `.safeAreaInset(edge: .bottom) { BarView() }` 挂在安全区，列表内容自动避开。

## 🎯 练习与实践

### 先完成一个可运行的联系人屏幕

前置：完成上一课的 SwiftUI App，能在 Xcode 中选定 iOS 模拟器。将工程的 `ContentView.swift` 内容替换为以下代码；保留已有 App 文件里的 `WindowGroup { ContentView() }`。本例只依赖 SwiftUI，不需要图片资源、网络或第三方库。

```swift
import SwiftUI

private struct Contact: Identifiable {
    let id: Int
    let name: String
}

struct ContentView: View {
    @State private var contacts = (1...30).map {
        Contact(id: $0, name: "联系人 \($0)")
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("共 \(contacts.count) 人")
                .font(.title2)
                .padding(.horizontal)
            List(contacts) { contact in
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: "person.circle")
                        .accessibilityHidden(true)
                    VStack(alignment: .leading, spacing: 4) {
                        Text(contact.name)
                        Text("等待联系")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    Button("删除") {
                        contacts.removeAll { $0.id == contact.id }
                    }
                    .buttonStyle(.borderless)
                }
            }
            .listStyle(.plain)
        }
        .padding(.top)
    }
}
```

输入是 30 个带固定 id 的联系人。外层 VStack 放标题与 List；行内 HStack 放图标、两行文字和按钮。中间 VStack 的 flexible frame 使用可用宽度，让按钮靠近尾端；它不赋予 Text 无限屏幕空间。点击首行删除后，预期标题为“共 29 人”，第一行变成“联系人 2”。重启后回到 30 人，因为 @State 只管理当前视图身份下的状态。

先在普通字体下运行，再把一个名字改为 40 个汉字，在窄屏和辅助功能大字体下检查。验收是内容可读且按钮能操作，不承诺任意字号下仍保持三栏；若横向空间不足，应把操作移到下一行，或以 ViewThatFits 提供垂直备选布局。不要用固定行高掩盖被裁掉的文字。

失败回查：看不到新屏幕时检查 App 的 WindowGroup 是否仍指向旧视图；重复 ContentView 定义时删除旧定义；行状态关联异常时检查 id 是否唯一且稳定。预览失败与模拟器构建失败分开记录，前者不能单独证明真机也失败。

本轮未在 macOS/Xcode、iOS 模拟器或真机运行本例；已作官方资料核对和静态阅读。Windows 上的 Swift 命令行运行不能代替 SwiftUI 的构建和布局验收。

反馈练习：给中间 VStack 加蓝色 background，分别放在 frame 前后。预期前者标记内容区域，后者标记 frame 的区域；若颜色铺开却文字仍居中，检查 frame 的 alignment。随后将删除操作改为下一页的详情导航，路由携带 contact.id，而不是数组下标。

### 练习一：基础练习

- [ ] 在 iPhone 与 iPad 模拟器分别运行上面的联系人屏幕，记录长标题与大字体下的变化
- [ ] 用两个 `GridItem(.flexible())` 做固定两列照片墙；再换 `.adaptive(minimum: 120)`，观察列数随容器宽度变化，它不保证两列
- [ ] 给 List 加两个 Section 与 `.swipeActions` 删除

### 进阶挑战

- [ ] 实现聊天页布局：自己的消息靠右（蓝底）、对方靠左（灰底），用 `HStack` + 条件 Spacer 完成
- [ ] 用 `GeometryReader` 让封面图高度 = 屏幕高度的 1/3

---

## 相关文档

- 📄 [06-navigation.md](./06-navigation.md) — 下一篇：多页面导航
- 📄 [01-swiftui-essentials.md](../reference/framework-essentials/01-swiftui-essentials.md) — 视图与修饰符全量速查
- 📄 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md) — 布局塌陷、滚动冲突等疑难排查

官方回查入口（2026-09-20）：[layoutPriority](https://developer.apple.com/documentation/swiftui/view/layoutpriority(_:))、[Spacer](https://developer.apple.com/documentation/swiftui/spacer)、[布局调整](https://developer.apple.com/documentation/swiftui/adjusting-the-space-between-views)、[LazyVStack](https://developer.apple.com/documentation/swiftui/lazyvstack)。继续导航前，应能解释当前行的状态由谁持有、id 为什么不能随删除重新编号。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
