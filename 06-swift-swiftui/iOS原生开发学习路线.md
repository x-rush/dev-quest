# iOS 原生开发学习路线：从语言基础到可交付应用

> **阅读准备**：会基本编程；语言基础阶段不要求 Apple 开发经验，界面与真机实践需要匹配的 macOS/Xcode 环境。

适合已经会基本编程、尚不熟悉 Apple 技术栈的读者。以能完成的任务安排进度，不以学过多少框架或固定几周“精通”作为目标。你需要能运行目标 Xcode 的 Mac；本库在 Windows 的文档验证不能代替模拟器、真机与签名验证。

## 起步：建立工具与反馈回路

先完成 [环境准备](basics/01-environment-setup.md) 与 [第一个 SwiftUI 应用](basics/02-first-swiftui-app.md)。记录 Xcode、Swift 语言模式与最低部署目标，创建工程、编译、设置断点、查看控制台，并用 Git 保存首次可运行版本。

验收：从干净检出能按 README 重建工程；修改一个 Text 后模拟器可看到变化；遇到编译错误知道先读第一条诊断。不要先引入网络库、架构库和自动化平台。

## 阶段一：能读懂与预测 Swift

按 [模块理解地图](LEARNING_GUIDE.md) 阅读语言基础，再以 reference 补齐查阅能力：

| 主题 | 需要解释的行为 | 小练习 |
|---|---|---|
| let/var、值与引用 | 赋值后两份变量是否共享修改 | 对照 struct 与 class |
| Optional、guard、错误 | 无值与失败原因如何表达 | 解析用户输入，区分空、非法、有效 |
| 集合与闭包 | map/filter/compactMap/reduce 的输入输出 | 聚合一周阅读记录 |
| 协议与泛型 | 约束、静态类型与存在类型 | 为存储定义可替换接口 |
| Foundation | 文本索引、JSON、日历与文件边界 | 解码并格式化本地 JSON |

查词入口：[关键字](reference/language-concepts/13-keywords-completion.md)、[集合与可选值](reference/language-concepts/02-optionals-collections.md)、[标准库与 Foundation](reference/library-guides/01-foundation-and-stdlib.md)。验收是能写输入、预测输出、说明错误行为，不只是编译成功。

## 阶段二：用状态构建界面

学习 View、State、Binding、Observation、布局、稳定身份、NavigationStack 与 Environment。制作内存版阅读清单：添加、编辑、完成、筛选与详情页。说明每份状态由谁持有、多久存活，正文不要塞入 body 的副作用中。

验收：插入或排序后行状态不串位；编辑取消不会保存草稿；空列表有提示；大字体、深色模式和 VoiceOver 可操作。参考 [状态工具](reference/language-concepts/04-swiftui-state-api.md) 与 [数据流](reference/framework-essentials/05-data-flow.md)。

## 阶段三：把数据接入真实边界

先用 URLSession/Codable 理解 HTTP 状态、解码错误和取消，再用 SwiftData 或适合产品的存储方案保存数据。完成 [天气项目](projects/02-weather-app.md) 或 [笔记项目](projects/01-notes-app.md)，一次选择一个。

验收：断网、404、错误 JSON、快速切换查询均有明确行为；旧响应不覆盖新查询；数据重启后还在；存储失败能反馈。随后增加 schema 版本并用旧测试库验证迁移，禁止靠删库“通过”升级测试。

## 阶段四：高级特性按实际问题扩展

| 问题 | 进阶内容 | 产出 |
|---|---|---|
| 请求重复或竞态 | actor、任务组、有界并发、取消 | 可控制返回顺序的测试 |
| 多服务编排 | 状态机、依赖注入，必要时评估 MVVM/TCA | 可替换网络的功能测试 |
| 滚动卡顿 | SwiftUI Instruments、图片尺寸、派生数据计算 | 同设备修改前后 trace |
| 系统集成 | 通知、定位、WidgetKit/App Intents | 拒绝权限时仍可用的替代路径 |
| 数据可视化 | Charts、日期聚合与统计口径 | 图表加文本/无障碍说明 |

UIKit 仍是系统集成与既有项目的重要能力，不仅是“维护旧代码”。先学 UIViewRepresentable/UIViewControllerRepresentable 的生命周期和状态桥接，再按需求深入。

## 阶段五：项目练习与交付

阅读清单 → 持久化笔记 → 天气查询 → [习惯追踪](projects/03-habit-tracker.md) → [生产化项目](projects/04-production-ios-app.md)。每个项目先做最小闭环，再加入一个进阶目标，避免同一轮同时更换架构、数据库与网络库。

最终交付包含可复现构建说明、核心流程测试、迁移测试、取消与错误行为、敏感数据处理、权限说明与性能证据。TestFlight/商店分发还需有效账号、签名和当时的提交要求，按 deployment 章节及 Apple 官方文档核对。

## 框架选择与长期维护

SwiftUI、Foundation、Swift Concurrency、SwiftData 与 UIKit 构成系统能力主线。第三方库只在明确缺口出现时引入，参见 [选型与边界](reference/library-guides/02-third-party-libs.md)。更新框架前阅读迁移说明、固定测试条件并保留回退点。没有框架能保证永不过时；状态所有权、类型、并发、数据一致性和验证方法更容易迁移到下一代工具。

完整阅读顺序与文章索引见 [LEARNING_GUIDE](LEARNING_GUIDE.md)，工具版本入口见 [README](README.md)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](LEARNING_GUIDE.md) · [完整目录与版本](README.md) · [通用术语](../shared-resources/glossary.md)
