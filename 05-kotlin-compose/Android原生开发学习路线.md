# Android 学习路线：从 Kotlin 到可维护的应用

> **阅读准备**：会基本编程即可进入路线；Kotlin 语法、Android 生命周期与 Compose 分阶段学习，不要求提前熟悉整个技术栈。

这条路线面向会基本编程、尚不熟悉 Android 的学习者。按能力验收推进，不要求同时掌握所有库。日常查阅从 [模块理解地图](LEARNING_GUIDE.md)进入；该地图列出了完整文章入口。

## 第一阶段：能解释一段 Kotlin 程序

先读 [语法基础](basics/03-kotlin-syntax-essentials.md)，遇到关键词查 [语言参考](reference/language-concepts/01-kotlin-keywords.md)。重点不是记住缩写，而是能解释 val/var、可空类型、when、data class、lambda 和集合操作的输入输出。

练习：实现命令行待办清单，支持添加、完成、按状态筛选。输入空标题、重复 ID、空集合都要有规定行为。验收：不依赖 !! 掩盖缺失数据；能说明 List 为什么不等于深度不可变、map 与 forEach 返回值如何不同。

进阶再学泛型、委托、扩展与 Sequence。先正确处理有限数据，再研究减少中间集合和短路执行。协程另学作用域、取消与挂起；suspend 不代表自动后台线程。

## 第二阶段：让状态驱动可操作的页面

从 [环境搭建](basics/01-environment-setup.md)使用兼容模板创建工程，再学 [Composable 与状态](basics/04-composables-state.md)、[布局](basics/05-layouts.md)。使用项目版本目录锁定 Kotlin、AGP、Gradle、Compose 组合，不把各依赖分别升到最大版本。

练习：把清单做成 Compose 页面，加入输入框、删除确认、空状态和稳定列表 key。验收：新增与删除后状态跟随记录；旋转和大字体下可用；屏幕阅读器能辨识按钮。查属性使用 [组件参考](reference/framework-essentials/01-compose-essentials.md)，不要一次背完整 API。

## 第三阶段：跨页面、跨重建、跨进程保存

学习 [导航](basics/06-navigation.md)、ViewModel、Room 与 DataStore。用事件向上、状态向下的数据流组织代码，Repository 负责数据来源和同步规则；UseCase 只在规则复用或编排复杂时引入。

练习：[笔记项目](basics/08-first-project.md)增加搜索与排序，数据库新增 pinned 字段并迁移旧数据。验收：旋转不丢 UI 状态，进程重启后笔记仍在，从旧数据库升级不丢记录。能区分 remember、保存状态、ViewModel 内存与磁盘数据的寿命。

## 第四阶段：网络和离线行为

学习 Retrofit/OkHttp 或适合跨平台需求的 Ktor，先选一套完成链路。序列化负责转换，不替代业务校验。用 [AndroidX](reference/library-guides/01-androidx-libraries.md) 与 [生态库](reference/library-guides/02-third-party-libs.md)参考补齐依赖职责。

练习：做新闻阅读器，先展示本地内容再同步远端，区分首次加载、空结果、刷新失败。验收：断网不清空可用数据，快速切换查询时旧结果不覆盖新页面，重试写操作不会重复创建记录。后台持久同步再考虑 WorkManager，它不承诺精确时刻运行。

## 第五阶段：带证据地测试与优化

先测纯 Kotlin 规则，再测 Repository 与数据库迁移，最后测关键 UI 行为。使用 [测试参考](reference/framework-essentials/07-compose-testing.md)编写“输入—操作—可见结果”断言。性能只针对已记录的慢交互优化，重组本身不是错误。

练习：让一个接口返回 500、一个保存动作失败、一个页面快速进出。验收：测试会在引入对应缺陷后失败，取消任务不留下错误提示，release 构建的滚动与启动有可复现记录。

## 第六阶段：交付与长期维护

读 [发布构建](deployment/01-release-build.md)，用测试签名制作 release，验证升级、混淆和错误还原。商店发布另按实际平台的当前要求检查；学习项目不必为了完成路线接入支付或真实个人数据。

进阶方向按需求选择：CameraX、Media3、复杂手势与 Canvas、大屏适配、Kotlin Multiplatform。新框架先验证维护状态、平台支持、迁移成本和它解决的真实问题；任何框架都可能变化，更长久的能力是状态建模、并发、数据一致性、测试和诊断。

官方补充材料：[Android Basics with Compose](https://developer.android.com/courses/android-basics-compose/course)、[Kotlin 文档](https://kotlinlang.org/docs/home.html)。读教程后用上述项目验收，不以“看完章节”替代会独立完成任务。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](LEARNING_GUIDE.md) · [完整目录与版本](README.md) · [通用术语](../shared-resources/glossary.md)
