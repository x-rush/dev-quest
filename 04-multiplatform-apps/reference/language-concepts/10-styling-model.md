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

RN 样式模型 = **CSS 子集 + 无级联**，使用 Yoga 进行布局计算；字体、原生组件和适配层仍可能产生平台差异：

- **不是 CSS**：没有 Web 式选择器和通用级联；嵌套 Text 的文字样式存在继承；样式是组件的 JS 对象属性，作用域天然隔离
- **Yoga 实现 Flexbox 子集**：主流 flex 属性齐备；与 Web 的关键默认差异——`flexDirection` 默认为 `column`（Web 是 `row`）
- **无单位数值**：数值布局尺寸通常是密度无关的逻辑单位；部分属性也接受百分比等指定形式，由目标平台映射到物理像素，不能据此保证截图一致
- **StyleSheet**：模块级创建样式表；数组样式实现条件叠加，后者覆盖前者
- **平台差异集中在修饰层**：阴影、模糊、安全区、状态栏等"外壳"能力各端参数不同（iOS shadow* / Android elevation）

## 📖 语法/签名

```tsx
// StyleSheet.create：类型检查 + 常量化（对象字面量 key 即样式名）
const styles = StyleSheet.create({
  card: { flexDirection: 'row', padding: 12, gap: 8 },   // 默认主轴是纵向，显式改横向
  title: { fontSize: 16, lineHeight: 22 },               // 指定字号与行高后仍需检查大字体
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
// 局部组件：按窗口宽度切换方向，仍需平台验收
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
  label: { flexShrink: 1, color: '#666' },
  value: { fontWeight: '600' },
});
```

## 从窗口布局走到容器约束

前置产物是已有 RN 工程中的可见屏幕。把 StatRow 与 styles 保存进同一个 `src/StatRow.tsx` 文件，给函数加 export；现有屏幕导入它，放在 padding 为 16 的 View，传入 `label="本月已完成的学习任务与复习记录"` 和 `value="128 项"`。这是组件片段，不含工程入口。

1. **先观察横排。** 暂时令 stacked 为 false。输入是两个字符串与父容器宽度，输出是横排 Text。label 的 flexShrink 允许横向空间不足时收缩换行；不用 flex: 1，避免切成 column 后无意分配纵向剩余空间。
2. **恢复断点。** 模拟器旋转或调整支持调整大小的窗口。宽度低于 400 时纵排，否则横排。断点是内容选择，不是设备类别；缩放截图不会触发真实窗口变化。
3. **扩大系统字体。** 检查两个文本读全且不重叠。很长的 value 也可能需要 flexShrink，或更早切纵排；用单行截断隐藏重要内容不算通过。
4. **放进窄卡片。** 大窗口中缩窄父卡片，窗口断点可能仍选横排。若组件应依据自身宽度排列，改由父容器 onLayout 提供 width；记录窗口与容器约束的区别。

| 失败现象 | 回查输入与约束 | 下一步观察 |
|---|---|---|
| flex 看起来无效 | 父容器是否有可分配空间 | 从根向内加临时边框检查宽高 |
| active 样式不生效 | 数组后项是否覆盖同名键 | 对调 padding 8/12 的样式顺序，最终值随最后一项变化 |
| 横屏正常，窄卡片溢出 | 是否把窗口宽度当组件宽度 | 使用真实容器约束后长标题能换行 |
| Android/iOS 换行不同 | 字体、缩放、字重与宽度 | 分平台记录，不假定 Yoga 保证像素一致 |

提交四项观察：窄屏、横屏、大字体、大窗口里的窄卡片。每项写输入尺寸、排列方向、是否读全内容，失败时指出约束来自哪层。布局验收后再加入阴影，避免视觉修饰掩盖尺寸问题。

**验证边界：** 本轮未构建或运行 RN/鸿蒙工程，未实测旋转与字体缩放。依据官方 [Style](https://reactnative.dev/docs/style)、[Flexbox](https://reactnative.dev/docs/flexbox) 和 [useWindowDimensions](https://reactnative.dev/docs/usewindowdimensions) 核对；以上验收仍待各目标平台执行。

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
