# 生态集成：官方周边库指南

## 概述

TanStack 官方生态除五大核心库外还有一批"小而美"的周边库。本篇按用途收录：调试、缓存持久化、虚拟滚动、滑块、轻量状态与速率控制。教程见 [环境搭建](../../basics/01-environment-setup.md)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Devtools` `#persist-client` `#FormDevtools` `#Virtual` `#Ranger` `#Store` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. React Query Devtools

### 定义

可视化缓存检查器：查看每条查询的 key、状态（fresh/stale）、dataUpdatedAt，可手动失效/重取/删除缓存条目。

### 语法

```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// 必须放在 QueryClientProvider 内部；生产构建自动摇树移除
<ReactQueryDevtools
  initialIsOpen={false}
  buttonPosition="bottom-right"
  toggleButtonAriaLabel="Query 面板"
/>
```

### 陷阱

- Devtools 显示的是**当前 Provider** 的缓存——多 QueryClient（如测试）时容易看错实例
- Router 也有对应面板：`@tanstack/router-devtools` 的 `<TanStackRouterDevtools />`，展示路由树与匹配状态

## 2. 缓存持久化：query-persist-client

### 定义

把 Query 缓存序列化到 localStorage/IndexedDB，刷新页面或下次进站时秒开内容。

### 安装与语法

```bash
pnpm add @tanstack/react-query-persist-client @tanstack/query-sync-storage-persister
```

```tsx
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client'
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister'

const persister = createSyncStoragePersister({
  storage: window.localStorage,
  key: 'app-query-cache',
});

<PersistQueryClientProvider
  client={queryClient}
  persistOptions={{
    persister,
    maxAge: 1000 * 60 * 60 * 24, // 缓存最长 24h
    buster: 'v1',                // 数据结构变更时手动升版本使旧缓存失效
  }}
>
  <App />
</PersistQueryClientProvider>
```

异步存储（IndexedDB 封装）换 persister 即可，Provider 结构不变：

```bash
pnpm add @tanstack/query-async-storage-persister
```

```tsx
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister'

const asyncPersister = createAsyncStoragePersister({
  // AsyncStorage 接口：三个方法都返回 Promise
  storage: {
    getItem: async (key) => (await idbGet(key)) ?? null,
    setItem: async (key, value) => { await idbSet(key, value) },
    removeItem: async (key) => { await idbRemove(key) },
  },
  key: 'app-query-cache-idb',
})
```

### 陷阱

- 恢复期间 Provider 协调查询启动；正常持久化订阅期间仍可重取——实时敏感数据要慎用
- 大缓存（数 MB）同步序列化会阻塞主线程，移动端建议 `@tanstack/query-async-storage-persister` + IndexedDB
- 忘改 `buster` 是"发版后旧数据污染"的经典来源

## 3. 虚拟滚动：TanStack Virtual

### 定义

只渲染视口内的行，配合 Table 渲染十万行级数据。同样是 Headless 设计。

### 安装与语法

```bash
pnpm add @tanstack/react-virtual
```

```tsx
import { useRef } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualRows({ rows }: { rows: string[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35, // 行高估算，越准滚动越稳
    overscan: 5,            // 视口外多渲染几行，减少白屏
  })

  return (
    <div ref={parentRef} style={{ height: 400, overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map((vi) => (
          <div key={vi.key} style={{
            position: 'absolute', top: 0, height: vi.size,
            transform: `translateY(${vi.start}px)`,
          }}>
            {rows[vi.index]}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 陷阱

- `estimateSize` 严重失准时滚动条会跳动，动态行高用 `measureElement` 实测
- 与 Table 组合时虚拟化的是 `table.getRowModel().rows`，行定位用绝对位移替代 `<table>` 原生布局

## 4. 滑块：TanStack Ranger

### 定义

Headless 多点滑块/区间选择逻辑，价格区间筛选的现成方案。

### 安装与语法

```bash
pnpm add @tanstack/react-ranger
```

```tsx
import { useRanger } from '@tanstack/react-ranger'

const rangerRef = useRef<HTMLDivElement>(null)
const [values, setValues] = useState<number[]>([20, 80]) // 双把手区间

const rangerInstance = useRanger<HTMLDivElement>({
  values, onChange: (instance) => setValues([...instance.sortedValues]),
  min: 0, max: 100, stepSize: 5,
  getRangerElement: () => rangerRef.current, // 轨道 DOM，把手 UI 自行渲染
})
```

### 陷阱

- Ranger 同样零 UI：轨道、把手、提示框全要自己画，样式要求不高时选原生 `input[type=range]` 更快

## 5. 其他成员：Store 与 Pacer

- **`@tanstack/store`**：框架无关的极简响应式 store，TanStack 内部多库的状态基座。`new Store(0)` 创建、`setState` 更新，React 侧用 `useStore(s)` 订阅；跨服务端渲染需按请求隔离实例。
- **`@tanstack/pacer`**：框架无关的防抖/节流/限速工具集，如 `debounce((q) => api.suggest(q), { wait: 300 })`；与 Form 内置 `onChangeDebounceMs` 功能重叠，同一场景别叠两层防抖。

## 6. Form Devtools

### 定义

`@tanstack/react-form-devtools` 提供 Form 表单状态面板（字段值、校验错误、提交状态）。两种挂法：作为插件挂进统一的 `@tanstack/react-devtools` 壳（与 Query/Router 面板同处一地），或单独渲染 `FormDevtoolsPanel`。

### 安装与语法

```bash
pnpm add @tanstack/react-form-devtools @tanstack/react-devtools
```

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools'
import {
  formDevtoolsPlugin,      // 插件形态：挂进 Devtools 壳
  FormDevtoolsPanel,       // 面板形态：单独渲染
} from '@tanstack/react-form-devtools'

function DevtoolsRoot() {
  // 插件挂法：与 Query/Router 面板并列出现在同一个壳里
  return <TanStackDevtools plugins={[formDevtoolsPlugin()]} />
}

function PanelOnly() {
  return <FormDevtoolsPanel />
}
```

### 陷阱

- 生产是否包含面板取决于包导出条件与构建配置，不要把 `/production` 名称直接等同于 NoOp；按安装版本的官方说明配置，并检查实际产物
- 插件形态依赖 `@tanstack/react-devtools` 壳（`plugins` 数组）；只想在页面角落开面板用 `FormDevtoolsPanel` 即可

## 相关文档

- 📄 **[环境搭建](../../basics/01-environment-setup.md)** - Devtools 安装步骤
- 📄 **[Table 核心 API](../language-concepts/02-table-core-api.md)** - 与 Virtual 组合的行模型
- 📄 **[缓存持久化](../language-concepts/14-query-persistence.md)** - persister 模式的字典级参考
- 📄 **[Form 核心 API](../language-concepts/04-form-core-api.md)** - 面板中各状态的来源
- 📄 **[相关库搭配](./02-related-libs.md)** - Zustand/Jotai 等三方选择


<!-- full-library-explanation -->
## 按具体缺口选择周边工具

先修：Query、Table 或 Form 的一个最小应用。Devtools 帮助观察状态，Virtual 减少 DOM 数量，persister 负责恢复缓存，Ranger 提供滑块交互逻辑。它们解决不同问题，不需要为了“完整技术栈”全部安装。

Virtual 不减少后端传输的数据量。十万条数据全部下载后仅渲染几十行，网络和内存成本仍存在；先判断需要分页、虚拟化还是两者组合。动态高度、键盘焦点、屏幕阅读器和滚动定位都应单独验证。

本页存储示例依赖浏览器；localStorage 访问可能抛错，IndexedDB 的 idbGet/idbSet/idbRemove 也需要实际实现。完整边界与 gcTime/maxAge 配置见[持久化条目](../language-concepts/14-query-persistence.md)。

**练习：** 对同一列表记录普通渲染与虚拟渲染的 DOM 节点数，再比较 HTTP 传输大小。验收：能解释为什么前者减少而后者不变。滑块还应测试键盘上下调节，不只测试鼠标拖动。

官方参考：[Ranger 示例](https://tanstack.com/ranger/latest/docs/framework/react/examples/basic)、[Form Devtools](https://tanstack.com/form/latest/docs/framework/react/guides/devtools)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
