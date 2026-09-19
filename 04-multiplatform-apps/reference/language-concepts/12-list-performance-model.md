# 列表性能模型 — FlatList 虚拟化与调参

> **难度**: ⭐⭐ | **前置**: 会用 FlatList 基础 Props（[02-components-props](./02-components-props.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#FlatList` `#虚拟化` `#列表性能` `#FlashList` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

FlatList 的核心是**虚拟化（windowing）**：只渲染视口附近的一小段数据，滚动时按批次增量渲染、卸载远离视口的条目。视图相关内存和渲染量受**渲染窗口大小**影响，数据数组和缓存仍随数据量增长——理解这一点，滚动空白常与补渲染跟不上有关；掉帧还可能来自昂贵计算、图片和布局，需要分别归因。

## 📖 原理与参数表

### 虚拟化原理

- **渲染窗口**：`windowSize` 以视口长度为单位配置目标范围；条目分批填充，不保证窗口立即全部挂载。远离窗口的条目可能卸载，默认首批条目还有保留优化
- **首批渲染**：挂载即渲染 `initialNumToRender` 条，建立首屏
- **增量批次**：滚动接近窗口边缘时，每 `updateCellsBatchingPeriod`（ms）补一批 `maxToRenderPerBatch` 条
- **虚拟化与复用**：FlatList 维护有限渲染窗口，离开窗口的条目可能卸载；FlashList 更强调复用已有 cell 承载不同项目，因此行内状态必须响应项目身份变化。不要把差异概括为“v1 只在原生层、v2 只在 JS 层”；具体实现与新架构要求需按所用版本核对。

### 性能参数逐项

| 参数 | 语义 | 默认 | 调节方向 |
|------|------|------|---------|
| `initialNumToRender` | 首批渲染数量；默认保留这些初始项以改善回顶体验，initialScrollIndex 等配置会影响行为 | 10 | 首屏条数固定的小卡片可调大；过大拖慢首屏 |
| `windowSize` | 渲染窗口 = 视口高度 × 该值 | 21 | 调大→白屏少、内存高；调小→省内存、快滚易白屏 |
| `maxToRenderPerBatch` | 每批增量渲染上限 | 10 | 调大→白屏少但每批 JS 工作量大、易掉帧 |
| `updateCellsBatchingPeriod` | 增量批次间隔（ms） | 50 | 调小→补渲染更密、更跟手，但 JS 更忙 |
| `getItemLayout` | 已知条目尺寸时提供 `(data, index) => {length, offset, index}`，跳过布局测量 | 无 | 可选优化；offset 必须包含分隔线尺寸，收益在目标设备测量 |
| `removeClippedSubviews` | 裁剪视口外子视图 | Android 常见默认值为 true；其他平台与当前版本须查官方 API | 先在目标设备记录内存、白屏、触摸和滚动结果；不能预先承诺收益 |
| `onEndReachedThreshold` | 触底加载的提前量（视口高度比例） | — | 配合分页请求，避免触底后等待感 |

### 白屏滚动：成因链与调参顺序

```
快速滚动 → 视口进入未渲染区 → JS 线程补渲染批次追不上 → 空白（白屏）
```

**调参顺序（先归因、后动手）**：

1. **确认尺寸是否确实固定**——已知尺寸再提供 `getItemLayout`，错误 offset 会破坏定位
2. **压单行渲染成本**：行组件 `memo` + 回调 `useCallback`、图片用缓存组件、行内少嵌套（见 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md)）
3. **调窗口**：`windowSize` 适度调大（如 11 → 21 已是默认，再往上要测内存）
4. **调批次**：`maxToRenderPerBatch` 调大、`updateCellsBatchingPeriod` 调小（滚动感更连续，代价是 JS 更忙）
5. **仍不能满足目标时评估其他列表实现**，使用相同输入、设备和交互比较，不以“千条”作为自动换库阈值

窗口与批次存在取舍，但白屏、掉帧、内存并非严格互斥；减少行内昂贵计算可能同时改善多项指标。每次只改变一个因素再比较。参数含义与取舍见[官方优化指南](https://reactnative.dev/docs/optimizing-flatlist-configuration)。

## 💡 示例

```tsx
const ITEM_H = 64; // 行高严格一致（含分隔线）

<FlatList
  data={messages}
  keyExtractor={(i) => i.id}
  // 仅在实际总行高等于 ITEM_H 时采用；收益需要设备测量
  getItemLayout={(_d, index) => ({ length: ITEM_H, offset: ITEM_H * index, index })}
  initialNumToRender={12}          // 首屏 12 条
  windowSize={21}                  // 默认窗口，白屏才考虑加大
  maxToRenderPerBatch={12}
  updateCellsBatchingPeriod={32}   // 补渲染更密
  renderItem={({ item }) => <MessageRow message={item} />}
  // MessageRow 可以是 memo 组件；renderItem 本身需要可调用的渲染函数
/>
```

**何时评估 FlashList**：条目上千、行结构复杂、`windowSize`/批次调参后白屏仍明显时，把它作为候选方案。FlashList v2 的新架构要求、JS 实现与 `estimatedItemSize` 迁移规则均会随版本变化，安装或升级前应对照所用版本的官方迁移说明。Expo 工程可用 `npx expo install @shopify/flash-list` 选择与 SDK 相容的包；随后在相同设备、数据量和交互脚本下比较首屏、滚动、内存与正确性。本文未提供 FlashList 的设备对比结果。

## ⚠️ 常见陷阱

- ❌ **把 `windowSize` 拉到 50 求稳**
  ✅ 窗口扩大可能减少空白，也会增加渲染和内存负担；按 profile 结果微调
- ❌ **动态高度列表硬塞 `getItemLayout`**
  ✅ 行高不一（含分隔线）时 `getItemLayout` 的 offset 全错，定位/跳转异常；改用测量或换 FlashList
- ❌ **`renderItem` 内联箭头函数 + 行组件未 memo**
  ✅ 可能增加更新计算；先看数据身份和分析结果，必要时稳定回调并缓存昂贵行组件
- ❌ **数据量一大就先换库**
  ✅ 先归因并建立基线，再比较候选实现，没有适用于所有设备的条目数阈值
- ❌ **滚动联动动画在 `onScroll` JS 回调里 setState**
  ✅ 帧级联动走 Reanimated `useAnimatedScrollHandler`（见 [动画与手势库](../library-guides/04-animation-gesture-libs.md)）

<!-- full-library-explanation -->
## 身份、渲染窗口与数据规模是三回事

虚拟化主要减少同时存在的视图和渲染工作，已下载的 `data` 数组仍占内存。把十万条数据放入 FlatList 不等于只持有一屏数据；服务端分页和列表虚拟化需要分别设计。

稳定 key 表示“这仍是同一条记录”。内联 `renderItem` 可能影响浅比较，却不会仅因函数引用变化就把所有行卸载重建。删除第一行后输入内容跑到下一行，优先检查是否用索引充当身份，而不是先加 memo。

练习：创建带输入框的列表，分别用索引和数据 ID 作为 key，编辑第三条后删除第一条。验收：内容跟随原记录；再快速滚动后返回，检查需要保存的草稿是否独立于临时行组件生命周期。FlashList 的回收意味着同一组件可能服务不同 item，局部状态也需处理身份变化。

## 实作：先保证选择状态，再比较滚动性能

前置：在已能运行的 RN 或 Expo 工程中替换一个屏幕，掌握 `useState`、不可变更新与 `FlatList`。产物是一份 1000 行、可选择与删除首项的列表，以及同设备上的参数对照记录。先用纯文本，排除网络图片和服务端请求的影响。

```tsx
import { useState } from 'react';
import { Button, FlatList, Pressable, Text, View } from 'react-native';

export default function ListLab() {
  const [rows, setRows] = useState(() => Array.from({ length: 1000 }, (_, i) => ({
    id: `row-${i}`, title: `记录 ${i}`,
  })));
  const [selectedId, setSelectedId] = useState<string | null>(null);
  return (
    <View style={{ flex: 1 }}>
      <Button title="删除首项" onPress={() => setRows(old => old.slice(1))} />
      <Text>已选：{selectedId ?? '无'}</Text>
      <FlatList
        data={rows}
        extraData={selectedId}
        keyExtractor={item => item.id}
        getItemLayout={(_, index) => ({ length: 64, offset: 64 * index, index })}
        renderItem={({ item }) => (
          <Pressable onPress={() => setSelectedId(item.id)}
            style={{ height: 64, justifyContent: 'center', paddingHorizontal: 16 }}>
            <Text numberOfLines={1}>{selectedId === item.id ? '✓ ' : ''}{item.title}</Text>
          </Pressable>
        )}
      />
    </View>
  );
}
```

本例未加分隔组件，总行高就是 64；若增加高 1 的分隔线，offset 应计入它，不能只改样式。若需要多行文本或动态字体扩展，先移除固定布局假设再实现测量。选中 ID 放在屏幕层，避免依赖可能卸载的行状态；`extraData` 显式传递 data 之外的渲染依赖。依据见 [FlatList API](https://reactnative.dev/docs/flatlist)。

| 输入或动作 | 可观察输出 | 失败回查 |
|---|---|---|
| 选择记录2，再删除首项 | 仍显示已选 row-2，勾选跟随记录2 | 是否用 index 作 key；是否原地修改 data |
| 滚远再返回 | row-2 仍被选中 | 是否把选择放进行内部，导致卸载后丢失 |
| 快速连续滚动10秒 | 记录是否空白、触摸是否延迟、内存峰值 | 区分补渲染不足、JS昂贵工作与图片内存 |
| 只把 windowSize 改成11后重复 | 对比同样10秒的结果，不预设一定更快 | 数据、构建模式、设备和滚动方式是否一致 |

先以 release 构建在目标设备记录 RN/Expo 版本、操作系统、数据量、参数和结果；开发模式的调试开销不能直接代表发布表现。没有性能分析工具时只记录肉眼空白与操作延迟，不虚构 FPS 或内存收益。完成正确性检查后进入[渲染性能](../../advanced-topics/performance/01-rendering-performance.md)，再逐项加入图片、复杂行和分页。

本轮仅核对官方资料与静态审阅，未启动 Metro、Android/iOS 构建或真机性能测量；代码和表格是复现入口，不能作为设备端性能验证记录。

## 🔗 相关条目

- 📄 **[核心组件 Props 全表](./02-components-props.md)** — FlatList 基础 Props 与性能 Props 速查
- 📄 **[渲染性能（解释篇）](../../advanced-topics/performance/01-rendering-performance.md)** — FlashList 对比的测量方案、掉帧归因清单
- 📄 **[动画与手势库](../library-guides/04-animation-gesture-libs.md)** — 滚动联动的帧级通道（worklet）
- 📄 **[CLI 与调试速查](../quick-references/01-cli-and-debug-cheatsheet.md)** — 列表掉帧的调试手法
- 📄 **[实战：聊天应用](../../projects/03-chat-app.md)** — 大列表替换 FlashList 的落地场景

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
