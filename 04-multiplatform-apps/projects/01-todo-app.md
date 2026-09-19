# 实战项目一 — 待办应用（入门）

## 分阶段练习与验收

**最小阶段**：在一个平台完成待办新增、完成和删除。

**验收结果**：空列表、长标题、重启后的保存行为均可解释。

**扩展顺序**：第二平台单独检查布局与存储，鸿蒙适配作为独立验收项。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 用一个"待办清单"App 走通移动开发的完整闭环：本地状态管理、持久化存储、列表渲染与增删改查，交付第一个可日常使用的跨平台应用
>
> **目标读者**: 已完成 basics 入门路径、需要第一个完整项目练手的初学者
>
> **前置知识**: 已完成 [综合练习 — 三端待办记账 App](../basics/08-first-project.md)；已读 [框架入门](../frameworks/01-react-native-basics.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（projects） |
| **难度** | ⭐ |
| **标签** | `#待办` `#Zustand` `#MMKV` `#FlatList` `#入门项目` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 项目目标

- ✅ 独立实现新增、切换完成状态、删除与未完成数量统计
- ✅ 数据本地持久化，杀进程后不丢失
- ✅ 掌握受控输入、列表渲染、空态处理三个基础模式
- 在 Android / iOS 开发构建中分别完成下方验收；鸿蒙需独立适配与工具链验证，本文代码不证明三端已运行

## 📐 需求定义

1. 输入待办标题，回车或点击按钮添加
2. 列表展示全部待办，点击切换完成状态（划线样式）
3. 删除单条待办（本篇用删除按钮简化，手势版见进阶项目）
4. 顶部统计：未完成数量
5. 关闭 App 重开，数据仍在

## 🛠️ 技术选型

| 关注点 | 选择 | 理由 |
|--------|------|------|
| 状态管理 | Zustand | 无 Provider 样板代码，学习成本最低（对比见[库指南](../reference/library-guides/01-state-and-data.md)） |
| 持久化 | MMKV + zustand persist | 同步读写 + 一个中间件搞定 |
| 列表 | FlatList | 数据量小够用；大列表换 FlashList（见[渲染性能](../advanced-topics/performance/01-rendering-performance.md)） |

```bash
npx create-expo-app@latest todo-app
cd todo-app && npx expo install expo-status-bar
npm install zustand
npx expo install expo-crypto react-native-mmkv react-native-nitro-modules
```

MMKV v4 是原生 Nitro Module，按 [MMKV 安装文档](https://github.com/mrousavy/react-native-mmkv#installation)安装配套模块并生成 development build；不能在只包含固定原生模块的 Expo Go 中直接加载它。Android 使用 `npx expo run:android`；iOS 在 macOS / Xcode 环境使用 `npx expo run:ios`。记录项目 SDK、React Native 和 MMKV 锁定版本，依赖升级后重新构建。

## 💻 核心实现

### 第一步：持久化 Store

先隔离纯业务规则，供 store 与[单元测试](../testing/01-unit-testing.md)复用。标题为空时返回 `null`，拒绝非法时间与空 id。id 由调用者生成，因此测试可控制它；实际应用使用 [Expo Crypto 的 randomUUID](https://docs.expo.dev/versions/latest/sdk/crypto/#cryptorandomuuid)。

```ts
// utils/todos.ts
export interface Todo {
  id: string;
  title: string;
  done: boolean;
  createdAt: number;
}

export function createTodo(title: string, id: string, createdAt: number): Todo | null {
  const normalized = title.trim();
  if (!normalized) return null;
  if (!id || !Number.isFinite(createdAt) || createdAt < 0) {
    throw new RangeError('id 和创建时间无效');
  }
  return { id, title: normalized, done: false, createdAt };
}

export function toggleTodo(todos: Todo[], id: string): Todo[] {
  if (!todos.some((todo) => todo.id === id)) return todos;
  return todos.map((todo) => todo.id === id ? { ...todo, done: !todo.done } : todo);
}

export function remainingCount(todos: Todo[]): number {
  return todos.filter((todo) => !todo.done).length;
}
```

```ts
// store/todos.ts —— 业务与持久化一体化
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { createMMKV } from 'react-native-mmkv';
import { randomUUID } from 'expo-crypto';
import { createTodo, toggleTodo, type Todo } from '../utils/todos';
export type { Todo } from '../utils/todos';

const storage = createMMKV(); // 全局唯一实例

interface TodoState {
  todos: Todo[];
  add: (title: string) => void;
  toggle: (id: string) => void;
  remove: (id: string) => void;
}

export const useTodoStore = create<TodoState>()(
  persist(
    (set) => ({
      todos: [],
      add: (title) => {
        if (!title.trim()) return;
        const todo = createTodo(title, randomUUID(), Date.now());
        if (todo) set((s) => ({ todos: [todo, ...s.todos] }));
      },
      toggle: (id) =>
        set((s) => ({
          todos: toggleTodo(s.todos, id),
        })),
      remove: (id) => set((s) => ({ todos: s.todos.filter((t) => t.id !== id) })),
    }),
    {
      name: 'todos',                          // MMKV 中的 key
      storage: createJSONStorage(() => ({     // 把 MMKV 适配成 zustand 存储接口
        getItem: (k) => storage.getString(k) ?? null,
        setItem: (k, v) => storage.set(k, v),
        removeItem: (k) => storage.remove(k),
      })),
    }
  )
);
```

### 第二步：输入与列表

```tsx
// app/index.tsx —— 主界面
import { useState } from 'react';
import { FlatList, Pressable, Text, TextInput, View, StyleSheet } from 'react-native';
import { useTodoStore, type Todo } from '@/store/todos';

export default function Home() {
  const [draft, setDraft] = useState('');
  const todos = useTodoStore((s) => s.todos);
  const add = useTodoStore((s) => s.add);
  const toggle = useTodoStore((s) => s.toggle);
  const remove = useTodoStore((s) => s.remove);
  const remaining = todos.filter((t) => !t.done).length;

  const submit = () => {
    if (!draft.trim()) return; // 空输入直接忽略
    add(draft);
    setDraft('');              // 清空输入框
  };

  return (
    <View style={styles.screen}>
      <Text style={styles.h1}>待办清单（未完成 {remaining}）</Text>
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={draft}
          onChangeText={setDraft}
          onSubmitEditing={submit}         // 回车即提交
          placeholder="今天要做点什么？"
          returnKeyType="done"
        />
        <Pressable style={styles.btn} onPress={submit}>
          <Text style={styles.btnText}>添加</Text>
        </Pressable>
      </View>

      <FlatList
        data={todos}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <TodoRow todo={item} onToggle={toggle} onRemove={remove} />}
        ListEmptyComponent={<Text style={styles.empty}>暂无待办，添加第一条吧</Text>} // 空态必须有
        contentContainerStyle={{ gap: 8, paddingBottom: 40 }}
      />
    </View>
  );
}

// 单行组件单独抽出：只依赖 todo 本身，配合 memo 减少无谓重渲染
const TodoRow = ({ todo, onToggle, onRemove }: {
  todo: Todo; onToggle: (id: string) => void; onRemove: (id: string) => void;
}) => (
  <Pressable style={styles.row} onPress={() => onToggle(todo.id)}>
    <Text style={[styles.title, todo.done && styles.done]} numberOfLines={1}>
      {todo.done ? '✓ ' : ''}{todo.title}
    </Text>
    <Pressable hitSlop={12} onPress={() => onRemove(todo.id)}>
      <Text style={styles.remove}>删除</Text>
    </Pressable>
  </Pressable>
);
```

### 第三步：三端验证

```bash
npx expo start
# 按 a 跑 Android 模拟器，按 i 跑 iOS 模拟器
# 添加 → 切换 → 删除 → 杀进程重开，确认数据完好
```

## ✅ 最佳实践与进阶方向

待办 id 要在项目需要的范围内保持唯一；毫秒时间戳不能保证连续快速创建不冲突，UUID 与 nanoid 是不同的标识方案，可按依赖与平台支持选择。排序、编辑和删除都应使用稳定 id，而不是数组位置。

单页应用完全可以把待办数组放在组件 state；多个页面要共享时再提升所有权或引入状态层。练习新增两条、修改其中一条、删除另一条并重启，检查数据身份和持久化都正确。扩展编辑弹窗时验证各平台支持差异，不能照搬只在一个平台存在的交互。

## ❓ 常见问题

**Q1: persist 后老数据结构变了怎么办？**
A: `persist` 支持 `version` + `migrate` 字段，升级结构时递增 version 并写迁移函数。

**Q2: 键盘弹起挡住输入框？**
A: 用 `KeyboardAvoidingView`（iOS 用 padding，Android 用 height）或引入 `react-native-keyboard-controller`。

---

## 🔗 相关文档

- 📖 [状态与数据请求库指南](../reference/library-guides/01-state-and-data.md) — Zustand/MMKV 的完整 API 与对比
- 📖 [Hooks 速查](../reference/language-concepts/03-hooks-reference.md) — 本项目 useState 用法详解
- 📖 [核心组件 Props 全表](../reference/language-concepts/02-components-props.md) — FlatList/TextInput 属性字典
- 📄 [综合练习 — 三端待办记账 App](../basics/08-first-project.md) — 本项目的教程版
- 🚀 [天气应用实战](./02-weather-app.md) — 下一个项目：加入网络与定位
- 🧪 [单元测试](../testing/01-unit-testing.md) — 给 store 写第一组测试


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
