# 组件测试 — React Native Testing Library

> **文档简介**: 用 RNTL 以"用户视角"测试组件：渲染查询、事件触发、异步等待与 Hook 测试，建立面向行为而非实现的前端测试习惯
>
> **目标读者**: 已能写单元测试、需要覆盖 UI 交互与渲染逻辑的开发者
>
> **前置知识**: 已完成 [单元测试](./01-unit-testing.md)（Jest 环境已可用）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（testing） |
| **难度** | ⭐⭐ |
| **标签** | `#RNTL` `#组件测试` `#renderHook` `#交互` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 安装并配置 React Native Testing Library
- ✅ 用 `getByRole`/`queryByText` 等查询断言界面状态
- ✅ 用 `userEvent`/`fireEvent` 模拟真实交互
- ✅ 用 `renderHook` 测试自定义 Hook（如 WebSocket 连接管理）

## 🛠️ 安装

```bash
npm install --save-dev @testing-library/react-native
```

RNTL 与 Jest 配合无需额外 preset（jest-expo 已含）；jest-expo 新版已内置自动 cleanup，无需手动 `afterEach(cleanup)`。

## 💻 核心用法

### 组件行为测试

```tsx
// __tests__/TodoList.test.tsx —— 测试[待办应用](../projects/01-todo-app.md)的列表组件
import { render, screen, fireEvent, userEvent } from '@testing-library/react-native';
import { TodoList } from '@/components/TodoList';

// 测试原则：像用户一样查询——按角色/文本，而不是按 testID 类名（testID 是兜底）
it('输入并提交后出现新待办', async () => {
  const user = userEvent.setup();           // userEvent 模拟更真实的输入序列
  render(<TodoList />);

  await user.type(screen.getByPlaceholderText('今天要做点什么？'), '买牛奶');
  fireEvent.press(screen.getByRole('button', { name: '添加' }));

  // findBy* 是异步等待版：自动轮询直到出现或超时
  expect(await screen.findByText(/买牛奶/)).toBeTruthy();
});

it('点击待办切换完成态', () => {
  render(<TodoList initialTodos={[{ id: '1', title: '写周报', done: false, createdAt: 0 }]} />);

  const row = screen.getByText('写周报');
  fireEvent.press(row);
  // 断言样式变化：从渲染实例读取 props，避免耦合内部实现
  expect(row.props.style).toEqual(
    expect.arrayContaining([expect.objectContaining({ textDecorationLine: 'line-through' })])
  );
});

it('空列表显示空态文案', () => {
  render(<TodoList />);
  expect(screen.getByText('暂无待办，添加第一条吧')).toBeTruthy(); // getBy*：不存在即抛错
});
```

### 查询家族速记

| 前缀 | 语义 | 用途 |
|------|------|------|
| `getBy*` | 同步，取不到就抛错 | 断言"应该在" |
| `queryBy*` | 同步，取不到返回 null | 断言"不应该在" |
| `findBy*` | 异步等待（默认 1s） | 断言"稍后应该在" |

### 测试自定义 Hook（renderHook）

```tsx
// __tests__/useChatSocket.test.tsx —— 测试聊天项目的连接 Hook
import { renderHook, act } from '@testing-library/react-native';
import { useChatSocket } from '@/hooks/useChatSocket';

// mock 掉真实 WebSocket：网络行为在单测里必须确定性
class MockWebSocket {
  static instances: MockWebSocket[] = [];
  onopen: () => void = () => {};
  onclose: () => void = () => {};
  constructor() { MockWebSocket.instances.push(this); }
  send = jest.fn();
  close = jest.fn();
}
global.WebSocket = MockWebSocket as unknown as typeof WebSocket;

it('连接成功后状态为 open', () => {
  const { result } = renderHook(() => useChatSocket(jest.fn()));
  expect(result.current.status).toBe('connecting');

  act(() => { MockWebSocket.instances[0].onopen(); }); // 手动触发回调
  expect(result.current.status).toBe('open');
});

it('send 会把文本交给底层连接', () => {
  const { result } = renderHook(() => useChatSocket(jest.fn()));
  const ws = MockWebSocket.instances[0];
  act(() => result.current.send('hello'));
  expect(ws.send).toHaveBeenCalledWith('hello');
});
```

### 常见 mock 片段（拷走即用）

```tsx
// 动画库：测试中不需要真动画，直接 mock 掉
jest.mock('react-native-reanimated', () =>
  require('react-native-reanimated/mock')
);

// expo-router：组件测试时不渲染真实导航
jest.mock('expo-router', () => ({
  useRouter: () => ({ push: jest.fn(), replace: jest.fn() }),
  useLocalSearchParams: () => ({ id: 'test-id' }),
  Link: ({ children }: { children: React.ReactNode }) => children,
}));
```

## ✅ 最佳实践

- ✅ **面向用户查询**：优先 `getByRole`/`getByText`，`testID` 只留给无法语义化的图标兜底
- ✅ **断言可观察结果**（出现的文本/调用的回调），不测内部 state
- ✅ **异步一律 `findBy*` 或 `waitFor`**，不要手写 sleep
- ❌ **不要 snapshot 测试整个屏幕**，一改样式全红，快照只会被无脑更新
- ❌ **不要在组件测试里 mock 被测组件自身**，mock 边界放在"网络/原生模块/导航"

## ❓ 常见问题

**Q1: "Unable to find an element"但界面明明有？**
A: 多数是异步未等待（改用 `findBy*`），或元素在 FlatList 虚拟区外未渲染——测试时用小数据集或普通 View。

**Q2: Reanimated worklet 在 Jest 里报错？**
A: 引入官方 `react-native-reanimated/mock`，并确认 babel 插件顺序正确（reanimated 必须最后）。

**Q3: act 警告刷屏？**
A: 事件都走 `userEvent`/`fireEvent`（内部包 act）；手动触发的回调包一层 `act()`。

---

## 🔗 相关文档

- 📖 [Hooks 速查](../reference/language-concepts/03-hooks-reference.md) — 被测 Hook 的行为定义
- 📖 [故障排除](../reference/quick-references/02-troubleshooting.md) — 测试环境报错速查
- 📄 [待办应用实战](../projects/01-todo-app.md) — 本篇被测组件的出处
- 🧪 [单元测试 — Jest](./01-unit-testing.md) — 环境配置与逻辑层测试
- 🧪 [端到端测试](./03-e2e-testing.md) — 真机层面的行为验证
- 🚀 [聊天应用实战](../projects/03-chat-app.md) — useChatSocket 的完整实现
