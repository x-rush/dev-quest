# 高级项目：协作看板（乐观更新 + 实时同步）

## 分阶段练习与验收

**最小阶段**：先做单用户卡片状态变更，再模拟两个用户。

**验收结果**：旧响应不会覆盖新操作，失败后客户端与服务器重新一致。

**扩展顺序**：拖拽外观放在状态与并发规则之后，冲突策略必须可解释。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 构建多人协作 Kanban：拖拽秒响应（乐观更新）+ 服务端 SSE 广播其他成员变更（setQueryData 增量合并），并给出冲突处理方案。
>
> **目标读者**: 已掌握乐观更新模式、要挑战多客户端状态一致性的进阶开发者
>
> **前置知识**: [Query 进阶](../frameworks/02-tanstack-query-advanced.md)、[Query 高级特性教程](../basics/07-advanced-features.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#实战项目` `#乐观更新` `#实时同步` `#sse` `#协同` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 项目目标

- 拖拽卡片跨列：本地立即生效，失败自动回滚
- 其他成员的增删改通过 SSE 推送，本地缓存增量合并（不整页刷新）
- 服务端带版本号广播，乱序/迟到消息不覆盖新数据

**核心思路**：本地操作走乐观更新，远端事件走缓存直写，两者都只操作同一个缓存条目——缓存仍是唯一事实来源。

---

## 1. 数据模型与缓存结构

```ts
// src/api/board.ts
export interface Card {
  id: string
  columnId: string
  title: string
  version: number // 服务端版本号，每次变更加 1
}

export interface Board {
  columns: { id: string; title: string; cardIds: string[] }[]
  cards: Record<string, Card>
}

export const boardKeys = {
  board: (boardId: string) => ['board', boardId] as const,
}

export async function fetchBoard(boardId: string): Promise<Board> {
  const res = await fetch(`/api/boards/${boardId}`)
  if (!res.ok) throw new Error('看板加载失败')
  return res.json()
}

export async function moveCard(cardId: string, toColumn: string, index: number) {
  const res = await fetch(`/api/cards/${cardId}/move`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ toColumn, index }),
  })
  if (!res.ok) throw new Error('移动失败')
  return res.json() as Promise<Card>
}
```

---

## 2. 拖拽移动：乐观更新 + 回滚

```ts
// src/hooks/use-move-card.ts
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { boardKeys, moveCard, type Board } from '../api/board'

export function useMoveCard(boardId: string) {
  const qc = useQueryClient()
  const key = boardKeys.board(boardId)

  return useMutation({
    mutationFn: (input: { cardId: string; toColumn: string; index: number }) =>
      moveCard(input.cardId, input.toColumn, input.index),

    onMutate: async ({ cardId, toColumn, index }) => {
      await qc.cancelQueries({ queryKey: key }) // ① 阻止在途请求覆盖乐观结果
      const previous = qc.getQueryData<Board>(key) // ② 快照

      qc.setQueryData<Board>(key, (old) => {
        if (!old) return old
        const card = old.cards[cardId]
        if (!card) return old
        const columns = old.columns.map((col) => {
          const ids = col.cardIds.filter((id) => id !== cardId)
          if (col.id === toColumn) ids.splice(index, 0, cardId) // ③ 乐观重排
          return { ...col, cardIds: ids }
        })
        return {
          ...old,
          columns,
          cards: { ...old.cards, [cardId]: { ...card, columnId: toColumn } },
        }
      })

      return { previous } // ④ 交给回滚（拖拽高频时，可改为仅在 onError 回滚、onSuccess 直写，见 §4）
    },

    onError: (_err, _input, ctx) => {
      if (ctx?.previous) qc.setQueryData(key, ctx.previous)
    },
    onSettled: () => qc.invalidateQueries({ queryKey: key }),
  })
}
```

---

## 3. SSE 订阅：远端变更写缓存

```ts
// src/hooks/use-board-sync.ts
import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { boardKeys, type Board, type Card } from '../api/board'

type ServerEvent =
  | { type: 'card.moved'; boardId: string; card: Card; index: number }
  | { type: 'card.created'; boardId: string; card: Card }
  | { type: 'card.deleted'; boardId: string; cardId: string }

export function useBoardSync(boardId: string) {
  const qc = useQueryClient()

  useEffect(() => {
    const es = new EventSource(`/api/boards/${boardId}/events`)

    es.onmessage = (e) => {
      const event = JSON.parse(e.data) as ServerEvent
      const key = boardKeys.board(event.boardId)

      qc.setQueryData<Board>(key, (old) => {
        if (!old) return old
        switch (event.type) {
          case 'card.moved': {
            // 版本号守卫：迟到的旧消息不覆盖新状态
            const existing = old.cards[event.card.id]
            if (existing && existing.version >= event.card.version) return old
            const columns = old.columns.map((col) => {
              const ids = col.cardIds.filter((id) => id !== event.card.id)
              if (col.id === event.card.columnId) ids.splice(event.index, 0, event.card.id)
              return { ...col, cardIds: ids }
            })
            return { ...old, columns, cards: { ...old.cards, [event.card.id]: event.card } }
          }
          case 'card.created':
            return {
              ...old,
              cards: { ...old.cards, [event.card.id]: event.card },
              columns: old.columns.map((c) =>
                c.id === event.card.columnId
                  ? { ...c, cardIds: [...c.cardIds, event.card.id] }
                  : c,
              ),
            }
          case 'card.deleted': {
            const cards = { ...old.cards }
            delete cards[event.cardId]
            return {
              ...old,
              cards,
              columns: old.columns.map((c) => ({
                ...c,
                cardIds: c.cardIds.filter((id) => id !== event.cardId),
              })),
            }
          }
        }
      })
    }

    // 断线兜底：EventSource 自动重连，重连成功后全量对齐一次
    es.onopen = () => void qc.invalidateQueries({ queryKey: boardKeys.board(boardId) })

    return () => es.close()
  }, [boardId, qc])
}
```

---

## 4. 双写冲突的取舍

本方案是"乐观本地写 + 版本号广播"的简化版，足够大多数团队看板使用：

| 方案 | 一致性 | 复杂度 | 适用 |
|------|--------|--------|------|
| 本文档：LWW + version 守卫 | 最终一致 | 低 | 看板、文档树 |
| 服务端拒绝 + 重放（OT 雏形） | 强一致 | 中 | 表格行编辑 |
| CRDT | 收敛一致 | 高 | 白板、富文本 |

**两条铁律**：
1. 本地乐观写与远端直写**都必须过版本号检查**，否则 last-write-wins 会静默丢更新
2. 断线重连后必须 `invalidateQueries` 全量对齐，SSE 只是"增量通道"，不是"事实来源"

---

## 5. 验收清单

- [ ] 拖拽卡片：松手即到位，0 感知延迟
- [ ] 拖拽时断网：卡片弹回原位（回滚生效），恢复后自动重新对齐
- [ ] 开两个浏览器窗口：A 移动卡片，B 在 200ms 内同步（无需刷新）
- [ ] Devtools 时间轴中看不到整板 refetch（远端事件走 setQueryData 直写）

---

## 🔗 相关文档

- 📄 **[Query 进阶](../frameworks/02-tanstack-query-advanced.md)** - 乐观更新四步模式出处
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - setQueryData / cancelQueries 字典
- 📄 **[Query 缓存架构与数据流](../advanced-topics/architecture/01-cache-architecture.md)** - 为什么缓存能当事实来源
- 📄 **[集成测试](../testing/03-integration-testing.md)** - 拖拽与 SSE 的测试策略
- 📄 **[SaaS 后台](../projects/04-saas-admin-platform.md)** - 更大规模的生产级整合


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
