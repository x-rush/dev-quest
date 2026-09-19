# 入门项目 - 本地笔记应用

## 分阶段练习与验收

**进入条件**：已在自己的 Android 工程完成[最小笔记应用](../basics/08-first-project.md)，通过构建及新增 A/B、删除 B、重启读回 A 的设备验收。沿用该工程的 Gradle/KSP 配置、`NotesDatabase`、领域模型 `Note`、`toDomain()` 与 `validateNote`，下面是编辑和搜索的增量练习，不是可直接替换整个工程的独立文件。

**最小产物**：在原工程增加按 id 查询、保留 id 的编辑保存、搜索输入及导航装配，并保留源码、Room schema 与设备验收记录。本文继续使用首项目的 `createdAt` 字段，不为搜索改名或重建表；将来增加更新时间时另做 schema 迁移。新界面替换旧界面时同步修改 Activity 的参数装配，`EmptyHint` 和 `NoteRow` 是需要自行实现的展示组件。

**验收动作**：新增 A/B，编辑 A 为 A2，记录数仍为 2；取消修改后内容不变；搜索 A2 只显示 A2，清空搜索恢复两项；删除 B 后重启，只有 A2。用失败 DAO 替身让保存抛错，表单保留且不能导航返回；空白标题被拒绝。分别记录构建、设备交互和失败路径结果，尚未执行的项目写“未验证”。

**失败回查**：编辑后多出一条记录先查 `noteId` 是否一路传入 `upsert`；编译时找不到领域类型返回首项目 Repository 段补齐；找不到 DAO 实现或 schema 不匹配查[KSP 配置](../reference/library-guides/03-ksp-configuration.md)与[故障排除](../reference/quick-references/02-troubleshooting.md)，不要清库来掩盖已有数据的升级问题。

**下一步**：编辑与搜索验收通过后再进入[天气应用](./02-weather-app.md)接入网络与依赖注入；首项目已有的加载、读取错误和删除错误处理在接线时仍需保留。

> **文档简介**: 用 Compose + Room + ViewModel 从零构建一个支持增删改查与搜索的本地笔记应用，覆盖现代 Android 应用最小的完整闭环
>
> **目标读者**: 完成 basics 全部教程、首次做完整项目的初学者
>
> **前置知识**: [第一个项目](../basics/08-first-project.md)（最小版笔记应用）、[生态集成](../frameworks/03-ecosystem-integration.md) 建议先读

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（projects） |
| **难度** | ⭐ |
| **标签** | `#room` `#viewmodel` `#crud` `#lazy-column` |
| **更新日期** | `2026年9月` |

</details>

---

## 🎯 项目目标

与 [basics 的最小笔记应用](../basics/08-first-project.md) 相比，本项目补齐"真实应用"要素：

- ✅ 笔记列表 + 新建/编辑 + 删除，数据落 **Room**
- ✅ 标题搜索（数据库层过滤，而非内存过滤）
- ✅ 查询结果集中在 **UiState**，删除错误独立展示；Compose 界面接收状态与事件
- ✅ 空态、加载态与可重试错误显式处理

不涉及网络与 DI——那是 [天气应用](02-weather-app.md) 的任务。

## 1️⃣ 数据模型与 DAO

```kotlin
@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val title: String,
    val content: String,
    val createdAt: Long = System.currentTimeMillis(),
)

@Dao
interface NoteDao {
    // 数据库执行过滤，减少传回 UI 的记录；包含搜索不保证使用普通索引。
    @Query("SELECT * FROM notes WHERE title LIKE '%' || :query || '%' ORDER BY createdAt DESC, id DESC")
    fun observeNotes(query: String): Flow<List<NoteEntity>>

    @Query("SELECT * FROM notes WHERE id = :id LIMIT 1")
    suspend fun getNote(id: Long): NoteEntity?

    @Upsert suspend fun upsert(note: NoteEntity)

    @Query("DELETE FROM notes WHERE id = :id")
    suspend fun deleteById(id: Long)
}
```

## 2️⃣ ViewModel：查询词也是状态

搜索输入应立即回显，结果则在防抖和查询结束后更新；等待期间不能把旧结果当成新查询的结果。以下增量还需要 `kotlinx.coroutines.delay`、`kotlinx.coroutines.CancellationException`、`kotlinx.coroutines.flow.*`、`kotlinx.coroutines.launch`。DAO 查询错误在每次查询内部捕获，避免一次失败就终止整个搜索流。

```kotlin
data class NotesUiState(
    val query: String = "",
    val notes: List<Note> = emptyList(),
    val loading: Boolean = true,
    val error: String? = null,
)

class NotesViewModel(private val dao: NoteDao) : ViewModel() {

    private val queryFlow = MutableStateFlow("")
    private val reload = MutableStateFlow(0)
    val deleteError = MutableStateFlow<String?>(null)

    // 输入改变即取消旧收集；新查询等待 300ms，快速输入只执行最后一次。
    @OptIn(ExperimentalCoroutinesApi::class)
    private val notesFlow = combine(queryFlow, reload) { q, _ -> q }
        .flatMapLatest { q ->
            flow {
                emit(NotesUiState(query = q))
                delay(300)
                emitAll(dao.observeNotes(q).map { list ->
                    NotesUiState(query = q, notes = list.map { it.toDomain() }, loading = false)
                })
            }.catch { failure ->
                if (failure is CancellationException) throw failure
                emit(NotesUiState(query = q, loading = false, error = "读取失败，请重试。"))
            }
        }

    val uiState: StateFlow<NotesUiState> =
        combine(queryFlow, notesFlow) { q, result ->
            if (q == result.query) result else NotesUiState(query = q)
        }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), NotesUiState())

    fun onQueryChange(q: String) { queryFlow.value = q }
    fun retry() { reload.value += 1 }

    suspend fun getNote(id: Long): NoteEntity? = dao.getNote(id)

    // 调用方等待成功后才离开编辑页；异常交给表单展示。
    suspend fun saveNote(noteId: Long?, title: String, content: String) {
        val draft = validateNote(title, content)
        val existing = noteId?.let { id ->
            requireNotNull(dao.getNote(id)) { "笔记已不存在，请返回列表刷新" }
        }
        dao.upsert(existing?.copy(title = draft.title, content = draft.content)
            ?: NoteEntity(title = draft.title, content = draft.content))
    }

    fun deleteNote(id: Long) = viewModelScope.launch {
        deleteError.value = null
        try {
            dao.deleteById(id)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: Exception) {
            deleteError.value = "删除失败，笔记仍保留，请重试。"
        }
    }
}
```

> `flatMapLatest/combine` 的完整语义见 [协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)。本例搜索词保留在 ViewModel，能跨 Activity 配置重建；尚未接入 SavedStateHandle，进程重建时搜索词回到空串，持久笔记仍由 Room 读取。

本例 SQL 的 `%` 和 `_` 仍是 LIKE 通配符，输入 `%` 会匹配所有标题；它不是字面量子串搜索。需要按字面搜索时另加转义规则和用例。前导 `%` 不满足 SQLite 的 LIKE 范围索引优化条件，不能凭“过滤在数据库”宣称大数据性能更好；先测查询计划，再考虑全文检索。依据：[SQLite LIKE 优化](https://www.sqlite.org/optoverview.html#the_like_optimization)。

## 3️⃣ 列表界面：LazyColumn + 加载、错误、空态与结果

```kotlin
@Composable
fun NotesScreen(
    state: NotesUiState,
    onQueryChange: (String) -> Unit,
    onNoteClick: (Long) -> Unit,
    onAddClick: () -> Unit,
    onDelete: (Long) -> Unit,
    onRetry: () -> Unit,
    deleteError: String?,
) {
    Scaffold(floatingActionButton = {
        FloatingActionButton(onClick = onAddClick) { Icon(Icons.Default.Add, "新建笔记") }
    }) { padding ->
        Column(Modifier.padding(padding)) {
            OutlinedTextField(
                value = state.query,
                onValueChange = onQueryChange,
                placeholder = { Text("搜索标题") },
                modifier = Modifier.fillMaxWidth().padding(16.dp),
            )
            deleteError?.let { Text(it) }
            when {
                state.loading -> LinearProgressIndicator(Modifier.fillMaxWidth())
                state.error != null -> Column {
                    Text(state.error)
                    Button(onClick = onRetry) { Text("重试") }
                }
                state.notes.isEmpty() -> EmptyHint()          // 显式空态
                else -> LazyColumn(
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    // 稳定 id 帮助 Compose 对应条目身份；仍需验证状态和动画。
                    items(state.notes, key = { it.id }) { note ->
                        NoteRow(
                            note = note,
                            onClick = { onNoteClick(note.id) },
                            onDelete = { onDelete(note.id) },
                        )
                    }
                }
            }
        }
    }
}
```

## 4️⃣ 编辑界面：表单状态留在 Composable 层

本段除首项目已有 import 外，需要 `androidx.compose.runtime.saveable.rememberSaveable`、`kotlinx.coroutines.CancellationException` 和 `kotlinx.coroutines.launch`。表单协程属于当前组合，离开页面或 Activity 重建会取消它；数据库提交与取消可能相邻发生，返回列表后以 Room 查询结果为准。本阶段只验收空闲草稿旋转恢复；若要求保存中旋转仍持续提交，应把保存任务和忙碌状态提升到 ViewModel，沿用首项目的写入协调方式。

```kotlin
@Composable
fun NoteEditorScreen(noteId: Long?, viewModel: NotesViewModel, onDone: () -> Unit) {
    // 只有"草稿"属于 UI；持久化才进 ViewModel/Room
    var title by rememberSaveable(noteId) { mutableStateOf("") }
    var content by rememberSaveable(noteId) { mutableStateOf("") }
    var loaded by rememberSaveable(noteId) { mutableStateOf(noteId == null) }
    var saving by remember(noteId) { mutableStateOf(false) }
    var error by remember(noteId) { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    // 编辑模式：进入时回填既有笔记（新建 noteId == null 跳过）
    LaunchedEffect(noteId) {
        if (!loaded && noteId != null) {
            try {
                val note = requireNotNull(viewModel.getNote(noteId)) { "笔记已不存在" }
                title = note.title
                content = note.content
                loaded = true
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (failure: Exception) {
                error = "读取失败，请返回列表后重试。"
            }
        }
    }

    Column(Modifier.padding(16.dp)) {
        OutlinedTextField(value = title, onValueChange = { title = it }, enabled = loaded && !saving, label = { Text("标题") })
        OutlinedTextField(value = content, onValueChange = { content = it }, enabled = loaded && !saving, minLines = 5)
        error?.let { Text(it) }
        Button(enabled = loaded && !saving && title.isNotBlank(), onClick = {
            if (!saving) {
                saving = true
                scope.launch {
                    try {
                        viewModel.saveNote(noteId, title, content)
                        onDone()
                    } catch (cancelled: CancellationException) {
                        throw cancelled
                    } catch (failure: Exception) {
                        error = failure.message ?: "保存失败，请重试。"
                    } finally {
                        saving = false
                    }
                }
            }
        }) { Text("保存") }
    }
}
```

- 草稿与已回填标记使用 `rememberSaveable`，在系统恢复保存状态时一起恢复，避免旋转后被数据库旧值覆盖；强制停止或全新启动不承诺恢复未保存草稿。
- **编辑模式必须回填**：`LaunchedEffect(noteId)` 在进入编辑页时触发一次性加载（ViewModel 暴露 `suspend fun getNote(id: Long): NoteEntity?`，转发给 DAO 的单次查询），否则编辑页永远是空表单；`noteId` 是 key，切换笔记自动重新加载；
- 保存把 `noteId` 一并传给 `saveNote(noteId, title, content)`——ViewModel 内部有 id 走 `upsert`（更新），没有则插入，单向数据流原理见[应用架构](../advanced-topics/architecture/01-app-architecture.md)。

## 5️⃣ 实施步骤

1. 复制已验收的首项目，保留 Compose、Room/KSP 和数据库配置；在工程根运行 Windows 的 `.\gradlew.bat :app:assembleDebug` 或 macOS/Linux 的 `./gradlew :app:assembleDebug`，先保存基线构建结果。
2. 增加 DAO 的搜索与按 id 查询。给 A 记录 id 和创建时间，改成 A2 后两项都应保持原值，数据库仍只有 A2/B 两条记录。
3. 接入 ViewModel 与列表：路由层用 `collectAsStateWithLifecycle()` 收集 `uiState`、`deleteError`，分别传入 `NotesScreen`；回调绑定 `viewModel::onQueryChange`、`viewModel::deleteNote` 和 `viewModel::retry`。保留首项目的 ViewModel Factory，不能直接在 Composable 重建 ViewModel。
4. 实现 `NoteRow(note, onClick, onDelete)` 和 `EmptyHint()` 两个展示函数，再接导航：新建传 `null`，编辑传所点击的 id，保存成功的 `onDone` 才返回列表。系统返回键作为取消，不调用保存。先补齐这些接线，再判断工程能否编译。
5. 完成下表行为记录；构建失败先检查 import、Factory、导航参数与新增回调，行为失败再定位状态或数据库。本文代码是增量片段，本轮未在 Android 工具链或设备执行，不能把阅读完成记为工程验证。

| 操作 | 成功条件 | 失败时优先检查 |
|---|---|---|
| 连续输入 A、B，等待超过 300ms | 输入立即回显；等待时显示加载，最终只显示 B 的结果 | 结果是否携带对应查询词；是否还在混用新输入与旧列表 |
| 搜索无结果、清空输入 | 分别出现空态、恢复全部笔记 | 空列表是否被误判为加载中 |
| DAO 查询第一次抛错，然后点重试 | 显示错误；同一查询可再次成功 | catch 是否在每个查询内部；重试是否触发新收集 |
| DAO 删除抛错 | 不崩溃，记录保留，可见错误；再次成功后才消失 | 回调是否接入、异常是否被捕获 |
| 编辑 A 后返回取消，再打开 A | 数据库内容未变；成功保存才更新原记录 | 草稿是否误写模型、是否丢失 id |
| 旋转空闲编辑页、终止并重启应用 | 前者恢复草稿；后者恢复已保存笔记，未保存草稿不作承诺 | 区分保存状态恢复与 Room 持久化 |

## 🎨 验收清单

- [ ] 旋转屏幕后列表与草稿不丢失
- [ ] 删除列表项不出现错位（key 生效）
- [ ] 搜索无结果时显示空态而非白屏
- [ ] 能为 NotesViewModel 写出一个[单元测试](../testing/01-unit-testing.md)

## 🔗 相关文档

- 📖 概念字典：[Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md) ｜ [可空性与集合 API 速查](../reference/language-concepts/02-null-safety-collections.md)
- 📖 前置教程：[第一个项目 - Compose + Room 笔记应用](../basics/08-first-project.md) ｜ [布局系统](../basics/05-layouts.md)
- 🚀 进阶项目：[天气应用：网络 + 定位](02-weather-app.md) ｜ [新闻阅读器：分页 + 缓存](03-news-reader.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
