# 单元测试 — Jest 与 Expo

> **文档简介**: 用 Jest 为 RN 应用搭建单元测试体系：Expo 预设配置、纯函数与 store 测试、mock 原生模块与定时器，让业务逻辑在 CI 中被自动验证
>
> **目标读者**: 开始编写业务代码、需要为逻辑层建立回归保障的开发者
>
> **前置知识**: 了解 ES Module 与 async/await；建议先读 [待办应用](../projects/01-todo-app.md) 中的 store 实现

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（testing） |
| **难度** | ⭐⭐ |
| **标签** | `#Jest` `#单元测试` `#Mock` `#CI` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 为 Expo 项目正确配置 Jest（preset + transform）
- ✅ 测试纯函数、zustand store 与时间相关逻辑的分支
- ✅ mock 原生模块（expo-location、MMKV 等）让测试脱离真机
- ✅ 用 fake timers 测试防抖/重连等时间逻辑

## 🛠️ 配置

```bash
npx expo install jest-expo jest -- --save-dev
npm install --save-dev jest @types/jest   # 确保 jest 本体与类型在
```

```json
// package.json 关键字段
{
  "scripts": { "test": "jest" },
  "jest": {
    "preset": "jest-expo",                // Expo 官方预设：处理 RN 特有模块与转换
    "transformIgnorePatterns": [
      "node_modules/(?!(jest-)?react-native|@react-native|@expo|expo.*|@tanstack)"
    ],
    "setupFiles": ["./jest.setup.ts"]
  }
}
```

`transformIgnorePatterns` 的含义：这些包以 ESM 发布，必须交给 babel 转换，否则报 "Unexpected token 'export'"——RN 测试配置最经典的报错（更多见[故障排除](../reference/quick-references/02-troubleshooting.md)）。

```ts
// jest.setup.ts —— 全局 mock 噪音源
jest.mock('react-native-mmkv', () => ({
  // 用内存 Map 模拟 MMKV，测试之间互不污染
  MMKV: jest.fn().mockImplementation(() => {
    const map = new Map<string, string>();
    return {
      set: (k: string, v: string) => map.set(k, v),
      getString: (k: string) => map.get(k) ?? undefined,
      delete: (k: string) => map.delete(k),
    };
  }),
}));
```

## 💻 测试示例

### 纯函数测试

```ts
// utils/todos.test.ts
import { toggleTodo, remainingCount } from './todos';

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
jest.useFakeTimers();
// 思路：触发 onclose → jest.advanceTimersByTime(1000) → 断言再次 connect
// 挂载 Hook 用 RNTL 的 renderHook，见组件测试篇
```

## ✅ 最佳实践

- ✅ **测试金字塔**：单元测试最快最多，聚焦 store/纯函数/工具；组件行为交给 RNTL（见[组件测试](../testing/02-component-testing.md)）
- ✅ **每个用例前重置全局状态**（`beforeEach`），杜绝用例间耦合
- ✅ **mock 返回合成数据**，不要引用线上真实接口响应
- ❌ **不要测实现细节**（内部函数调用次数），测行为与输出
- ❌ **不要在单测里渲染整棵组件树**，那是组件测试的职责，单测只管逻辑

## ❓ 常见问题

**Q1: SyntaxError: Cannot use import statement outside a module？**
A: 该包没进 `transformIgnorePatterns` 白名单，把包名前缀加进正则。

**Q2: 测试里 setState 不生效？**
A: zustand 在组件外更新必须包 `act(...)`，否则断言时序不稳。

**Q3: CI 上测试偶发超时？**
A: 检查是否有真实 setTimeout/网络泄漏；统一用 fake timers 并在 `afterEach` 清理。

---

## 🔗 相关文档

- 📖 [故障排除 — 常见错误与解法](../reference/quick-references/02-troubleshooting.md) — Jest 报错速查
- 📖 [状态与数据请求库指南](../reference/library-guides/01-state-and-data.md) — 被测对象（store/Query）的实现参考
- 📄 [待办应用实战](../projects/01-todo-app.md) — 本篇被测代码的出处
- 🧪 [组件测试 — RNTL](./02-component-testing.md) — 测试金字塔的下一层
- 🧪 [端到端测试](./03-e2e-testing.md) — 测试金字塔的顶层
- 🚀 [生产级移动应用](../projects/04-production-mobile-app.md) — 单测纳入 CI 门禁的完整流程
