# ViewModifier 与修饰符链

> **文档简介**: 视图修饰符的条目式参考：包装语义、修饰顺序的布局后果、ViewModifier 协议与自定义封装
>
> **目标读者**: 被 `.padding().background()` 顺序坑过、想系统封装样式的学习者
>
> **前置知识**: 建议先学 [basics/04-views-state.md](../../basics/04-views-state.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#ViewModifier` `#修饰符` `#视图包装` `#样式封装` |
| **更新日期** | `2026年9月` |

</details>

---

## 📌 定义

**修饰符**是对视图的高阶包装：每个 `.foo()` 都返回一个**包装了原视图的新视图**。链式调用形成洋葱结构——

```swift
Text("Hi").padding().background(.yellow)
// 等价于 Background(Padding(Text("Hi")))
```

因此**修饰顺序就是嵌套顺序**：先写的靠近原始内容，后写的包装前一步结果、位于更外层；具体布局行为仍取决于修饰符。

**ViewModifier 协议**是自定义这种包装的官方抽象；实践中常再用 `extension View` 把它包装成流畅的链式 API。

## 📖 语法 / 签名

### ViewModifier 协议

```swift
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {   // content：被包装的原视图
        content
            .padding()
            .background(.background, in: .rect(cornerRadius: 12))
            .shadow(radius: 2)
    }
}

// 应用（两种等价写法）
SomeView().modifier(CardStyle())

// 惯例：再包一层 View 扩展，调用点更自然
extension View {
    func cardStyle() -> some View { modifier(CardStyle()) }
}
```

### 顺序决定布局

```swift
Text("Hello")
    .padding()                 // 1. 先包一层内边距
    .background(.yellow)       // 2. 黄底包含 padding 区域

Text("Hello")
    .background(.yellow)       // 1. 黄底紧贴文字
    .padding()                 // 2. 边距在黄底之外（透明）
```

### 条件样式的稳妥写法

```swift
extension View {
    func highlighted(_ active: Bool) -> some View {
        background(active ? Color.yellow : Color.clear)
    }
}
```

## 💡 示例

### 设计系统里的语义修饰符

```swift
struct PrimaryButtonStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .font(.headline)
            .foregroundStyle(.white)
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
            .background(.tint, in: .capsule)
    }
}

extension View {
    func primaryButton() -> some View { modifier(PrimaryButtonStyle()) }
}

// 使用：语义清晰，改样式只改一处
Button("提交") { submit() }.primaryButton()
```

### 顺序调试小实验

```swift
// .frame 在 .border 内 vs 外，边框画的范围不同
Text("A").frame(width: 200).border(.red)   // 边框围住 200 宽的 frame
Text("A").border(.red).frame(width: 200)   // 边框紧贴文字，再整体变宽
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| 修饰顺序想当然 | padding/background/frame 顺序不同结果完全不同 | 记住"洋葱模型"：后写的包装前一步结果 |
| 用 if 拼接不同修饰符链 | 视图身份变化，动画与状态丢失 | 尽可能保持结构，令同一修饰符的参数随条件变化 |
| 长修饰符链塞满 body | 可读性差、重算排查困难 | 封装成 ViewModifier；按钮等使用 ButtonStyle 等具体样式协议 |
| 以为修饰符"修改"原视图 | 它们创建新视图节点 | 理解包装后顺序问题自解 |
| 在 modifier 里读重状态 | 包装视图本身参与重算 | 状态读取留在内容层 |

<!-- full-library-explanation -->
## 用边框观察布局提案与包装范围

把上面的两个 frame/border 示例并排放入 VStack：两者都占 200 宽，但第一条红框为 200，第二条红框只围文字。background 也作用于它接收到的视图尺寸，不会自动跟随后面新加的 frame 扩大。

练习：为卡片依次应用 padding、background、frame(maxWidth: .infinity)，交换后两项并画出背景范围。验收应能先预测再观察，而不是反复调参直到“看起来差不多”。按钮外观优先封装 ButtonStyle，以访问 configuration.isPressed 并保持按钮语义；ViewModifier 适合跨多种视图复用的装饰、布局和行为。

条件只改变颜色时，保持同一条修饰链即可。@ViewBuilder 允许不同分支类型组成合法 View，不承诺两个分支共享同一状态身份。Modifier 可以拥有或读取状态，但要明确为何该状态属于这层，避免装饰外观时顺带发起难以追踪的业务请求。

## 🔗 相关条目

- 📄 [01-swiftui-essentials.md](./01-swiftui-essentials.md) — 高频修饰符速查表
- 📄 [03-state-driven-views.md](./03-state-driven-views.md) — 视图描述与重算模型
- 📄 [basics/05-layouts.md](../../basics/05-layouts.md) — 布局系统教程（顺序与布局的关系）
- 📄 [frameworks/02-swiftui-advanced.md](../../frameworks/02-swiftui-advanced.md) — 进阶封装任务指南


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
