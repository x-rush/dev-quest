# 状态管理模型 — 分层与放置

> **难度**: ⭐ | **前置**: 理解 useState（[04-state-hooks](../../basics/04-state-hooks.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#状态管理` `#useState` `#Context` `#useSyncExternalStore` |
| **更新日期** | `2026年9月` |

## 📌 定义

状态管理的本质不是"选哪个库"，而是**把每一份状态放到正确的层**。按读写特征分五层：

| 层 | 特征 | 典型载体 |
|----|------|---------|
| 组件局部状态 | 只影响本组件渲染 | `useState` / `useReducer` |
| 跨组件共享状态 | 父子/兄弟间传递 | 状态提升 + Props、Context |
| 全局客户端状态 | 登录态、主题、设置 | 外部 store（Zustand 等） |
| 服务端数据缓存 | 来自 API、可失效重取 | 数据请求库（TanStack Query 等） |
| 持久化状态 | 重启后仍需存在 | 存储层（见[存储方案选型](../library-guides/03-storage-options.md)） |

**分层原则**：能用局部状态就不用全局；服务端数据不进客户端 store；持久化是状态的"快照投影"而非状态本体。

## 📖 语法/签名

```tsx
// 1. 组件局部
const [query, setQuery] = useState('');

// 2. 跨组件：Context（value 必须 memo，否则级联重渲染）
const ThemeContext = createContext<Theme>('light');

// 3. 外部 store 的标准接入签名：React 18+ 推荐经 useSyncExternalStore 订阅
const snapshot = useSyncExternalStore(
  store.subscribe,   // (onStoreChange: () => void) => () => void  返回退订函数
  store.getSnapshot, // () => T  必须返回不可变快照
  store.getServerSnapshot, // 可选：SSR 快照
);

// 4. 服务端缓存（伪代码，请求库负责去重/失效/重试）
const { data, isPending } = useQuery({ queryKey: ['todos'], queryFn: fetchTodos });
```

## 💡 示例

```tsx
// 一个最小外部 store（Zustand 同款模型）：模块级可变 store + 订阅通知
let listeners = new Set<() => void>();
let count = 0;

export const counterStore = {
  subscribe(onChange: () => void) {
    listeners.add(onChange);
    return () => listeners.delete(onChange);
  },
  getSnapshot: () => count,
  increment() {
    count += 1; // 通知前先变更快照，保证快照不可变语义
    listeners.forEach((l) => l());
  },
};

function Counter() {
  const count = useSyncExternalStore(counterStore.subscribe, counterStore.getSnapshot);
  return <Button title={`${count}`} onPress={counterStore.increment} />;
}
```

## ⚠️ 常见陷阱

- **服务端数据塞进全局 store**：失去缓存失效/去重/后台刷新能力；交给请求库
- **Context value 不 memo**：Provider 每次渲染都换引用，全树订阅者级联重渲染
- **把所有状态上提到全局**："全局变量化"让数据流不可追踪；先局部、再提升、最后全局
- **直接改快照对象**：外部 store 的快照必须不可变（换引用而非改字段），否则 React 检测不到变化
- **持久化整棵状态树**：只持久化必要字段（设置、token），大对象与缓存交给存储层按需读写

## 🔗 相关条目

- 📄 [状态与数据请求库指南](../library-guides/01-state-and-data.md) — Zustand/Query 的库级选型
- 📄 [Hooks 速查](./03-hooks-reference.md) — useSyncExternalStore/useContext 签名细节
- 📄 [存储方案选型](../library-guides/03-storage-options.md) — 持久化层的载体选择
- 📄 [组件生命周期](./06-component-lifecycle.md) — 副作用与状态更新的时序

*延伸: React 官方文档 "Scaling Up with Reducer and Context" · Zustand 文档*
