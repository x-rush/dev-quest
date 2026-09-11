# ViewModifier 与修饰符链

> **文档简介**: 视图修饰符的条目式参考：包装语义、修饰顺序的布局后果、ViewModifier 协议与自定义封装
>
> **目标读者**: 被 `.padding().background()` 顺序坑过、想系统封装样式的学习者
>
> **前置知识**: 建议先学 [basics/04-views-state.md](../../basics/04-views-state.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#ViewModifier` `#修饰符` `#视图包装` `#样式封装` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

**修饰符**是对视图的高阶包装：每个 `.foo()` 都返回一个**包装了原视图的新视图**。链式调用形成洋葱结构——

```swift
Text("Hi").padding().background(.yellow)
// 等价于 Background(Padding(Text("Hi")))
```

因此**修饰顺序就是嵌套顺序**：先写的在外层（更靠近"父布局"），后写的在内层。

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
    .padding()                 // 1. 外层：留出内边距
    .background(.yellow)       // 2. 黄底包含 padding 区域

Text("Hello")
    .background(.yellow)       // 1. 黄底紧贴文字
    .padding()                 // 2. 边距在黄底之外（透明）
```

### 条件样式的稳妥写法

```swift
extension View {
    @ViewBuilder
    func highlighted(_ active: Bool) -> some View {
        if active {
            self.background(.yellow)
        } else {
            self                    // @ViewBuilder 保证两个分支类型可合成
        }
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
| 修饰顺序想当然 | padding/background/frame 顺序不同结果完全不同 | 记住"洋葱模型"：先写的在外层 |
| 用 if 拼接不同修饰符链 | 视图身份变化，动画与状态丢失 | @ViewBuilder 分支内保持视图相同 + 条件属性 |
| 长修饰符链塞满 body | 可读性差、重算排查困难 | 封装成 ViewModifier / ViewStyle |
| 以为修饰符"修改"原视图 | 它们创建新视图节点 | 理解包装后顺序问题自解 |
| 在 modifier 里读重状态 | 包装视图本身参与重算 | 状态读取留在内容层 |

## 🔗 相关条目

- 📄 [01-swiftui-essentials.md](./01-swiftui-essentials.md) — 高频修饰符速查表
- 📄 [03-state-driven-views.md](./03-state-driven-views.md) — 视图描述与重算模型
- 📄 [basics/05-layouts.md](../../basics/05-layouts.md) — 布局系统教程（顺序与布局的关系）
- 📄 [frameworks/02-swiftui-advanced.md](../../frameworks/02-swiftui-advanced.md) — 进阶封装任务指南
