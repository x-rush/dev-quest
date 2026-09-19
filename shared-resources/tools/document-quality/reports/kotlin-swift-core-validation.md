# Kotlin / Swift 核心语义与首项目复核

本轮直接运行三个正文程序，3 / 3 通过。原始代码、源文档哈希、工具链输出、命令和断言结果见 [kotlin-swift-core.json](./kotlin-swift-core.json)。这是限定案例的运行证据，不是 Android 或 iOS 工程通过记录。

| 文档 | 修正与增强 | 实际执行范围 |
|---|---|---|
| [Kotlin 语法基础](../../../../05-kotlin-compose/basics/03-kotlin-syntax-essentials.md) | val 与可变对象、浅拷贝、equals 属性范围、Compose 重组误解、扩展静态解析、截断输出错误、作用域函数区别 | 原文完整程序：共享列表与独立列表、空白输入、回调只在调用时执行 |
| [Compose + Room 首项目](../../../../05-kotlin-compose/basics/08-first-project.md) | Room 库显式版本、相同时间戳排序、领域校验、ViewModel 工厂和 Activity 入口、区分加载/空/失败、保存成功才关闭、防重复提交、取消传播 | 原文 NoteDraft/validateNote 声明与原文 main：空标题、标题与正文边界、裁剪标题但保留正文 |
| [Swift 语法基础](../../../../06-swift-swiftui/basics/03-swift-syntax-essentials.md) | Optional 与崩溃边界、struct 非自动并发安全、actor 重入、Codable 恢复 id、避免把无效年龄伪装成 0 | 原文完整程序：JSON 编解码保留 UUID、值拷贝与引用共享、年龄缺失/非法/越界 |

## 复现

在仓库根执行：

```sh
python shared-resources/tools/document-quality/verify_kotlin_swift_core.py
```

需要 Docker。实际使用 Kotlin/JVM 2.4.20、JDK 21.0.12（本机已有 `dev-quest-validation:local` 镜像）和 `swift:6.3.3-noble`。本仓库未分发前者镜像构建定义，其他机器可以把 `DEV_QUEST_KOTLIN_IMAGE` 设置为提供 `kotlinc`/`java` 的镜像，或将正文完整程序保存后按文中的命令直接运行。验证器不安装依赖、不添加缺失 import 或模拟 Android API，缺少工具链会失败而不会计为通过。

每个程序在无网络、只读根文件系统、只读源码挂载的独立容器执行；仅临时目录可写。验证器要求退出码为 0 且标准输出精确匹配。Kotlin 项目案例只拼接正文已有的领域声明与正文已有 main，未替换领域实现。

## 设备边界

本机未找到 Android SDK；本轮没有执行 Gradle、KSP、Room 数据库、Lifecycle 或 Compose UI 构建。iOS 需要 macOS/Xcode，本轮没有执行 SwiftUI、SwiftData 或设备交互。Kotlin 首项目已补完整的接线步骤和设备验收表，但这些仍应在目标工具链记录构建与设备结果；三段纯语言程序通过不能证明原生工程通过。

本轮官方资料复核入口为 [Kotlin data class](https://kotlinlang.org/docs/data-classes.html)、[扩展解析](https://kotlinlang.org/docs/extensions.html)、[Compose strong skipping](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping)、[Room 发行说明](https://developer.android.com/jetpack/androidx/releases/room)、[Room 异步查询](https://developer.android.com/training/data-storage/room/async-queries) 与 [Swift 语言书](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/)。版本页面会变化，JSON 记录的是本次实际使用的运行时。
