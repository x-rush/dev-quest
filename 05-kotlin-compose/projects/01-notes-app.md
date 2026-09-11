# 入门项目 - 本地笔记应用

> **文档简介**: 用 Compose + Room + ViewModel 从零构建一个支持增删改查与搜索的本地笔记应用，覆盖现代 Android 应用最小的完整闭环
>
> **目标读者**: 完成 basics 全部教程、首次做完整项目的初学者
>
> **前置知识**: [第一个项目](../basics/08-first-project.md)（最小版笔记应用）、[生态集成](../frameworks/03-ecosystem-integration.md) 建议先读

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（projects） |
| **难度** | ⭐ |
| **标签** | `#room` `#viewmodel` `#crud` `#lazy-column` |
| **更新日期** | `2026年9月` |

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
    val updatedAt: Long = System.currentTimeMillis(),
)

@Dao
interface NoteDao {
    // 搜索在 SQL 层完成：数据量大时远快于内存过滤
    @Query("SELECT * FROM notes WHERE title LIKE '%' || :query || '%' ORDER BY updatedAt DESC")
    fun observeNotes(query: String): Flow<List<NoteEntity>>

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
    @OptIn(FlowPreview::class)
    private val notesFlow = queryFlow
        .debounce(300)
        .flatMapLatest { q -> dao.observeNotes(q).map { list -> list.map { it.toDomain() } } }

    val uiState: StateFlow<NotesUiState> =
        combine(queryFlow, notesFlow) { q, notes ->
            NotesUiState(query = q, notes = notes, loading = false)
        }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), NotesUiState())

    fun onQueryChange(q: String) { queryFlow.value = q }

    fun saveNote(title: String, content: String) = viewModelScope.launch {
        dao.upsert(NoteEntity(title = title, content = content))
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

```kotlin
@Composable
fun NoteEditorScreen(noteId: Long?, viewModel: NotesViewModel, onDone: () -> Unit) {
    // 只有"草稿"属于 UI；持久化才进 ViewModel/Room
    var title by rememberSaveable { mutableStateOf("") }
    var content by rememberSaveable { mutableStateOf("") }

    // 编辑模式：进入时回填既有笔记（新建 noteId == null 跳过）
    LaunchedEffect(noteId) {
        noteId?.let { id ->
            viewModel.getNote(id)?.let { note ->
                title = note.title
                content = note.content
            }
        }
    }

    Column(Modifier.padding(16.dp)) {
        OutlinedTextField(value = title, onValueChange = { title = it }, label = { Text("标题") })
        OutlinedTextField(value = content, onValueChange = { content = it }, minLines = 5)
        Button(onClick = {
            viewModel.saveNote(noteId, title, content)
            onDone()
        }) { Text("保存") }
    }
}
```

- 草稿用 `rememberSaveable`，旋转屏幕/进程恢复不丢失；
- **编辑模式必须回填**：`LaunchedEffect(noteId)` 在进入编辑页时触发一次性加载（ViewModel 暴露 `suspend fun getNote(id: Long): NoteEntity?`，转发给 DAO 的单次查询），否则编辑页永远是空表单；`noteId` 是 key，切换笔记自动重新加载；
- 保存把 `noteId` 一并传给 `saveNote(noteId, title, content)`——ViewModel 内部有 id 走 `upsert`（更新），没有则插入，单向数据流原理见[应用架构](../advanced-topics/architecture/01-app-architecture.md)。

- 草稿用 `rememberSaveable`，旋转屏幕/进程恢复不丢失；
- 保存动作只调用 ViewModel 事件——单向数据流，原理见[应用架构](../advanced-topics/architecture/01-app-architecture.md)。

## 5️⃣ 实施步骤

1. 新建项目（Compose 模板），接入 Room（KSP 编译器）
2. 实现数据层：Entity → DAO → Database，写一个 DAO 冒烟测试
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
