# 高级特性 — 新架构 Fabric、Hermes 与动画

> **文档简介**: 理解新架构渲染器 Fabric 与 Hermes 引擎如何影响应用性能，掌握 Reanimated 动画开发与交互流畅度的基本调优手法
>
> **目标读者**: 完成入门路径、关注"帧率与手感"的开发者
>
> **前置知识**: 完成 [06-native-modules](./06-native-modules.md)，理解 RN 渲染链路

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#Fabric` `#Hermes` `#Reanimated` `#性能优化` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 说清新架构三件套（Fabric/TurboModules/Codegen）各自的职责
- ✅ 解释 Hermes 字节码对启动速度与内存的意义
- ✅ 用 Reanimated 4 写出 60fps 的手势跟手动画
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

**对业务的直接体感**: 长列表滚动更稳、模态/键盘弹出不再"跳变"、第三方原生组件兼容性由 Codegen 保障。新架构自 RN 0.82 起是唯一架构（旧架构已移除），业务代码通常无需改动；未适配的旧库已无法使用，需换 Fabric 适配版或替代库。

### Hermes — 面向 RN 的 JS 引擎

**定义**: Meta 专为移动端打造的 JavaScript 引擎，构建期把 JS 预编译为字节码（AOT），运行时直接执行。

**收益**:
- 启动提速：省去设备端即时编译（JIT 预热）
- 内存降低：字节码 mmap 映射，按需加载
- 调试增强：支持 Hermes 调试协议（React Native DevTools 即基于此）

Hermes 默认启用，RN 0.84 起 V1 引擎为默认版本。Expo 工程开箱即用；bare 工程检查方式：iOS 看 `Podfile` 中 `:hermes_enabled => true`，Android 看 `gradle.properties` 的 `hermesEnabled=true`。

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

export function SwipeCard({ title, onDelete }: { title: string; onDelete: () => void }) {
  const translateX = useSharedValue(0);

  const pan = Gesture.Pan()
    .onUpdate((e) => {
      // UI 线程直接更新，不经过 setState，不掉帧
      translateX.value = e.translationX;
    })
    .onEnd(() => {
      // 超过阈值滑出并回调删除，否则弹回
      if (Math.abs(translateX.value) > 120) {
        translateX.value = withSpring(400);
        onDelete();
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

**要点**: `useSharedValue` + `useAnimatedStyle` 的组合让"值变化 → 样式更新"完全在 UI 线程闭环；worklet 函数内不要引用 React 状态。

## 💻 性能问题定位

1. **Perf Monitor**: 开发者菜单打开，观察 JS 与 UI 两条线程的帧率
2. **React Native DevTools**: React DevTools 面板定位重渲染（Highlight updates + Profiler）
3. **Hermes 采样分析**: 抓取 Hermes heap/CPU 分析 JS 侧热点
4. **Systrace/Perfetto**: 分析原生侧挂载与布局耗时

| 症状 | 大概率原因 | 首选手段 |
|------|-----------|---------|
| 列表滑动掉帧 | renderItem 重渲染 | `React.memo` + `getItemLayout` |
| 点击响应慢 200ms+ | JS 线程阻塞 | 交互改 Reanimated，重活移出 JS 线程 |
| 启动慢 | bundle 过大 | 按需 import、Hermes 字节码、代码分割评估 |
| 内存持续上涨 | 泄漏 | 检查未清理的订阅/定时器 |

更多调试工具命令见 [CLI 命令与调试速查](../reference/quick-references/01-cli-and-debug-cheatsheet.md)，系统性优化将归档于 `advanced-topics/performance/`。

## 🎨 最佳实践

### ✅ 推荐做法
- **升级前查适配表**: 三方库是否标注 "New Architecture ready"（RNOH 亦要求同版本对齐）
- **动画一律 Reanimated**: 内置 Animated 仅用于简单透明度/位移过渡
- **对图片做预算**: 大图用缓存库 + 固定尺寸，避免解码阻塞

### ❌ 避免陷阱
- **在动画 worklet 里 setState**: 会跨线程往返，性能全毁；用 sharedValue 通信
- **把 Fabric 当"自动优化"**: 渲染器只影响挂载链路，JS 侧过度重渲染仍会卡
- **忽略鸿蒙端验证**: Reanimated 等动画库需使用 RNOH 适配分支，直接 npm 装最新版可能不兼容

## ❓ 常见问题

### Q1: 怎么确认我的 App 跑在新架构上？
**A**: 现行 RN 全部默认新架构（0.82 起为唯一架构，旧架构开关已删除）；DevTools 启动日志可确认；老库混用时以官方 Upgrade Helper 结果为准。

### Q2: Reanimated 与 Gesture Handler 的安装顺序？
**A**: `npx expo install` 安装即可——Expo 工程的 `babel-preset-expo` 已自动包含 worklets 插件（Reanimated 4 起插件移交 `react-native-worklets`，仍需放插件列表最后）；bare 工程需手动确认，然后重新构建原生工程。

### Q3: 鸿蒙端动画库怎么选？
**A**: 使用 RNOH 官方适配列表中的版本（其组织下提供 harmony 补丁包），见 [05-harmonyos-rnoh-api](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

## 🎯 练习与实践

### 练习一：跟手拖拽排序

**任务要求**:
1. 实现 5 张卡片的列表，长按拖拽换位（Gesture Handler + Reanimated）
2. 拖动全程 Perf Monitor 保持在 55fps 以上

**评估标准**: 松手后卡片动画平滑归位，无跳变。

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
