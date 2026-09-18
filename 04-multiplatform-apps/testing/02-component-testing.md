# 组件测试 — React Native Testing Library

> **文档简介**: 用 RNTL 以"用户视角"测试组件：渲染查询、事件触发、异步等待与 Hook 测试，建立面向行为而非实现的前端测试习惯
>
> **目标读者**: 已能写单元测试、需要覆盖 UI 交互与渲染逻辑的开发者
>
> **前置知识**: 已完成 [单元测试](./01-unit-testing.md)（Jest 环境已可用）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（testing） |
| **难度** | ⭐⭐ |
| **标签** | `#RNTL` `#组件测试` `#renderHook` `#交互` |
| **更新日期** | 2026年9月 |

</details>

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

点击保存后，断言新标题出现或预期回调收到正确数据，而不是读取组件私有 state。先按角色、标签等可理解语义定位控件；测试标识用于必要补充，但不替代无障碍检查。

异步操作等待预期条件出现，并设置失败上限，避免猜一个 sleep 时间。保持被测组件真实，只替换网络或原生等外部边界。快照适合稳定且可审阅的输出，整屏大快照若难以判断差异，应改成更具体的行为断言。

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


<!-- acceptance-exercise -->
## 练习与验收：按可见行为测试加载与重试

给列表组件注入可控制完成时机的假服务：请求未结束时显示加载；返回空数组显示空态；失败后显示重试；点击重试成功后显示项目。预期同一操作不会重复提交请求，卸载后晚到响应不产生新界面更新。验收使用可访问名称查询按钮并模拟用户操作，不直接调用组件内部 setter；组件测试仍不能证明真实原生手势或布局尺寸。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
