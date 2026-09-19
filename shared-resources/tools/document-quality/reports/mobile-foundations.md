# 移动端基础与首项目复核

本报告覆盖本次改写的 4 篇正文，完整运行记录、源文件哈希、抽取代码与断言保存在 [mobile-foundations.json](./mobile-foundations.json)。它不代表三个移动平台已经完成设备构建。

| 正文 | 已修复内容 | 本地验证范围 |
|---|---|---|
| [RN 首项目](../../../../04-multiplatform-apps/basics/08-first-project.md) | 金额整段校验、JSON 结构验证、读取前禁写、串行写入、失败保留输入、本地月份统计 | 直接抽取正文的金额和结构校验函数，Node 24 执行边界断言通过；Hook 与原生存储未运行 |
| [RN 平台 API 地图](../../../../04-multiplatform-apps/reference/language-concepts/13-platform-api-map.md) | 语言内置/宿主/原生能力分层，社区模块归属，更新调度与 OTA 边界 | 人工依据官方环境文档复核；平台能力需以工程版本和设备实测 |
| [Kotlin 作用域函数](../../../../05-kotlin-compose/reference/language-concepts/07-scope-functions.md) | 无接收者 run、takeUnless 的反向条件、null 与对象身份、提前求值 | 直接抽取两个完整程序，以 Kotlin/JVM 编译运行通过；不使用 Android SDK |
| [Swift 首项目](../../../../06-swift-swiftui/basics/08-first-project.md) | 分组删除正确绑定对象、补齐 App/统计界面、整数分、显式 save 与失败 rollback | 直接抽取纯金额函数，以 Swift 6.3.3 Linux 运行断言通过；SwiftUI/SwiftData 未构建 |

## 复现

在仓库根运行 `python shared-resources/tools/document-quality/verify_mobile_foundations.py`。需要 Docker 及本地镜像 `dev-quest-validation:local`（提供 Kotlin/JDK）、`node:24-bookworm-slim`、`swift:6.3.3-noble`。Kotlin 镜像是本次验证环境已有的本地镜像，仓库没有分发其构建定义；其他机器可把 `DEV_QUEST_KOTLIN_IMAGE` 设为自身提供 `kotlinc` 与 `java` 的镜像。报告记录了实际工具链输出，也可以复制正文完整 Kotlin 程序，用同版本命令直接复现。缺少工具链时验证会失败，不会跳过后标为通过。

容器使用无网络、只读根文件系统、临时工作目录和资源限制。抽取函数保持正文不变，断言 harness 单独记录。当前结果为 4 个验证单元全部通过。

## 未覆盖的验收

- RN Hook 的挂载、延迟读取、卸载、并发点击及原生 AsyncStorage 错误需要组件或设备测试。替身存储的具体失败场景已写入教程，尚无通过记录。
- SwiftUI/SwiftData 需 macOS/Xcode，金额函数在 Linux 的通过不证明界面类型检查、模型宏展开、存储提交或回滚成功。
- Android、iOS、HarmonyOS 需要分别记录工程依赖、目标系统、构建与运行结果。云端构建成功也不能代替权限、手势、布局或重启持久化的设备验收。
