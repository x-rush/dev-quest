# 列表性能模型 — FlatList 虚拟化与调参

> **难度**: ⭐⭐ | **前置**: 会用 FlatList 基础 Props（[02-components-props](./02-components-props.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#FlatList` `#虚拟化` `#列表性能` `#FlashList` |
| **更新日期** | `2026年9月` |

## 📌 定义

FlatList 的核心是**虚拟化（windowing）**：只渲染视口附近的一小段数据，滚动时按批次增量渲染、卸载远离视口的条目。内存占用与渲染量取决于**渲染窗口大小**而非数据总量——理解这一点，白屏与掉帧问题都能归因到同一句话：**渲染窗口追不上滚动速度**。

## 📖 原理与参数表

### 虚拟化原理

- **渲染窗口**：视口高度 × `windowSize`，窗口内的条目保持挂载，窗口外被卸载
- **首批渲染**：挂载即渲染 `initialNumToRender` 条，建立首屏
- **增量批次**：滚动接近窗口边缘时，每 `updateCellsBatchingPeriod`（ms）补一批 `maxToRenderPerBatch` 条
- **"回收"的语义**：FlatList 的回收发生在 **JS 层**——视口外 cell 被卸载、原位置留空白占位，滚回时组件重新挂载（React 实例不复用）。真正的**原生视图池复用**（cell 复用同一批原生视图、只换内容）是 FlashList 的机制，这是两者最大的模型差异

### 性能参数逐项

| 参数 | 语义 | 默认 | 调节方向 |
|------|------|------|---------|
| `initialNumToRender` | 首屏首批渲染条数；回到列表顶时也按此数量重置渲染区 | 10 | 首屏条数固定的小卡片可调大；过大拖慢首屏 |
| `windowSize` | 渲染窗口 = 视口高度 × 该值 | 21 | 调大→白屏少、内存高；调小→省内存、快滚易白屏 |
| `maxToRenderPerBatch` | 每批增量渲染上限 | 10 | 调大→白屏少但每批 JS 工作量大、易掉帧 |
| `updateCellsBatchingPeriod` | 增量批次间隔（ms） | 50 | 调小→补渲染更密、更跟手，但 JS 更忙 |
| `getItemLayout` | 条目**定高**时提供 `(data, index) => {length, offset, index}`，跳过异步测量 | 无 | 定高列表必给；跳转/滚动定位性能大增 |
| `removeClippedSubviews` | 裁剪视口外子视图 | false | Android 收益明显，iOS 需实测 |
| `onEndReachedThreshold` | 触底加载的提前量（视口高度比例） | — | 配合分页请求，避免触底后等待感 |

### 白屏滚动：成因链与调参顺序

```
快速滚动 → 视口进入未渲染区 → JS 线程补渲染批次追不上 → 空白（白屏）
```

**调参顺序（先归因、后动手）**：

1. **定高必给 `getItemLayout`**——异步测量本身是白屏放大器
2. **压单行渲染成本**：行组件 `memo` + 回调 `useCallback`、图片用缓存组件、行内少嵌套（见 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md)）
3. **调窗口**：`windowSize` 适度调大（如 11 → 21 已是默认，再往上要测内存）
4. **调批次**：`maxToRenderPerBatch` 调大、`updateCellsBatchingPeriod` 调小（滚动感更连续，代价是 JS 更忙）
5. **千条以上 / 复杂行 / 调参无解 → 换 FlashList**（判断依据见下）

**权衡三角**：白屏↓ 与 掉帧↓ 与 内存↓ 三者互斥——每一步调整都先测掉帧与内存，不做无归因的参数堆砌。

## 💡 示例

```tsx
const ITEM_H = 64; // 行高严格一致（含分隔线）

<FlatList
  data={messages}
  keyExtractor={(i) => i.id}
  // 定高列表：跳过异步测量，快速滚动/定位白屏显著减少
  getItemLayout={(_d, index) => ({ length: ITEM_H, offset: ITEM_H * index, index })}
  initialNumToRender={12}          // 首屏 12 条
  windowSize={21}                  // 默认窗口，白屏才考虑加大
  maxToRenderPerBatch={12}
  updateCellsBatchingPeriod={32}   // 补渲染更密
  renderItem={MessageRow}          // 行组件已 React.memo
/>
```

**何时换 FlashList**：条目上千、行结构复杂、`windowSize`/批次调参后白屏仍明显。FlashList 用原生回收视图池换内容，行高可预测是前提（`estimatedItemSize` 必须认真给，回收机制依赖行高估计准确）。Expo 工程用 `npx expo install @shopify/flash-list` 安装版本对齐的包；用法差异与实测对比见 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md)。

## ⚠️ 常见陷阱

- ❌ **把 `windowSize` 拉到 50 求稳**
  ✅ 白屏与掉帧互斥：窗口越大 JS 越忙、内存越高；按 profile 结果微调
- ❌ **动态高度列表硬塞 `getItemLayout`**
  ✅ 行高不一（含分隔线）时 `getItemLayout` 的 offset 全错，定位/跳转异常；改用测量或换 FlashList
- ❌ **`renderItem` 内联箭头函数 + 行组件未 memo**
  ✅ 每次重渲染全列表重建行实例；行组件 `React.memo` + 回调 `useCallback`
- ❌ **数据量一大就先换库**
  ✅ 先归因（掉帧 vs 白屏 vs 内存），千条以上复杂行才是 FlashList 的主场
- ❌ **滚动联动动画在 `onScroll` JS 回调里 setState**
  ✅ 帧级联动走 Reanimated `useAnimatedScrollHandler`（见 [动画与手势库](../library-guides/04-animation-gesture-libs.md)）

## 🔗 相关条目

- 📄 **[核心组件 Props 全表](./02-components-props.md)** — FlatList 基础 Props 与性能 Props 速查
- 📄 **[渲染性能（解释篇）](../../advanced-topics/performance/01-rendering-performance.md)** — FlashList 对比实测、掉帧归因清单
- 📄 **[动画与手势库](../library-guides/04-animation-gesture-libs.md)** — 滚动联动的帧级通道（worklet）
- 📄 **[CLI 与调试速查](../quick-references/01-cli-and-debug-cheatsheet.md)** — 列表掉帧的调试手法
- 📄 **[实战：聊天应用](../../projects/03-chat-app.md)** — 大列表替换 FlashList 的落地场景

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
