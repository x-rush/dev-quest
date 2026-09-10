# 应用架构 - 官方分层与单向数据流（UDF）

> **文档简介**: 剖析 Android 官方推荐架构的设计动机：UI/领域/数据三层职责、单向数据流（UDF）不变量、状态持有者分工，以及它为什么能消灭"状态竞争"
>
> **目标读者**: 已按[生态集成](../../frameworks/03-ecosystem-integration.md)搭过完整链路、想理解"为什么这样组织"的中高级学习者
>
> **前置知识**: ViewModel 与 StateFlow 实践、[Compose 状态 API 详解](../../reference/language-concepts/04-compose-state-api.md)、[协程与 Flow API 全表](../../reference/language-concepts/03-coroutines-flow-api.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 深度解释（advanced-topics） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#architecture` `#udf` `#layering` `#state-holder` |
| **更新日期** | `2026年9月` |

---

## 1️⃣ 官方推荐分层

```
┌──────────────────────────────────────────────────┐
│ UI 层   Composable（渲染）+ ViewModel（状态持有）   │ ← "屏幕上是什么"
├──────────────────────────────────────────────────┤
│ 领域层  UseCase（可选）：组合业务规则               │ ← "业务规则是什么"
├──────────────────────────────────────────────────┤
│ 数据层  Repository ← Data Sources(Remote/Local)   │ ← "数据从哪来、如何一致"
└──────────────────────────────────────────────────┘
   依赖方向永远向下；上层知道下层，下层不知道上层
```

两套核心模式贯穿各层：

- **单向数据流（UDF）**：状态从上往下流，事件从下往上传，任何一层只改自己持有的状态
- **关注点分离**：每层只暴露接口与领域模型，不泄露实现（Room 实体不出数据层）

## 2️⃣ 为什么是 UDF？

回忆没有 UDF 的年代：Fragment 与 Activity 互相改对方控件、异步回调里改全局变量、
任何线程都可能写任何状态——bug 的根源是**状态可从多个方向被修改**。

UDF 把写路径收敛为单一方向：

```
事件（用户/系统）→ ViewModel → Repository → 数据源
状态：数据源 → Flow → ViewModel(UiState) → Composable 渲染
```

由此得到的三个不变量：

1. **单一事实来源（SSOT）**：每个状态只有一名所有者（[Compose 状态 API 详解](../../reference/language-concepts/04-compose-state-api.md)）
2. **状态向下、事件向上**：Compose 组件永远可以被无状态复用
3. **可测试**：整条链路除边界外都是纯 Kotlin，可 Fake 注入（见[单元测试](../../testing/01-unit-testing.md)）

## 3️⃣ UI 层内部：两种状态持有者

| | ViewModel | 普通状态持有者（state holder 类） |
|---|-----------|--------------------------------|
| 管什么 | 业务状态（列表、错误、加载） | UI 状态（滚动位置、输入草稿、动画标志） |
| 生命周期 | 配置变更存活 | 可跟随界面重建 |
| 依赖 | Repository（业务依赖） | 无业务依赖，纯 Compose/平台 API |
| 测试 | JVM 单元测试 | 可单元可 UI 测试 |

```kotlin
// UI 逻辑抽成普通类：不占 ViewModel，可复用可测试
class MessageListState(
    private val listState: LazyListState = LazyListState(),
) {
    val showScrollToTop: Boolean
        get() = listState.firstVisibleItemIndex > 5
    suspend fun scrollToTop() = listState.animateScrollToItem(0)
}

@Composable
fun rememberMessageListState() = remember { MessageListState() }
```

判断口诀：**涉及"业务决策"进 ViewModel，只关乎"界面表现"留 Composable/状态持有者**。
这正呼应[架构分层蓝图](../../frameworks/03-ecosystem-integration.md)中 Room→ViewModel→UI 的收束。

## 4️⃣ 领域层何时引入

默认**不要**建 UseCase——多一层就多一分间接性。只有出现以下信号时才引入：

- 多个 ViewModel 重复同一段业务规则（如"下单前校验库存+风控"）
- ViewModel 因业务编排过于臃肿（合并多个 Repository + 时序 + 重试）
- 规则需要独立测试且被多入口复用

```kotlin
// 引入后的形态：业务规则的唯一居所
class PlaceOrderUseCase @Inject constructor(
    private val orders: OrderRepository,
    private val inventory: InventoryRepository,
) {
    suspend operator fun invoke(cart: Cart): Result<Order> {
        inventory.validate(cart) ?: return Result.failure(InsufficientStockException())
        return orders.submit(cart)
    }
}
```

## 5️⃣ 数据层的不变量

- **Repository 是 API 的抽象，不是"DAO 的转发器"**：决定网络优先还是缓存优先、如何去重合并
- 多源数据在 Repository 内 merge（[新闻阅读器](../../projects/03-news-reader.md) 的 RemoteMediator 是官方范式）
- 数据层抛领域错误而非平台异常（转译模式见[生产级应用](../../projects/04-production-android-app.md)）

## 6️⃣ 常见反模式

| 反模式 | 危害 | 纠正 |
|--------|------|------|
| Composable 直接调 Repository | 绕过状态收敛，不可测试 | 事件只交 ViewModel |
| ViewModel 返回 MutableStateFlow 给 UI | UI 可越权写状态 | `asStateFlow()` 只读暴露 |
| 两个屏幕互相同步对方状态 | 状态竞争，永远对不齐 | 状态上提到共享父级/共享 VM |
| 数据层返回 Room Entity 到 UI | 表结构变更波及界面 | DTO/Entity/Domain 三模型隔离 |

## 7️⃣ 与多模块的映射

分层与[多模块结构](../../projects/04-production-android-app.md)是一体两面：
`core/database`、`core/network` 实现数据层；`feature/*` 各自封装 UI 层；
模块间依赖规则 = 分层依赖规则的物理化（feature 只能依赖 core 抽象，不能横向依赖）。

## 🔗 相关文档

- 📖 概念字典：[Compose 状态 API 详解](../../reference/language-concepts/04-compose-state-api.md) ｜ [协程与 Flow API 全表](../../reference/language-concepts/03-coroutines-flow-api.md)
- 📖 操作指南：[生态集成](../../frameworks/03-ecosystem-integration.md) ｜ [生产级 Android 应用](../../projects/04-production-android-app.md)
- 🎓 延伸解释：[重组优化](../performance/01-recomposition-optimization.md) ｜ [安全实践](../security/01-security-practices.md)
