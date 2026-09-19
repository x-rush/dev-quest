# 单元测试 — Jest 与 Expo

> **文档简介**: 用 Jest 为 RN 应用搭建单元测试体系：Expo 预设配置、纯函数与 store 测试、mock 原生模块与定时器，让业务逻辑在 CI 中被自动验证
>
> **目标读者**: 开始编写业务代码、需要为逻辑层建立回归保障的开发者
>
> **前置知识**: 了解 ES Module 与 async/await；建议先读 [待办应用](../projects/01-todo-app.md) 中的 store 实现

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（testing） |
| **难度** | ⭐⭐ |
| **标签** | `#Jest` `#单元测试` `#Mock` `#CI` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 学习目标

- ✅ 为 Expo 项目正确配置 Jest（preset + transform）
- ✅ 测试纯函数、zustand store 与时间相关逻辑的分支
- ✅ mock 原生模块（expo-location、MMKV 等）让测试脱离真机
- ✅ 用 fake timers 测试防抖/重连等时间逻辑

## 🛠️ 配置

```bash
npx expo install jest-expo jest @types/jest --dev
npx expo install @testing-library/react-native --dev
```

```json
{
  "scripts": { "test": "jest" },
  "jest": {
    "preset": "jest-expo",
    "setupFiles": ["./jest.setup.ts"]
  }
}
```

先使用 `jest-expo` 对当前 Expo SDK 的默认转换规则；若具体依赖出现未转换语法，再按 [Expo Jest 指南](https://docs.expo.dev/develop/unit-testing/)检查 Babel 和 `transformIgnorePatterns`。不要为了单个报错覆盖整套预设，也不要假定所有第三方包都需要相同处理。

```ts
// jest.setup.ts —— 全局 mock 噪音源
jest.mock('react-native-mmkv', () => ({
  // 每个实例一个 Map；同一 store 跨测试仍会复用实例，必须显式重置。
  createMMKV: jest.fn(() => {
    const map = new Map<string, string>();
    return {
      set: (k: string, v: string) => map.set(k, v),
      getString: (k: string) => map.get(k) ?? undefined,
      remove: (k: string) => map.delete(k), // v4 中删除键的方法为 remove（返回是否删除）
    };
  }),
}));
```

## 💻 测试示例

### 纯函数测试

```ts
// utils/todos.test.ts
import { createTodo, toggleTodo, remainingCount } from './todos';

it('创建时规范标题并拒绝空输入', () => {
  expect(createTodo('  买菜  ', 'a', 0)).toEqual({ id: 'a', title: '买菜', done: false, createdAt: 0 });
  expect(createTodo('  ', 'a', 0)).toBeNull();
  expect(() => createTodo('买菜', '', 0)).toThrow(RangeError);
});

describe('toggleTodo', () => {
  const base = { id: '1', title: '买菜', done: false, createdAt: 0 }; // createdAt 毫秒时间戳

  it('未完成 → 已完成', () => {
    expect(toggleTodo([base], '1')[0].done).toBe(true);
  });
  it('不存在 id 时原数组不变', () => {
    expect(toggleTodo([base], 'x')).toEqual([base]); // 不抛错、不改内容
  });
});

describe('remainingCount', () => {
  it('只统计未完成', () => {
    const todos = [
      { id: '1', title: 'a', done: false, createdAt: 0 },
      { id: '2', title: 'b', done: true, createdAt: 0 },
    ];
    expect(remainingCount(todos)).toBe(1);
  });
});
```

### Store 测试（含状态重置）

```ts
// store/todos.test.ts
import { useTodoStore } from './todos';
import { act } from '@testing-library/react-native';

beforeEach(() => {
  act(() => useTodoStore.setState({ todos: [] }));   // 每个用例前重置状态
});

it('add 会 trim 并置顶插入', () => {
  act(() => useTodoStore.getState().add('  写测试  '));
  const todos = useTodoStore.getState().todos;
  expect(todos[0].title).toBe('写测试');
  expect(todos).toHaveLength(1);
});

it('直接调用 store 也不能插入空标题', () => {
  useTodoStore.getState().add('   ');
  expect(useTodoStore.getState().todos).toEqual([]);
});
```

### Mock 原生模块 + 定时器

```ts
// hooks/usePosition.test.ts
jest.mock('expo-location', () => ({
  requestForegroundPermissionsAsync: jest.fn().mockResolvedValue({ status: 'granted' }),
  Accuracy: { Balanced: 3 },
  getCurrentPositionAsync: jest.fn().mockResolvedValue({
    coords: { latitude: 31.23, longitude: 121.47 }, // 合成坐标，非真实数据
  }),
}));

// 时间相关逻辑（重连指数退避、防抖）：统一用 fake timers
beforeEach(() => jest.useFakeTimers());
afterEach(() => {
  jest.clearAllTimers();
  jest.useRealTimers();
});
// 思路：触发 onclose → jest.advanceTimersByTime(1000) → 断言再次 connect
// 挂载 Hook 用 RNTL 的 renderHook，见组件测试篇
```

## ✅ 最佳实践

单元测试优先验证纯逻辑的输入输出，例如重复添加、金额汇总和无效标题；外部网络、时间或原生能力可由可控依赖替代。用例每次建立自己的初始状态，连续运行和单独运行都应一致。

是否渲染组件取决于要验证的边界，而不是名称禁令。调用次数只有在它本身属于契约时才值得断言，例如一次点击不能重复扣费；其他情况下优先检查用户可见结果和保存的数据。

## ❓ 常见问题

**Q1: SyntaxError: Cannot use import statement outside a module？**
A: 该包没进 `transformIgnorePatterns` 白名单，把包名前缀加进正则。

**Q2: 测试里 setState 不生效？**
A: 先区分同步 store 与 React 订阅者。`getState()` / `setState()` 本身同步；只有测试已渲染的组件或 Hook 时，直接触发更新才需要 React 的 `act` 来完成提交。持久化恢复和异步 action 还应等待自己的完成条件，不能靠 `act` 自动等待一切。参见 [Zustand 测试指南](https://zustand.docs.pmnd.rs/guides/testing)。

**Q3: CI 上测试偶发超时？**
A: 检查未结束网络、定时器和原生订阅。只在验证时间逻辑时启用 fake timers，并恢复真实时钟；盲目全局启用会让依赖真实时间的异步等待永远不推进。

---

## 🔗 相关文档

- 📖 [故障排除 — 常见错误与解法](../reference/quick-references/02-troubleshooting.md) — Jest 报错速查
- 📖 [状态与数据请求库指南](../reference/library-guides/01-state-and-data.md) — 被测对象（store/Query）的实现参考
- 📄 [待办应用实战](../projects/01-todo-app.md) — 本篇被测代码的出处
- 🧪 [组件测试 — RNTL](./02-component-testing.md) — 测试金字塔的下一层
- 🧪 [端到端测试](./03-e2e-testing.md) — 测试金字塔的顶层
- 🚀 [生产级移动应用](../projects/04-production-mobile-app.md) — 单测纳入 CI 门禁的完整流程


<!-- acceptance-exercise -->
## 练习与验收：从纯函数开始，保留能抓住错误的断言

为价格汇总或表单验证选择一个纯函数，列出空输入、一个有效项、边界数量和非法输入。故意把加法改成减法，测试必须失败，再恢复。使用合成数据，不访问真实设备服务。验收是错误实现会被行为断言发现，且测试单独运行与整套运行一致；快照文件变了就接受新快照不能作为验证方法。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
