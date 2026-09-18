# 常见错误与故障排除

> **阅读准备**：能获取完整编译错误、Logcat 与依赖版本；按具体故障查阅，不需先通读全部参考。

> Compose/Kotlin 开发高频故障的症状→原因→修复速查：重组死循环、状态丢失、协程泄漏、性能陷阱与构建问题

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#故障排除` `#重组` `#状态丢失` `#协程泄漏` `#性能` |
| **更新日期** | `2026年9月` |

**使用方式**: 按症状定位词条 → 核对"原因"确认前提 → 应用"修复"。每个词条独立，可任意跳入。

---

## 1. 无限重组死循环

### 症状
应用卡死，Logcat 刷屏 "Recomposer ... frames" 或最终栈溢出崩溃。

### 原因
在**组合期间**直接写状态：写状态 → 触发重组 → 再次写 → 无限循环。

```kotlin
@Composable
fun Broken() {
    var count by remember { mutableStateOf(0) }
    count++                                    // ❌ 组合中写状态
    Text("$count")
}
```

### 修复
状态写入只允许出现在：事件回调（`onClick`）、`LaunchedEffect`、`SideEffect`、ViewModel。

```kotlin
LaunchedEffect(Unit) { count = 10 }            // ✅ 副作用 API 中写
Button(onClick = { count++ }) { Text("$count") }  // ✅ 事件回调中写
```

---

## 2. 旋转屏幕后状态丢失

### 症状
输入一半的文字、选中的标签在旋转后归零。

### 原因分层排查
1. 用了 `remember`（只扛重组，不扛配置变更）
2. 状态放在 Composable 里而非 ViewModel
3. Activity 被重建但 ViewModel 也跟着没了（跨进程被杀）

### 修复
```kotlin
// 层级 1：简单 UI 状态 → rememberSaveable
var query by rememberSaveable { mutableStateOf("") }

// 层级 2：业务状态 → ViewModel + StateFlow
class VM : ViewModel() { val query = MutableStateFlow("") }

// 层级 3：进程被杀也恢复 → 持久化（Room/DataStore）或 rememberSaveable
```

### 陷阱
大列表（几百 KB+）塞 `rememberSaveable` 会因 Bundle 体积限制崩溃（TransactionTooLargeException）——大数据可由 ViewModel 在内存持有；跨进程恢复仍需数据库等持久化。

---

## 3. "Not enough information to infer type variable T"

### 症状
`mutableStateOf()` 不带初值调用处编译报泛型推断错误。

### 原因
`mutableStateOf` 只有**一个泛型重载**（不存在基本类型特化重载），且 value 参数无默认值——不带初值时推断器拿不到 T 的信息。带初值调用（如 `mutableStateOf(0)`）类型可正常推断，不会报错。

### 修复
```kotlin
val a = remember { mutableStateOf<Int?>(null) }   // 显式类型参数 + 给初值
val b = remember { mutableIntStateOf(0) }         // 基本类型直接用专用 API（免装箱）
```

---

## 4. 协程泄漏 / 页面退出后任务仍在跑

### 症状
离开页面后 Toast 还在弹、数据库还在写、甚至 NPE 崩溃。

### 原因
1. 用 `GlobalScope` 启动业务协程（没有页面级自动取消关系）
2. 自己 `CoroutineScope(Dispatchers.Main)` 却从不 cancel
3. `catch` 吞掉了 `CancellationException`，破坏取消机制

### 修复
```kotlin
viewModelScope.launch { ... }                    // ✅ 随 ViewModel 取消

try { task() }
catch (e: CancellationException) { throw e }     // ⭐ 必须重新抛出
catch (e: Exception) { showError(e) }
```

### 检查清单
- [ ] 全局搜索 `GlobalScope` —— 业务代码应为 0 处
- [ ] 自建 Scope 必须有对应 cancel 时机
- [ ] `withTimeout`/`select` 场景同样注意 CancellationException 透传

---

## 5. Flow 被重复收集 / 事件重放

### 症状
旋转后 Snackbar 又弹了一次旧消息；或接口被意外调用了两次。

### 原因
- 冷流（`flow {}`/Room Flow）每个收集者独立执行一次 → 多处收集 = 多份执行
- `SharedFlow(replay > 0)` 在订阅重连时重放缓存事件

### 修复
```kotlin
// 共享数据源：冷流转 StateFlow（单一上游）
val data = repo.flow().stateIn(scope, WhileSubscribed(5_000), initial)

// 一次性事件：replay = 0 + 手动发射
private val _toast = MutableSharedFlow<String>(extraBufferCapacity = 1)
```

---

## 6. LazyColumn 滚动跳变 / 删除动画错乱

### 症状
删除某项后另一项闪烁；插入新项时列表跳回顶部。

### 原因
`items` 未提供 `key`，Compose 按位置匹配条目，数据顺序变化即错位。

### 修复
```kotlin
items(notes, key = { it.id }) { note -> NoteCard(note) }   // ⭐ 稳定唯一 key
```

### 陷阱
key 必须真正唯一且与条目绑定——用列表索引 `key = { index }` 等于没设。

---

## 7. 整屏都在重组（性能差）

### 症状
Layout Inspector / Recomposition Counts 显示一个输入每帧触发整页重组，滚动掉帧。

### 原因与修复

| 原因 | 修复 |
|------|------|
| 状态读取过早（页面级读取，全局传递） | 把读取下沉到需要的最小子组件；或传 lambda 延迟读取 |
| 高频源直接驱动低频 UI | `derivedStateOf` 收敛（如滚动位置 → 是否显示按钮） |
| 参数不稳定（`List`/lambda 每次新实例） | 参数用不可变 data class；结合编译器模式和捕获检查 lambda；rememberUpdatedState 用于长期任务读取最新值，不是通用跳过开关 |
| LazyColumn 的 item lambda 捕获易变状态 | item 内只依赖 item 数据，事件经稳定回调上抛 |

```kotlin
// ❌ 每帧读取 scrollOffset 并整页传递
val offset = listState.firstVisibleItemScrollOffset
HeavyPage(offset)

// ✅ 派生为低频布尔
val showTop by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
TopButton(visible = showTop)
```

---

## 8. LaunchedEffect 不执行 / 重复执行

### 症状
- 请求未执行 → 检查是否进入组合、协程是否立即取消/失败；false 也可作为合法 key，不是禁用开关
- 请求发了两次 → key 抖动

### 原因与修复
```kotlin
// key 是普通表达式，每次组合可能变化 → 抖动重启
LaunchedEffect(user.id) { load(user.id) }       // ✅ 用稳定的标识做 key
LaunchedEffect(true) { oneShotInit() }          // ✅ 仅进组合执行一次的惯例写法

// snapshotFlow 忘记收集 → 永不执行
LaunchedEffect(query) {
    snapshotFlow { query.text }.collect { suggest(it) }   // ⭐ 必须有终端操作
}
```

---

## 9. 返回键拦截不生效 / onBackPressed 报废弃

### 症状
想在当前 Composable 内拦截系统返回键，`onBackPressed` 已弃用。

### 修复
```kotlin
BackHandler(enabled = drawerOpen) {              // enabled=false 时不拦截
    drawerOpen = false
}
```

### 陷阱
`BackHandler` 必须在**组合中且 enabled** 才生效；多个 BackHandler 时最内层（最后组合）的胜出。

---

## 10. Preview 渲染失败

### 症状
预览面板报错或空白，模拟器却正常。

### 原因与修复
- Composable 依赖真机环境（`LocalContext` 取资源、数据库、网络）→ 把数据改为参数，预览传假数据
- 没包主题 → Preview 里手动 `AppTheme { }`
- 用了 `Build.VERSION.SDK_INT` 分支 → Preview 默认 SDK 可能落进未定义分支，提供参数控制

```kotlin
@Preview(showBackground = true)
@Composable
fun NoteCardPreview() {
    AppTheme { NoteCard(note = Note(1, "示例标题", "示例内容"), onDelete = {}) }  // 假数据
}
```

---

## 11. 构建期：KSP 与 Kotlin 版本不匹配

### 症状
Sync 失败："KSP version is not compatible with the Kotlin version"。

### 原因与修复
KSP 已改用**独立版本号**（如 `2.3.11`），不再使用 `kotlin版本-ksp版本` 拼接格式——KSP2 基于 Analysis API，与项目 Kotlin 版本解耦。出现不匹配报错时，把 KSP 插件升级到与当前 Kotlin 兼容的最新稳定版即可。

```toml
[versions]
kotlin = "2.4.20"
ksp = "2.3.11"            # 独立版本号，升级时仍须核对兼容性
```

### 关联问题
- KSP 配置全景（插件声明/ksp(...) 写法/处理器选库）→ [KSP 代码生成配置指南](../library-guides/03-ksp-configuration.md)
- JDK 不匹配（AGP 9.x 需 JDK 17+）→ `Settings → Gradle JDK` 选内置 JBR
- 依赖混版本冲突 → 所有 Compose 库统一走 BOM，不带独立版本号

---

## 快速对照表

| 症状关键词 | 首查词条 |
|-----------|----------|
| 卡死/刷屏重组 | #1 死循环 |
| 旋转后数据没了 | #2 状态丢失 |
| 无初值 mutableStateOf 推断报错 | #3 mutableStateOf |
| 页面退出还在跑 | #4 协程泄漏 |
| Toast 弹两次 | #5 事件重放 |
| 列表错位 | #6 LazyColumn key |
| 掉帧/全页重组 | #7 性能 |
| Effect 没跑/跑两次 | #8 LaunchedEffect |
| 拦截返回键 | #9 BackHandler |
| 预览空白 | #10 Preview |
| Sync 失败 | #11 构建问题 |

---

## 相关文档

- 📄 **[Kotlin + Compose 速查表](./01-kotlin-compose-cheatsheet.md)** - 正确写法的一行式对照
- 📄 **[Compose 状态 API 详解](../language-concepts/04-compose-state-api.md)** - remember/Saveable/derivedStateOf 原理
- 📄 **[协程与 Flow API 全表](../language-concepts/03-coroutines-flow-api.md)** - 取消与异常传播机制
- 📖 **[Compose 性能官方指南](https://developer.android.com/develop/ui/compose/performance)** - 性能问题权威排查


<!-- full-library-explanation -->
## 最小复现要保留触发条件

“旋转后丢失”先记录 Activity 是否重建、ViewModel 属于哪个 owner、数据是否只在内存；“请求两次”先记录收集者数量、Effect key 与进出组合次数。错误表列出候选原因，不证明每个同名症状都来自同一个根因。

练习：为一个请求加资源 ID 与任务编号日志，模拟快速切换 A/B 和后台恢复。验收：能从日志定位任务由谁启动、何时取消、哪个结果写入当前状态。避免记录 token 或用户正文；不要仅用时间戳猜两个请求是否同一次任务。

SideEffect 中无条件增加被 UI 读取的计数同样可能造成循环。把代码搬出组合体不是充分修复，必须解释这次状态变化为什么发生、由哪个输入触发，以及最终是否能稳定下来。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
