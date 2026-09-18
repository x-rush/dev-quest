# React Native 框架入门 — 组件、样式与 Flexbox

## 先看框架承担哪部分职责

**原生组件与布局**：React Native 使用平台控件与自己的布局规则。共享 React 写法，不代表 DOM、CSS 和浏览器 API 都能直接搬过来。

**最小练习与预期结果**：在目标设备测试长文本、窄屏和输入键盘；内容不遮挡操作，文本处于 Text 组件内。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 以任务为导向掌握 React Native 的组件模型、StyleSheet 样式体系与移动端 Flexbox 布局，写出结构清晰、三端一致的界面代码
>
> **目标读者**: 已完成模块入门路径、准备系统梳理 RN 界面开发知识的开发者
>
> **前置知识**: 已完成 [核心组件与 Flexbox 初识](../basics/03-components-jsx.md)，有 React 函数组件基础

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐ |
| **标签** | `#ReactNative` `#StyleSheet` `#Flexbox` `#组件` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 学习目标

- ✅ 熟练组合核心组件搭建真实界面（组件属性全表见 [reference](../reference/language-concepts/02-components-props.md)）
- ✅ 用类型安全的 `StyleSheet` 管理样式，避免内联对象的重复创建
- ✅ 掌握移动端 Flexbox 与 Web 的差异，能实现常见移动布局
- ✅ 用 `Platform` 与 `useColorScheme` 做平台与暗黑模式适配

## 🛠️ 组件组合：从静态到交互

界面开发的核心是把核心组件（View/Text/Image/Pressable/ScrollView）组合成可复用单元。组件完整 API 速查见 [RN 核心 API 字典](../reference/language-concepts/01-rn-core-api.md)。

```tsx
// components/UserCard.tsx —— 一个可复用的用户卡片
import { Pressable, Image, Text, View, StyleSheet } from 'react-native';

interface UserCardProps {
  avatar: string;      // 头像 URL
  name: string;        // 用户名
  onPress?: () => void; // 点击回调，可选则不渲染按压反馈
}

export function UserCard({ avatar, name, onPress }: UserCardProps) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
    >
      {/* 推荐用 expo-image 替代内置 Image：自带磁盘缓存与占位图 */}
      <Image source={{ uri: avatar }} style={styles.avatar} />
      <View style={styles.info}>
        <Text style={styles.name}>{name}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: { flexDirection: 'row', alignItems: 'center', padding: 12, gap: 12 },
  cardPressed: { opacity: 0.6 },
  avatar: { width: 44, height: 44, borderRadius: 22 },
  info: { flex: 1 },
  name: { fontSize: 16, fontWeight: '600' },
});
```

**关键点解析**：
- `Pressable` 是新架构推荐的触控组件，函数式 `style` 可拿到 `pressed` 状态
- `gap` 在现行 RN 完整支持，替代手动 margin 拼间距
- 数组样式 `[styles.card, pressed && styles.cardPressed]` 是条件样式惯用法，`false` 项会被忽略

## 🎨 StyleSheet：样式管理规范

**为什么不用内联对象**：`style={{ padding: 12 }}` 每次渲染都创建新对象，破坏渲染器对样式树的复用；`StyleSheet.create` 在模块级创建一次，且提供静态检查。

```tsx
// 样式复用与合并的四种姿势
const styles = StyleSheet.create({
  base: { padding: 16, borderRadius: 8 },
  primary: { backgroundColor: '#2563eb' },
  text: { fontSize: 14, lineHeight: 20 }, // 始终写 lineHeight，三端文字度量一致
});

// 1. 数组合并（后者覆盖前者）
<View style={[styles.base, styles.primary]} />

// 2. 条件拼接
<View style={[styles.base, isDark && { backgroundColor: '#111' }]} />

// 3. StyleSheet.compose —— 与数组等价，利于调试器展示
<View style={StyleSheet.compose(styles.base, styles.primary)} />

// 4. 平台专属样式文件：styles.ios.ts / styles.android.ts
//    Metro 按扩展名自动解析，import 语句保持不变；鸿蒙端（RNOH）命中 .android.ts
import { styles } from './styles';
```

## 📐 Flexbox 布局：移动端差异

RN 的 Flexbox 与 Web 同源，但关键默认值不同，这是布局 bug 的头号来源：

| 属性 | Web 默认 | RN 默认 | 实践含义 |
|------|---------|---------|---------|
| `flexDirection` | `row` | **`column`** | 移动界面天然纵向滚动 |
| `alignContent` | `stretch` | `flex-start` | — |
| `flexShrink` | `1` | `0` | 文本溢出需手动 `flexShrink: 1` |

```tsx
// 经典"头部固定 + 内容滚动 + 底部操作栏"骨架
import { View, Text, ScrollView, StyleSheet } from 'react-native';

export function ScreenSkeleton() {
  return (
    <View style={styles.screen}>
      <View style={styles.header}><Text style={styles.title}>标题</Text></View>
      {/* flex: 1 让滚动区吃掉剩余空间，ScrollView 必须有明确高度约束 */}
      <ScrollView contentContainerStyle={styles.content}>
        <Text>滚动内容…</Text>
      </ScrollView>
      <View style={styles.footer} />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },                  // 撑满父容器，一切布局的起点
  header: { padding: 16, paddingTop: 60 },
  title: { fontSize: 20, fontWeight: '700' },
  content: { padding: 16, gap: 8 },     // contentContainerStyle 作用于滚动内容
  footer: { height: 56, backgroundColor: '#f1f5f9' },
});
```

**文本截断配方**：`numberOfLines={1}` + `ellipsizeMode="tail"`；若文本在 row 中溢出，给包裹它的 `View` 设 `flex: 1` 或 `flexShrink: 1`。

## 🔀 平台与暗黑模式适配

```tsx
import { Platform, useColorScheme, StyleSheet } from 'react-native';

// Platform.select：按平台取值；鸿蒙端（RNOH）命中 android 分支
const shadow = Platform.select({
  ios: { shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 8 },
  android: { elevation: 4 }, // 阴影 API 两端不通用，是最高频适配点
});

// useColorScheme：跟随系统外观；hairlineWidth 画出 0.5px~1px 的细分隔线
function useTheme() {
  const dark = useColorScheme() === 'dark';
  return {
    dark,
    background: dark ? '#0f172a' : '#ffffff',
    text: dark ? '#e2e8f0' : '#0f172a',
    hairline: StyleSheet.hairlineWidth,
  };
}
```

## ✅ 最佳实践

布局优先表达相对关系：容器如何伸缩、内容如何换行、长列表如何滚动。固定浮层可以使用绝对定位，但把整页位置写死会在字体缩放和不同屏幕上暴露问题。用小屏和大字体检查按钮仍可触及、文字没有遮挡。

样式既可集中定义，也可按状态动态生成；不要把内联对象本身当错误。长列表避免再包同向普通滚动容器，用列表的页头/页尾表达混排内容，并在真机检查滚动与点击。

## ❓ 常见问题

**Q1: 为什么我的 `row` 布局里文字不换行直接溢出？**
A: RN 默认 `flexShrink: 0`。给文本容器加 `flex: 1`，并保留 `numberOfLines` 限制行数。

**Q2: iOS 有阴影 Android 没有？**
A: 两端阴影 API 不互通（`shadow*` vs `elevation`），用 `Platform.select` 分别设置。

**Q3: 状态栏内容被刘海遮挡？**
A: 用 `react-native-safe-area-context` 的 `SafeAreaView` 包裹根布局，不要手写 paddingTop 常量。

---

## 🔗 相关文档

- 📖 [核心组件 Props 全表](../reference/language-concepts/02-components-props.md) — 本文组件用法的完整属性字典
- 📖 [RN 核心 API 字典](../reference/language-concepts/01-rn-core-api.md) — Platform/Dimensions 等适配 API 速查
- 📖 [Hooks 速查](../reference/language-concepts/03-hooks-reference.md) — useColorScheme 等官方 Hook 详解
- 📄 [核心组件、JSX 与 Flexbox 布局](../basics/03-components-jsx.md) — 本文的入门版教程
- 📄 [状态管理 — Hooks 与自定义 Hook](../basics/04-state-hooks.md) — 让界面动起来的下一步
- 🚀 [待办应用实战](../projects/01-todo-app.md) — 用本文知识交付第一个完整项目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
