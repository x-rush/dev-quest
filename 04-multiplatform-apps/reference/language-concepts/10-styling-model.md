# 样式与布局模型 — Yoga、Flexbox 子集与平台差异

> **难度**: ⭐ | **前置**: 读过[核心组件与 Flexbox 教程](../../basics/03-components-jsx.md)更佳

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Yoga` `#Flexbox` `#StyleSheet` `#平台差异` |
| **更新日期** | `2026年9月` |

## 📌 定义

RN 样式模型 = **CSS 子集 + 无级联**，由 Yoga 布局引擎在 C++ 层统一计算（三端一致）：

- **不是 CSS**：无选择器、无继承、无伪类；样式是组件的 JS 对象属性，作用域天然隔离
- **Yoga 实现 Flexbox 子集**：主流 flex 属性齐备；与 Web 的关键默认差异——`flexDirection` 默认为 `column`（Web 是 `row`）
- **无单位数值**：所有尺寸是密度无关的逻辑像素，三端自动映射到物理像素
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
- **文字不加 lineHeight**：三端字体度量不同，只给 fontSize 会出现基线错位与裁切
- **阴影两端写法互斥**：Android 只认 elevation，iOS 用 shadow* 家族；统一封装，勿散落
- **以为样式会"继承"**：父 View 的样式不影响子 Text，除非显式传递（Text 内嵌套除外，文本属性可在嵌套 Text 间继承）
- **内联样式对象**：每渲染新建引用破坏样式复用与 diff；一律 StyleSheet.create（动态值用数组第二项）

## 🔗 相关条目

- 📄 [核心组件 Props 全表](./02-components-props.md) — 各组件可用的样式属性清单
- 📄 [RN 框架入门](../../frameworks/01-react-native-basics.md) — StyleSheet 规范的任务式展开
- 📄 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md) — 哪些样式属性触发昂贵的重布局
- 📄 [组件生命周期](./06-component-lifecycle.md) — 样式对象引用与重渲染的关系

*延伸: React Native 官方文档 "Style" · "Layout with Flexbox" · Yoga 引擎文档*
