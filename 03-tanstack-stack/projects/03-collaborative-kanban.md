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

**核心思路**：服务器持有权威数据，客户端缓存只保存最近读取的快照和临时乐观状态。下面先展示单个在途移动请求的练习；不能把整板快照回滚直接用于并发拖拽。并发、删除后的旧消息和离线补偿需要第 4 节的协议设计。

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

先复制[单元测试篇的 `applyMove`](../testing/01-unit-testing.md)到 `src/features/board/optimistic.ts`，运行未知卡片、未知目标、非法位置和输入不可变性用例。它使用本节 `src/api/board.ts` 中的类型。界面在一次移动结算前禁用新的拖拽；下列整板快照回滚示例仅用于这个串行练习。

```ts
// src/hooks/use-move-card.ts
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { boardKeys, moveCard, type Board } from '../api/board'
import { applyMove } from '../features/board/optimistic'

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
        return applyMove(old, cardId, toColumn, index) // ③ 校验目标后进行不可变重排
      })

      return { previous } // ④ 串行练习的回滚快照；不适用于并发移动
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

上面的 SSE 示例只展示单条移动消息的版本比较，尚未构成完整的协作协议：`card.deleted` 没有删除版本（墓碑），迟到的 `card.created` 可以重新插入已经删除的卡片；重复的创建事件也会重复追加 id。服务端 `version` 不能保护没有服务器版本号的本地乐观修改，整板回滚还可能覆盖在请求期间收到的其他用户更新。

完成单用户阶段后，按下面顺序扩展协议，并先用合成事件序列测试再接 SSE：

1. 每个看板事件携带单调递增的 `revision`。客户端只接收下一个版本；重复版本忽略，遇到版本缺口重新获取权威快照。所有事件先做运行时结构校验并确认 `boardId` 与当前订阅一致。
2. 创建事件按 id 去重，移动时验证目标列；删除事件携带版本并保留墓碑，阻止旧创建或移动消息复活已删除卡片。
3. 将服务器快照与本地待确认操作分开保存。失败时只撤销本次操作，再在最新服务器快照上重放其余操作；不要恢复过时的整板快照。请求还应有幂等操作 id。
4. 重连后带游标补发事件或拉取权威快照；只有服务端确认成功才从待确认队列删除本地操作。

| 方案 | 一致性 | 复杂度 | 适用 |
|------|--------|--------|------|
| 单个请求 + 失败后重取快照 | 由服务器决定最终状态 | 低 | 本文最小练习 |
| 版本冲突拒绝 + 应用层重放 | 取决于事务、版本检查及客户端协议 | 中 | 需要明确冲突反馈的看板 |
| CRDT | 满足具体算法前提时收敛 | 高 | 多端离线编辑；须选择与数据类型匹配的算法 |

上表的重放不等于 OT，也不自动保证强一致。对初学者，先把 SSE 当作“数据已变化”的通知，仅触发受控重新获取即可建立正确基线；完成协议测试后再用增量直写减少请求。

---

## 5. 验收清单

- [ ] 最小阶段：跨列、同列首尾移动、非法目标都不会丢卡或产生重复 id；输入快照未被修改。
- [ ] 一个在途请求时禁止再次拖拽；服务器返回 500 后恢复并重新读取，客户端最终等于服务器。
- [ ] 双窗口记录操作、服务器确认和远端可见时刻，报告实际延迟；不把无测试环境说明的 200ms 当作通用保证。
- [ ] 进阶阶段：按“创建 v1、删除 v2、迟到创建 v1”和重复事件输入验证不会复活或重复；版本缺口触发重取。
- [ ] 本地移动待确认期间收到远端更新，再让本地请求失败，远端更新仍保留。此项通过前不宣称支持并发协作。

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
