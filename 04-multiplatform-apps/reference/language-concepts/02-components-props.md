# 核心组件 Props 全表

> **难度**: ⭐ | **前置**: 已了解核心组件用途（[03-components-jsx](../../basics/03-components-jsx.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Props` `#View` `#Text` `#Image` `#FlatList` `#ScrollView` `#KeyboardAvoidingView` `#StatusBar` |
| **更新日期** | `2026年9月` |

## View

| Prop | 类型 | 说明 |
|------|------|------|
| `style` | Style \| Style[] | Flexbox 布局、背景、边框（数组后者覆盖前者） |
| `onLayout` | `(e) => void` | 布局完成回调，`e.nativeEvent.layout` 含 x/y/width/height |
| `pointerEvents` | `'auto' \| 'none' \| 'box-none' \| 'box-only'` | 控制触摸穿透 |
| `testID` | string | E2E 测试定位 |
| `accessibilityLabel` | string | 无障碍朗读文本 |
| `hitSlop` | object | 扩大触摸热区，如 `{ top: 10, left: 10 }` |

**陷阱**: `pointerEvents` 是 View 的 prop 而非 style 属性；`box-none` 只允许子元素响应触摸，是最常用的覆盖层配置。

## Text

| Prop | 类型 | 说明 |
|------|------|------|
| `numberOfLines` | number | 截断行数，配合 `ellipsizeMode` |
| `ellipsizeMode` | `'head' \| 'middle' \| 'tail' \| 'clip'` | 截断省略位置，默认 `tail` |
| `selectable` | boolean | 文本是否可长按选择 |
| `adjustsFontSizeToFit` | boolean | 自适应缩放字号以适配行宽（iOS/Android 支持度有差异） |
| `onLongPress` / `onPress` | function | Text 也可响应点击（内嵌可点链接常用） |

```tsx
<Text numberOfLines={1} ellipsizeMode="middle" style={styles.path}>
  /very/long/file/path/in/deep/directory.txt
</Text>
```

**陷阱**: 嵌套 Text 继承外层样式；`fontVariant: ['tabular-nums']` 让数字等宽，金额列表必备。

## Image

| Prop | 类型 | 说明 |
|------|------|------|
| `source` | `require(...)` \| `{ uri }` | 本地资源必须字面量路径；网络图必须给宽高 |
| `resizeMode` | `'cover' \| 'contain' \| 'stretch' \| 'center'` | 缩放模式，默认 `cover` |
| `onLoad` / `onError` | function | 加载回调，错误兜底必备 |
| `loadingIndicatorSource` | ImageSource | 加载中占位图 |
| `fadeDuration` | number | Android 渐显时长（ms） |

**陷阱**: `require()` 参数必须是静态字符串字面量，模板字符串拼接路径在构建期无法解析。

## TextInput

| Prop | 类型 | 说明 |
|------|------|------|
| `value` / `onChangeText` | string / `(text) => void` | 受控输入标配 |
| `keyboardType` | `'default' \| 'numeric' \| 'email-address' \| 'decimal-pad' …` | 键盘类型 |
| `secureTextEntry` | boolean | 密码输入 |
| `multiline` | boolean | 多行，行数配 `numberOfLines`（Android） |
| `returnKeyType` | `'done' \| 'search' \| 'next' …` | 回车键文案 |
| `onSubmitEditing` | function | 回车提交 |
| `autoFocus` | boolean | 挂载即聚焦 |

**陷阱**: 受控模式下 `value` 与 `onChangeText` 必须成对；iOS 多行输入的 `clearButtonMode` 无效。

## ScrollView

| Prop | 类型 | 说明 |
|------|------|------|
| `horizontal` | boolean | 横向滚动 |
| `showsVerticalScrollIndicator` | boolean | 滚动条显隐 |
| `refreshControl` | RefreshControl | 下拉刷新 |
| `onScroll` | function | 滚动回调，配 `scrollEventThrottle` |
| `scrollEventThrottle` | number | 回调节流（ms），iOS 实时监听建议设 ≤16 |
| `contentContainerStyle` | Style | 内容容器样式（padding/对齐写在这里） |
| `keyboardShouldPersistTaps` | `'never' \| 'always' \| 'handled'` | 点输入框外时键盘与点击的冲突处理 |

**陷阱**: `style` 与 `contentContainerStyle` 作用对象不同——外框样式写 `style`，内容间距写 `contentContainerStyle`。

## FlatList / SectionList

### 基础 Props

| Prop | 类型 | 说明 |
|------|------|------|
| `data` | Item[] | 数据源（FlatList）；SectionList 为 `sections` |
| `renderItem` | `(info) => ReactNode` | 条目渲染 |
| `keyExtractor` | `(item, index) => string` | 稳定 key，不设则用 index（有删除时闪烁） |
| `ListEmptyComponent` | ReactNode | 空状态 |
| `ListHeaderComponent` / `ListFooterComponent` | ReactNode | 头/尾组件 |
| `ItemSeparatorComponent` | Component | 分隔条（不随条目重渲染，优于手写 border） |
| `onEndReached` / `onEndReachedThreshold` | function / number | 触底加载更多，threshold 为视口高度比例 |
| `onRefresh` / `refreshing` | function / boolean | 下拉刷新受控模式 |
| `inverted` | boolean | 倒序渲染（聊天记录场景） |

### 性能 Props（长列表优化核心）

| Prop | 类型 | 说明 |
|------|------|------|
| `initialNumToRender` | number | 首屏渲染条数，默认 10 |
| `maxToRenderPerBatch` | number | 每批增量渲染上限 |
| `windowSize` | number | 渲染窗口 = 视口高度 × windowSize，默认 21；调小省内存、调大减白屏 |
| `getItemLayout` | function | 条目定高时跳过异步测量，跳转/滚动性能大增 |
| `removeClippedSubviews` | boolean | 裁剪视口外子视图（Android 收益明显） |
| `updateCellsBatchingPeriod` | number | 批次间隔（ms） |
| `viewabilityConfig` | object | 曝光判定规则，配 `onViewableItemsChanged` 做埋点 |

```tsx
<FlatList
  data={items}
  keyExtractor={(i) => i.id}
  initialNumToRender={12}
  windowSize={11}
  getItemLayout={(_d, index) => ({ length: ITEM_H, offset: ITEM_H * index, index })}
/>
```

**陷阱**: `getItemLayout` 要求条目高度严格一致（含分隔线），动态高度列表不可用；`windowSize` 过小会造成快速滑动白屏。

## Pressable / TouchableOpacity

| Prop | 类型 | 说明 |
|------|------|------|
| `onPress` / `onLongPress` / `onPressIn` / `onPressOut` | function | 完整按压生命周期 |
| `disabled` | boolean | 禁用 |
| `hitSlop` | object | 扩大热区 |
| `style`（Pressable） | function 形式 | `({ pressed }) => style`，按压态样式 |
| `activeOpacity`（TouchableOpacity） | number | 按压透明度，默认 0.2 |
| `android_ripple`（Pressable） | object | 原生水波纹 `({ color, borderless })` |

**陷阱**: Pressable 是官方推荐的新触控组件；TouchableOpacity 内不要再包 Pressable 造成双击态。

## KeyboardAvoidingView

| Prop | 类型 | 说明 |
|------|------|------|
| `behavior` | `'height' \| 'position' \| 'padding'` | 避让策略三模式：iOS 常用 `padding`（整体上移）；`position` 按绝对布局移动；`height` 压缩自身高度。Android 一般不走本组件，交给 manifest 的 `windowSoftInputMode: adjustResize` |
| `keyboardVerticalOffset` | number | 视图与键盘的额外偏移，补偿导航头部等高度 |
| `enabled` | boolean | 是否启用避让，常配 `Platform.OS` 条件开关 |

```tsx
<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : undefined} // Android 交给系统 adjustResize
  keyboardVerticalOffset={headerHeight}
  style={{ flex: 1 }}
>
```

**陷阱**: 三端避让机制不同，`behavior` 按 `Platform.select` 分支，勿一套通吃；嵌套两层 KeyboardAvoidingView 会双重避让，只保留最外层（见 [核心 API 字典](./01-rn-core-api.md) Keyboard 词条）。

## SafeAreaView

| Prop | 类型 | 说明 |
|------|------|------|
| （继承 View 全部 Props） | — | 本身是 View 的安全区特化，无独立 Prop |

**陷阱**: RN 内置 `SafeAreaView` 仅在 iOS 实现，只覆盖刘海，不处理底部 home indicator 与 Android 边到边；跨端通用方案是 `react-native-safe-area-context` 的 `SafeAreaProvider` / `SafeAreaView` / `useSafeAreaInsets()`（Expo 模板默认自带），内边距与缺口判断都从它取。

## StatusBar（组件形态）

| Prop | 类型 | 说明 |
|------|------|------|
| `barStyle` | `'default' \| 'light-content' \| 'dark-content'` | 状态栏前景内容颜色 |
| `backgroundColor` | string | 背景色，**仅 Android 生效** |
| `translucent` | boolean | Android 半透明沉浸式（内容绘制到状态栏下） |
| `hidden` | boolean | 隐藏状态栏 |
| `animated` | boolean | 属性变化时加过渡动画 |

**陷阱**: `backgroundColor`/`translucent` 是 Android 专属，iOS 静默忽略——"设置了没效果"先看平台；沉浸式行为与系统版本相关，逐端验证；Expo 工程推荐 `expo-status-bar` 封装（跨端语义统一）。

## RefreshControl

| Prop | 类型 | 说明 |
|------|------|------|
| `refreshing` | boolean | 受控刷新状态，**结束后必须置回 false**，否则指示器永转 |
| `onRefresh` | function | 下拉触发回调 |
| `tintColor` / `titleColor`（iOS） | color | iOS 指示器与标题颜色 |
| `colors` / `progressBackgroundColor`（Android） | color[] / color | Android 指示器颜色组与背景 |
| `progressViewOffset` | number | 指示器垂直偏移，嵌套吸顶头部时修正位置 |

**陷阱**: FlatList/ScrollView 自带 `onRefresh` + `refreshing` 受控属性已托管刷新指示器，不要同时又给 `refreshControl` prop 手挂组件，造成两套状态与重复触发。

## Switch / ActivityIndicator / Modal 速览

| 组件 | 关键 Props | 备注 |
|------|-----------|------|
| `Switch` | `value` `onValueChange` `trackColor` `thumbColor` | 受控开关 |
| `ActivityIndicator` | `size` `color` `animating` | 加载指示 |
| `Modal` | `visible` `animationType` `transparent` `onRequestClose` | Android 必须给 `onRequestClose` 处理返回键 |

## 🔗 相关文档

- 📄 **[RN 核心 API 字典](./01-rn-core-api.md)**: Platform/Dimensions 等 API
- 📄 **[Hooks 速查](./03-hooks-reference.md)**: 列表场景常用 Hook 组合
- 📄 **[列表性能模型](./12-list-performance-model.md)**: FlatList 虚拟化原理、白屏成因与换 FlashList 判断
- 📄 **[CLI 与调试速查](../quick-references/01-cli-and-debug-cheatsheet.md)**: 列表掉帧的调试手法
- 📄 **[核心组件与样式教程](../../basics/03-components-jsx.md)**: 这些组件的系统化学习路径

*相关教程: [组件 Props 在实战中的应用](../../basics/08-first-project.md)*
