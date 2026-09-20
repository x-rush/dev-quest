# SwiftUI 核心视图与修饰符速查

> **文档简介**: SwiftUI 常用视图、布局容器、修饰符与动画 API 的分类速查表，按"找什么→用什么"组织
>
> **目标读者**: 需要快速定位 API 名称与参数的全体学习者
>
> **前置知识**: 无；教程侧见 [basics/05-layouts.md](../../basics/05-layouts.md)、[basics/06-navigation.md](../../basics/06-navigation.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#SwiftUI` `#视图` `#修饰符` `#速查` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. 基础视图

| 视图 | 用途 | 关键参数 |
|------|------|----------|
| `Text` | 文本 | `verbatim:` 禁本地化 |
| `Image` | 图片 | `systemName:` SF Symbol；`Image("name")` 资源图 |
| `Button` | 按钮 | `Button { } label: { }`；`role: .destructive` |
| `Toggle` | 开关 | `isOn:` Binding |
| `Slider` | 滑杆 | `value:in:` |
| `Stepper` | 步进器 | `value:in:step:` |
| `TextField` | 输入框 | `text:` Binding、`.keyboardType()` |
| `SecureField` | 密码输入 | 同 TextField |
| `Picker` | 选择器 | `selection:`；`.pickerStyle(.menu/.segmented)` |
| `DatePicker` | 日期选择 | `selection:displayedComponents:` |
| `ProgressView` | 进度 | `value:total:`；不确定态无参 |
| `Gauge` | 仪表（iOS 16+） | `value:in:` + gaugeStyle |
| `ContentUnavailableView` | 空状态（iOS 17+） | `Label` + description + actions |
| `ForEach` | 数据驱动渲染（集合→视图） | 元素需 `Identifiable` 或传 `id:`；`id: \.self` 用值本身作标识 |

---

## 2. 布局容器

| 容器 | 说明 |
|------|------|
| `VStack / HStack(alignment:spacing:)`；`ZStack(alignment:)` | 垂直、水平与叠放；ZStack 没有 spacing 参数 |
| `LazyVStack / LazyHStack` | 按需创建可见附近内容；适合长列表，但项目中仍要测量行视图成本、图片解码和状态更新 |
| `Grid`（iOS 16+） | 二维网格，`GridRow` 分行 |
| `LazyVGrid(columns:)` | 按行排列的自适应列网格（不是瀑布流）：`[GridItem(.adaptive(minimum: 120))]` |
| `ScrollView(.vertical/.horizontal)` | 滚动容器 |
| `ScrollViewReader` | 程序化滚动：`scrollTo(id, anchor:)` |
| `List` | 表格列表，Section/swipeActions/editActions |
| `Form` | 设置表单风格 List |
| `Divider` | 分割线 |
| `Spacer(minLength:)` | 弹性空白 |
| `Canvas` | 以 `GraphicsContext` 自定义绘制；适合需要合并大量绘制命令的场景，是否优于普通 View 层级须用 Instruments 针对目标交互测量 |
| `ViewThatFits` | 在候选布局中放得下的那个（横竖屏适配利器） |

---

## 3. 呈现与导航

| API | 用途 |
|------|------|
| `NavigationStack { }` / `NavigationStack(path:)` | 压栈导航 |
| `NavigationLink(value:label:)` | 值驱动链接 |
| `.navigationDestination(for:)` | 值→目标映射 |
| `.navigationTitle / .navigationBarTitleDisplayMode` | 标题栏 |
| `.toolbar { ToolbarItem(placement:) }` | 导航栏按钮 |
| `.navigationBarHidden / .navigationBarBackButtonHidden` | 隐藏栏/返回键 |
| `TabView { }` / `Tab("t", systemImage:)`（iOS 18+） | 标签页 |
| `.sheet(isPresented:) / .sheet(item:)` | 底部弹窗 |
| `.fullScreenCover` | 全屏弹窗 |
| `.popover` | 浮层（iPad） |
| `.alert(_:isPresented:actions:)` | 警告框 |
| `.confirmationDialog(_:isPresented:titleVisibility:)` | 操作确认菜单 |
| `.presentationDetents([.medium, .large])` | sheet 高度档位 |
| `.interactiveDismissDisabled(true)` | 禁下滑关闭 |
| `.searchable(text:prompt:)` | 搜索栏（List/NavigationStack 内） |

---

## 4. 高频修饰符

### 4.1 外观

```swift
Text("a")
    .font(.title2)                      // 或 .font(.system(size: 14, weight: .bold))
    .fontWeight(.semibold)
    .foregroundStyle(.secondary)        // 颜色/材质
    .tint(.blue)                        // 控件主色
    .background(.background, in: RoundedRectangle(cornerRadius: 12))
    .overlay(alignment: .topTrailing) { Badge() }
    .clipShape(Circle())
    .shadow(radius: 4, y: 2)
    .opacity(0.8)
    .cornerRadius(12)                   // ⚠️ 已软弃用，首选 clipShape/background(in:)
```

### 4.2 尺寸与间距

```swift
    .frame(width: 100, height: 40)
    .frame(maxWidth: .infinity, alignment: .leading)
    .padding(.horizontal, 16)           // 四方向分别控制
    .padding(12)
    .fixedSize(horizontal: false, vertical: true)   // 允许换行拒绝压缩
    .layoutPriority(1)
    .ignoresSafeArea(.container, edges: .bottom)
    .safeAreaInset(edge: .bottom) { Banner() }      // 安全区内嵌内容
```

### 4.3 状态与生命周期

```swift
    .onAppear { } / .onDisappear { }
    .task { } / .task(id: x) { }
    .onChange(of: value) { oldValue, newValue in }   // iOS 17+ 双参数
    .refreshable { await load() }                    // 下拉刷新
    .disabled(isBusy)
    .redacted(reason: .placeholder)                  // 骨架屏
```

---

## 5. 动画与过渡

```swift
// 隐式动画：状态变化自动应用
Toggle("开关", isOn: $on)
    .animation(.spring(duration: 0.3), value: on)   // 必须绑定 value 限定范围

// 显式动画
withAnimation(.easeInOut(duration: 0.25)) { expanded.toggle() }

// 过渡：视图插入/移除
if expanded {
    Detail().transition(.slide.combined(with: .opacity))
}

// 匹配几何：跨视图共享元素
@Namespace private var ns
Image("hero").matchedGeometryEffect(id: "hero", in: ns)
```

| 动画曲线 | 场景 |
|----------|------|
| `.linear` | 匀速 |
| `.easeIn / .easeOut / .easeInOut` | 缓入缓出 |
| `.spring(duration:bounce:)` | 弹性（UI 首选） |
| `.bouncy / .snappy / .smooth` | iOS 17 预设 |

**关键原则**: 动画必须绑定或包裹**状态变化**；把 `.animation` 挂整个视图且不带 value 是误动画之源。

---

## ⚠️ 高频陷阱速查

- **修饰符顺序即布局**：`.padding().background()` 与 `.background().padding()` 结果不同——先记"由内向外生效"
- **List 里放 Button 触发整行**：Button 默认样式占满行；加 `.buttonStyle(.borderless)` 或 `.plain` 限定
- **`.onTapGesture` 与 List 手势冲突**：优先 NavigationLink/Button 的系统手势
- **深色模式硬编码颜色**：`Color(red:)` 不随主题；用语义色 `.primary/.secondary/.background` 或 Asset Catalog

## 相关文档

- 📄 [04-swiftui-state-api.md](../language-concepts/04-swiftui-state-api.md) — 数据流工具全表
- 📄 [02-swiftdata-observability.md](./02-swiftdata-observability.md) — SwiftData 速查
- 📄 [02-troubleshooting.md](../quick-references/02-troubleshooting.md) — UI 故障排查


<!-- full-library-explanation -->
## 把 API 拼成可操作的界面

速查表中的链式片段省略了上下文；下面是完整 View 类型，放入导入 SwiftUI 的 iOS 工程后可作为页面展示（无需复制前面的占位 Badge/Banner）。

```swift
import SwiftUI

struct ReadingSettings: View {
    @State private var name = ""
    @State private var reminders = false
    @State private var pages = 10
    var body: some View {
        Form {
            TextField("计划名称", text: $name)
            Toggle("提醒我阅读", isOn: $reminders)
            Stepper("每天 \(pages) 页", value: $pages, in: 1...100)
            Text(name.isEmpty ? "请填写名称" : "\(name)：每天 \(pages) 页")
        }
    }
}
```

TextField 和 Stepper 通过 Binding 写回同一份状态，Text 从状态推导说明，无须额外保存 summary。建议在 Xcode 的目标模拟器或设备验收：输入名称后说明是否更新、步进器是否低于 1、切换提醒是否保留名称，以及大字体与深色模式下能否操作。本仓库没有 Apple SDK 运行记录，因此这些是待执行的验收条件，不是已通过结论。

列表身份必须在插入、排序时保持稳定：`id: \.self` 适合确实唯一且稳定的值，重复字符串不满足条件。装饰图片可标记为不参与无障碍阅读，操作按钮要有可读标签；redacted 只改变视觉呈现，不等于隐藏敏感值或禁用交互。真实加载态应同时设计交互规则与辅助功能说明。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
