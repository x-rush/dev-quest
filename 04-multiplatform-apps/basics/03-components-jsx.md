# 核心组件、JSX 与 Flexbox 布局

## 先理解，再动手

JSX 表达组件树，View 组织布局，Text 显示文字。原生布局中的尺寸、主轴和交叉轴需要结合父容器理解。

**本节自测**：做一行图标与可换行标题，再改为纵向排列。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

能用 flexDirection 解释排列变化，并观察长文本是否挤出按钮。

</details>

> **文档简介**: 系统学习 React Native 的核心组件（View/Text/Image/ScrollView/FlatList）与样式系统，掌握移动端 Flexbox 布局思维
>
> **目标读者**: 已能运行 RN 工程、需要搭建真实界面的初学者
>
> **前置知识**: 完成 [02-first-app](./02-first-app.md)，有 Web Flexbox 经验更佳

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#核心组件` `#Flexbox` `#FlatList` `#样式` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 区分 RN 五大基础组件的职责与适用场景
- ✅ 用 Flexbox 实现常见的移动端布局（列表、九宫格、底部固定栏）
- ✅ 用 FlatList 渲染长列表并理解其性能价值
- ✅ 知道 Web CSS 与 RN 样式的关键差异

## 🔍 核心组件速览

| 组件 | 类比 Web | 用途 |
|------|---------|------|
| `View` | `div` | 布局容器，支持 Flexbox |
| `Text` | `p`/`span` | 唯一能渲染文本的组件 |
| `Image` | `img` | 网络图/本地资源/URI 图片 |
| `ScrollView` | overflow 滚动区 | 全量渲染内容的滚动容器 |
| `FlatList` | 无直接对应 | 虚拟化长列表，按需渲染 |

**核心规则**: RN 中文本必须包在 `<Text>` 里，`<View>hello</View>` 会直接报错。

## 💻 样式与 Flexbox

RN 样式是 CSS 的子集，没有单位（数字 = 密度无关像素 dp），不支持伪类与选择器，属性名一律驼峰。

```tsx
import { StyleSheet, Text, View } from 'react-native';

function LayoutDemo() {
  return (
    // 默认 flexDirection 是 'column'（Web 默认 row），这是新手第一大坑
    <View style={styles.page}>
      <View style={styles.header}>
        <Text style={styles.headerText}>顶部栏</Text>
      </View>
      <View style={styles.body}>
        <View style={styles.card}>
          <Text>卡片一：flex:1 平分剩余空间</Text>
        </View>
        <View style={styles.card}>
          <Text>卡片二</Text>
        </View>
      </View>
      <View style={styles.footer}>
        <Text>底部固定栏</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1 },
  header: { height: 56, backgroundColor: '#4A90D9', justifyContent: 'center', alignItems: 'center' },
  headerText: { color: '#fff', fontSize: 18 },
  body: { flex: 1, flexDirection: 'row', padding: 12, gap: 12 },
  card: { flex: 1, backgroundColor: '#f0f2f5', borderRadius: 8, padding: 16 },
  footer: { height: 64, backgroundColor: '#eee', justifyContent: 'center', alignItems: 'center' },
});
```

**Web ↔ RN 差异对照**:

- `flexDirection` 默认 `column`（Web 默认 `row`）
- 主轴为 column 时，`alignItems`/`justifyContent` 的作用方向与 Web 直觉相反
- 无 `position: static`；默认 `relative`，`absolute` 相对父容器定位
- 支持简写 `flex: 1`（等价 `flexGrow: 1, flexShrink: 1, flexBasis: 0%`）
- 尺寸无 `px`/`rem`，纯数字按 dp/pt 处理；可用 `PixelRatio` 换算

## 💻 Image 的三种来源

```tsx
import { Image } from 'react-native';

// 1. 本地静态资源（构建期打包，必须用 require 且路径为字面量）
const imageExamples = <>
<Image source={require('./assets/logo.png')} style={{ width: 40, height: 40 }} />

// 2. 网络图片（必须显式声明宽高）
<Image
  source={{ uri: 'https://example.com/avatar.png' }}
  style={{ width: 48, height: 48, borderRadius: 24 }}
/>

// 3. base64 / data URI
<Image source={{ uri: 'data:image/png;base64,iVBORw0KG...' }} style={{ width: 24, height: 24 }} />
</>;
```

## 💻 ScrollView vs FlatList

**ScrollView**: 一次性渲染全部子元素。适合表单、设置页等确定数量的内容。

**FlatList**: 只渲染可视区域附近的条目。列表超过 20 条就应使用 FlatList。

```tsx
import { FlatList, Text, View } from 'react-native';

interface Todo {
  id: string;
  title: string;
  done: boolean;
}

const TODOS: Todo[] = Array.from({ length: 200 }, (_, i) => ({
  id: `${i}`,
  title: `任务 ${i + 1}`,
  done: i % 3 === 0,
}));

function TodoList() {
  return (
    <FlatList
      data={TODOS}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <View style={{ padding: 16, borderBottomWidth: 1, borderColor: '#eee' }}>
          <Text style={{ textDecorationLine: item.done ? 'line-through' : 'none' }}>
            {item.title}
          </Text>
        </View>
      )}
      // 性能相关 props 的完整清单见 reference 组件 Props 全表
      initialNumToRender={10}
      getItemLayout={(data, index) => ({
        length: 57, // 条目固定高度时可指定，跳过测量
        offset: 57 * index,
        index,
      })}
      ListEmptyComponent={<Text>暂无待办</Text>}
      ItemSeparatorComponent={() => <View style={{ height: 1, backgroundColor: '#eee' }} />}
    />
  );
}
```

FlatList 性能 props（`windowSize`、`removeClippedSubviews` 等）的完整参数表见 [组件 Props 全表](../reference/language-concepts/02-components-props.md)。

## 🎨 最佳实践

列表中的 key 用来识别项目身份，插入或排序后仍应对应同一条数据；用数组下标可能让输入状态跟错行。大量内容用虚拟列表减少同时挂载的项目，并通过滚动检查空白、复用和触控行为。

StyleSheet 有助于组织与检查样式，动态样式对象也合法；是否值得稳定引用要看实际渲染成本。网络图需要可确定的布局尺寸，测量布局用 onLayout，不靠猜测延时。长列表的页头可交给列表自身，避免外层同向滚动容器削弱虚拟化。

## ❓ 常见问题

### Q1: 为什么我的元素不显示？
**A**: 三查——父容器是否有 `flex: 1` 撑开、元素是否有显式宽高或 flex、`Text` 是否存在。RN 没有 Web 的"内容自动撑高"兜底那么宽松。

### Q2: 阴影样式在 Android 上不生效？
**A**: Android 只支持 `elevation`，iOS 用 `shadowColor/shadowOffset/shadowOpacity/shadowRadius`，两端需分别设置。

### Q3: FlatList 滑动掉帧怎么办？
**A**: `getItemLayout` 跳过测量、`renderItem` 里的组件用 `React.memo`、图片用固定宽高，进阶优化见 [07-advanced-features](./07-advanced-features.md)。

## 🎯 练习与实践

### 练习一：个人资料卡

**任务要求**:
1. 用 View/Image/Text 实现一张资料卡：头像（网络图）、姓名、简介、三个横排统计数字
2. 头像圆形，卡片圆角带 `elevation` 阴影

**评估标准**: 布局在 Android 与 iOS 两端观感一致。

### 练习二：长列表性能对比

**任务要求**:
1. 分别用 ScrollView 和 FlatList 渲染 500 条数据
2. 用开发者菜单的 "Show Perf Monitor" 对比两端帧率

**提示**: ScrollView 渲染 500 条会有明显卡顿甚至 OOM，这正是虚拟化存在的意义。

---

## 🔗 相关文档

- 📄 **[状态与 Hooks](./04-state-hooks.md)**: 下一课，让组件动起来
- 📄 **[组件 Props 全表](../reference/language-concepts/02-components-props.md)**: 本文组件的完整属性字典
- 📄 **[React Navigation API 速查](../reference/framework-essentials/02-navigation-essentials.md)**: 搭配导航组件使用
- 📄 **[TS 类型模式](../reference/language-concepts/04-typescript-patterns.md)**: 给组件 Props 加类型

> 💡 **学习建议**: 每学一个组件就在练习 App 里造一个真实场景的小界面，比通读文档十遍都有效。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
