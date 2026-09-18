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

SwiftUI 每一帧对每个视图执行：

1. **父级提议尺寸**：父视图给子视图一个建议尺寸（可能很宽松或固定）
2. **子级自报尺寸**：子视图依据自身内容与 modifier 决定自己的尺寸并返回
3. **父级放置**：父视图把子视图放进容器坐标系的某个位置

理解它的两个推论：

- `Text` 的默认尺寸由**内容**决定；`Image(systemName:)` 同理
- `.background(Color.red)` 在文字**实际尺寸**外扩红——要全屏红应放到容器层

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
| `spacing` | 子视图间距 | 由平台默认值决定（约 8pt） |

**布局优先级**：空间不足时，SwiftUI 按子视图的 `layoutPriority`（默认 0）从高到低压缩。

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

- 有相邻固定视图时 Spacer 吞掉全部剩余空间
- `Spacer(minLength: 20)` 可设下限
- 无固定邻居时（如单个 Spacer 独占 VStack 一行）取默认 8pt 并居中——想"左对齐"配 `.frame(maxWidth:.infinity, alignment:.leading)` 更直观

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

> 💡 **Lazy vs 非 Lazy**：`VStack`/`HStack` 一次性构建全部子视图；`LazyVStack`/`LazyHGrid` 只构建可见区域。长内容务必用 Lazy 系列或 List，否则滚动时内存与首帧都会劣化。

## ✅ 最佳实践

布局从内容需求推导容器：垂直表单需要文本换行与键盘避让，平行操作需要横向空间分配，大量数据需要滚动和适当的延迟构建。不要只在一个固定设备尺寸下用 padding 凑位置。

fixedSize 与 frame 会改变父子尺寸协商，可能帮助内容按理想尺寸展示，也可能让内容超出可用范围，不能统一解释成必然截断。验收至少包括大字体、窄屏和横屏；限宽数值从内容可读性选择，而非固定 480。

## ❓ 常见问题

### Q1: Text 在 HStack 里显示"一行被截成…"而不是换行？

空间不足时 SwiftUI 默认截断。加 `.lineLimit(2)`（限制）或 `.fixedSize(horizontal: false, vertical: true)`（允许换行拒绝水平压缩），并给关键文本 `.layoutPriority(1)`。

### Q2: ZStack 里两个视图为什么重叠错位？

ZStack 用 `alignment` 统一对齐所有子视图（默认 `.center`）。想让文字贴底部：`ZStack(alignment: .bottom) { … }`。

### Q3: ScrollView 内容不满一屏也想让底部按钮固定住？

不要把按钮放 ScrollView 里，用 `.safeAreaInset(edge: .bottom) { BarView() }` 挂在安全区，列表内容自动避开。

## 🎯 练习与实践

### 练习一：基础练习

- [ ] 复刻 ProfileCard 并在 iPhone 与 iPad 模拟器各运行一次，确认限宽行为
- [ ] 用 LazyVGrid 做 2 列照片墙（`GridItem(.adaptive(minimum: 120))`）
- [ ] 给 List 加两个 Section 与 `.swipeActions` 删除

### 进阶挑战

- [ ] 实现聊天页布局：自己的消息靠右（蓝底）、对方靠左（灰底），用 `HStack` + 条件 Spacer 完成
- [ ] 用 `GeometryReader` 让封面图高度 = 屏幕高度的 1/3

---

## 相关文档

- 📄 [06-navigation.md](./06-navigation.md) — 下一篇：多页面导航
- 📄 [01-swiftui-essentials.md](../reference/framework-essentials/01-swiftui-essentials.md) — 视图与修饰符全量速查
- 📄 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md) — 布局塌陷、滚动冲突等疑难排查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
