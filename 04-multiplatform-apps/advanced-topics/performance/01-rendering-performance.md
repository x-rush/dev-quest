# 渲染性能 — 帧率、列表与重渲染治理

> **文档简介**: 系统讲解 RN 渲染管线的性能模型：JS/UI 双线程分工、重渲染的成因与治理、长列表虚拟化与 UI 线程动画，把"跟手不卡顿"变成可复现的工程实践
>
> **目标读者**: 已具备完整开发经验、负责性能攻坚的开发者
>
> **前置知识**: 已读 [新架构解析](../architecture/01-new-architecture.md) 与 [框架进阶](../../frameworks/02-react-native-advanced.md)（Reanimated 基础）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 解释（advanced-topics） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#性能` `#渲染` `#FlashList` `#重渲染` `#Reanimated` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 用双线程模型给卡顿归因：JS 帧率 vs UI 帧率
- ✅ 治理重渲染：状态下放、memo、稳定引用三板斧
- ✅ 为长列表选对虚拟化方案并调参
- ✅ 建立性能测量闭环，杜绝"感觉卡"式优化

## 🧵 渲染管线与卡顿归因

新架构下（见 [架构解析](../architecture/01-new-architecture.md)），一帧的旅程：

```
JS 线程：执行 render 函数 → 产出组件树快照
    │ (JSI 直调，无桥)
C++ Fabric：Yoga 计算布局 → Shadow Tree commit
    │
UI 线程（主线程）：挂载视图 / 绘制
```

**归因口诀**：开发菜单开启双帧率监控，分别看 JS 与 UI 帧率——

- **JS 帧率低**：JS 线程忙（重渲染、复杂计算）→ 治理重渲染、拆分长任务
- **UI 帧率低**：主线程忙（过度绘制、大图解码、动画跑错线程）→ 降层级、换 UI 线程动画
- **两者都低**：先修 JS；JS 拥塞会拖累后续 commit，通常连带 UI

## 🔁 重渲染治理三板斧

```tsx
// 反面教材：三个常见"全屏重渲染"元凶
function Parent() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  return (
    <>
      {/* 元凶 1：搜索框每敲一键 → 整个 Parent 重渲染 → 沉重的 List 跟着重来 */}
      <SearchBar value={query} onChangeText={setQuery} />
      {/* 元凶 2：内联函数 props，子组件 memo 全部失效 */}
      <HeavyList onPress={() => console.log('x')} />
      {/* 元凶 3：结果与输入没有分离，输入即全屏重渲染 */}
    </>
  );
}

// 治理后：状态下放 + 子组件隔离
function ParentFixed() {
  const [results, setResults] = useState([]);
  return (
    <>
      {/* 输入状态移到 SearchBar 内部，Parent 只持有结果 */}
      <SearchBar onChangeResult={setResults} />
      <HeavyList results={results} />   {/* props 少而稳定，memo 生效 */}
    </>
  );
}

const HeavyList = memo(function HeavyList({ results }: Props) { /* … */ });
```

**三板斧清单**：
1. **状态下放**：把易变状态移到最小的共同父组件，甚至组件内部
2. **稳定引用**：`useCallback`/`useMemo` 包住传给 memo 子组件的函数与对象；列表行数据避免运行时拼装
3. **memo 隔离**：列表行、图表、输入区全部 `memo`，配合选择器订阅（`useCart((s) => s.count)` 而非解构 store）

**Context 的额外陷阱**：Provider 的 value 变化会让所有消费者重渲染——高频状态（输入、滚动位置）不要进 Context，用 zustand 选择器或组件内部 state。

## 📃 长列表虚拟化

| 方案 | 机制 | 适用 |
|------|------|------|
| `FlatList` | 视口 ± windowSize 区域渲染 | 通用，中等数据量 |
| `FlashList`（Shopify） | 单一回收视图池，cell 复用 | 千条以上、复杂行 |
| `SectionList` | 分组包装 | 联系人/分组场景 |

```tsx
// FlashList v2：JS-only 实现，无需 v1 的 estimatedItemSize（该 prop 已不存在）
import { FlashList } from '@shopify/flash-list';

<FlashList
  data={messages}
  keyExtractor={(m) => m.id}
  renderItem={renderItem}
  // 可预测行高时补 getItemLayout，滚动定位零测量
  getItemLayout={(_d, index) => ({ length: 72, offset: 72 * index, index })}
/>
```

**列表调参要点**：`windowSize`（默认 21 个视口）调小省内存但滑快时白屏；`initialNumToRender` 决定首屏成本，影响 TTI（与 [启动优化](./02-startup-optimization.md) 联动）；聊天倒置列表配方见 [聊天应用](../../projects/03-chat-app.md)。

## 🎬 动画线程：让 JS 挂了也不卡

```tsx
// 原则：动画数值只进共享值，绝不过 JS 线程
import Animated, { useSharedValue, useAnimatedStyle, withRepeat, withTiming } from 'react-native-reanimated';

function Spinner() {
  const rotation = useSharedValue(0);
  // 启动一次，之后每帧都在 UI 线程插值；JS 完全不参与
  rotation.value = withRepeat(withTiming(360, { duration: 1000 }), -1);

  const style = useAnimatedStyle(() => ({
    transform: [{ rotateZ: `${rotation.value}deg` }],
  }));
  return <Animated.View style={style} />;
}
```

**规避清单**：动画 width/height/margin（触发布局）→ 改 transform；setInterval 驱动动画 → 改共享值插值；列表滚动联动用 Reanimated 的 `useAnimatedScrollHandler`。

## 📏 测量闭环

1. **开发期**：DevTools Profiler 录制交互定位重渲染热点；Perf Monitor 看双线程帧率（工具见 [开发工具链](../../frameworks/04-devtools.md)）
2. **提交前**：关键页面基准脚本化，对比 PR 前后 commit 次数
3. **线上**：Sentry Performance 采集真实用户帧率/慢渲染，验证优化收益（接入见 [OTA 与可观测性](../../deployment/03-ota-updates-observability.md)）

## ✅ 要点回顾

- ✅ **先归因后优化**：JS 帧率 vs UI 帧率决定完全不同的药方
- ✅ **重渲染是万恶之源**：状态下放 > 稳定引用 > memo，顺序不能乱
- ✅ **千行以上列表上 FlashList**（v2 已无需行高估计，用法见 [列表性能模型](../../reference/language-concepts/12-list-performance-model.md)）
- ❌ **不要在生产验证前轻信 dev 数据**：dev 包 JS 执行慢数倍，结论不可信
- ❌ **不要优化没有基线的东西**：先测量、再优化、后复测，否则是玄学

## ❓ 常见问题

**Q1: 交互触发后两三帧才响应？**
A: 典型 JS 线程拥塞。把非紧急更新用 `startTransition`/`useDeferredValue` 降级，重活用 `requestIdleCallback` 错峰（`InteractionManager` 已从 RN 0.87 移除，见 [RN 核心 API](../../reference/language-concepts/01-rn-core-api.md)）。

**Q2: 图片滚动时闪/卡？**
A: 用 `expo-image`（内存/磁盘缓存 + 降采样）；确认给了明确宽高，避免解码后二次布局。

**Q3: 大量文本渲染慢？**
A: 长文本拆段 + `numberOfLines` 限制；富文本分页虚拟化，Hermes 下字符串操作成本不可忽视。

---

## 🔗 相关文档

- 📖 [核心组件 Props 全表](../../reference/language-concepts/02-components-props.md) — FlatList 调参属性字典
- 📖 [状态与数据请求库指南](../../reference/library-guides/01-state-and-data.md) — 选择器订阅与状态库分工
- 📄 [框架进阶 — 新架构、原生模块与动画](../../frameworks/02-react-native-advanced.md) — Reanimated 用法篇
- 📄 [聊天应用实战](../../projects/03-chat-app.md) — 本文手法在真实项目中的组合
- 🎓 [启动优化](./02-startup-optimization.md) — 性能的另一主战场
- 🎓 [新架构解析](../architecture/01-new-architecture.md) — 本文的管线模型出处
