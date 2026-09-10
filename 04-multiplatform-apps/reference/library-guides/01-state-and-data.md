# 状态与数据请求库指南 — Zustand / Redux / TanStack Query

> **难度**: ⭐⭐ | **前置**: Context 与 Hooks 用法（[04-state-hooks](../../basics/04-state-hooks.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Zustand` `#Redux Toolkit` `#TanStack Query` `#AsyncStorage` |
| **更新日期** | `2026年9月` |

## 选型决策表

| 场景 | 首选 | 理由 |
|------|------|------|
| 客户端 UI 状态（主题、登录态） | Zustand | 轻量、无样板代码 |
| 大型团队、强规范、中间件生态 | Redux Toolkit | DevTools 时旅行、规范化约定 |
| 服务端数据（列表/详情/缓存） | TanStack Query | 缓存、去重、失效、重试全家桶 |
| 表单局部状态 | 组件内 useState | 别为表单引入全局 store |
| 本地持久化 | AsyncStorage / expo-secure-store | 与上述库配合而非替代 |

**核心心法**: 服务端数据不进 Zustand/Redux——交给 TanStack Query；全局 store 只存"客户端状态"。

## Zustand

### 描述
极简全局状态库：一个 `create` 搞定，天然支持 selector 粒度订阅，移动端重渲染友好。

### 语法和示例
```tsx
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface TodoState {
  todos: { id: string; title: string; done: boolean }[];
  toggle: (id: string) => void;
}

export const useTodoStore = create<TodoState>()(
  persist(
    (set) => ({
      todos: [],
      toggle: (id) =>
        set((state) => ({
          todos: state.todos.map((t) => (t.id === id ? { ...t, done: !t.done } : t)),
        })),
    }),
    {
      name: 'todo-storage',
      storage: createJSONStorage(() => AsyncStorage), // RN 侧持久化
    },
  ),
);
```

```tsx
// 组件内：selector 粒度订阅，只订阅 todos 长度则长度不变不重渲染
const count = useTodoStore((s) => s.todos.length);
const toggle = useTodoStore((s) => s.toggle);
```

### 陷阱
- 不写 selector 订阅整个 store 会放大重渲染
- `createJSONStorage` 必须传入 AsyncStorage（RN 无 localStorage）
- 异步 action 直接在函数里 `await`，无需中间件

## Redux Toolkit（RTK）

### 描述
Redux 官方推荐形态：`createSlice` + `configureStore`，内置 Immer 不可变更新与 thunk。

### 语法和示例
```tsx
import { createSlice, configureStore } from '@reduxjs/toolkit';

const todosSlice = createSlice({
  name: 'todos',
  initialState: [] as { id: string; title: string }[],
  reducers: {
    added: (state, action) => { state.push(action.payload); }, // Immer 代理
    removed: (state, action) => state.filter((t) => t.id !== action.payload),
  },
});

export const store = configureStore({ reducer: { todos: todosSlice.reducer } });
export const { added, removed } = todosSlice.actions;
```

```tsx
import { Provider, useDispatch, useSelector } from 'react-redux';

// <Provider store={store}> 包裹根组件
const todos = useSelector((s: RootState) => s.todos);
const dispatch = useDispatch();
dispatch(added({ id: '1', title: '学习 RNOH' }));
```

### 陷阱
- RN 中 redux-persist 需要配 AsyncStorage storage；新项目建议 Zustand + Query 组合，仅在团队规范要求时选 RTK
- 调试需配合 React Native DevTools 的 redux 面板或远程调试

## TanStack Query

### 描述
服务端状态管理库：请求去重、缓存、聚焦重取、失效与乐观更新。与 02-nextjs-frontend 模块使用同一套 API，学习成本几乎为零。

### 语法和示例
```tsx
import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const queryClient = new QueryClient();

// 入口挂 Provider（与 NavigationContainer 平级）
// <QueryClientProvider client={queryClient}> <NavigationContainer/> </QueryClientProvider>

// 列表页
function TodoList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['todos'],
    queryFn: () => fetch('https://api.example.com/todos').then((r) => r.json()),
    staleTime: 60_000,
  });
  return null;
}

// 新增后失效缓存
function useAddTodo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (title: string) =>
      fetch('https://api.example.com/todos', { method: 'POST', body: JSON.stringify({ title }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['todos'] }),
  });
}
```

### 陷阱
- RN 默认无 window focus 事件，`refetchOnWindowFocus` 需配合 `AppState` 自定义 focusManager；最常用的是 `refetchOnMount` + 主动失效
- queryKey 必须包含全部请求参数，参数变化不换 key 会拿到旧缓存

## 本地持久化速查

| 方案 | 适用 | 说明 |
|------|------|------|
| `@react-native-async-storage/async-storage` | 键值 JSON | 事实标准；鸿蒙用 RNOH 适配版 |
| `expo-secure-store` | 敏感小数据 | 加密存储（token/密钥） |
| `react-native-mmkv` | 高频读写 | 同步 API + C++，性能最好；鸿蒙需适配版 |
| SQLite（expo-sqlite / op-sqlite） | 关系数据 | 离线优先应用的存储层 |

## 🔗 相关文档

- 📄 **[Hooks 速查](../language-concepts/03-hooks-reference.md)**: store 与 Hook 的组合
- 📄 **[RN 核心 API 字典](../language-concepts/01-rn-core-api.md)**: AppState 驱动的缓存刷新
- 📄 **[RNOH 架构](../language-concepts/05-harmonyos-rnoh-api.md)**: 持久化库的鸿蒙适配版
- 📄 **[状态与 Hooks 教程](../../basics/04-state-hooks.md)**: Context 基础
- 📄 **[综合练习教程](../../basics/08-first-project.md)**: AsyncStorage 实战

*延伸: zustand 文档 · TanStack Query 官方文档（与 Web 侧同源）*
