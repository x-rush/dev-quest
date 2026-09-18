# 样式与布局模型 — Yoga、Flexbox 子集与平台差异

> **难度**: ⭐ | **前置**: 读过[核心组件与 Flexbox 教程](../../basics/03-components-jsx.md)更佳

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Yoga` `#Flexbox` `#StyleSheet` `#平台差异` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

RN 样式模型 = **CSS 子集 + 无级联**，由 Yoga 布局引擎在 C++ 层统一计算（三端一致）：

- **不是 CSS**：没有 Web 式选择器和通用级联；嵌套 Text 的文字样式存在继承；样式是组件的 JS 对象属性，作用域天然隔离
- **Yoga 实现 Flexbox 子集**：主流 flex 属性齐备；与 Web 的关键默认差异——`flexDirection` 默认为 `column`（Web 是 `row`）
- **无单位数值**：数值布局尺寸通常是密度无关的逻辑单位；部分属性也接受百分比等指定形式，三端自动映射到物理像素
- **StyleSheet**：模块级创建样式表；数组样式实现条件叠加，后者覆盖前者
- **平台差异集中在修饰层**：阴影、模糊、安全区、状态栏等"外壳"能力各端参数不同（iOS shadow* / Android elevation）

## 📖 语法/签名

```tsx
// StyleSheet.create：类型检查 + 常量化（对象字面量 key 即样式名）
const styles = StyleSheet.create({
  card: { flexDirection: 'row', padding: 12, gap: 8 },   // 默认主轴是纵向，显式改横向
  title: { fontSize: 16, lineHeight: 22 },               // 文字始终成对给 fontSize + lineHeight
});

// 合并规则：数组叠加，后者覆盖同名属性；false/null 项被忽略
<View style={[styles.card, isActive && styles.cardActive]} />
```

```ts
// 平台差异的标准收敛写法
import { Platform, StyleSheet } from 'react-native';

const shadow = Platform.select({
  ios: { shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 8, shadowOffset: { width: 0, height: 2 } },
  android: { elevation: 4 },
  default: {},
});
```

## 💡 示例

```tsx
// 响应式两栏：用 flex 权重而非固定宽度，天然适配三端屏幕宽度
import { View, Text, StyleSheet, useWindowDimensions } from 'react-native';

function StatRow({ label, value }: { label: string; value: string }) {
  const { width } = useWindowDimensions(); // 旋转/分屏自动触发的响应式尺寸
  const stacked = width < 400;

  return (
    <View style={[styles.row, stacked && styles.column]}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  column: { flexDirection: 'column', alignItems: 'flex-start' }, // 窄屏改纵向
  label: { flex: 1, color: '#666' },
  value: { fontWeight: '600' },
});
```

## ⚠️ 常见陷阱

- **按 Web 习惯假设默认主轴**：RN 的 flexDirection 默认 column；`row` 需显式声明
- **写死像素尺寸做适配**：用 flex/gap/百分比 + useWindowDimensions，避免硬编码宽度
- **写死过小的 lineHeight**：字体度量与系统缩放有差异，应检查多语言、大字号，必要时设置合适行高
- **忽略阴影 API 的平台范围**：传统 shadow*、elevation 及较新 boxShadow 的支持不同，按实际 RN/系统版本核对并封装
- **以为样式会"继承"**：父 View 的样式不影响子 Text，除非显式传递（Text 内嵌套除外，文本属性可在嵌套 Text 间继承）
- **把内联样式当成必然性能故障**：静态样式可用 StyleSheet.create 便于复用与检查，动态值可内联；是否需要稳定引用应由测量决定

<!-- full-library-explanation -->
## 沿父级约束找布局问题

子元素 `flex: 1` 需要父容器有可分配空间。一个 ScrollView 还需要高度受约束；只在最里面加 flex，不能修复外层无限延伸。调试时给每层暂时加边框，从根容器向内看尺寸，区分视口与内容容器。

样式数组按顺序覆盖同名属性，不会累加 padding。`[{padding: 8}, {padding: 12}]` 最终为 12；布局尺寸通常用逻辑单位，百分比还取决于父级约束。字体缩放和屏幕密度是两件事。

练习：给示例传入一段长标题，测试窄屏、横屏和系统大字体。验收：重要内容可读，必要时换行或改纵向排列；不能仅用缩小字号“修好”溢出。记录断点为什么取该值，它是内容约束的选择，不是通用设备分类。

## 🔗 相关条目

- 📄 [核心组件 Props 全表](./02-components-props.md) — 各组件可用的样式属性清单
- 📄 [RN 框架入门](../../frameworks/01-react-native-basics.md) — StyleSheet 规范的任务式展开
- 📄 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md) — 哪些样式属性触发昂贵的重布局
- 📄 [组件生命周期](./06-component-lifecycle.md) — 样式对象引用与重渲染的关系

*延伸: React Native 官方文档 "Style" · "Layout with Flexbox" · Yoga 引擎文档*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
