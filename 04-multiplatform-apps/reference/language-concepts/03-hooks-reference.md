# Hooks 速查 — 官方与 RN 常用

> **难度**: ⭐ | **前置**: 理解 Hook 基本用法（[04-state-hooks](../../basics/04-state-hooks.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Hooks` `#useEffect` `#useMemo` `#useNavigation` |
| **更新日期** | `2026年9月` |

## React 官方 Hooks（RN 全部可用）

### useState

### 描述
组件局部可变状态，变更触发重渲染。

### 语法和示例
```tsx
const [visible, setVisible] = useState(false);
const [list, setList] = useState<Item[]>(() => loadInitial()); // 惰性初始化
```

### 陷阱
- 初始值是昂贵计算时用函数式惰性初始化
- 连续 setState 依赖旧值时必须用 `setX((prev) => ...)` 函数式更新

### useEffect

### 描述
处理渲染后的副作用（订阅/请求/定时器），返回清理函数。

### 语法和示例
```tsx
useEffect(() => {
  const sub = AppState.addEventListener('change', handler);
  return () => sub.remove();
}, [deps]);
```

### 陷阱
- 依赖数组如实填写，用 `eslint-plugin-react-hooks` 强制检查
- 与外部系统同步才用它；纯派生数据用 useMemo 或直接计算

### useLayoutEffect

### 描述
原生视图挂载后同步执行，先于绘制。用于测量布局后立即调整。

### 陷阱
- 会阻塞绘制，勿滥用；常规副作用仍用 useEffect

### useMemo / useCallback

### 描述
缓存计算结果 / 函数引用，避免子组件因引用变化重渲染。

### 语法和示例
```tsx
const total = useMemo(() => items.reduce((s, i) => s + i.amount, 0), [items]);
const onSubmit = useCallback((v: string) => add(v), [add]);
```

### 陷阱
- 只对"昂贵计算"或"作为 props 传给 memo 组件"的值使用；到处包裹反而增加开销
- Context 的 value 必须 useMemo，否则级联重渲染

### useRef

### 描述
持有跨渲染的可变引用，或引用原生视图实例。

### 语法和示例
```tsx
const listRef = useRef<FlatList<Item>>(null);
listRef.current?.scrollToOffset({ offset: 0, animated: true });
```

### 陷阱
- `.current` 变化不触发渲染；需要"值变即渲染"用 useState

### useTransition / useDeferredValue

### 描述
并发特性：把非紧急更新降级，输入框打字不卡列表。

### 陷阱
- 需 React 18+（现行 RN 均满足）；长列表过滤场景收益明显

## RN 专用 Hooks（react-native 内置）

| Hook | 用途 | 等价的旧写法 |
|------|------|-------------|
| `useWindowDimensions` | 响应式窗口尺寸（旋转/分屏自动更新） | `Dimensions.get` + 事件监听 |
| `useColorScheme` | 系统深浅色模式 `'light' \| 'dark' \| null` | Appearance API |
| `useAnimatedValue` | 创建 `Animated.Value` | `new Animated.Value()` |

```tsx
function ThemedHeader() {
  const scheme = useColorScheme();
  const { width } = useWindowDimensions();
  return <Text style={{ color: scheme === 'dark' ? '#fff' : '#000' }}>
    {width > 600 ? '宽屏' : '窄屏'}
  </Text>;
}
```

## React Navigation Hooks

| Hook | 用途 |
|------|------|
| `useNavigation()` | 拿 navigation 对象（深组件免层层传递） |
| `useRoute()` | 拿当前路由（含 params） |
| `useFocusEffect(cb)` | 页面聚焦时执行 cb，返回清理函数（Tab 切换场景核心） |
| `useIsFocused()` | 布尔值：页面是否聚焦 |
| `usePreventRemove(condition, callback)` | 拦截返回（未保存提示） |

```tsx
import { useFocusEffect } from '@react-navigation/native';
import { useCallback } from 'react';

useFocusEffect(
  useCallback(() => {
    refetch(); // 每次回到该页刷新数据
    return () => pausePolling();
  }, [refetch]),
);
```

完整导航 API 见 [navigation-essentials](../framework-essentials/02-navigation-essentials.md)。

## 通用校验清单

- ✅ Hook 只在组件/自定义 Hook 顶层调用（不在循环/条件/嵌套函数内）
- ✅ 每个 useEffect 都审视过清理函数
- ✅ 列表 renderItem 中的回调已 useCallback + 子组件 memo
- ✅ 深层组件用 `useNavigation` 替代 props 透传

## 🔗 相关文档

- 📄 **[RN 核心 API 字典](./01-rn-core-api.md)**: 与 Hook 对应的命令式 API
- 📄 **[TS 类型模式](./04-typescript-patterns.md)**: 自定义 Hook 的类型写法
- 📄 **[状态与数据请求库指南](../library-guides/01-state-and-data.md)**: 复杂状态交给 Zustand/Query
- 📄 **[状态与 Hooks 教程](../../basics/04-state-hooks.md)**: 系统学习路径

*相关教程: [导航中的 Hook 实战](../../basics/05-navigation.md)*
