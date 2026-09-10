# Compose 入门核心 - Composable 函数、状态与布局

> **文档简介**: 以任务视角掌握 Jetpack Compose 三大基石——Composable 函数、状态管理与基础布局
>
> **目标读者**: 完成 basics 教程后、希望按任务快速落地 Compose 核心能力的 Android 初学者
>
> **前置知识**: Kotlin 基础语法、[Composable 与状态](../basics/04-composables-state.md)、[布局系统](../basics/05-layouts.md) 的基本概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐ |
| **标签** | `#jetpack-compose` `#composable` `#状态管理` `#布局` |
| **更新日期** | `2026年9月` |

## 🎯 本篇任务清单

完成本文后，你将能够：

- ✅ 定义并组合 Composable 函数，理解重组的基本规则
- ✅ 使用 `remember` + `mutableStateOf` 管理 UI 状态
- ✅ 用状态提升（State Hoisting）设计可复用、可预览、可测试的组件
- ✅ 用 Column / Row / Box 搭出常见的界面结构

---

## 1️⃣ Composable 函数：UI 即函数

Compose 中没有 XML 与 View 树操作，UI 就是嵌套调用的 Kotlin 函数。

```kotlin
// 普通 Kotlin 函数 + @Composable 注解 = 一个 UI 单元
@Composable
fun GreetingCard(name: String) {
    // 嵌套调用另一个 Composable，形成 UI 树
    Text(text = "你好，$name！")
}
```

三条必须内化的规则：

| 规则 | 说明 |
|------|------|
| **幂等** | 相同入参应产出相同 UI，函数体内不要写副作用 |
| **任意顺序执行** | Compose 可能以任何顺序、任何频率重组函数体 |
| **只描述 UI** | 遵循 "UI = f(state)"，改变界面靠改变状态，而非操作视图 |

> 概念级速查（组件清单、参数表）见 [Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md)，本文只讲"怎么用"。

## 2️⃣ 状态：remember + mutableStateOf

```kotlin
import androidx.compose.runtime.*

@Composable
fun Counter() {
    // remember：重组时保留对象；mutableStateOf：让 Compose 追踪对其的读写
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("点击了 $count 次")
    }
}
```

工作原理拆解：

1. `count++` 触发 `MutableState.value` 的写入；
2. Compose 在上次重组中记录了**读取**过该状态的所有函数；
3. 下一帧只重新执行这些函数（即"重组"），UI 随之更新。

完整的 `State` / `MutableState` / `collectAsStateWithLifecycle` API 对照见
[Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md)。

**注意**：不带 `remember` 的 `mutableStateOf` 在每次重组都会新建状态，UI 永远停在初值——这是最常见的入门错误（更多坑见[故障排除](../reference/quick-references/02-troubleshooting.md)）。

## 3️⃣ 状态提升：可复用组件的关键

把状态从组件里"提"到调用方，组件就变成无状态的纯函数——可预览、可测试、可复用。

```kotlin
// ① 无状态组件：只接收值和回调，逻辑全部外置
@Composable
fun CounterCard(
    count: Int,                 // 状态由调用方传入（向下）
    onIncrement: () -> Unit,    // 事件向上回调
    modifier: Modifier = Modifier,
) {
    Card(modifier = modifier.padding(8.dp)) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("计数：$count", style = MaterialTheme.typography.headlineSmall)
            Button(onClick = onIncrement) { Text("+1") }
        }
    }
}

// ② 有状态包装：持有状态，内部复用无状态组件
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    CounterCard(count = count, onIncrement = { count++ })
}
```

**参数命名约定**：`value: T, onValueChange: (T) -> Unit`；顺序为"必填数据 → modifier（带默认值）→ 可选参数 → 回调"。

## 4️⃣ 布局：Column / Row / Box

```kotlin
@Composable
fun ProfileCard() {
    Box(modifier = Modifier.fillMaxWidth()) {          // 层叠容器：子项可重叠
        Column(                                        // 纵向排列
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text("用户名", style = MaterialTheme.typography.titleLarge)
            Text("签名：保持好奇", style = MaterialTheme.typography.bodyMedium)
            Row(                                       // 横向排列
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // weight(1f)：两个按钮平分剩余宽度
                Button(onClick = { /* 关注 */ }, modifier = Modifier.weight(1f)) {
                    Text("关注")
                }
                OutlinedButton(onClick = { /* 私信 */ }, modifier = Modifier.weight(1f)) {
                    Text("私信")
                }
            }
        }
    }
}
```

要点：

- **Modifier 顺序即生效顺序**：`padding()` 写在 `background()` 前后，留白效果完全不同；
- **长列表用 LazyColumn**：普通 `Column` 会一次性组合全部子项，Lazy 按需组合（详见[布局系统教程](../basics/05-layouts.md)）。

## 🎨 最佳实践

### ✅ 推荐

- **无状态优先**：组件设计为"状态提升"形态，预览与 UI 测试都因此变简单（见 [Compose UI 测试](../testing/02-ui-testing.md)）
- **样式走主题**：用 `MaterialTheme.typography/color`，不硬编码 sp/Color（主题速查见 [Material 3 主题系统](../reference/framework-essentials/02-compose-material3.md)）
- **状态尽量上提**：提到最近需要共享的祖先，或直接提到 ViewModel（见 [生态集成](03-ecosystem-integration.md)）

### ❌ 避免陷阱

- 在 Composable 内做 IO、改全局单例等副作用——用[侧效应 API](02-compose-advanced.md) 表达
- 组合期间直接启动协程（用 `LaunchedEffect` / `rememberCoroutineScope`）
- 嵌套超过 3 层不拆分，导致重组范围过大、可读性差

## 🔗 相关文档

- 📖 概念字典：[Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md) ｜ [Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md)
- 📖 前置教程：[Composable 与状态](../basics/04-composables-state.md) ｜ [布局系统](../basics/05-layouts.md)
- 🚀 后续学习：[Compose 进阶：侧效应、导航与动画](02-compose-advanced.md) ｜ [入门项目：本地笔记应用](../projects/01-notes-app.md)
