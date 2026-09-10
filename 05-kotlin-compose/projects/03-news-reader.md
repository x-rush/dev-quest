# 进阶项目 - 新闻阅读器（分页 + 缓存）

> **文档简介**: 用 Paging 3 + Room 构建无限滚动新闻阅读器，掌握 RemoteMediator 分页缓存架构与列表加载状态处理
>
> **目标读者**: 已完成天气应用、熟悉 Repository 模式的进阶学习者
>
> **前置知识**: [生态集成](../frameworks/03-ecosystem-integration.md)、[天气应用](02-weather-app.md)、[Flow API](../reference/language-concepts/03-coroutines-flow-api.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（projects） |
| **难度** | ⭐⭐ |
| **标签** | `#paging3` `#room` `#remote-mediator` `#offline-first` |
| **更新日期** | `2026年9月` |

---

## 🎯 项目目标

- ✅ LazyColumn 无限滚动，滚动到底自动加载下一页
- ✅ **RemoteMediator**：网络分页写入 Room，UI 只读 Room（离线可看已缓存内容）
- ✅ 追加失败重试 + 加载指示条
- ✅ 分页键（页码）随缓存事务化管理

## 1️⃣ 架构总览

```
LazyColumn ◀─ PagingData ◀─ Pager ──▶ RemoteMediator ─▶ 网络(Retrofit)
     ▲                                       │
     └── Room(articles 表，唯一事实来源) ◀───┘
```

与[生态集成](../frameworks/03-ecosystem-integration.md)的区别：数据不再由"一次 refresh"灌入，
而是 Pager 在滚动过程中按页驱动 RemoteMediator 拉取并写库。

## 2️⃣ 数据层：实体 + 远程键表

```kotlin
@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: Long,
    val title: String,
    val publishedAt: Long,
)

// RemoteMediator 需要一张"远程键"表记住"翻到第几页了"
@Entity(tableName = "remote_keys")
data class RemoteKeyEntity(
    @PrimaryKey val articleId: Long,
    val prevKey: Int?,
    val nextKey: Int?,
)

@Dao
interface ArticleDao {
    @Query("SELECT * FROM articles ORDER BY publishedAt DESC")
    fun pagingSource(): PagingSource<Int, ArticleEntity>   // Paging 与 Room 原生集成

    @Upsert suspend fun upsertAll(articles: List<ArticleEntity>)
    @Query("DELETE FROM articles") suspend fun clear()
}

@Dao
interface RemoteKeyDao {
    @Upsert suspend fun upsertAll(keys: List<RemoteKeyEntity>)
    suspend fun byArticleId(id: Long): RemoteKeyEntity?
    @Query("DELETE FROM remote_keys") suspend fun clear()
}
```

## 3️⃣ RemoteMediator：网络 ↔ 缓存的桥梁

```kotlin
@OptIn(ExperimentalPagingApi::class)
class NewsRemoteMediator(
    private val api: NewsApi,
    private val db: AppDatabase,
) : RemoteMediator<Int, ArticleEntity>() {

    override suspend fun initialize(): InitializeAction =
        InitializeAction.LAUNCH_INITIAL_REFRESH          // 启动时刷新一次

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, ArticleEntity>,
    ): MediatorResult {
        val page = when (loadType) {
            LoadType.REFRESH -> 1
            LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
            LoadType.APPEND -> {
                // 取列表最后一项的远程键确定下一页
                val last = state.pages.lastOrNull()?.data?.lastOrNull()
                    ?: return MediatorResult.Success(endOfPaginationReached = true)
                db.remoteKeyDao().byArticleId(last.id)?.nextKey
                    ?: return MediatorResult.Success(endOfPaginationReached = true)
            }
        }
        return try {
            val response = api.topHeadlines(page = page)
            db.withTransaction {
                // 远程键与文章必须同事务写入，否则会出现重复请求同一页
                if (loadType == LoadType.REFRESH) {
                    db.articleDao().clear(); db.remoteKeyDao().clear()
                }
                db.articleDao().upsertAll(response.articles.map { it.toEntity() })
                db.remoteKeyDao().upsertAll(response.articles.map {
                    RemoteKeyEntity(it.id, page - 1, if (response.hasMore) page + 1 else null)
                })
            }
            MediatorResult.Success(endOfPaginationReached = !response.hasMore)
        } catch (e: IOException) {
            MediatorResult.Error(e)      // 断网：UI 显示重试，缓存仍可浏览
        }
    }
}
```

## 4️⃣ ViewModel：暴露 PagingData 流

```kotlin
@HiltViewModel
class NewsViewModel @Inject constructor(db: AppDatabase, api: NewsApi) : ViewModel() {

    val articles: Flow<PagingData<Article>> = Pager(
        config = PagingConfig(pageSize = 20, prefetchDistance = 5, enablePlaceholders = false),
        remoteMediator = NewsRemoteMediator(api, db),
        pagingSourceFactory = { db.articleDao().pagingSource() },
    ).flow.map { paging -> paging.map { it.toDomain() } }
        .cachedIn(viewModelScope)          // 关键：配置变更期间复用同一份流
}
```

## 5️⃣ UI：collectAsLazyPagingItems 与加载状态

```kotlin
@Composable
fun NewsScreen(viewModel: NewsViewModel = hiltViewModel()) {
    val lazyItems = viewModel.articles.collectAsLazyPagingItems()

    LazyColumn(contentPadding = PaddingValues(16.dp)) {
        items(count = lazyItems.itemCount, key = lazyItems.itemKey { it.id }) { index ->
            lazyItems[index]?.let { ArticleRow(it) }
        }
        // 追加页加载中/失败指示器
        when {
            lazyItems.loadState.append is LoadState.Loading ->
                item { LinearProgressIndicator(Modifier.fillMaxWidth()) }
            lazyItems.loadState.append is LoadState.Error -> item {
                RetryRow(message = "加载失败", onRetry = lazyItems::retry)
            }
        }
    }
}
```

## ⚠️ 三个高频坑

| 现象 | 原因 | 对策 |
|------|------|------|
| 列表滚动回顶端 | 没有稳定的 `key` | `itemKey { it.id }` 必须唯一且稳定 |
| 重复请求同一页 | 远程键读写不在同一事务 | `db.withTransaction` 包住全部写操作 |
| 配置变更后重新加载 | 忘记 `cachedIn(viewModelScope)` | PagingData 流必须缓存 |

## 🔗 相关文档

- 📖 概念字典：[AndroidX 官方库指南](../reference/library-guides/01-androidx-libraries.md) ｜ [泛型与委托属性速查](../reference/language-concepts/05-generics-delegates.md)
- 📖 前置教程：[布局系统](../basics/05-layouts.md) ｜ [第一个项目](../basics/08-first-project.md)
- 🚀 精通挑战：[生产级 Android 应用](04-production-android-app.md) ｜ 深度原理：[重组优化](../advanced-topics/performance/01-recomposition-optimization.md)
