# 状态管理模型 — 分层与放置

> **难度**: ⭐ | **前置**: 理解 useState（[04-state-hooks](../../basics/04-state-hooks.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#状态管理` `#useState` `#Context` `#useSyncExternalStore` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

状态管理的本质不是"选哪个库"，而是**把每一份状态放到正确的层**。按读写特征分五层：

| 层 | 特征 | 典型载体 |
|----|------|---------|
| 组件局部状态 | 只影响本组件渲染 | `useState` / `useReducer` |
| 跨组件共享状态 | 父子/兄弟间传递 | 状态提升 + Props、Context |
| 全局客户端状态 | 登录态、主题、设置 | 外部 store（Zustand 等） |
| 服务端数据缓存 | 来自 API、可失效重取 | 数据请求库（TanStack Query 等） |
| 持久化状态 | 重启后仍需存在 | 存储层（见[存储方案选型](../library-guides/03-storage-options.md)） |

**分层原则**：能用局部状态就不用全局；避免无意维护重复的服务端数据副本；自行放入 store 时也要承担缓存一致性职责；持久化是状态的"快照投影"而非状态本体。

## 📖 语法/签名

```tsx
// 1. 组件局部
const [query, setQuery] = useState('');

// 2. 跨组件：Context（对象 value 的身份变化会通知消费者，是否 memo 按需要决定）
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
- **每次创建相同内容的 Context 对象**：会产生新的 value 身份；常量引用或基础值无需为此添加 memo
- **把所有状态上提到全局**："全局变量化"让数据流不可追踪；先局部、再提升、最后全局
- **直接改快照对象**：外部 store 的快照必须不可变（换引用而非改字段），否则 React 检测不到变化
- **持久化整棵状态树**：只持久化必要字段（设置、token），大对象与缓存交给存储层按需读写

<!-- full-library-explanation -->
## 以编辑待办为例决定唯一来源

服务端返回的待办是当前服务器快照；编辑框里的未提交文字是草稿；是否打开弹窗是 UI 状态；磁盘上的副本是恢复用快照。同一个标题不应在四处都被当成权威值。打开编辑器时复制初始文字可以，保存后应以服务端结果更新缓存，再关闭草稿。

`useSyncExternalStore.getSnapshot` 在数据没变时必须返回稳定结果。若每次读取都返回一个新对象，即使内容相同也可能反复更新；本例返回数字，因此未修改 count 时天然稳定。若改为对象，应在状态变化时生成新快照，并在读取时返回该快照。

练习：将 Counter 改成 `{count}` 快照，连续读取两次应 `Object.is(a, b) === true`；increment 后再次读取应与旧快照不同。反馈：快照变化负责通知渲染，磁盘写入负责持久化，这两个职责可以协调但不能混为同一个动作。

## 🔗 相关条目

- 📄 [状态与数据请求库指南](../library-guides/01-state-and-data.md) — Zustand/Query 的库级选型
- 📄 [Hooks 速查](./03-hooks-reference.md) — useSyncExternalStore/useContext 签名细节
- 📄 [存储方案选型](../library-guides/03-storage-options.md) — 持久化层的载体选择
- 📄 [组件生命周期](./06-component-lifecycle.md) — 副作用与状态更新的时序

*延伸: React 官方文档 "Scaling Up with Reducer and Context" · Zustand 文档*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
