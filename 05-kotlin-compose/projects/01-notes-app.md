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
- ✅ **UiState 单一状态** + 状态提升的 Compose 界面
- ✅ 空态/加载态显式处理

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
    // 搜索在 SQL 层完成：数据量大时远快于内存过滤
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

```kotlin
data class NotesUiState(
    val query: String = "",
    val notes: List<Note> = emptyList(),
    val loading: Boolean = true,
)

class NotesViewModel(private val dao: NoteDao) : ViewModel() {

    private val queryFlow = MutableStateFlow("")

    // 搜索词防抖 300ms，再映射为数据库查询
    @OptIn(FlowPreview::class, ExperimentalCoroutinesApi::class)
    private val notesFlow = queryFlow
        .debounce(300)
        .flatMapLatest { q -> dao.observeNotes(q).map { list -> list.map { it.toDomain() } } }

    val uiState: StateFlow<NotesUiState> =
        combine(queryFlow, notesFlow) { q, notes ->
            NotesUiState(query = q, notes = notes, loading = false)
        }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), NotesUiState())

    fun onQueryChange(q: String) { queryFlow.value = q }

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

    fun deleteNote(id: Long) = viewModelScope.launch { dao.deleteById(id) }
}
```

> `debounce/flatMapLatest/combine` 的完整语义见 [协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)。

## 3️⃣ 列表界面：LazyColumn + 三种状态

```kotlin
@Composable
fun NotesScreen(
    state: NotesUiState,
    onQueryChange: (String) -> Unit,
    onNoteClick: (Long) -> Unit,
    onAddClick: () -> Unit,
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
            when {
                state.loading -> LinearProgressIndicator(Modifier.fillMaxWidth())
                state.notes.isEmpty() -> EmptyHint()          // 显式空态
                else -> LazyColumn(
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    // key 保证删除/搜索后动画与状态复用正确
                    items(state.notes, key = { it.id }) { note ->
                        NoteRow(
                            note = note,
                            onClick = { onNoteClick(note.id) },
                            onDelete = { /* 调用 VM 删除 */ },
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
    var title by rememberSaveable { mutableStateOf("") }
    var content by rememberSaveable { mutableStateOf("") }
    var loaded by rememberSaveable(noteId) { mutableStateOf(noteId == null) }
    var saving by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
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

1. 复制已验收的首项目作为本次练习，保留 Compose、Room/KSP 和数据库配置
2. 增加 DAO 的搜索与按 id 查询，检查编辑保存保留原 id 和创建时间
3. 实现 ViewModel：`stateIn` 收敛 UiState，接搜索防抖
4. 搭列表页（三态渲染）+ 编辑页，用 Navigation Compose 连接
5. 真机跑通增删改查 + 搜索，用 [Layout Inspector](../frameworks/04-devtools.md) 检查列表重组

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
