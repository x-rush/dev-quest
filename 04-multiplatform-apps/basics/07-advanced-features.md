# 高级特性 — 新架构 Fabric、Hermes 与动画

## 先理解，再动手

新架构与动画工具解决不同层次的问题。先测出 JS 执行、布局或绘制哪个环节变慢，再选优化手段。

**本节自测**：在列表滚动时增加一次重计算，比较去掉计算后的响应。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

用可重复现象定位瓶颈；不能仅因使用新架构就宣称动画始终流畅。

</details>

> **文档简介**: 理解新架构渲染器 Fabric 与 Hermes 引擎如何影响应用性能，掌握 Reanimated 动画开发与交互流畅度的基本调优手法
>
> **目标读者**: 完成入门路径、关注"帧率与手感"的开发者
>
> **前置知识**: 完成 [06-native-modules](./06-native-modules.md)，理解 RN 渲染链路

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#Fabric` `#Hermes` `#Reanimated` `#性能优化` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 说清新架构三件套（Fabric/TurboModules/Codegen）各自的职责
- ✅ 解释 Hermes 字节码对启动速度与内存的意义
- ✅ 用 Reanimated 4 写出手势跟手动画，并用目标设备的采样数据判断是否达到体验目标
- ✅ 使用 Perf Monitor 与 DevTools 定位掉帧环节

## 🔍 核心概念

### Fabric — 新渲染器

**定义**: Fabric 是新架构的渲染器，负责把 React 组件树同步到原生视图。

**与旧渲染器的差异**:

| 能力 | 旧渲染器 | Fabric |
|------|---------|--------|
| 渲染提交 | 异步批量，双向桥 | C++ 同步管道，可同步测量/布局 |
| 优先级 | 全局统一 | 支持 Synchronous 渲染（如手势跟手） |
| 挂载 | JS → 原生命令队列 | C++ 侧直接挂载，抖动更小 |

**对业务的影响**：Fabric 提供同步布局读取、多优先级更新和跨平台 C++ 核心等能力，但它不保证任意列表、键盘或模态动画都会自动变流畅。RN 0.82 起应用运行时只使用新架构；兼容层仍会让部分 Legacy 库继续运行，是否可用必须用目标 RN 版本、库发布说明和真实构建确认。

### Hermes — 面向 RN 的 JS 引擎

**定义**: Meta 专为移动端打造的 JavaScript 引擎，构建期把 JS 预编译为字节码（AOT），运行时直接执行。

**可能的收益**：构建可生成 Hermes 字节码，减少设备端解析/编译开销；其内存和启动影响取决于 bundle、设备和构建配置。React Native 通常使用 Hermes，禁用后可能改用 JavaScriptCore；远程 JS 调试又是另一运行环境。不要把某个 Hermes 主版本、启动提速百分比或内存下降量写成跨项目保证。

**确认方式**：记录实际 RN/Expo 版本、构建类型和运行时；在同一台目标设备进行多次冷启动、内存与交互测量。bare 工程的引擎配置字段随模板版本变化，应以生成项目与构建日志为准；Expo 工程先查所用 SDK 的版本固定文档，不要根据最新页面反推旧项目。

## 💻 动画：Reanimated 4

**为什么不用 Animated**: 内置 `Animated` 的驱动逻辑跑在 JS 线程（或退化为原生驱动但能力受限），JS 繁忙时动画掉帧。Reanimated 把动画计算完全放到 UI 线程，手势跟手不卡顿。

```tsx
// 手势跟手的滑动删除卡片
import { Pressable, StyleSheet, Text } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import { scheduleOnRN } from 'react-native-worklets';

export function SwipeCard({ title, onDelete }: { title: string; onDelete: () => void }) {
  const translateX = useSharedValue(0);

  const pan = Gesture.Pan()
    .onUpdate((e) => {
      // UI runtime 直接更新 shared value；“不掉帧”仍须在设备上测量
      translateX.value = e.translationX;
    })
    .onEnd(() => {
      // 超过阈值先滑出；完成后才回 RN runtime 更新 React 状态
      if (Math.abs(translateX.value) > 120) {
        const exitX = translateX.value < 0 ? -400 : 400;
        translateX.value = withSpring(exitX, {}, (finished) => {
          if (finished) scheduleOnRN(onDelete);
        });
      } else {
        translateX.value = withSpring(0);
      }
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <GestureDetector gesture={pan}>
      <Animated.View style={[styles.card, animatedStyle]}>
        <Text>{title}</Text>
        <Pressable onPress={onDelete}>
          <Text style={styles.delete}>删除</Text>
        </Pressable>
      </Animated.View>
    </GestureDetector>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 6,
    borderRadius: 12,
    backgroundColor: '#fff',
    elevation: 2,
  },
  delete: { color: '#c00' },
});
```

**要点**: `useSharedValue` + `useAnimatedStyle` 让样式计算可在 UI runtime 执行。Gesture 回调通常也会 worklet 化；它不能直接调用普通 React 回调。Reanimated 4 使用 `scheduleOnRN` 把删除状态更新调度回 RN runtime，且它是异步的；worklet 内不要读取或修改 React state。

## 💻 性能问题定位

1. **Perf Monitor**: 开发者菜单打开，观察 JS 与 UI 两条线程的帧率
2. **React Native DevTools**: React DevTools 面板定位重渲染（Highlight updates + Profiler）
3. **Hermes 采样分析**: 抓取 Hermes heap/CPU 分析 JS 侧热点
4. **Systrace/Perfetto**: 分析原生侧挂载与布局耗时

| 症状 | 大概率原因 | 首选手段 |
|------|-----------|---------|
| 列表滑动掉帧 | renderItem 重渲染 | `React.memo` + `getItemLayout` |
| 点击响应慢 | JS 线程、同步布局或原生 I/O 竞争 | 先采样确定线程；短暂视觉反馈可用 UI runtime，重活需拆分、缓存或移到合适的原生/后台任务 |
| 启动慢 | bundle、初始化、图片解码、网络或设备状态 | 记录冷启动定义和多次样本，再逐项剖析；Hermes 只是可能因素 |
| 内存持续上涨 | 泄漏 | 检查未清理的订阅/定时器 |

更多调试工具命令见 [CLI 命令与调试速查](../reference/quick-references/01-cli-and-debug-cheatsheet.md)，系统性优化将归档于 `advanced-topics/performance/`。

## 🎨 最佳实践

升级原生依赖前先检查目标平台与架构支持，再在固定依赖的工程中构建验证。动画库按交互复杂度选择，简单动画不需要为了“高级”换库；持续掉帧时分别观察 JS 工作量、布局和图片解码。

worklet 与 React 状态所在执行环境不同，跨环境更新要使用库支持的调度方式，不能假定可直接调用所有 JS 函数。大图先限定展示与解码尺寸，在真实目标设备比较内存和帧表现；新渲染器不会自动消除业务代码中的重复计算。

## ❓ 常见问题

### Q1: 怎么确认我的 App 跑在新架构上？
**A**: 现行 RN 全部默认新架构（0.82 起为唯一架构，旧架构开关已删除）；DevTools 启动日志可确认；老库混用时以官方 Upgrade Helper 结果为准。

### Q2: Reanimated 与 Gesture Handler 的安装顺序？
**A**: Expo 工程先用 `npx expo install react-native-reanimated react-native-worklets`，再查该 SDK 的固定文档；当前 Expo 预设会自动配置所需插件。bare 工程按 Reanimated 与 Gesture Handler 对应版本文档配置，随后重新构建原生应用。不要在已有 Expo 配置中重复手加插件后再声称“顺序无关”。

### Q3: 鸿蒙端动画库怎么选？
**A**: 使用 RNOH 官方适配列表中的版本（其组织下提供 harmony 补丁包），见 [05-harmonyos-rnoh-api](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

## 🎯 练习与实践

### 练习一：跟手拖拽排序

**任务要求**:
1. 实现 5 张卡片的列表，长按拖拽换位（Gesture Handler + Reanimated）
2. 在固定设备、固定构建类型下各执行 10 次相同拖动，记录 JS/UI 帧率、是否丢帧、卡片是否在动画结束后才删除

**评估标准**: 未过阈值时卡片归位；左右超过阈值时向对应方向退出，动画完成后列表才移除该项。把设备型号、构建类型、样本数和测得的帧率写入记录，而不是只写“流畅”。

### 练习二：启动性能体检

**任务要求**:
1. 分别在 Hermes 开启/关闭下记录冷启动到首屏时间（各 5 次取均值）
2. 记录 bundle 与内存占用差异

**提示**: Android 可用 `adb shell am start -W` 获取启动耗时。

---

## 🔗 相关文档

- 📄 **[综合练习](./08-first-project.md)**: 下一课，把所学串成完整 App
- 📄 **[CLI 命令与调试速查](../reference/quick-references/01-cli-and-debug-cheatsheet.md)**: DevTools 与性能工具命令
- 📄 **[RNOH 架构](../reference/language-concepts/05-harmonyos-rnoh-api.md)**: 鸿蒙端动画库适配
- 📄 **[组件 Props 全表](../reference/language-concepts/02-components-props.md)**: FlatList 性能参数完整清单

> 💡 **学习建议**: 性能优化的第一原则是"测量先于优化"。先建立可复现的帧率/启动数据基线，再动手改代码，否则你不知道改动是优化还是劣化。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
