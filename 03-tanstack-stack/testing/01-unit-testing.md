# 单元测试：Vitest 与 Query 逻辑

> **文档简介**: 用 Vitest 覆盖 Query 项目的纯逻辑单元：fetch 封装、Query Key 工厂、乐观更新器函数——不挂载 React，跑得飞快。
>
> **目标读者**: 需要为 Query 项目建立测试底座的开发者
>
> **前置知识**: [Todo App](../projects/01-todo-app.md)、TypeScript 基础

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#vitest` `#单元测试` `#tanstack-query` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 完成后你将能够

- 配置支持 TS 路径别名与 React 生态的 Vitest
- 测试 api 层、键工厂、乐观更新器等纯单元
- 明确"单元测试"与 [Mock 服务测试](./02-mocking-server.md)、[集成测试](./03-integration-testing.md) 的分工

---

## 1. Vitest 配置

```bash
npm install -D vitest @vitejs/plugin-react
```

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'node', // 纯逻辑用 node；渲染测试文件再切 jsdom（见集成测试）
    include: ['src/**/*.test.{ts,tsx}'],
    coverage: {
      reporter: ['text', 'lcov'],
      include: ['src/api/**', 'src/hooks/**', 'src/shared/**'],
      thresholds: { lines: 80 }, // 数据层是核心，阈值设高些
    },
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
})
```

```json
// package.json scripts
{ "test": "vitest run", "test:watch": "vitest", "test:coverage": "vitest run --coverage" }
```

---

## 2. 测什么：Query 项目的三类单元

### 2.1 API 层（错误分支最重要）

```ts
// src/api/todos.test.ts
import { describe, it, expect, vi, afterEach } from 'vitest'
import { todoApi } from './todos'

describe('todoApi', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('list：正常返回解析后的 JSON', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify([{ id: 1, title: 'a', done: false }]), { status: 200 }),
    ))
    await expect(todoApi.list()).resolves.toHaveLength(1)
  })

  it('list：非 2xx 抛出带状态码的错误', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', { status: 500 })))
    await expect(todoApi.list()).rejects.toThrow('请求失败 500')
  })
})
```

### 2.2 Query Key 工厂（键错了缓存全错）

```ts
// src/api/keys.test.ts
import { describe, it, expect } from 'vitest'
import { todoKeys } from './todos'

describe('todoKeys', () => {
  it('detail 键必须以 details 为前缀（前缀失效依赖此结构）', () => {
    expect(todoKeys.detail(7)).toEqual(['todos', 'detail', 7])
    expect(todoKeys.detail(7).slice(0, 2)).toEqual(todoKeys.details().slice(0, 2))
  })

  it('all 是一切键的最长公共前缀', () => {
    expect(todoKeys.lists().slice(0, 1)).toEqual(todoKeys.all)
    expect(todoKeys.detail(1).slice(0, 1)).toEqual(todoKeys.all)
  })
})
```

### 2.3 乐观更新器（纯函数部分抽出来测）

把 setQueryData 的 updater 写成独立纯函数，就能脱离 React 单测：

```ts
// src/features/board/optimistic.ts
import type { Board } from './types'
export function applyMove(board: Board, cardId: string, toColumn: string, index: number): Board {
  // 与 useMoveCard 中 setQueryData 的逻辑完全一致
  const card = board.cards[cardId]
  if (!card) return board
  const columns = board.columns.map((col) => {
    const ids = col.cardIds.filter((id) => id !== cardId)
    if (col.id === toColumn) ids.splice(index, 0, cardId)
    return { ...col, cardIds: ids }
  })
  return { ...board, columns, cards: { ...board.cards, [cardId]: { ...card, columnId: toColumn } } }
}
```

```ts
// src/features/board/optimistic.test.ts
import { describe, it, expect } from 'vitest'
import { applyMove } from './optimistic'

const board = {
  columns: [
    { id: 'c1', title: '待办', cardIds: ['a', 'b'] },
    { id: 'c2', title: '进行中', cardIds: [] },
  ],
  cards: { a: { id: 'a', columnId: 'c1', title: 'A', version: 1 } },
}

describe('applyMove', () => {
  it('跨列移动：源列移除、目标列按 index 插入', () => {
    const next = applyMove(board, 'a', 'c2', 0)
    expect(next.columns[0].cardIds).toEqual(['b'])
    expect(next.columns[1].cardIds).toEqual(['a'])
  })

  it('卡片不存在时返回原对象（不可变约定）', () => {
    expect(applyMove(board, 'ghost', 'c2', 0)).toBe(board)
  })
})
```

---

## 3. 与其他测试层的分工

| 层 | 工具 | 覆盖 | 本文范围 |
|----|------|------|----------|
| 单元 | Vitest + vi.stubGlobal | 纯函数、错误分支 | ✅ |
| 服务模拟 | MSW | hook 与真实 HTTP 语义 | → [02](./02-mocking-server.md) |
| 集成 | Testing Library | hook + 组件 + 缓存协作 | → [03](./03-integration-testing.md) |
| 端到端 | Playwright | 真实浏览器全链路 | → [04](./04-e2e-testing.md) |

---

## 🎨 最佳实践速查

将乐观更新的数据变换提成纯函数，可以直接验证空列表、目标不存在和重复修改。需要验证 Hook 与缓存交互时，应使用独立 QueryClient 和 Provider；测试类别取决于验证边界，不存在“单元测试绝不能挂 Provider”的规则。

保留 Query 的真实行为，优先替换网络边界，并控制重试和时间以获得可预测反馈。至少验证首次失败、重试成功、后台失败保留已有数据，避免只断言 mock 被调用过。

---

## 🔗 相关文档

- 📄 **[Mock 服务：MSW](./02-mocking-server.md)** - 下一层：带真实 HTTP 语义的测试
- 📄 **[集成测试](./03-integration-testing.md)** - renderHook 与组件级验证
- 📄 **[入门项目 Todo App](../projects/01-todo-app.md)** - 被测代码来源
- 📄 **[Query 进阶](../frameworks/02-tanstack-query-advanced.md)** - 乐观更新器逻辑出处
- 📄 **[CI/CD 流水线](../deployment/01-ci-cd-pipelines.md)** - 把本层测试挂进流水线


<!-- acceptance-exercise -->
## 练习与验收：验证键工厂与输入边界

选择项目中的 queryKey 工厂和分页解析函数：同一资源的相同参数产生等价键，不同账号或分页不得误共用；非法页码回到约定默认值或明确拒绝。把账号字段故意从键里删除，至少一个隔离测试应失败。验收：恢复后测试通过，改变执行顺序仍通过；这组纯函数测试不需要真实网络，也不能证明 Provider 和界面订阅正确。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
