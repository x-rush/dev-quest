# Compose 入门核心 - Composable 函数、状态与布局

## 先看框架承担哪部分职责

**Compose 核心**：Composable 描述当前状态下的 UI，事件回调改变状态。Modifier 参与布局和交互，顺序可能改变效果。

**最小练习与预期结果**：将一个计数器拆成状态持有者和纯展示组件；两个预览输入不同 count 应显示不同值而无网络或存储副作用。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 以任务视角掌握 Jetpack Compose 三大基石——Composable 函数、状态管理与基础布局
>
> **目标读者**: 完成 basics 教程后、希望按任务快速落地 Compose 核心能力的 Android 初学者
>
> **前置知识**: Kotlin 基础语法、[Composable 与状态](../basics/04-composables-state.md)、[布局系统](../basics/05-layouts.md) 的基本概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐ |
| **标签** | `#jetpack-compose` `#composable` `#状态管理` `#布局` |
| **更新日期** | `2026年9月` |

</details>

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

状态提升是把共享状态交给共同使用者的合适所有者，例如父组件保存选择值，子组件接收值和 onSelect。只属于单个控件的状态可以留在本地；不要为了分层把所有东西推到 ViewModel。

Composable 描述界面，网络或订阅由具备生命周期的机制管理，避免重新组合时重复启动工作。拆组件以职责和复用为依据，不用嵌套三层作为性能定律。主题统一颜色与文字样式后，还要实际检查深色和大字体。

## 🔗 相关文档

- 📖 概念字典：[Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md) ｜ [Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md)
- 📖 前置教程：[Composable 与状态](../basics/04-composables-state.md) ｜ [布局系统](../basics/05-layouts.md)
- 🚀 后续学习：[Compose 进阶：侧效应、导航与动画](02-compose-advanced.md) ｜ [入门项目：本地笔记应用](../projects/01-notes-app.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
