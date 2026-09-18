# 实战项目三 — 聊天应用（实时通信 + 列表优化）

## 分阶段练习与验收

**最小阶段**：先做一个会话中的发送、接收和断线恢复。

**验收结果**：每条消息有稳定 ID，重连不会无限重复，发送失败可以识别。

**扩展顺序**：图片消息、推送与长列表优化分阶段添加。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 构建一个实时聊天 App：WebSocket 双向通信、倒置消息列表、键盘避让与输入性能优化，掌握"高频更新界面"的工程方法论
>
> **目标读者**: 已能处理网络请求与状态管理、准备挑战交互密集型界面的开发者
>
> **前置知识**: 已完成 [天气应用](./02-weather-app.md)；了解列表组件（[核心组件教程](../basics/03-components-jsx.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（projects） |
| **难度** | ⭐⭐ |
| **标签** | `#WebSocket` `#FlatList` `#键盘处理` `#实时通信` `#性能` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 项目目标

- ✅ 用 WebSocket 建立长连接并处理断线重连
- ✅ 用 `inverted` 列表实现"从底部向上堆叠"的聊天布局
- ✅ 掌握键盘避让与输入流畅度的移动端配方
- ✅ 应用 memo/稳定回调控制高频重渲染

## 📐 需求定义

1. 连接 WebSocket 服务（示例用公共回显服务模拟对端）
2. 发送文本消息，本地立即上屏（乐观更新），对端回复自动追加
3. 消息列表 Newest 在底部，历史向上滚动
4. 断网自动重连，顶部显示"重连中"横幅
5. 输入时不卡顿：连续输入保持 60fps

## 💻 核心实现

### 第一步：WebSocket 连接管理

```ts
// hooks/useChatSocket.ts —— 连接生命周期封装成 Hook
import { useEffect, useRef, useState } from 'react';
import type { Message } from '@/types';

// 回显服务：把发出去的消息原样返回，用于模拟对端
const ECHO_WS_URL = 'wss://echo.websocket.events';

export function useChatSocket(onMessage: (msg: Message) => void) {
  const [status, setStatus] = useState<'connecting' | 'open' | 'closed'>('connecting');
  const wsRef = useRef<WebSocket | null>(null);
  // onMessage 存入 ref：回调变化不必重建连接（稳定依赖的经典解法）
  const cbRef = useRef(onMessage);
  cbRef.current = onMessage;

  useEffect(() => {
    let retry = 0;
    let timer: ReturnType<typeof setTimeout>;

    const connect = () => {
      setStatus('connecting');
      const ws = new WebSocket(ECHO_WS_URL);
      wsRef.current = ws;

      ws.onopen = () => { retry = 0; setStatus('open'); };
      ws.onmessage = (e) => {
        const msg: Message = { id: String(Date.now()), text: String(e.data), mine: false, sentAt: Date.now() };
        cbRef.current(msg);
      };
      ws.onclose = () => {
        setStatus('closed');
        // 指数退避重连：1s、2s、4s…上限 30s，避免服务端被打爆
        timer = setTimeout(connect, Math.min(1000 * 2 ** retry++, 30_000));
      };
    };

    connect();
    return () => { clearTimeout(timer); wsRef.current?.close(); }; // 卸载时清理
  }, []);

  return {
    status,
    send: (text: string) => wsRef.current?.send(text),
  };
}
```

### 第二步：倒置消息列表

```tsx
// app/chat.tsx —— 聊天主界面
import { memo, useCallback, useState } from 'react';
import { FlatList, KeyboardAvoidingView, Platform, Pressable, Text, TextInput, View } from 'react-native';
import { useChatSocket } from '@/hooks/useChatSocket';
import type { Message } from '@/types';

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState('');

  const { status, send } = useChatSocket(
    useCallback((msg: Message) => setMessages((prev) => [msg, ...prev]), []) // 稳定引用
  );

  const submit = () => {
    const text = draft.trim();
    if (!text) return;
    // 乐观更新：本地先上屏，再发网络（失败场景可加标红重试）
    setMessages((prev) => [{ id: String(Date.now()), text, mine: true, sentAt: Date.now() }, ...prev]);
    send(text);
    setDraft('');
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined} // Android 自带窗口缩放
    >
      {status !== 'open' && <Text style={styles.banner}>连接中…</Text>}

      {/* inverted 让列表首元素渲染在底部：新消息 unshift 进数组即"向上堆叠"，
          且键盘弹起时无需手动滚到底部 —— 这是聊天界面的标准解法 */}
      <FlatList
        inverted
        data={messages}
        keyExtractor={(m) => m.id}
        renderItem={({ item }) => <Bubble msg={item} />}
        contentContainerStyle={{ padding: 12 }}
      />

      <View style={styles.inputRow}>
        <TextInput style={styles.input} value={draft} onChangeText={setDraft}
          placeholder="输入消息" multiline />
        <Pressable onPress={submit}><Text>发送</Text></Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

// memo 隔离：其他消息变化时，已渲染气泡不重渲染
const Bubble = memo(function Bubble({ msg }: { msg: Message }) {
  return (
    <View style={[styles.bubble, msg.mine && styles.mine]}>
      <Text style={styles.text}>{msg.text}</Text>
      {/* sentAt 为毫秒时间戳，展示层再格式化 */}
      <Text style={styles.time}>{new Date(msg.sentAt).toLocaleTimeString()}</Text>
    </View>
  );
});
```

## ⚡ 列表优化要点

| 优化 | 手段 | 效果 |
|------|------|------|
| 稳定回调 | `useCallback` + ref 存回调 | 连接不重建、子组件 props 不变 |
| 细粒度 memo | `memo(Bubble)` + 简单 props | 千条消息只渲染新增项 |
| 大列表替换 | FlashList（cell 复用） | 超长会话内存显著降低（见[渲染性能](../advanced-topics/performance/01-rendering-performance.md)） |
| 输入不卡顿 | 受控 `TextInput` 本身即可 | 避免在 onChangeText 里做重活 |

## ✅ 最佳实践

聊天先区分本地待发送、服务端已确认与发送失败三种消息状态，并用消息 id 对齐重试和回执，避免同一消息显示两次。新消息插入与历史分页要保持滚动位置；是否使用 inverted 取决于列表方向和交互设计，并非强制。

断线后以带抖动的退避重连，设置上限并补拉缺失消息。函数式更新有助于避免闭包旧值覆盖新消息；高频拷贝或渲染若成为瓶颈，再测量分页和 memo 的收益。验收包含“发送后断网再重试”以及“查看历史时收到新消息”。

## ❓ 常见问题

**Q1: iOS 键盘弹起输入框被遮住？**
A: 用 `KeyboardAvoidingView behavior="padding"`；复杂场景换 `react-native-keyboard-controller`，可监听键盘动画同步位移。

**Q2: inverted 列表顶部出现跳动？**
A: 通常由分页加载历史与 padding 同时触发；保证 key 稳定并避免插入时整表重排，或加 `maintainVisibleContentPosition`。

**Q3: 鸿蒙端 WebSocket 有差异吗？**
A: RNOH 走系统网络栈，API 一致；域名配置与排错见 [RNOH 字典](../reference/language-concepts/05-harmonyos-rnoh-api.md) 与 [故障排除](../reference/quick-references/02-troubleshooting.md)。

---

## 🔗 相关文档

- 📖 [核心组件 Props 全表](../reference/language-concepts/02-components-props.md) — FlatList inverted 等属性字典
- 📖 [TypeScript 类型模式](../reference/language-concepts/04-typescript-patterns.md) — Message 类型的工程化定义
- 📄 [核心组件、JSX 与 Flexbox 布局](../basics/03-components-jsx.md) — 列表组件入门
- 🚀 [生产级移动应用](./04-production-mobile-app.md) — 把聊天功能纳入完整产品工程
- 🎓 [渲染性能](../advanced-topics/performance/01-rendering-performance.md) — 本文优化手段的原理篇
- 🧪 [端到端测试](../testing/03-e2e-testing.md) — 用 Maestro 自动化验证聊天流程


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
