# 跨模块正文审查与改写记录

本轮针对用户指出的“术语解释术语”问题，处理简短建议清单、缺少适用条件的结论，以及与正文矛盾的示例。每个模块都包含实际正文修改。

结构扫描覆盖 673 篇 Markdown，其中技术模块 640 篇。专项记录包含 199 篇文章的 278 个改写段落；加上后续纠错，本轮实际正文或目标说明修改涉及 206 个文件。

这些数字分别表示扫描范围、段落改写范围和文件修改范围，不表示所有文章逐行人工深审、所有 API 已复核或所有代码已运行。

## 各模块的段落改写

| 模块 | 有前后对照的文章 | 改写段落 |
|---|---:|---:|
| 01-go-backend | 7 | 82 |
| 02-nextjs-frontend | 15 | 19 |
| 03-tanstack-stack | 12 | 12 |
| 04-multiplatform-apps | 23 | 23 |
| 05-kotlin-compose | 13 | 13 |
| 06-swift-swiftui | 18 | 18 |
| 07-php-mastery | 12 | 12 |
| 08-java-revisited | 26 | 26 |
| 09-nodejs-backend | 19 | 19 |
| 10-python-discovery | 15 | 15 |
| 11-rust-cross-platform | 39 | 39 |

完整前后文本保存在 [editorial-changes.json](editorial-changes.json)。记录中的 original_line 是改写前行号，不能当成当前文件行号。逐篇处理层级见 [coverage.md](coverage.md)。

## 改写达到什么程度

- 名称重复：说明它处理的具体问题，以及输入、输出或职责边界。
- 操作建议：解释机制、使用条件与不适用场景，避免把按需选项写成固定规则。
- 学习目标：提供读者可以操作或判断的结果，替换单独的“理解”“掌握”。
- 技术断言：对已发现的错误检查官方资料，并同步检查附近示例；没有核验的内容不追加“已验证”标签。

例如 QueryClient 的稳定实例需要区分浏览器与 SSR 请求隔离；React 的对象初始状态并非一律要用惰性初始化；Java record 的字段不可重新赋值不等于引用对象深度不可变；Rust repr(C) 也不等于跨机器的序列化协议。相关段落已分别说明条件。

## 追加的正文与代码纠错

- [01-go-backend/advanced-topics/architecture/01-microservices-design.md](../../../../01-go-backend/advanced-topics/architecture/01-microservices-design.md)：重写业务边界、拆分依据与一致性选择，增加订单流程及失败场景。
- [01-go-backend/frameworks/03-gorm-orm-complete.md](../../../../01-go-backend/frameworks/03-gorm-orm-complete.md)：纠正查询钩子、隐式延迟加载和复合主键说明，移除无依据的功能最完整断言。
- [01-go-backend/frameworks/01-gin-framework-basics.md](../../../../01-go-backend/frameworks/01-gin-framework-basics.md)：解释绑定、业务校验、授权和统一错误响应的责任边界。
- [01-go-backend/reference/framework-essentials/02-gorm-orm.md](../../../../01-go-backend/reference/framework-essentials/02-gorm-orm.md)：替换含伪密码哈希和异步使用事务的钩子示例；修正学生关联查询的结果接收对象。Go 示例尚未编译运行。
- [01-go-backend/reference/framework-essentials/01-gin-framework.md](../../../../01-go-backend/reference/framework-essentials/01-gin-framework.md)：请求媒体类型改用解析，实际读取增加大小限制；解释读取错误映射与尾随数据校验。Go 示例尚未编译运行。
- [01-go-backend/reference/language-concepts/03-go-programming-essentials.md](../../../../01-go-backend/reference/language-concepts/03-go-programming-essentials.md)：说明何时需要自定义错误类型，以及与错误包装的区别。
- [02-nextjs-frontend/basics/08-first-project.md](../../../../02-nextjs-frontend/basics/08-first-project.md)：把性能监控扩展改为固定条件下的测量和改动对比。
- [01-go-backend/basics/01-environment-setup.md](../../../../01-go-backend/basics/01-environment-setup.md)：解释编辑器扩展与工具链的关系，移除额外插件是必需项的说法。
- [01-go-backend/deployment/02-ci-cd-pipelines.md](../../../../01-go-backend/deployment/02-ci-cd-pipelines.md)：将掌握工作流改为触发、执行和失败状态的可检验目标。
- [01-go-backend/README.md](../../../../01-go-backend/README.md)：将微服务经验说明改为边界、超时、重试与一致性目标。

## 复核边界

全仓短条目检测剩余命中不直接视为缺陷：项目中的“ORM：GORM”“数据库：Supabase 托管数据库”属于工具选型映射，应结合下文判断，无需为了消除信号改成长段落。App Store 文档的“无门槛”指审核访问条件，也不是学习零前提声明；该平台规则本轮未重新核验。

本轮被移除的内部小标题使用近似 GitHub slug 查找站内入链，未发现指向它们的入链；后续另做静态章节锚点检查，见 anchors.json；没有声称验证全部渲染器。文件相对链接、代码围栏与 diff 空白检查结果见 [validation.json](validation.json)。运行示例记录仅覆盖其中列明的样例。

后续全库补充已处理台账中的导航整理文章，记录见 full-library-pass.json 与 coverage.md。本文件只描述较早专项改写，不能用它的范围代替最终台账；语言集合逐项版本核对、大型历史工程运行和易变版本维护仍需持续进行。
